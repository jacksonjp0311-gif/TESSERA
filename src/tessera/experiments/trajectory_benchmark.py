from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass

import numpy as np

from tessera.plugin import TesseraPlugin
from tessera.plugin.contracts import AgentEvent
from tessera.plugin.trajectory import vectorize_events


def _trajectory(
    *,
    seed: int,
    degraded: bool,
    length: int = 12,
    explicit_failure: bool = True,
) -> list[AgentEvent]:
    rng = np.random.default_rng(seed)
    events = []
    for index in range(length):
        progress = max(0.0, (index - (length - 4)) / 3.0)
        pressure = progress if degraded else 0.0
        duration = 100.0 + rng.normal(0.0, 5.0) + 180.0 * pressure
        tokens = 300.0 + rng.normal(0.0, 12.0) + 120.0 * pressure
        retry = float(
            explicit_failure and degraded and index >= length - 2
        )
        error = float(
            explicit_failure and degraded and index == length - 1
        )
        events.append(
            AgentEvent(
                event_id=f"trajectory-{seed}-{index}",
                kind=("tool_call" if index % 3 else "test_result"),
                timestamp=float(index),
                features={
                    "duration_ms": float(duration),
                    "token_count": float(tokens),
                    "retry": retry,
                    "error": error,
                    "tests_failed": error,
                },
            )
        )
    return events


def _recency_policy(events: list[AgentEvent]) -> tuple[bool, bool]:
    matrix = vectorize_events(events)
    current = matrix[-1]
    previous = matrix[-2]
    duration_index = 0
    jump = current[duration_index] > max(
        previous[duration_index] * 1.5, previous[duration_index] + 50.0
    )
    explicit = bool(
        events[-1].features.get("error", 0.0)
        or events[-1].features.get("retry", 0.0)
    )
    warning = bool(jump or explicit)
    return warning, not warning


def _summary_policy(events: list[AgentEvent]) -> tuple[bool, bool]:
    matrix = vectorize_events(events)
    history = matrix[:-1]
    current = matrix[-1]
    center = np.median(history, axis=0)
    mad = np.median(np.abs(history - center), axis=0)
    scale = np.where(mad > 1e-6, 1.4826 * mad, 1.0)
    score = float(np.mean(np.abs(current - center) / scale))
    warning = score > 1.5
    return warning, not warning


@dataclass(frozen=True)
class PhaseDurationBound:
    phase: str
    support: int
    median_ms: float
    mad_ms: float
    upper_ms: float


def trajectory_profile(events: list[AgentEvent]) -> str:
    """Hash only privacy-safe phase/state structure, never payload content."""
    structure = [
        [
            str(event.metadata.get("phase", "UNKNOWN")).upper(),
            str(event.metadata.get("state", "")).upper(),
        ]
        for event in events
    ]
    payload = json.dumps(structure, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def calibrate_phase_duration_policy(
    trajectories: list[tuple[list[AgentEvent], bool]],
    *,
    false_warning_budget: float = 0.05,
    execution_jitter_guard_ms: float = 10.0,
) -> dict:
    """Finite-sample rank calibration from declared-clean trajectories only."""
    if not 0.0 < false_warning_budget < 1.0:
        raise ValueError("false_warning_budget must be between zero and one")
    minimum_support = math.ceil(1.0 / false_warning_budget) - 1
    by_phase: dict[str, list[float]] = {}
    clean_count = 0
    profiles: dict[str, int] = {}
    for events, degraded in trajectories:
        if degraded:
            continue
        clean_count += 1
        profile = trajectory_profile(events)
        profiles[profile] = profiles.get(profile, 0) + 1
        for event in events:
            duration = float(event.features.get("duration_ms", 0.0))
            phase = str(event.metadata.get("phase", "UNKNOWN")).upper()
            state = str(event.metadata.get("state", "")).upper()
            if duration <= 0.0 or state != "OK":
                continue
            by_phase.setdefault(phase, []).append(duration)
    bounds = {}
    for phase, values in sorted(by_phase.items()):
        sample = np.asarray(values, dtype=float)
        center = float(np.median(sample))
        mad = float(np.median(np.abs(sample - center)))
        rank = min(
            len(sample),
            math.ceil(
                (len(sample) + 1) * (1.0 - false_warning_budget)
            ),
        )
        rank_value = float(np.sort(sample)[rank - 1])
        bound = PhaseDurationBound(
            phase=phase,
            support=len(values),
            median_ms=center,
            mad_ms=mad,
            upper_ms=rank_value + execution_jitter_guard_ms,
        )
        if bound.support >= minimum_support:
            bounds[phase] = asdict(bound)
    return {
        "schema": "TESSERA-PHASE-DURATION-CALIBRATION-v0.2",
        "clean_trajectory_count": clean_count,
        "false_warning_budget": false_warning_budget,
        "minimum_support": minimum_support,
        "execution_jitter_guard_ms": execution_jitter_guard_ms,
        "profile_counts": profiles,
        "allowed_profiles": sorted(
            profile
            for profile, support in profiles.items()
            if support >= minimum_support
        ),
        "bounds": bounds,
        "calibration_sufficient": bool(bounds)
        and bool(profiles)
        and all(
            len(values) >= minimum_support for values in by_phase.values()
        )
        and any(
            support >= minimum_support for support in profiles.values()
        ),
        "claim_boundary": (
            "Finite-sample rank calibration assumes exchangeable clean "
            "sessions and does not establish production operating limits."
        ),
    }


def _phase_conditioned_policy(
    events: list[AgentEvent],
    calibration: dict,
) -> tuple[bool, bool, bool, list[dict]]:
    """Return warning, memory candidate, abstention, and phase evidence."""
    profile = trajectory_profile(events)
    if (
        not calibration.get("calibration_sufficient", False)
        or profile not in calibration.get("allowed_profiles", [])
    ):
        return False, False, True, [
            {
                "profile": profile,
                "reason": (
                    "insufficient_calibration"
                    if not calibration.get("calibration_sufficient", False)
                    else "workflow_profile_mismatch"
                ),
            }
        ]
    evidence = []
    for event in events:
        duration = float(event.features.get("duration_ms", 0.0))
        phase = str(event.metadata.get("phase", "UNKNOWN")).upper()
        state = str(event.metadata.get("state", "")).upper()
        bound = calibration["bounds"].get(phase)
        if duration <= 0.0 or state != "OK" or bound is None:
            continue
        evidence.append(
            {
                "phase": phase,
                "duration_ms": duration,
                "upper_ms": float(bound["upper_ms"]),
                "exceeded": duration > float(bound["upper_ms"]),
            }
        )
    abstained = not evidence
    warning = any(item["exceeded"] for item in evidence)
    memory = bool(evidence) and not warning
    return warning, memory, abstained, evidence


def archive_trajectory_cohort(
    path: str,
    out_path: str,
    *,
    role: str,
    minimum_prefix: int = 9,
    last_enriched_sessions: int | None = None,
    session_ids: list[str] | None = None,
) -> dict:
    """Write an immutable privacy-sanitized cohort outside rotating latest."""
    from pathlib import Path

    from tessera.plugin.privacy_capture import capture_local_trajectories

    trajectories, manifest = capture_local_trajectories(
        path,
        minimum_prefix=minimum_prefix,
        last_enriched_sessions=last_enriched_sessions,
        session_ids=session_ids,
    )
    rows = []
    for events, degraded in trajectories:
        rows.append(
            {
                "degraded": degraded,
                "profile": trajectory_profile(events),
                "events": [
                    {
                        "event_id": event.event_id,
                        "kind": event.kind,
                        "timestamp": event.timestamp,
                        "features": event.features,
                        "metadata": event.metadata,
                    }
                    for event in events
                ],
            }
        )
    cohort_payload = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    data = {
        "schema": "TESSERA-SANITIZED-TRAJECTORY-COHORT-v0.1",
        "role": role,
        "cohort_sha256": hashlib.sha256(
            cohort_payload.encode("utf-8")
        ).hexdigest(),
        "capture_manifest": manifest,
        "trajectory_count": len(rows),
        "clean_count": sum(not row["degraded"] for row in rows),
        "degraded_count": sum(row["degraded"] for row in rows),
        "trajectories": rows,
        "claim_boundary": (
            "Archived sanitized cohorts retain numeric operational metadata "
            "only and grant no monitoring or intervention authority."
        ),
    }
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(data, indent=2)
    if target.exists() and target.read_text(encoding="utf-8") != rendered:
        raise FileExistsError(f"immutable cohort already exists: {target}")
    target.write_text(rendered, encoding="utf-8")
    return data


def load_trajectory_cohort(path: str) -> list[tuple[list[AgentEvent], bool]]:
    from pathlib import Path

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    payload = json.dumps(
        data["trajectories"], sort_keys=True, separators=(",", ":")
    )
    observed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if observed != data["cohort_sha256"]:
        raise ValueError("trajectory cohort hash mismatch")
    trajectories = []
    for row in data["trajectories"]:
        events = [
            AgentEvent(
                event_id=event["event_id"],
                kind=event["kind"],
                timestamp=float(event["timestamp"]),
                features={
                    key: float(value)
                    for key, value in event["features"].items()
                },
                metadata={
                    key: str(value)
                    for key, value in event["metadata"].items()
                },
            )
            for event in row["events"]
        ]
        trajectories.append((events, bool(row["degraded"])))
    return trajectories


def evaluate_phase_specialist(
    trajectories: list[tuple[list[AgentEvent], bool]],
    calibration: dict,
    *,
    measure_latency: bool = True,
) -> dict:
    rows = []
    for events, degraded in trajectories:
        start = time.perf_counter()
        warning, memory, abstained, evidence = _phase_conditioned_policy(
            events, calibration
        )
        row = {
            "degraded": degraded,
            "warning": warning,
            "memory_candidate": memory,
            "abstained": abstained,
            "profile": trajectory_profile(events),
            "phase_evidence": evidence,
        }
        if measure_latency:
            row["latency_ms"] = (time.perf_counter() - start) * 1000.0
        rows.append(row)
    covered = [row for row in rows if not row["abstained"]]
    result = {
        "trajectory_count": len(rows),
        "coverage": len(covered) / max(1, len(rows)),
        "warning_rate": (
            sum(row["warning"] for row in covered) / max(1, len(covered))
        ),
        "rows": rows,
    }
    if covered and any(row["degraded"] for row in covered) and any(
        not row["degraded"] for row in covered
    ):
        result["policy"] = _summarize(covered)
    return result


def run_evo020_archived_benchmark(
    calibration_path: str,
    confirmation_path: str,
    natural_shadow_path: str,
) -> dict:
    calibration_set = load_trajectory_cohort(calibration_path)
    confirmation_set = load_trajectory_cohort(confirmation_path)
    natural_set = load_trajectory_cohort(natural_shadow_path)
    calibration = calibrate_phase_duration_policy(calibration_set)
    return {
        "schema": "TESSERA-EVO-020-ARCHIVED-SHADOW-v0.1",
        "calibration": calibration,
        "controlled_confirmation": evaluate_phase_specialist(
            confirmation_set, calibration, measure_latency=False
        ),
        "natural_shadow": evaluate_phase_specialist(
            natural_set, calibration, measure_latency=False
        ),
        "authority": {
            "read_only": True,
            "warning_emitted_to_host": False,
            "memory_write": False,
            "intervention": False,
        },
        "claim_boundary": (
            "Shadow evaluation measures coverage and diagnostic behavior only; "
            "it does not authorize live warnings, interventions, or memory."
        ),
    }


def _summarize(rows: list[dict]) -> dict:
    labels = np.asarray([row["degraded"] for row in rows], dtype=int)
    warnings = np.asarray([row["warning"] for row in rows], dtype=int)
    memories = np.asarray([row["memory_candidate"] for row in rows], dtype=int)
    anomaly = labels == 1
    normal = labels == 0
    summary = {
        "failure_recall": float(warnings[anomaly].mean()),
        "false_intervention_rate": float(warnings[normal].mean()),
        "safe_memory_recall": float(memories[normal].mean()),
        "unsafe_memory_rate": float(memories[anomaly].mean()),
        "decision_accuracy": float(np.mean(warnings == labels)),
    }
    if rows and all("latency_ms" in row for row in rows):
        summary["mean_latency_ms"] = float(
            np.mean([row["latency_ms"] for row in rows])
        )
    if any("abstained" in row for row in rows):
        summary["abstention_rate"] = float(
            np.mean([row.get("abstained", False) for row in rows])
        )
    return summary


def evaluate_labeled_trajectories(
    trajectories: list[tuple[list[AgentEvent], bool]],
) -> dict:
    rows = {"recency": [], "summary": [], "tessera": []}
    for events, degraded in trajectories:
        for name, policy in (
            ("recency", _recency_policy),
            ("summary", _summary_policy),
        ):
            start = time.perf_counter()
            warning, memory = policy(events)
            rows[name].append(
                {
                    "degraded": degraded,
                    "warning": warning,
                    "memory_candidate": memory,
                    "latency_ms": (time.perf_counter() - start) * 1000.0,
                }
            )
        plugin = TesseraPlugin(neural_min_events=8)
        plugin.observe(events)
        start = time.perf_counter()
        packet = plugin.infer()
        rows["tessera"].append(
            {
                "degraded": degraded,
                "warning": packet.warning,
                "memory_candidate": packet.memory_candidate,
                "latency_ms": (time.perf_counter() - start) * 1000.0,
                "selected_prediction_expert": (
                    packet.selected_prediction_expert
                ),
            }
        )
    summaries = {name: _summarize(value) for name, value in rows.items()}
    return {
        "policies": summaries,
        "tessera_beats_both_controls": bool(
            summaries["tessera"]["decision_accuracy"]
            > max(
                summaries["recency"]["decision_accuracy"],
                summaries["summary"]["decision_accuracy"],
            )
        ),
        "rows": rows,
    }


def run_trajectory_benchmark(
    *,
    seeds: list[int] | None = None,
    length: int = 12,
    explicit_failure: bool = True,
) -> dict:
    seeds = seeds or list(range(12))
    trajectories = []
    for index, seed in enumerate(seeds):
        degraded = bool(index % 2)
        events = _trajectory(
            seed=seed,
            degraded=degraded,
            length=length,
            explicit_failure=explicit_failure,
        )
        trajectories.append((events, degraded))
    evaluation = evaluate_labeled_trajectories(trajectories)
    return {
        "schema": "TESSERA-OFFLINE-TRAJECTORY-BENCHMARK-v0.1",
        "trajectory_count": len(seeds),
        "trajectory_length": length,
        "explicit_failure": explicit_failure,
        "degraded_count": sum(index % 2 for index in range(len(seeds))),
        **evaluation,
        "claim_boundary": (
            "Synthetic offline trajectory utility is not live agent utility, "
            "production readiness, or autonomous authority."
        ),
    }


def run_local_capture_benchmark(
    path: str,
    *,
    minimum_prefix: int = 7,
    last_enriched_sessions: int | None = None,
) -> dict:
    from tessera.plugin.privacy_capture import (
        audit_trajectory_identifiability,
        capture_local_trajectories,
    )

    trajectories, manifest = capture_local_trajectories(
        path,
        minimum_prefix=minimum_prefix,
        last_enriched_sessions=last_enriched_sessions,
    )
    evaluation = evaluate_labeled_trajectories(trajectories)
    return {
        "schema": "TESSERA-LOCAL-TRAJECTORY-BENCHMARK-v0.1",
        "capture_manifest": manifest,
        "identifiability_audit": audit_trajectory_identifiability(
            trajectories
        ),
        **evaluation,
        "claim_boundary": (
            "Small privacy-sanitized local history is an offline diagnostic, "
            "not live agent utility or monitoring authority."
        ),
    }


def run_phase_conditioned_holdout_benchmark(
    path: str,
    *,
    minimum_prefix: int = 9,
    calibration_sessions: int = 8,
    holdout_sessions: int = 8,
) -> dict:
    """Calibrate on one controlled cohort and evaluate a later frozen holdout."""
    from tessera.plugin.privacy_capture import (
        audit_trajectory_identifiability,
        capture_local_trajectories,
    )

    total = calibration_sessions + holdout_sessions
    trajectories, manifest = capture_local_trajectories(
        path,
        minimum_prefix=minimum_prefix,
        last_enriched_sessions=total,
    )
    if len(trajectories) != total:
        raise ValueError(
            f"expected {total} captured sessions, got {len(trajectories)}"
        )
    calibration_set = trajectories[:calibration_sessions]
    holdout_set = trajectories[calibration_sessions:]
    calibration = calibrate_phase_duration_policy(calibration_set)
    evaluation = evaluate_phase_specialist(holdout_set, calibration)
    return {
        "schema": "TESSERA-PHASE-CONDITIONED-HOLDOUT-v0.1",
        "capture_manifest": manifest,
        "calibration_session_count": len(calibration_set),
        "holdout_session_count": len(holdout_set),
        "calibration": calibration,
        "calibration_identifiability": audit_trajectory_identifiability(
            calibration_set
        ),
        "holdout_identifiability": audit_trajectory_identifiability(
            holdout_set
        ),
        "policy": evaluation.get("policy", {}),
        "coverage": evaluation["coverage"],
        "rows": evaluation["rows"],
        "claim_boundary": (
            "Fresh controlled telemetry holdout evidence validates only this "
            "privacy-safe phase-duration diagnostic, not live agent utility."
        ),
    }
