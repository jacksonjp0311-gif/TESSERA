from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from tessera.baselines.ewma import evaluate_ewma
from tessera.baselines.persistence import evaluate_persistence
from tessera.data.manifest import make_manifest
from tessera.data.splits import features_labels
from tessera.evidence.package import make_evidence_package
from tessera.experiments.integrity import model_parameter_count
from tessera.graph.topologies import make_operator
from tessera.memory.gates import apply_triadic_gates
from tessera.metrics.anomaly import calibrate_anomaly_model, score_anomalies
from tessera.metrics.rate_distortion import add_rate_distortion
from tessera.model.prediction_experts import prediction_losses, select_prediction_expert
from tessera.model.train import evaluate_sequence, fit_tessera_model


NAB_WINDOWS = {
    "real_1": [[287, 307], [490, 513]],
    "real_2": [[400, 420]],
    "real_3": [[300, 320], [500, 520]],
    "real_4": [[350, 370]],
    "real_5": [[280, 300], [480, 500]],
    "real_6": [[310, 330]],
    "real_7": [[290, 310], [470, 490]],
    "real_8": [[320, 340]],
    "real_9": [[300, 320]],
    "real_10": [[350, 370], [550, 570]],
}


def load_yahoo_s5_stream(csv_path: str | Path, anomaly_windows: list[list[int]] | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Load a Yahoo S5 CSV stream and return (values, labels)."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Yahoo S5 data not found: {csv_path}")

    df = pd.read_csv(csv_path)
    # Yahoo S5 format: timestamp, value, anomaly (0/1)
    if "value" not in df.columns:
        # Try to infer: second column is value
        cols = list(df.columns)
        if len(cols) >= 2:
            df = df.rename(columns={cols[1]: "value"})
    if "anomaly" not in df.columns and "is_anomaly" in df.columns:
        df = df.rename(columns={"is_anomaly": "anomaly"})
    if "anomaly" not in df.columns:
        # Use provided windows to create labels
        df["anomaly"] = 0
        if anomaly_windows:
            for start, end in anomaly_windows:
                df.loc[start:end, "anomaly"] = 1

    values = df["value"].to_numpy(dtype="float32").reshape(-1, 1)
    labels = df["anomaly"].to_numpy(dtype=int) if "anomaly" in df else np.zeros(len(df), dtype=int)
    return values, labels


def run_yahoo_s5_transfer(
    data_dir: str | Path = "datasets/yahoo_s5",
    *,
    field_dim: int = 16,
    code_dim: int = 8,
    alpha: float = 0.5,
    epochs: int = 4,
    seed: int = 42,
    hidden_dim: int | None = None,
    depth: int = 2,
    stream_name: str = "A1Benchmark_real_1.csv",
    anomaly_windows: list[list[int]] | None = None,
) -> dict:
    """Run Yahoo S5 transfer evaluation on a single stream.

    This is the third dataset family evaluation per EVO-044 preregistration.
    """
    data_dir = Path(data_dir)
    csv_path = data_dir / stream_name
    if not csv_path.exists():
        return {
            "status": "data_not_found",
            "path": str(csv_path),
            "message": "Yahoo S5 data not downloaded. Download from Yahoo Webscope.",
        }

    values, labels = load_yahoo_s5_stream(csv_path, anomaly_windows)
    n = len(values)

    # Chronological splits (same protocol as NAB/UCR)
    split_cal = max(4, int(n * 0.10))
    split_train = max(8, int(n * 0.20))
    split_val = max(12, int(n * 0.52))
    split_replay = max(16, int(n * 0.74))

    cal = values[:split_cal]
    train = values[split_cal:split_train]
    val = values[split_train:split_val]
    replay = values[split_val:split_replay]
    test = values[split_replay:]
    test_labels = labels[split_replay:]
    cal_labels = labels[:split_cal]
    val_labels = labels[split_train:split_val]
    replay_labels = labels[split_val:split_replay]

    # Normalize on training data only
    scaler = StandardScaler().fit(train)
    train_n = scaler.transform(train).astype("float32")
    val_n = scaler.transform(val).astype("float32")
    replay_n = scaler.transform(replay).astype("float32")
    test_n = scaler.transform(test).astype("float32")
    cal_n = scaler.transform(cal).astype("float32")

    # Train model
    operator = make_operator("ring", field_dim, seed=seed)
    effective_hidden = hidden_dim or max(64, 2 * field_dim)
    model = fit_tessera_model(
        train_n, operator, code_dim=code_dim, alpha=alpha,
        epochs=epochs, seed=seed, X_validation=val_n,
        hidden_dim=effective_hidden, depth=depth,
    )

    # Evaluate
    eval_rows = evaluate_sequence(model, test_n)["rows"]
    eval_df = pd.DataFrame(eval_rows)
    eval_df = add_rate_distortion(eval_df)
    if len(eval_df) > 0 and len(test_labels) > 1:
        eval_df["label"] = test_labels[1:len(eval_df) + 1]

    cal_rows = evaluate_sequence(model, cal_n)["rows"]
    cal_df = pd.DataFrame(cal_rows)
    cal_df = add_rate_distortion(cal_df)

    anomaly = calibrate_anomaly_model(cal_df)
    scored = score_anomalies(eval_df, anomaly)

    from tessera.memory.gates import calibrate_thresholds
    thresholds = calibrate_thresholds(cal_df)
    gated = apply_triadic_gates(scored, thresholds, labels=eval_df["label"].values if "label" in eval_df else None)

    # Replay
    replay_rows = evaluate_sequence(model, replay_n)["rows"]
    replay_df = pd.DataFrame(replay_rows)
    replay_df = add_rate_distortion(replay_df)
    if len(replay_df) > 0 and len(replay_labels) > 1:
        replay_df["label"] = replay_labels[1:len(replay_df) + 1]
    replay_scored = score_anomalies(replay_df, anomaly)
    replay_gated = apply_triadic_gates(replay_scored, thresholds, labels=replay_df["label"].values if "label" in replay_df else None)

    # Metrics
    neural_loss = float(np.mean([r["prediction_loss"] for r in eval_rows])) if eval_rows else 999.0
    persistence_loss = evaluate_persistence(test_n).get("mean_prediction_loss", 999.0)
    ewma_loss = evaluate_ewma(test_n).get("mean_prediction_loss", 999.0)
    best_baseline = min(persistence_loss, ewma_loss)
    baseline_gap = neural_loss - best_baseline

    promoted = int(gated["memory_candidate"].sum()) if "memory_candidate" in gated else 0
    false_mem = int(((gated.get("memory_candidate", 0) == 1) & (gated.get("label", 0) == 1)).sum()) if "label" in gated and "memory_candidate" in gated else 0
    total_anom = int(gated["label"].sum()) if "label" in gated else 0
    detected = int(((gated.get("warn", 0) == 1) & (gated.get("label", 0) == 1)).sum()) if "label" in gated and "warn" in gated else 0
    recall = detected / max(1, total_anom)
    fmr = false_mem / max(1, promoted) if promoted > 0 else 0.0
    replay_pass = float(replay_gated["replay_pass"].mean()) if "replay_pass" in replay_gated and len(replay_gated) > 0 else 0.0

    # AUC
    try:
        from sklearn.metrics import roc_auc_score
        scores = scored["anomaly_score"].to_numpy()
        labs = scored["label"].to_numpy()[:len(scores)]
        auc = roc_auc_score(labs, scores) if len(np.unique(labs)) > 1 else 0.5
    except Exception:
        auc = float("nan")

    # Expert selection
    expert, _ = select_prediction_expert(train_n, val_n)
    expert_losses = prediction_losses(expert, test_n, history=train_n)
    expert_loss = float(np.mean(expert_losses))

    t1_supported = auc > 0.9 if not np.isnan(auc) else False

    return {
        "status": "evaluated",
        "stream": stream_name,
        "n_samples": n,
        "auc": auc,
        "recall": recall,
        "false_memory_rate": fmr,
        "replay_pass_rate": replay_pass,
        "neural_prediction_loss": neural_loss,
        "best_baseline_loss": best_baseline,
        "baseline_gap": baseline_gap,
        "selected_expert": expert.name,
        "expert_loss": expert_loss,
        "t1_supported": t1_supported,
        "parameter_count": model_parameter_count(model),
        "depth": depth,
        "hidden_dim": effective_hidden,
    }
