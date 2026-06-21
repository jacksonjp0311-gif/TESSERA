from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from tessera.experiments.natural_checkpoint_utility import _session_vector
from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.model.prediction_experts import (
    predict_with_expert,
    select_prediction_expert,
)
from tessera.plugin.neural_checkpoints import (
    neural_awareness_features,
    train_neural_checkpoint,
)


def _select_router(
    scores: dict[str, np.ndarray],
    errors: np.ndarray,
    start: int,
    end: int,
    coverages: list[float],
) -> tuple[dict, list[dict]]:
    candidates = []
    values = errors[start:end]
    for name, full_score in scores.items():
        local = full_score[start:end]
        for coverage in coverages:
            keep = math.ceil(len(local) * float(coverage))
            threshold = float(np.sort(local)[keep - 1])
            retained = local <= threshold
            candidates.append({
                "score": name,
                "target_coverage": float(coverage),
                "threshold": threshold,
                "validation_coverage": float(np.mean(retained)),
                "validation_risk": float(np.mean(values[retained])),
            })
    selected = min(
        candidates,
        key=lambda row: (
            row["validation_risk"],
            -row["validation_coverage"],
            row["score"],
        ),
    )
    return selected, candidates


def _evaluate_router(
    selected: dict,
    scores: dict[str, np.ndarray],
    errors: np.ndarray,
    start: int,
    end: int,
) -> dict:
    local = scores[selected["score"]][start:end]
    retained = local <= selected["threshold"]
    return {
        "coverage": float(np.mean(retained)),
        "retained_risk": float(np.mean(errors[start:end][retained])),
        "retained_count": int(np.sum(retained)),
    }


def run_neural_uncertainty_router(preregistration_path: str) -> dict:
    plan = json.loads(
        Path(preregistration_path).read_text(encoding="utf-8")
    )
    trajectories = []
    for cohort in plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(cohort))
    if len(trajectories) != 120 or any(label for _, label in trajectories):
        raise ValueError("uncertainty_router_requires_120_clean_sessions")
    raw = np.asarray(
        [_session_vector(events) for events, _ in trajectories],
        dtype="float32",
    )
    varying = raw[:100].std(axis=0) > 1e-6
    sequence = raw[:, varying]
    payload, checkpoint_metrics = train_neural_checkpoint(sequence[:100])
    mean = np.asarray(payload["normalization"]["mean"], dtype=float)
    scale = np.asarray(payload["normalization"]["scale"], dtype=float)
    normalized = (sequence - mean) / scale
    stable_expert, selection = select_prediction_expert(
        normalized[:60],
        normalized[60:80],
    )
    stable_predictions = predict_with_expert(stable_expert, normalized)
    targets = normalized[1:]
    errors = np.mean((stable_predictions - targets) ** 2, axis=1)
    neural_scores = neural_awareness_features(
        payload,
        normalized,
        stable_predictions,
    )
    simple_scores = {
        "recent_observation_jump": np.asarray([
            0.0 if index == 0
            else float(np.mean(
                (normalized[index] - normalized[index - 1]) ** 2
            ))
            for index in range(len(normalized) - 1)
        ])
    }
    validation = (59, 79)
    replay = (79, 99)
    final_test = (99, 119)
    neural_selected, neural_candidates = _select_router(
        neural_scores,
        errors,
        *validation,
        plan["target_coverages"],
    )
    simple_selected, simple_candidates = _select_router(
        simple_scores,
        errors,
        *validation,
        plan["target_coverages"],
    )
    neural_replay = _evaluate_router(
        neural_selected, neural_scores, errors, *replay
    )
    simple_replay = _evaluate_router(
        simple_selected, simple_scores, errors, *replay
    )
    replay_full_risk = float(np.mean(errors[slice(*replay)]))
    replay_gate = (
        neural_replay["retained_risk"]
        <= replay_full_risk
        * float(
            plan["replay_gate"][
                "maximum_risk_ratio_to_full_coverage"
            ]
        )
        and neural_replay["coverage"]
        >= neural_selected["target_coverage"]
        - float(
            plan["replay_gate"]["minimum_coverage_below_target"]
        )
        and neural_replay["coverage"]
        <= neural_selected["target_coverage"]
        + float(
            plan["replay_gate"]["maximum_coverage_above_target"]
        )
        and neural_replay["retained_risk"]
        <= simple_replay["retained_risk"]
        * float(
            plan["replay_gate"][
                "maximum_risk_ratio_to_simple_router"
            ]
        )
    )
    neural_final = _evaluate_router(
        neural_selected, neural_scores, errors, *final_test
    )
    simple_final = _evaluate_router(
        simple_selected, simple_scores, errors, *final_test
    )
    final_full_risk = float(np.mean(errors[slice(*final_test)]))
    final_gate = (
        replay_gate
        and neural_final["retained_risk"]
        <= final_full_risk
        * float(
            plan["final_test_gate"][
                "maximum_risk_ratio_to_full_coverage"
            ]
        )
        and neural_final["retained_risk"]
        <= simple_final["retained_risk"]
        * float(
            plan["final_test_gate"][
                "maximum_risk_ratio_to_simple_router"
            ]
        )
        and neural_final["coverage"]
        >= float(plan["final_test_gate"]["minimum_coverage"])
    )
    return {
        "schema": "TESSERA-EVO-032-NEURAL-UNCERTAINTY-ROUTER-v0.1",
        "preregistration": plan,
        "varying_session_features": int(varying.sum()),
        "checkpoint_metrics": checkpoint_metrics,
        "stable_expert": selection["selected_expert"],
        "validation": {
            "full_risk": float(np.mean(errors[slice(*validation)])),
            "neural_selected": neural_selected,
            "simple_selected": simple_selected,
            "neural_candidates": neural_candidates,
            "simple_candidates": simple_candidates,
        },
        "replay": {
            "full_risk": replay_full_risk,
            "neural": neural_replay,
            "simple": simple_replay,
            "gate_passed": replay_gate,
        },
        "final_test": {
            "full_risk": final_full_risk,
            "neural": neural_final,
            "simple": simple_final,
            "gate_passed": final_gate,
        },
        "forecast_mutated": False,
        "neural_uncertainty_routing_supported": final_gate,
        "decision": (
            "promote_neural_uncertainty_abstention"
            if final_gate
            else "reject_neural_router_preserve_full_coverage_expert"
        ),
        "claim_boundary": (
            "Selective clean-session risk does not establish natural failure "
            "sensitivity, task success, or production readiness."
        ),
    }
