from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from tessera.baselines.ewma import evaluate_ewma
from tessera.baselines.persistence import evaluate_persistence
from tessera.data.adapters import DatasetDescriptor, NabKnownCauseAdapter
from tessera.data.splits import features_labels, fixed_index_splits
from tessera.experiments.integrity import model_parameter_count
from tessera.graph.topologies import make_operator
from tessera.memory.gates import apply_triadic_gates
from tessera.metrics.anomaly import (
    anomaly_ablation,
    calibrate_anomaly_model,
    score_anomalies,
)
from tessera.metrics.governance import summarize_gates
from tessera.metrics.rate_distortion import add_rate_distortion
from tessera.model.prediction_experts import (
    prediction_losses,
    select_prediction_expert,
)
from tessera.model.train import evaluate_sequence, fit_tessera_model


def run_nab_diagnostic(
    root: Path = Path("datasets/nab"),
    *,
    field_dim: int = 16,
    code_dim: int = 8,
    alpha: float = 0.5,
    epochs: int = 4,
    seed: int = 42,
    hidden_dim: int | None = None,
    depth: int = 2,
    channels: list[str] | None = None,
) -> dict:
    """Evaluate the enhanced network under the pinned NAB T1 protocol."""
    if channels:
        raise ValueError("pinned NAB diagnostic accepts one declared stream")
    root = Path(root)
    if not (root / "machine_temperature_system_failure.csv").exists():
        candidate = root / "datasets" / "nab"
        if candidate.exists():
            root = candidate
    adapter = NabKnownCauseAdapter(
        root / "machine_temperature_system_failure.csv",
        root / "combined_windows.json",
        "realKnownCause/machine_temperature_system_failure.csv",
        DatasetDescriptor(
            name="nab_machine_temperature_system_failure",
            version="NAB@ea702d75cc2258d9d7dd35ca8e5e2539d71f3140",
            source="https://github.com/numenta/NAB",
            license="MIT",
            label_policy="official_windows_evaluation_only",
            known_caveats=(
                "12 duplicate timestamps preserved",
                "anomaly windows are not instantaneous failure labels",
                "single univariate stream",
            ),
        ),
    )
    frame = adapter.load()
    splits = fixed_index_splits(
        frame,
        calibration_end=850,
        train_end=1700,
        validation_end=6000,
        replay_end=18000,
    )
    parts = [
        features_labels(getattr(splits, name))
        for name in (
            "calibration",
            "train",
            "validation",
            "replay",
            "final_test",
        )
    ]
    (X_cal, _), (X_train, _), (X_val, _), (
        X_replay,
        y_replay,
    ), (X_test, y_test) = parts
    scaler = StandardScaler().fit(X_train)
    X_cal_s, X_train_s, X_val_s, X_replay_s, X_test_s = [
        scaler.transform(values).astype("float32")
        for values in (X_cal, X_train, X_val, X_replay, X_test)
    ]

    operator = make_operator("ring", field_dim, seed=seed)
    hdim = hidden_dim or max(64, 2 * field_dim)
    model = fit_tessera_model(
        X_train_s,
        operator,
        code_dim=code_dim,
        alpha=alpha,
        epochs=epochs,
        seed=seed,
        X_validation=X_val_s,
        hidden_dim=hdim,
        depth=depth,
    )
    expert, expert_selection = select_prediction_expert(
        X_train_s, X_val_s
    )

    normal_reference = np.concatenate([X_cal_s, X_train_s], axis=0)
    normal_rows = add_rate_distortion(
        pd.DataFrame(evaluate_sequence(model, normal_reference)["rows"])
    )
    anomaly_model = calibrate_anomaly_model(
        normal_rows,
        warn_quantile=0.90,
        block_quantile=0.995,
        memory_quantile=0.70,
    )

    def evaluate(
        values: np.ndarray,
        labels: np.ndarray,
    ) -> pd.DataFrame:
        rows = add_rate_distortion(
            pd.DataFrame(evaluate_sequence(model, values)["rows"])
        )
        rows["neural_prediction_loss"] = rows["prediction_loss"]
        rows["selected_prediction_loss"] = prediction_losses(
            expert, values, history=X_train_s
        )
        scored = score_anomalies(rows, anomaly_model)
        return apply_triadic_gates(
            scored, anomaly_model, labels=labels[1:]
        )

    replay_rows = evaluate(X_replay_s, y_replay)
    test_rows = evaluate(X_test_s, y_test)
    replay_summary = summarize_gates(replay_rows)
    summary = summarize_gates(test_rows)
    summary["mean_neural_prediction_loss"] = float(
        test_rows["neural_prediction_loss"].mean()
    )
    summary["mean_prediction_loss"] = float(
        test_rows["selected_prediction_loss"].mean()
    )
    summary["selected_prediction_expert"] = expert.name
    summary["replay_pass_rate"] = replay_summary["replay_pass_rate"]
    summary["replay_false_memory_rate"] = replay_summary[
        "false_memory_rate"
    ]
    summary["anomaly_ablation"] = anomaly_ablation(test_rows)

    persistence_loss = evaluate_persistence(X_test_s)[
        "mean_prediction_loss"
    ]
    ewma_loss = evaluate_ewma(X_test_s)["mean_prediction_loss"]
    best_baseline = min(persistence_loss, ewma_loss)
    summary["persistence_loss"] = float(persistence_loss)
    summary["ewma_loss"] = float(ewma_loss)
    summary["best_baseline_prediction_loss"] = float(best_baseline)
    summary["baseline_gap"] = float(
        best_baseline - summary["mean_prediction_loss"]
    )
    detector_memory_bundle = (
        summary.get("auc", 0.0) > 0.60
        and summary["replay_pass_rate"] >= 0.60
        and summary.get("missed_warning", 1.0) < 0.35
        and summary.get("false_memory_rate", 1.0) <= 0.05
    )
    prediction_bundle = (
        summary["mean_prediction_loss"] < best_baseline
        and summary["mean_prediction_loss"] <= ewma_loss * 1.05
    )
    supported = detector_memory_bundle and prediction_bundle
    return {
        "schema": "TESSERA-NAB-ENHANCED-DIAGNOSTIC-v0.14",
        "dataset": adapter.descriptor.name,
        "dataset_version": adapter.descriptor.version,
        "n_samples": len(frame),
        "official_anomaly_rows": int(frame["label"].sum()),
        "final_test_anomaly_rows": int(y_test.sum()),
        "split_policy": {
            "calibration": "0:850",
            "train": "850:1700",
            "validation": "1700:6000",
            "replay": "6000:18000",
            "final_test": f"18000:{len(frame)}",
        },
        "architecture": {
            "depth": depth,
            "hidden_dim": hdim,
            "field_dim": field_dim,
            "code_dim": code_dim,
        },
        "metrics": summary,
        "prediction_expert_selection": expert_selection,
        "parameter_count": model_parameter_count(model),
        "dataset_scoped_T1_supported": supported,
        "claim_ceiling": (
            "dataset_scoped_T1_supported"
            if supported
            else "dataset_scoped_T1_diagnostic"
        ),
        "non_claim_lock": (
            "Enhanced NAB evaluation is dataset-scoped and grants no live "
            "memory, repair, tool, or autonomous authority."
        ),
    }
