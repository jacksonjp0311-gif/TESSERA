from __future__ import annotations

import hashlib
import json
import math
import time
from copy import deepcopy
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


def _completed_phase_durations(events: list[AgentEvent]) -> dict[str, float]:
    values = {}
    for event in events:
        duration = float(event.features.get("duration_ms", 0.0))
        phase = str(event.metadata.get("phase", "UNKNOWN")).upper()
        state = str(event.metadata.get("state", "")).upper()
        if duration > 0.0 and state == "OK":
            values[phase] = duration
    return values


def calibrate_workflow_session_policy(
    trajectories: list[tuple[list[AgentEvent], bool]],
    *,
    false_warning_budget: float = 0.05,
    minimum_scale_ms: float = 5.0,
) -> dict:
    """Split-conformal calibration of one maximum cross-phase session score."""
    if not 0.0 < false_warning_budget < 1.0:
        raise ValueError("false_warning_budget must be between zero and one")
    minimum_support = math.ceil(1.0 / false_warning_budget) - 1
    clean = [
        events for events, degraded in trajectories if not degraded
    ]
    profiles = {trajectory_profile(events) for events in clean}
    reference_count = len(clean) // 2
    reference = clean[:reference_count]
    score_calibration = clean[reference_count:]
    phases = sorted(
        set.intersection(
            *[
                set(_completed_phase_durations(events))
                for events in reference
            ]
        )
    ) if reference else []
    phase_reference = {}
    for phase in phases:
        sample = np.asarray(
            [
                _completed_phase_durations(events)[phase]
                for events in reference
            ],
            dtype=float,
        )
        center = float(np.median(sample))
        mad = float(np.median(np.abs(sample - center)))
        phase_reference[phase] = {
            "median_ms": center,
            "mad_ms": mad,
            "scale_ms": max(minimum_scale_ms, 1.4826 * mad),
            "support": len(sample),
        }

    def score(events: list[AgentEvent]) -> float:
        durations = _completed_phase_durations(events)
        return max(
            (
                (durations[phase] - values["median_ms"])
                / values["scale_ms"]
                for phase, values in phase_reference.items()
                if phase in durations
            ),
            default=float("-inf"),
        )

    calibration_scores = [score(events) for events in score_calibration]
    threshold = None
    if calibration_scores:
        rank = min(
            len(calibration_scores),
            math.ceil(
                (len(calibration_scores) + 1)
                * (1.0 - false_warning_budget)
            ),
        )
        threshold = float(np.sort(calibration_scores)[rank - 1])
    sufficient = (
        len(profiles) == 1
        and len(reference) >= minimum_support
        and len(score_calibration) >= minimum_support
        and bool(phase_reference)
        and threshold is not None
    )
    return {
        "schema": "TESSERA-WORKFLOW-SESSION-CALIBRATION-v0.1",
        "clean_trajectory_count": len(clean),
        "reference_count": len(reference),
        "score_calibration_count": len(score_calibration),
        "false_warning_budget": false_warning_budget,
        "minimum_support_per_partition": minimum_support,
        "minimum_scale_ms": minimum_scale_ms,
        "allowed_profiles": sorted(profiles) if sufficient else [],
        "phase_reference": phase_reference,
        "session_score_threshold": threshold,
        "calibration_sufficient": sufficient,
        "claim_boundary": (
            "Split-conformal calibration controls one session-level score "
            "under exchangeability; it does not establish production safety."
        ),
    }


def _workflow_session_policy(
    events: list[AgentEvent],
    calibration: dict,
) -> tuple[bool, bool, bool, list[dict]]:
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
    durations = _completed_phase_durations(events)
    evidence = []
    scores = []
    for phase, reference in calibration["phase_reference"].items():
        if phase not in durations:
            continue
        score = (
            durations[phase] - float(reference["median_ms"])
        ) / float(reference["scale_ms"])
        scores.append(score)
        evidence.append(
            {
                "phase": phase,
                "duration_ms": durations[phase],
                "score": score,
            }
        )
    if not scores:
        return False, False, True, [
            {"profile": profile, "reason": "no_calibrated_phase_observed"}
        ]
    session_score = max(scores)
    threshold = float(calibration["session_score_threshold"])
    warning = session_score > threshold
    evidence.append(
        {
            "session_score": session_score,
            "session_score_threshold": threshold,
            "exceeded": warning,
        }
    )
    return warning, not warning, False, evidence


def evaluate_workflow_session_specialist(
    trajectories: list[tuple[list[AgentEvent], bool]],
    calibration: dict,
) -> dict:
    rows = []
    for events, degraded in trajectories:
        warning, memory, abstained, evidence = _workflow_session_policy(
            events, calibration
        )
        rows.append(
            {
                "degraded": degraded,
                "warning": warning,
                "memory_candidate": memory,
                "abstained": abstained,
                "profile": trajectory_profile(events),
                "evidence": evidence,
            }
        )
    covered = [row for row in rows if not row["abstained"]]
    return {
        "trajectory_count": len(rows),
        "coverage": len(covered) / max(1, len(rows)),
        "warning_rate": (
            sum(row["warning"] for row in covered) / max(1, len(covered))
        ),
        "rows": rows,
    }


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


def run_evo021_natural_clean_benchmark(
    calibration_path: str,
    confirmation_path: str,
) -> dict:
    calibration_set = load_trajectory_cohort(calibration_path)
    confirmation_set = load_trajectory_cohort(confirmation_path)
    calibration = calibrate_workflow_session_policy(calibration_set)
    return {
        "schema": "TESSERA-EVO-021-NATURAL-SESSION-SHADOW-v0.1",
        "calibration": calibration,
        "confirmation": evaluate_workflow_session_specialist(
            confirmation_set, calibration
        ),
        "failure_recall_measured": False,
        "authority": {
            "read_only": True,
            "warning_emitted_to_host": False,
            "memory_write": False,
            "intervention": False,
        },
        "claim_boundary": (
            "Natural clean session shadow measures profile coverage and "
            "false-warning behavior only; failure sensitivity remains "
            "unmeasured."
        ),
    }


def inject_phase_delay(
    events: list[AgentEvent],
    *,
    phase: str,
    delay_ms: float,
) -> list[AgentEvent]:
    """Return a copied trajectory with delay added to one completed phase."""
    target_phase = phase.upper()
    injected = False
    result = []
    for event in events:
        features = deepcopy(event.features)
        metadata = deepcopy(event.metadata)
        if (
            not injected
            and str(metadata.get("phase", "")).upper() == target_phase
            and str(metadata.get("state", "")).upper() == "OK"
            and float(features.get("duration_ms", 0.0)) > 0.0
        ):
            features["duration_ms"] = (
                float(features["duration_ms"]) + float(delay_ms)
            )
            injected = True
        result.append(
            AgentEvent(
                event_id=event.event_id,
                kind=event.kind,
                timestamp=event.timestamp,
                features=features,
                metadata=metadata,
                contains_sensitive_data=event.contains_sensitive_data,
            )
        )
    if not injected:
        raise ValueError(f"completed phase not found for injection: {phase}")
    return result


def run_evo022_perturbation_ladder(
    base_cohort_path: str,
    calibration_path: str,
    preregistration_path: str,
) -> dict:
    from pathlib import Path

    base = load_trajectory_cohort(base_cohort_path)
    calibration = json.loads(
        Path(calibration_path).read_text(encoding="utf-8")
    )
    plan = json.loads(
        Path(preregistration_path).read_text(encoding="utf-8")
    )
    phase_rows = []
    for phase in plan["target_phases"]:
        delay_rows = []
        previous_rate = -1.0
        monotonic = True
        for delay_ms in plan["delay_ladder_ms"]:
            perturbed = [
                (
                    inject_phase_delay(
                        events,
                        phase=phase,
                        delay_ms=float(delay_ms),
                    ),
                    degraded,
                )
                for events, degraded in base
            ]
            evaluation = evaluate_workflow_session_specialist(
                perturbed, calibration
            )
            rate = float(evaluation["warning_rate"])
            monotonic = monotonic and rate >= previous_rate
            previous_rate = rate
            delay_rows.append(
                {
                    "delay_ms": delay_ms,
                    "detection_rate": rate,
                    "coverage": evaluation["coverage"],
                    "detected_count": sum(
                        row["warning"] for row in evaluation["rows"]
                    ),
                    "trajectory_count": evaluation["trajectory_count"],
                }
            )
        any_delays = [
            row["delay_ms"]
            for row in delay_rows
            if row["detection_rate"] > 0.0
        ]
        full_delays = [
            row["delay_ms"]
            for row in delay_rows
            if row["detection_rate"] == 1.0
        ]
        phase_rows.append(
            {
                "phase": phase,
                "monotonic_response": monotonic,
                "minimum_delay_with_any_detection": (
                    min(any_delays) if any_delays else None
                ),
                "minimum_delay_with_full_detection": (
                    min(full_delays) if full_delays else None
                ),
                "ladder": delay_rows,
            }
        )
    zero_delay_rates = [
        row["ladder"][0]["detection_rate"] for row in phase_rows
    ]
    gate = plan["promotion_gate"]
    passed = (
        max(zero_delay_rates, default=1.0)
        <= float(gate["zero_delay_warning_rate_max"])
        and all(row["monotonic_response"] for row in phase_rows)
        and all(
            row["minimum_delay_with_full_detection"] is not None
            and row["minimum_delay_with_full_detection"]
            <= int(gate["full_detection_required_by_ms"])
            for row in phase_rows
        )
    )
    return {
        "schema": "TESSERA-EVO-022-PERTURBATION-RESPONSE-v0.1",
        "preregistration": plan,
        "base_trajectory_count": len(base),
        "calibration_schema": calibration.get("schema"),
        "phase_results": phase_rows,
        "promotion_gate_passed": passed,
        "claim_boundary": (
            "Offline deterministic delay response is not natural failure "
            "recall, production prediction, or intervention authority."
        ),
    }


def run_evo023_mode_audit(
    cohort_path: str,
    preregistration_path: str,
) -> dict:
    from pathlib import Path

    trajectories = load_trajectory_cohort(cohort_path)
    plan = json.loads(
        Path(preregistration_path).read_text(encoding="utf-8")
    )
    split = int(plan["chronological_split"]["discovery_sessions"])
    discovery = trajectories[:split]
    validation = trajectories[split:]
    minimum_scale = float(plan["tail_definition"]["minimum_scale_ms"])
    threshold = float(plan["tail_definition"]["robust_score_threshold"])
    phase_names = sorted(
        set.intersection(
            *[
                set(_completed_phase_durations(events))
                for events, _ in discovery
            ]
        )
    )
    reference = {}
    for phase in phase_names:
        values = np.asarray(
            [
                _completed_phase_durations(events)[phase]
                for events, _ in discovery
            ],
            dtype=float,
        )
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        reference[phase] = {
            "median_ms": center,
            "scale_ms": max(minimum_scale, 1.4826 * mad),
        }

    def signature(events: list[AgentEvent]) -> tuple[str, ...]:
        durations = _completed_phase_durations(events)
        return tuple(
            phase
            for phase in phase_names
            if (
                durations[phase] - reference[phase]["median_ms"]
            ) / reference[phase]["scale_ms"] > threshold
        )

    def counts(rows):
        result: dict[tuple[str, ...], int] = {}
        examples: dict[tuple[str, ...], list[str]] = {}
        for events, _ in rows:
            value = signature(events)
            if not value:
                continue
            result[value] = result.get(value, 0) + 1
            examples.setdefault(value, []).append(
                events[0].metadata.get("session_id", "")
            )
        return result, examples

    discovery_counts, discovery_examples = counts(discovery)
    validation_counts, validation_examples = counts(validation)
    min_discovery = int(
        plan["candidate_mode_requirements"]["minimum_discovery_support"]
    )
    min_validation = int(
        plan["candidate_mode_requirements"]["minimum_validation_support"]
    )
    signatures = sorted(
        set(discovery_counts) | set(validation_counts)
    )
    candidates = []
    for value in signatures:
        discovery_support = discovery_counts.get(value, 0)
        validation_support = validation_counts.get(value, 0)
        candidates.append(
            {
                "tail_phase_signature": list(value),
                "discovery_support": discovery_support,
                "validation_support": validation_support,
                "discovery_session_ids": discovery_examples.get(value, []),
                "validation_session_ids": validation_examples.get(value, []),
                "accepted": (
                    discovery_support >= min_discovery
                    and validation_support >= min_validation
                ),
            }
        )
    accepted = [row for row in candidates if row["accepted"]]
    return {
        "schema": "TESSERA-EVO-023-MODE-AUDIT-v0.1",
        "preregistration": plan,
        "discovery_count": len(discovery),
        "validation_count": len(validation),
        "reference": reference,
        "candidate_signatures": candidates,
        "accepted_mode_count": len(accepted),
        "mode_separation_supported": bool(accepted),
        "decision": (
            "accept_recurrent_modes"
            if accepted
            else "reject_mode_separation_keep_calibration_unchanged"
        ),
        "claim_boundary": (
            "Tail recurrence audit does not identify causes, failures, or "
            "production incident classes."
        ),
    }


def _rank(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(len(values), dtype=float)
    unique, inverse, counts = np.unique(
        values, return_inverse=True, return_counts=True
    )
    for index, count in enumerate(counts):
        if count > 1:
            positions = np.flatnonzero(inverse == index)
            ranks[positions] = float(np.mean(ranks[positions]))
    return ranks


def _spearman(left: list[float], right: list[float]) -> float:
    if len(left) < 3 or len(right) != len(left):
        return 0.0
    x = _rank(np.asarray(left, dtype=float))
    y = _rank(np.asarray(right, dtype=float))
    if float(np.std(x)) <= 1e-12 or float(np.std(y)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def run_evo024_context_attribution(
    cohort_path: str,
    preregistration_path: str,
) -> dict:
    from pathlib import Path

    trajectories = load_trajectory_cohort(cohort_path)
    plan = json.loads(
        Path(preregistration_path).read_text(encoding="utf-8")
    )
    split = int(plan["chronological_split"]["discovery_sessions"])
    halves = {
        "discovery": trajectories[:split],
        "validation": trajectories[split:],
    }
    phases = plan["target_phases"]
    fields = plan["context_fields"]
    threshold = float(
        plan["association_gate"]["tail_robust_score_threshold"]
    )

    def phase_rows(rows, phase):
        values = []
        for events, _ in rows:
            for event in events:
                if (
                    str(event.metadata.get("phase", "")).upper() == phase
                    and str(event.metadata.get("state", "")).upper() == "OK"
                    and float(event.features.get("duration_ms", 0.0)) > 0.0
                ):
                    values.append(event)
                    break
        return values

    results = []
    min_corr = float(
        plan["association_gate"]["minimum_absolute_spearman_both_halves"]
    )
    min_tail = int(
        plan["association_gate"]["minimum_tail_support_both_halves"]
    )
    for phase in phases:
        phase_halves = {
            name: phase_rows(rows, phase)
            for name, rows in halves.items()
        }
        references = {}
        for name, events in phase_halves.items():
            durations = np.asarray(
                [event.features["duration_ms"] for event in events],
                dtype=float,
            )
            center = float(np.median(durations))
            mad = float(np.median(np.abs(durations - center)))
            scale = max(5.0, 1.4826 * mad)
            references[name] = (center, scale)
        for field in fields:
            halves_result = {}
            for name, events in phase_halves.items():
                durations = [
                    float(event.features["duration_ms"]) for event in events
                ]
                context = [
                    float(event.features.get(field, -1.0))
                    for event in events
                ]
                valid = [
                    index for index, value in enumerate(context)
                    if value >= 0.0
                ]
                duration_valid = [durations[index] for index in valid]
                context_valid = [context[index] for index in valid]
                center, scale = references[name]
                tail_count = sum(
                    (value - center) / scale > threshold
                    for value in duration_valid
                )
                halves_result[name] = {
                    "support": len(valid),
                    "spearman": _spearman(
                        duration_valid, context_valid
                    ),
                    "tail_support": tail_count,
                }
            discovery = halves_result["discovery"]
            validation = halves_result["validation"]
            same_sign = (
                discovery["spearman"] * validation["spearman"] > 0.0
            )
            accepted = (
                abs(discovery["spearman"]) >= min_corr
                and abs(validation["spearman"]) >= min_corr
                and same_sign
                and discovery["tail_support"] >= min_tail
                and validation["tail_support"] >= min_tail
            )
            results.append(
                {
                    "phase": phase,
                    "context_field": field,
                    "discovery": discovery,
                    "validation": validation,
                    "same_sign": same_sign,
                    "accepted": accepted,
                }
            )
    accepted = [row for row in results if row["accepted"]]
    return {
        "schema": "TESSERA-EVO-024-CONTEXT-ATTRIBUTION-v0.1",
        "preregistration": plan,
        "trajectory_count": len(trajectories),
        "associations": results,
        "accepted_association_count": len(accepted),
        "context_conditioning_supported": bool(accepted),
        "decision": (
            "allow_context_conditioning_hypothesis"
            if accepted
            else "reject_context_conditioning_keep_calibration_unchanged"
        ),
        "claim_boundary": (
            "Aggregate context association is not causal attribution, natural "
            "failure prediction, or intervention authority."
        ),
    }


def run_evo025_mechanism_attribution(
    cohort_path: str,
    preregistration_path: str,
) -> dict:
    result = run_evo024_context_attribution(
        cohort_path,
        preregistration_path,
    )
    result["schema"] = "TESSERA-EVO-025-MECHANISM-ATTRIBUTION-v0.1"
    result["mechanism_conditioning_supported"] = result.pop(
        "context_conditioning_supported"
    )
    result["decision"] = (
        "allow_mechanism_conditioning_hypothesis"
        if result["mechanism_conditioning_supported"]
        else "reject_mechanism_conditioning_keep_calibration_unchanged"
    )
    result["claim_boundary"] = (
        "Subprocess-startup and aggregate disk-I/O association is not causal "
        "attribution, natural failure prediction, or intervention authority."
    )
    return result


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
