from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import numpy as np

from tessera.plugin.contracts import AgentEvent
from tessera.plugin.trajectory import vectorize_events


ALLOWED_SOURCE_FIELDS = {"schema", "timestamp", "phase", "state"}
SAFE_TELEMETRY_FIELDS = {
    "session_id",
    "event_index",
    "elapsed_ms",
    "exit_code",
}
DENIED_SOURCE_FIELDS = {
    "command",
    "detail",
    "root",
    "mirror_dir",
}
ALLOWED_PHASES = {
    "REHYDRATE",
    "MIRROR",
    "GEOMETRY",
    "LOOPBOOK",
    "CHECK",
    "RUN",
    "VALIDATE",
    "LEDGER",
    "PUSH",
    "ROOT",
    "LESSON",
}
ALLOWED_STATES = {"RUN", "OK", "SKIP", "FAIL"}


def _parse_time(value: str) -> float:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return 0.0


def audit_event_source(path: str | Path) -> dict:
    path = Path(path)
    records = []
    malformed = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                records.append(value)
        except json.JSONDecodeError:
            malformed += 1
    keys = {str(key) for record in records for key in record}
    return {
        "schema": "TESSERA-LOCAL-TRAJECTORY-PRIVACY-AUDIT-v0.1",
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "record_count": len(records),
        "malformed_count": malformed,
        "observed_fields": sorted(keys),
        "allowed_fields": sorted(ALLOWED_SOURCE_FIELDS),
        "safe_optional_fields": sorted(SAFE_TELEMETRY_FIELDS),
        "denied_fields_present": sorted(keys & DENIED_SOURCE_FIELDS),
        "raw_payload_retained": False,
        "capture_permitted": not malformed
        and ALLOWED_SOURCE_FIELDS.issubset(keys),
        "claim_boundary": (
            "Privacy audit permits numeric metadata capture only; it does not "
            "authorize prompts, commands, paths, details, or raw outputs."
        ),
    }


def _load_records(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def _sessions(records: list[dict]) -> list[list[dict]]:
    enriched = [record for record in records if record.get("session_id")]
    if enriched:
        order = []
        grouped: dict[str, list[dict]] = {}
        for record in enriched:
            session_id = str(record["session_id"])
            if session_id not in grouped:
                grouped[session_id] = []
                order.append(session_id)
            grouped[session_id].append(record)
        legacy = [record for record in records if not record.get("session_id")]
        return _sessions(legacy) + [grouped[session_id] for session_id in order]
    sessions = []
    current = []
    for record in records:
        current.append(record)
        if str(record.get("phase", "")).upper() == "ROOT":
            sessions.append(current)
            current = []
    if current:
        sessions.append(current)
    return sessions


def _sanitize_prefix(
    records: list[dict],
    *,
    session_index: int,
) -> list[AgentEvent]:
    events = []
    previous_time = None
    phase_counts: dict[str, int] = {}
    previous_phase = ""
    for index, record in enumerate(records):
        phase = str(record.get("phase", "")).upper()
        state = str(record.get("state", "")).upper()
        if phase not in ALLOWED_PHASES or state not in ALLOWED_STATES:
            continue
        timestamp = _parse_time(str(record.get("timestamp", "")))
        timestamp_duration = (
            0.0 if previous_time is None or timestamp <= 0.0
            else max(0.0, (timestamp - previous_time) * 1000.0)
        )
        duration_ms = float(
            record.get("elapsed_ms", timestamp_duration) or 0.0
        )
        phase_counts[phase] = phase_counts.get(phase, 0) + 1
        transition = float(bool(previous_phase and phase != previous_phase))
        phase_code = float(sorted(ALLOWED_PHASES).index(phase) + 1)
        events.append(
            AgentEvent(
                event_id=f"captured-{session_index}-{index}",
                kind="plan_transition",
                timestamp=timestamp,
                features={
                    "duration_ms": duration_ms,
                    "history_turns": float(index + 1),
                    "resource_cost": phase_code,
                    "tool_count": transition,
                    "retry": float(max(0, phase_counts[phase] - 1)),
                    "blocked": float(state == "SKIP"),
                    "finish_reason_length": float(
                        record.get("exit_code", 0) or 0
                    ),
                    "error": 0.0,
                    "token_count": 0.0,
                },
                metadata={
                    "capture": "privacy_sanitized_v0.1",
                    "phase": phase,
                    "state": state,
                },
            )
        )
        previous_time = timestamp
        previous_phase = phase
    return events


def capture_local_trajectories(
    path: str | Path,
    *,
    minimum_prefix: int = 7,
    last_enriched_sessions: int | None = None,
) -> tuple[list[tuple[list[AgentEvent], bool]], dict]:
    path = Path(path)
    audit = audit_event_source(path)
    if not audit["capture_permitted"]:
        raise ValueError("event source failed privacy audit")
    captured = []
    excluded = []
    sessions = _sessions(_load_records(path))
    if last_enriched_sessions is not None:
        enriched = [
            session for session in sessions
            if session and session[0].get("session_id")
        ]
        sessions = enriched[-last_enriched_sessions:]
    for session_index, session in enumerate(sessions):
        failure_indices = [
            index
            for index, record in enumerate(session)
            if str(record.get("state", "")).upper() == "FAIL"
        ]
        degraded = bool(failure_indices)
        available = (
            failure_indices[0]
            if degraded
            else next(
                (
                    index
                    for index, record in enumerate(session)
                    if str(record.get("phase", "")).upper() == "ROOT"
                ),
                len(session),
            )
        )
        if available < minimum_prefix:
            excluded.append(
                {
                    "session_index": session_index,
                    "reason": "insufficient_precursor_context",
                    "available_events": available,
                }
            )
            continue
        prefix = session[:minimum_prefix]
        captured.append(
            (
                _sanitize_prefix(prefix, session_index=session_index),
                degraded,
            )
        )
    manifest = {
        "schema": "TESSERA-LOCAL-TRAJECTORY-CAPTURE-v0.1",
        "privacy_audit": audit,
        "minimum_prefix": minimum_prefix,
        "last_enriched_sessions": last_enriched_sessions,
        "captured_session_count": len(captured),
        "degraded_session_count": sum(label for _, label in captured),
        "clean_session_count": sum(not label for _, label in captured),
        "excluded_sessions": excluded,
        "retained_fields": [
            "duration_ms",
            "phase",
            "state",
            "phase_code",
            "transition",
            "phase_repetition",
            "skip_indicator",
            "event_index",
        ],
        "denied_fields": sorted(DENIED_SOURCE_FIELDS),
        "raw_payload_retained": False,
        "claim_boundary": (
            "Sanitized local capture is an offline diagnostic dataset only."
        ),
    }
    return captured, manifest


def audit_trajectory_identifiability(
    trajectories: list[tuple[list[AgentEvent], bool]],
) -> dict:
    """Measure whether opposite labels share identical allowed observations."""
    groups: dict[str, list[bool]] = {}
    for events, label in trajectories:
        matrix = vectorize_events(events)
        signature = hashlib.sha256(
            np.asarray(matrix, dtype="float32").tobytes()
        ).hexdigest()
        groups.setdefault(signature, []).append(bool(label))
    conflicting = {
        signature: labels
        for signature, labels in groups.items()
        if len(set(labels)) > 1
    }
    total = max(1, len(trajectories))
    majority_correct = sum(
        max(labels.count(False), labels.count(True))
        for labels in groups.values()
    )
    degraded = sum(label for _, label in trajectories)
    clean_signatures = {
        signature
        for signature, labels in groups.items()
        if False in labels
    }
    identifiable_degraded = sum(
        labels.count(True)
        for signature, labels in groups.items()
        if signature not in clean_signatures
    )
    return {
        "schema": "TESSERA-TRAJECTORY-IDENTIFIABILITY-AUDIT-v0.1",
        "trajectory_count": len(trajectories),
        "unique_observation_count": len(groups),
        "conflicting_observation_count": len(conflicting),
        "conflicting_trajectory_count": sum(
            len(labels) for labels in conflicting.values()
        ),
        "deterministic_accuracy_upper_bound": majority_correct / total,
        "failure_recall_upper_bound_at_zero_false_intervention": (
            identifiable_degraded / max(1, degraded)
        ),
        "identifiable_for_zero_false_intervention": not conflicting,
        "claim_boundary": (
            "Identifiability audit detects observational limits; it does not "
            "prove any model can reach the upper bound."
        ),
    }
