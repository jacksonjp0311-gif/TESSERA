from __future__ import annotations

import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from tessera.data.synthetic import generate_synthetic_telemetry
from tessera.data.splits import chronological_splits, features_labels
from tessera.graph.topologies import make_operator
from tessera.model.train import fit_tessera_model, evaluate_sequence
from tessera.baselines.ewma import evaluate_ewma
from tessera.baselines.persistence import evaluate_persistence
from tessera.metrics.rate_distortion import add_rate_distortion
from tessera.metrics.anomaly import calibrate_anomaly_model, score_anomalies
from tessera.memory.gates import calibrate_thresholds, apply_triadic_gates
from tessera.experiments.integrity import model_parameter_count


@dataclass
class SeedResult:
    seed: int
    auc: float
    recall: float
    false_memory_rate: float
    replay_pass_rate: float
    prediction_loss: float
    best_baseline_loss: float
    baseline_gap: float
    memory_selectivity: float
    wall_seconds: float
    parameter_count: int


@dataclass
class ArchitectureConfig:
    name: str
    depth: int
    hidden_dim: int


def run_single_seed(
    seed: int,
    *,
    steps: int = 900,
    channels: int = 6,
    topology: str = "q4",
    field_dim: int = 16,
    code_dim: int = 8,
    alpha: float = 0.5,
    epochs: int = 6,
    architecture: ArchitectureConfig | None = None,
) -> SeedResult:
    arch = architecture or ArchitectureConfig(name="default", depth=2, hidden_dim=field_dim * 2)
    t0 = time.time()
    df, labels = generate_synthetic_telemetry(steps=steps, channels=channels, seed=seed)
    splits = chronological_splits(df)
    train_n, train_labels = features_labels(splits.train)
    val_n, val_labels = features_labels(splits.validation)
    replay_n, replay_labels = features_labels(splits.replay)
    test_n, test_labels = features_labels(splits.final_test)
    cal_n, cal_labels = features_labels(splits.calibration)
    operator = make_operator(topology, field_dim, seed=seed)
    effective_hidden = arch.hidden_dim if arch.hidden_dim > 0 else max(64, 2 * field_dim)
    model = fit_tessera_model(
        train_n, operator, code_dim=code_dim, alpha=alpha,
        epochs=epochs, seed=seed, X_validation=val_n,
        hidden_dim=effective_hidden, depth=arch.depth,
    )
    eval_rows = evaluate_sequence(model, test_n)["rows"]
    eval_df = pd.DataFrame(eval_rows)
    eval_df = add_rate_distortion(eval_df)
    if len(eval_df) > 0 and len(test_labels) > 1:
        eval_df["label"] = test_labels[1:len(eval_df)+1]
    cal_rows = evaluate_sequence(model, cal_n)["rows"]
    cal_df = pd.DataFrame(cal_rows)
    cal_df = add_rate_distortion(cal_df)
    anomaly = calibrate_anomaly_model(cal_df)
    scored = score_anomalies(eval_df, anomaly)
    thresholds = calibrate_thresholds(cal_df)
    gated = apply_triadic_gates(scored, thresholds, labels=eval_df["label"].values if "label" in eval_df else None)
    replay_rows = evaluate_sequence(model, replay_n)["rows"]
    replay_df = pd.DataFrame(replay_rows)
    replay_df = add_rate_distortion(replay_df)
    if len(replay_df) > 0 and len(replay_labels) > 1:
        replay_df["label"] = replay_labels[1:len(replay_df)+1]
    replay_scored = score_anomalies(replay_df, anomaly)
    replay_gated = apply_triadic_gates(replay_scored, thresholds, labels=replay_df["label"].values if "label" in replay_df else None)
    replay_pass = float(replay_gated["replay_pass"].mean()) if "replay_pass" in replay_gated and len(replay_gated) > 0 else 0.0
    promoted = int(gated["memory_candidate"].sum()) if "memory_candidate" in gated else 0
    false_memories = int(((gated.get("memory_candidate", 0)==1) & (gated.get("label", 0)==1)).sum()) if "label" in gated and "memory_candidate" in gated else 0
    total_anomalies = int(gated["label"].sum()) if "label" in gated else 0
    detected = int(((gated.get("warn", 0)==1) & (gated.get("label", 0)==1)).sum()) if "label" in gated and "warn" in gated else 0
    recall = detected / max(1, total_anomalies)
    false_memory_rate = false_memories / max(1, promoted) if promoted > 0 else 0.0
    neural_loss = float(np.mean([r["prediction_loss"] for r in eval_rows])) if eval_rows else 999.0
    persistence_loss = evaluate_persistence(test_n)["mean_prediction_loss"]
    ewma_loss = evaluate_ewma(test_n)["mean_prediction_loss"]
    best_baseline = min(persistence_loss, ewma_loss)
    baseline_gap = neural_loss - best_baseline
    try:
        from sklearn.metrics import roc_auc_score
        scores = scored["anomaly_score"].to_numpy()
        labs = scored["label"].to_numpy()[:len(scores)]
        auc = roc_auc_score(labs, scores) if len(np.unique(labs)) > 1 else 0.5
    except Exception:
        auc = float("nan")
    selectivity = promoted / max(1, len(gated)) if len(gated) > 0 else 0.0
    return SeedResult(
        seed=seed, auc=auc, recall=recall, false_memory_rate=false_memory_rate,
        replay_pass_rate=replay_pass, prediction_loss=neural_loss,
        best_baseline_loss=best_baseline, baseline_gap=baseline_gap,
        memory_selectivity=selectivity, wall_seconds=time.time() - t0,
        parameter_count=model_parameter_count(model),
    )


def multi_seed_benchmark(
    seeds: list[int] | None = None,
    *,
    steps: int = 900,
    channels: int = 6,
    topology: str = "q4",
    field_dim: int = 16,
    code_dim: int = 8,
    alpha: float = 0.5,
    epochs: int = 6,
    architectures: list[dict] | None = None,
) -> dict:
    seeds = seeds or [11, 23, 37]
    architectures = architectures or [{"name": "default", "depth": 2, "hidden_dim": -1}]
    all_results = {}
    for arch_cfg in architectures:
        arch = ArchitectureConfig(
            name=arch_cfg.get("name", f"d{arch_cfg.get('depth',2)}_h{arch_cfg.get('hidden_dim',64)}"),
            depth=arch_cfg.get("depth", 2),
            hidden_dim=arch_cfg.get("hidden_dim", -1),
        )
        arch_results = []
        for seed in seeds:
            result = run_single_seed(
                seed, steps=steps, channels=channels, topology=topology,
                field_dim=field_dim, code_dim=code_dim, alpha=alpha, epochs=epochs,
                architecture=arch,
            )
            arch_results.append(asdict(result))
        losses = [r["prediction_loss"] for r in arch_results]
        baselines = [r["best_baseline_loss"] for r in arch_results]
        gaps = [r["baseline_gap"] for r in arch_results]
        recalls = [r["recall"] for r in arch_results]
        false_rates = [r["false_memory_rate"] for r in arch_results]
        replays = [r["replay_pass_rate"] for r in arch_results]
        params = [r["parameter_count"] for r in arch_results]
        all_results[arch.name] = {
            "config": {"depth": arch.depth, "hidden_dim": arch.hidden_dim},
            "seeds": arch_results,
            "summary": {
                "mean_prediction_loss": float(np.mean(losses)),
                "std_prediction_loss": float(np.std(losses)),
                "mean_baseline_loss": float(np.mean(baselines)),
                "mean_baseline_gap": float(np.mean(gaps)),
                "mean_recall": float(np.mean(recalls)),
                "mean_false_memory_rate": float(np.mean(false_rates)),
                "mean_replay_pass_rate": float(np.mean(replays)),
                "mean_parameter_count": float(np.mean(params)),
                "baseline_parity": float(np.mean(gaps)) < 0.01 * float(np.mean(baselines)),
                "seed_count": len(seeds),
            },
        }
    return all_results
