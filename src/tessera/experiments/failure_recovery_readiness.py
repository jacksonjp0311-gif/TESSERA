from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.model.prediction_experts import predict_with_expert
from tessera.plugin.host_adapters import (
    SessionSummaryContract,
    full_session_summary,
)
from tessera.plugin.incident_governor import IncidentGovernor
from tessera.plugin.neural_checkpoints import (
    deserialize_expert,
    neural_awareness_features,
    train_neural_checkpoint,
)


def run_failure_recovery_readiness(
    preregistration_path: str | Path,
    failure_path: str | Path,
    recovery_path: str | Path,
    *,
    root: str | Path = ".",
) -> dict:
    root = Path(root)
    plan = json.loads(Path(preregistration_path).read_text(encoding="utf-8"))
    router_plan = json.loads(
        (root / "docs/research/EVO032_NEURAL_UNCERTAINTY_ROUTER_PREREGISTRATION.json")
        .read_text(encoding="utf-8")
    )
    trajectories = []
    for cohort in router_plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(str(root / cohort)))
    failure = load_trajectory_cohort(str(failure_path))
    recovery = load_trajectory_cohort(str(recovery_path))
    if len(failure) != 1 or not failure[0][1]:
        raise ValueError("evo036_requires_one_degraded_failure_prefix")
    if len(recovery) != 1 or recovery[0][1]:
        raise ValueError("evo036_requires_one_clean_recovery_prefix")

    raw = np.asarray(
        [full_session_summary(events) for events, _ in trajectories],
        dtype="float32",
    )
    selected_indices = tuple(
        int(index)
        for index in np.flatnonzero(raw[:100].std(axis=0) > 1e-6)
    )
    contract = SessionSummaryContract(selected_indices)
    sequence = raw[:, selected_indices]
    payload, checkpoint_metrics = train_neural_checkpoint(sequence[:100])
    additions = np.asarray([
        contract.project(failure[0][0]),
        contract.project(recovery[0][0]),
    ], dtype="float32")
    combined = np.concatenate([sequence, additions], axis=0)
    mean = np.asarray(payload["normalization"]["mean"], dtype=float)
    scale = np.asarray(payload["normalization"]["scale"], dtype=float)
    normalized = (combined - mean) / scale
    expert = deserialize_expert(payload["prediction_expert"])
    predictions = predict_with_expert(expert, normalized)
    scores = neural_awareness_features(
        payload,
        normalized,
        predictions,
    )["latent_drift"]
    threshold = float(plan["router"]["threshold"])
    failure_score = float(scores[119])
    recovery_score = float(scores[120])
    failure_abstained = failure_score > threshold
    recovery_released = recovery_score <= threshold

    governor = IncidentGovernor(recovery_sessions_required=1)
    before_failure = governor.govern(
        "trusted",
        neural_memory_candidate=True,
    )
    governor.record_outcome(failed=True, terminal_ok=False)
    during_incident = governor.govern(
        "trusted",
        neural_memory_candidate=True,
    )
    governor.record_outcome(failed=False, terminal_ok=True)
    after_recovery = governor.govern(
        "trusted",
        neural_memory_candidate=True,
    )

    observed_failure_episodes = len(failure)
    observed_recovery_episodes = len(recovery)
    minimum = int(
        plan["promotion_gate"]["minimum_independent_failure_episodes"]
    )
    support_sufficient = (
        observed_failure_episodes >= minimum
        and observed_recovery_episodes >= minimum
    )
    checks = {
        "preregistration_frozen_before_scoring": bool(
            plan["frozen_before_scoring"]
        ),
        "failure_prefix_excludes_failure_event": all(
            event.metadata.get("state") != "FAIL"
            for event in failure[0][0]
        ),
        "recovery_prefix_is_clean": all(
            event.metadata.get("state") != "FAIL"
            for event in recovery[0][0]
        ),
        "failure_abstained": failure_abstained,
        "recovery_released": recovery_released,
        "abstention_suppresses_memory": failure_abstained,
        "minimum_episode_support_met": support_sufficient,
        "incident_latch_forces_abstention": (
            before_failure.route == "trusted"
            and during_incident.route == "abstain"
            and during_incident.incident_latched
        ),
        "incident_latch_suppresses_memory": (
            not during_incident.memory_candidate
        ),
        "clean_terminal_session_releases_latch": (
            after_recovery.route == "trusted"
            and not after_recovery.incident_latched
        ),
    }
    promoted = all(checks.values())
    return {
        "schema": "TESSERA-EVO-036-FAILURE-RECOVERY-v0.1",
        "passed": all(checks[name] for name in (
            "preregistration_frozen_before_scoring",
            "failure_prefix_excludes_failure_event",
            "recovery_prefix_is_clean",
            "incident_latch_forces_abstention",
            "incident_latch_suppresses_memory",
            "clean_terminal_session_releases_latch",
        )),
        "natural_failure_recovery_promoted": promoted,
        "decision": (
            "promote_natural_failure_recovery"
            if promoted
            else "retain_router_reject_failure_recovery_claim"
        ),
        "checks": checks,
        "session_contract": contract.as_dict(),
        "metrics": {
            **checkpoint_metrics,
            "failure_episodes": observed_failure_episodes,
            "recovery_episodes": observed_recovery_episodes,
            "minimum_failure_episodes": minimum,
            "failure_latent_drift": failure_score,
            "recovery_latent_drift": recovery_score,
            "router_threshold": threshold,
            "failure_abstention_recall": float(failure_abstained),
            "recovery_release_rate": float(recovery_released),
            "memory_candidate_on_failure": not failure_abstained,
            "incident_latch_recovery_sessions_required": 1,
        },
        "source_roles": {
            "failure": "untouched post-EVO-035 natural failed full-loop prefix",
            "recovery": "subsequent post-fix successful full-loop prefix",
        },
        "claim_boundary": (
            "One natural incident and one recovery session reveal observed "
            "behavior only. They do not establish general failure sensitivity "
            "or production intervention authority."
        ),
    }
