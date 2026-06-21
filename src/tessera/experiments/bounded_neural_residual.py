from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tessera.experiments.natural_checkpoint_utility import _session_vector
from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.model.prediction_experts import predict_with_expert
from tessera.plugin.neural_checkpoints import (
    deserialize_expert,
    neural_sequence_predictions,
    train_neural_checkpoint,
)


def _loss(predictions, targets) -> float:
    return float(np.mean((predictions - targets) ** 2))


def _bounded_predictions(
    stable: np.ndarray,
    neural: np.ndarray,
    *,
    gain: float,
    clip_fraction: float,
    innovation_scale: np.ndarray,
) -> np.ndarray:
    correction = gain * (neural - stable)
    limit = clip_fraction * innovation_scale
    return stable + np.clip(correction, -limit, limit)


def run_bounded_neural_residual(preregistration_path: str) -> dict:
    plan = json.loads(
        Path(preregistration_path).read_text(encoding="utf-8")
    )
    trajectories = []
    for cohort in plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(cohort))
    if len(trajectories) != 120 or any(label for _, label in trajectories):
        raise ValueError("residual_gate_requires_120_clean_sessions")
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
    expert = deserialize_expert(payload["prediction_expert"])
    stable_predictions = predict_with_expert(
        expert,
        normalized,
        history=None,
    )
    neural_predictions = neural_sequence_predictions(payload, normalized)
    targets = normalized[1:]

    train_end = 60
    validation_end = 80
    replay_end = 100
    innovation_scale = np.maximum(
        np.std(
            normalized[1:train_end] - normalized[: train_end - 1],
            axis=0,
        ),
        1e-3,
    )

    def segment(start_session, end_session):
        start = start_session - 1
        end = end_session - 1
        return (
            stable_predictions[start:end],
            neural_predictions[start:end],
            targets[start:end],
        )

    stable_val, neural_val, targets_val = segment(
        train_end, validation_end
    )
    candidates = []
    for gain in plan["residual_candidates"]["gains"]:
        for clip_fraction in plan["residual_candidates"][
            "clip_scale_fractions"
        ]:
            predictions = _bounded_predictions(
                stable_val,
                neural_val,
                gain=float(gain),
                clip_fraction=float(clip_fraction),
                innovation_scale=innovation_scale,
            )
            candidates.append({
                "gain": float(gain),
                "clip_fraction": float(clip_fraction),
                "validation_loss": _loss(predictions, targets_val),
            })
    selected = min(
        candidates,
        key=lambda row: (
            row["validation_loss"],
            row["gain"],
            row["clip_fraction"],
        ),
    )
    stable_replay, neural_replay, targets_replay = segment(
        validation_end, replay_end
    )
    replay_predictions = _bounded_predictions(
        stable_replay,
        neural_replay,
        gain=selected["gain"],
        clip_fraction=selected["clip_fraction"],
        innovation_scale=innovation_scale,
    )
    stable_replay_rows = np.mean(
        (stable_replay - targets_replay) ** 2,
        axis=1,
    )
    residual_replay_rows = np.mean(
        (replay_predictions - targets_replay) ** 2,
        axis=1,
    )
    stable_replay_loss = float(np.mean(stable_replay_rows))
    residual_replay_loss = float(np.mean(residual_replay_rows))
    row_win_rate = float(
        np.mean(residual_replay_rows < stable_replay_rows)
    )
    replay_gate = (
        selected["gain"] > 0.0
        and residual_replay_loss
        <= stable_replay_loss
        * float(
            plan["replay_gate"][
                "maximum_mean_loss_ratio_to_stable_expert"
            ]
        )
        and row_win_rate
        >= float(plan["replay_gate"]["minimum_row_win_rate"])
    )
    deployed_gain = selected["gain"] if replay_gate else 0.0
    stable_final, neural_final, targets_final = segment(
        replay_end, 120
    )
    final_predictions = _bounded_predictions(
        stable_final,
        neural_final,
        gain=deployed_gain,
        clip_fraction=selected["clip_fraction"],
        innovation_scale=innovation_scale,
    )
    stable_final_loss = _loss(stable_final, targets_final)
    residual_final_loss = _loss(final_predictions, targets_final)
    final_supported = (
        replay_gate
        and residual_final_loss <= stable_final_loss
    )
    return {
        "schema": "TESSERA-EVO-031-BOUNDED-NEURAL-RESIDUAL-v0.1",
        "preregistration": plan,
        "varying_session_features": int(varying.sum()),
        "checkpoint_metrics": checkpoint_metrics,
        "validation": {
            "candidates": candidates,
            "selected": selected,
            "stable_loss": _loss(stable_val, targets_val),
        },
        "replay": {
            "stable_loss": stable_replay_loss,
            "residual_loss": residual_replay_loss,
            "loss_ratio": residual_replay_loss / stable_replay_loss,
            "row_win_rate": row_win_rate,
            "gate_passed": replay_gate,
        },
        "authority": {
            "selected_gain": selected["gain"],
            "deployed_gain": deployed_gain,
            "collapsed_to_zero": deployed_gain == 0.0,
        },
        "final_test": {
            "stable_loss": stable_final_loss,
            "residual_loss": residual_final_loss,
            "loss_ratio": residual_final_loss / stable_final_loss,
        },
        "bounded_residual_supported": final_supported,
        "decision": (
            "promote_bounded_neural_residual"
            if final_supported
            else "reject_residual_authority_preserve_stable_expert"
        ),
        "claim_boundary": (
            "Bounded residual prediction does not establish failure "
            "sensitivity, task success, or production readiness."
        ),
    }
