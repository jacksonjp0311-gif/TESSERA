from __future__ import annotations

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


def calibrate_phase_duration_policy(
    trajectories: list[tuple[list[AgentEvent], bool]],
    *,
    minimum_support: int = 3,
    minimum_margin_ms: float = 25.0,
    mad_multiplier: float = 3.0,
) -> dict:
    """Calibrate phase duration bounds from declared-clean trajectories only."""
    by_phase: dict[str, list[float]] = {}
    clean_count = 0
    for events, degraded in trajectories:
        if degraded:
            continue
        clean_count += 1
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
        margin = max(minimum_margin_ms, mad_multiplier * 1.4826 * mad)
        bound = PhaseDurationBound(
            phase=phase,
            support=len(values),
            median_ms=center,
            mad_ms=mad,
            upper_ms=center + margin,
        )
        if bound.support >= minimum_support:
            bounds[phase] = asdict(bound)
    return {
        "schema": "TESSERA-PHASE-DURATION-CALIBRATION-v0.1",
        "clean_trajectory_count": clean_count,
        "minimum_support": minimum_support,
        "minimum_margin_ms": minimum_margin_ms,
        "mad_multiplier": mad_multiplier,
        "bounds": bounds,
        "claim_boundary": (
            "Normal-only controlled calibration creates bounded diagnostic "
            "thresholds; it does not establish production operating limits."
        ),
    }


def _phase_conditioned_policy(
    events: list[AgentEvent],
    calibration: dict,
) -> tuple[bool, bool, bool, list[dict]]:
    """Return warning, memory candidate, abstention, and phase evidence."""
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
        "decision_accuracy": float(
            np.mean(warnings == labels)
        ),
        "mean_latency_ms": float(
            np.mean([row["latency_ms"] for row in rows])
        ),
    }
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
    rows = []
    for events, degraded in holdout_set:
        start = time.perf_counter()
        warning, memory, abstained, evidence = _phase_conditioned_policy(
            events, calibration
        )
        rows.append(
            {
                "degraded": degraded,
                "warning": warning,
                "memory_candidate": memory,
                "abstained": abstained,
                "phase_evidence": evidence,
                "latency_ms": (time.perf_counter() - start) * 1000.0,
            }
        )
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
        "policy": _summarize(rows),
        "rows": rows,
        "claim_boundary": (
            "Fresh controlled telemetry holdout evidence validates only this "
            "privacy-safe phase-duration diagnostic, not live agent utility."
        ),
    }
