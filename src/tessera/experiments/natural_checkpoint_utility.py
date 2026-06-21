from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.model.prediction_experts import predict_with_expert
from tessera.plugin.checkpoints import CheckpointStore, ReplayGate
from tessera.plugin.neural_checkpoints import (
    deserialize_expert,
    train_neural_checkpoint,
)
from tessera.plugin.trajectory import vectorize_events


def _session_vector(events) -> np.ndarray:
    matrix = vectorize_events(events)
    return np.concatenate(
        [matrix.mean(axis=0), matrix.std(axis=0), matrix[-1]],
        axis=0,
    )


def _ewma_predictions(
    sequence: np.ndarray,
    start: int,
    alpha: float,
) -> np.ndarray:
    state = sequence[start - 1].copy()
    predictions = []
    for current in sequence[start - 1 : -1]:
        state = alpha * current + (1.0 - alpha) * state
        predictions.append(state.copy())
    return np.asarray(predictions)


def _rolling_mean_predictions(
    sequence: np.ndarray,
    start: int,
    window: int,
) -> np.ndarray:
    predictions = []
    for index in range(start, len(sequence)):
        predictions.append(sequence[max(0, index - window) : index].mean(0))
    return np.asarray(predictions)


def _nearest_transition_predictions(
    sequence: np.ndarray,
    start: int,
) -> np.ndarray:
    predictions = []
    for index in range(start, len(sequence)):
        current = sequence[index - 1]
        candidates = sequence[: index - 1]
        targets = sequence[1:index]
        distances = np.mean((candidates - current) ** 2, axis=1)
        predictions.append(targets[int(np.argmin(distances))])
    return np.asarray(predictions)


def _loss(predictions: np.ndarray, targets: np.ndarray) -> float:
    return float(np.mean((predictions - targets) ** 2))


def run_natural_checkpoint_utility(
    preregistration_path: str,
    store_path: str,
) -> dict:
    plan = json.loads(
        Path(preregistration_path).read_text(encoding="utf-8")
    )
    trajectories = []
    for cohort in plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(cohort))
    if len(trajectories) != int(plan["chronological_sessions"]):
        raise ValueError("chronological_session_count_mismatch")
    if any(degraded for _, degraded in trajectories):
        raise ValueError("natural_clean_utility_requires_clean_sessions")

    raw = np.asarray(
        [_session_vector(events) for events, _ in trajectories],
        dtype="float32",
    )
    checkpoint_count = int(plan["checkpoint_sessions"])
    varying = raw[:checkpoint_count].std(axis=0) > 1e-6
    sequence = raw[:, varying]
    payload, metrics = train_neural_checkpoint(
        sequence[:checkpoint_count]
    )
    gate = ReplayGate(
        baseline_loss=metrics["baseline_loss"],
        candidate_loss=metrics["candidate_loss"],
        max_regression_fraction=float(
            plan["admission_gate"][
                "maximum_mean_loss_regression_fraction"
            ]
        ),
        minimum_replay_pass_rate=float(
            plan["admission_gate"]["minimum_row_replay_pass_rate"]
        ),
        replay_pass_rate=metrics["replay_pass_rate"],
    )
    store = CheckpointStore(store_path)
    candidate = store.write_candidate(
        payload=payload,
        lineage={
            "operation": "TESSERA-EVO-030",
            "cohorts": plan["cohorts"],
        },
        metrics=metrics,
    )
    admission = store.admit(candidate["candidate_id"], gate)

    mean = np.asarray(payload["normalization"]["mean"], dtype=float)
    scale = np.asarray(payload["normalization"]["scale"], dtype=float)
    normalized = (sequence - mean) / scale
    start = checkpoint_count
    targets = normalized[start:]
    expert = deserialize_expert(payload["prediction_expert"])
    checkpoint_predictions = predict_with_expert(
        expert,
        normalized[start - 1 :],
        history=normalized[: start - 1],
    )
    controls = {
        "persistence": normalized[start - 1 : -1],
        "rolling_mean_8": _rolling_mean_predictions(
            normalized, start, 8
        ),
        "nearest_transition_retrieval": _nearest_transition_predictions(
            normalized, start
        ),
    }
    validation_start = int(checkpoint_count * 0.60)
    validation_end = int(checkpoint_count * 0.80)
    ewma_scores = {}
    validation_targets = normalized[validation_start:validation_end]
    for alpha in (0.05, 0.1, 0.2, 0.5, 0.8):
        predictions = _ewma_predictions(
            normalized[:validation_end],
            validation_start,
            alpha,
        )
        ewma_scores[alpha] = _loss(predictions, validation_targets)
    selected_alpha = min(ewma_scores, key=ewma_scores.get)
    controls["validation_selected_ewma"] = _ewma_predictions(
        normalized, start, selected_alpha
    )
    losses = {
        "checkpoint": _loss(checkpoint_predictions, targets),
        **{
            name: _loss(predictions, targets)
            for name, predictions in controls.items()
        },
    }
    best_control_name = min(
        controls,
        key=lambda name: losses[name],
    )
    best_control_loss = losses[best_control_name]
    utility_supported = (
        admission["admitted"]
        and losses["checkpoint"] <= best_control_loss
    )
    return {
        "schema": "TESSERA-EVO-030-NATURAL-CHECKPOINT-UTILITY-v0.1",
        "preregistration": plan,
        "session_count": len(trajectories),
        "varying_session_features": int(varying.sum()),
        "checkpoint_metrics": metrics,
        "admission": admission,
        "final_test": {
            "session_count": len(targets),
            "losses": losses,
            "selected_ewma_alpha": selected_alpha,
            "best_control": best_control_name,
            "best_control_loss": best_control_loss,
            "checkpoint_loss_ratio_to_best_control": (
                losses["checkpoint"] / best_control_loss
            ),
        },
        "natural_checkpoint_utility_supported": utility_supported,
        "decision": (
            "promote_natural_checkpoint_utility"
            if utility_supported
            else "reject_natural_checkpoint_admission_preserve_fast_path"
        ),
        "claim_boundary": (
            "Clean-session next-state prediction does not establish natural "
            "failure sensitivity, task success, or production readiness."
        ),
    }
