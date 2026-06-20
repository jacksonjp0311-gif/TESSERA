from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from tessera.baselines.dense_autoencoder import evaluate_dense_autoencoder
from tessera.baselines.ewma import evaluate_ewma
from tessera.baselines.matrix_profile import evaluate_matrix_profile
from tessera.baselines.pca_codec import evaluate_pca_codec
from tessera.baselines.persistence import evaluate_persistence
from tessera.baselines.random_projection import evaluate_random_projection
from tessera.baselines.reservoir import evaluate_reservoir
from tessera.data.adapters import DatasetDescriptor, TelemanomChannelAdapter
from tessera.data.manifest import make_manifest
from tessera.data.splits import SplitBundle, features_labels
from tessera.evidence.package import make_evidence_package, write_evidence
from tessera.experiments.integrity import (
    ExperimentBudget,
    Timer,
    model_parameter_count,
    preprocessing_hash,
    split_hashes,
)
from tessera.graph.spectral import graph_declaration
from tessera.graph.topologies import make_operator
from tessera.memory.certificates import make_dataset_transfer_certificate, write_json
from tessera.memory.gates import apply_triadic_gates
from tessera.memory.wound_ledger import classify_wounds, write_wounds
from tessera.metrics.anomaly import anomaly_ablation, calibrate_anomaly_model, score_anomalies
from tessera.metrics.governance import summarize_gates
from tessera.metrics.rate_distortion import add_rate_distortion
from tessera.model.train import evaluate_sequence, fit_tessera_model
from tessera.utils.hashing import sha256_json
from tessera.utils.paths import make_run_dir
from tessera.visuals.plots import write_plots

TELEMANOM_COMMIT = "2e6c5b6c3558e7835601519b7bdef37c649bdbdc"


def run(
    *,
    root: str | Path = ".",
    out: str | Path = "outputs/transfers/smap-p1",
    channel_id: str = "P-1",
    epochs: int = 5,
    seed: int = 42,
) -> Path:
    root = Path(root).resolve()
    base = root / "datasets" / "telemanom" / "extracted" / "data" / "data"
    adapter = TelemanomChannelAdapter(
        train_path=base / "train" / f"{channel_id}.npy",
        test_path=base / "test" / f"{channel_id}.npy",
        labels_path=root / "datasets" / "telemanom" / "labeled_anomalies.csv",
        channel_id=channel_id,
        descriptor=DatasetDescriptor(
            name=f"nasa_smap_{channel_id.lower().replace('-', '_')}",
            version=f"Telemanom@{TELEMANOM_COMMIT}",
            source="https://github.com/khundman/telemanom",
            license="Apache-2.0",
            label_policy="expert_anomaly_sequences_on_official_test_partition",
            known_caveats=(
                "published arrays scaled using test-set extrema",
                "timestamps and channel identities anonymized",
                "sparse one-hot command and event context",
            ),
        ),
    )
    train_frame = adapter.load_train()
    test_frame = adapter.load_test()
    train_n = len(train_frame)
    calibration_end = int(train_n * 0.15)
    fit_end = int(train_n * 0.70)
    replay_end = len(test_frame) // 2
    splits = SplitBundle(
        calibration=train_frame.iloc[:calibration_end].copy(),
        train=train_frame.iloc[calibration_end:fit_end].copy(),
        validation=train_frame.iloc[fit_end:].copy(),
        replay=test_frame.iloc[:replay_end].copy(),
        final_test=test_frame.iloc[replay_end:].copy(),
    )
    arrays = [features_labels(getattr(splits, name)) for name in (
        "calibration", "train", "validation", "replay", "final_test"
    )]
    (X_cal, _), (X_train, _), (X_val, _), (X_replay, y_replay), (X_test, y_test) = arrays
    scaler = StandardScaler().fit(X_train)
    X_cal_s, X_train_s, X_val_s, X_replay_s, X_test_s = [
        scaler.transform(values).astype("float32")
        for values in (X_cal, X_train, X_val, X_replay, X_test)
    ]
    raw_hashes = adapter.raw_hashes()
    manifest = make_manifest(
        adapter.descriptor.name,
        rows=train_n + len(test_frame),
        channels=X_train.shape[1],
        preprocess_hash=preprocessing_hash(scaler),
        split_hashes=split_hashes(splits),
        dataset_version=adapter.descriptor.version,
        raw_data_hash=sha256_json(raw_hashes),
        source=adapter.descriptor.source,
        license_name=adapter.descriptor.license,
        labels_hash=raw_hashes["labels"],
        timebase="SMAP one-minute buckets; timestamps anonymized",
        known_caveats=adapter.descriptor.known_caveats,
        split_policy={
            "calibration": f"official train rows 0:{calibration_end}",
            "train": f"official train rows {calibration_end}:{fit_end}",
            "validation": f"official train rows {fit_end}:{train_n}",
            "replay": f"official test rows 0:{replay_end}",
            "final_test": f"official test rows {replay_end}:{len(test_frame)}",
        },
        leakage_overrides={
            "upstream_preprocessing_independent_of_test": False,
        },
    ).to_dict()

    operator = make_operator("q4", 16, seed=seed)
    graph = graph_declaration(operator, "q4", 0.618)
    with Timer() as timer:
        model = fit_tessera_model(
            X_train_s,
            operator,
            code_dim=8,
            alpha=0.618,
            epochs=epochs,
            seed=seed,
            X_validation=X_val_s,
            sequence_chunk_size=128,
            prediction_target_dims=1,
        )
    def target_rows(values):
        rows = pd.DataFrame(evaluate_sequence(model, values)["rows"])
        rows["prediction_loss"] = rows["target_prediction_loss"]
        rows["reconstruction_loss"] = rows["target_reconstruction_loss"]
        return add_rate_distortion(rows)

    normal_sequence = np.concatenate([X_cal_s, X_train_s], axis=0)
    normal_rows = target_rows(normal_sequence)
    thresholds = calibrate_anomaly_model(
        normal_rows,
        warn_quantile=0.90,
        block_quantile=0.995,
        memory_quantile=0.70,
        components=("delta_phi", "rate"),
        fusion="mean_instant",
    )

    def evaluate(values, labels):
        rows = target_rows(values)
        rows = score_anomalies(rows, thresholds)
        return apply_triadic_gates(rows, thresholds, labels=labels[1:])

    replay_rows = evaluate(X_replay_s, y_replay)
    test_rows = evaluate(X_test_s, y_test)
    replay_summary = summarize_gates(replay_rows)
    summary = summarize_gates(test_rows)
    summary["mean_prediction_loss"] = float(test_rows["prediction_loss"].mean())
    summary["replay_pass_rate"] = replay_summary["replay_pass_rate"]
    summary["replay_false_memory_rate"] = replay_summary["false_memory_rate"]
    summary["anomaly_ablation"] = anomaly_ablation(test_rows)

    target_train = X_train_s[:, :1]
    target_test = X_test_s[:, :1]
    baselines = [
        evaluate_persistence(target_test),
        evaluate_ewma(target_test),
        evaluate_pca_codec(target_train, target_test, 1),
        evaluate_random_projection(target_train, target_test, 1, seed),
        evaluate_dense_autoencoder(target_train, target_test, 1, seed=seed),
        evaluate_reservoir(target_train, target_test, seed=seed),
        evaluate_matrix_profile(target_train, target_test),
    ]
    best = min(row["mean_prediction_loss"] for row in baselines)
    summary["best_baseline_prediction_loss"] = float(best)
    summary["baseline_gap"] = float(best - summary["mean_prediction_loss"])

    run_dir = make_run_dir(out)
    run_id = run_dir.name
    budget = ExperimentBudget(
        epochs=epochs,
        parameter_count=model_parameter_count(model),
        train_rows=len(X_train_s),
        latency_ms=timer.elapsed_ms,
    )
    codec = {
        "predictor": "ewma_anchor_plus_sparse_neural_innovation",
        "anomaly_sensor": "spacecraft_field_energy_mean_instant",
        "input_schema": "feature_0_target_features_1_24_command_event_context",
        "prediction_target_dims": 1,
        "field_dim": 16,
        "code_dim": 8,
        "correction_gain": model.correction_gain,
        "training_epochs": epochs,
        "parameter_count": budget.parameter_count,
        "live_repair_enabled": False,
        "memory_promotion_enabled": False,
    }
    wounds = classify_wounds(test_rows, thresholds)
    certificate = make_dataset_transfer_certificate(
        run_id, manifest, graph, codec, summary, baselines, wounds
    )
    test_rows.to_csv(run_dir / "metrics" / "tessera_timeseries.csv", index=False)
    replay_rows.to_csv(run_dir / "metrics" / "replay_timeseries.csv", index=False)
    pd.DataFrame([summary]).to_csv(run_dir / "metrics" / "model_summary.csv", index=False)
    pd.DataFrame([replay_summary]).to_csv(run_dir / "metrics" / "replay_summary.csv", index=False)
    pd.DataFrame(baselines).to_csv(run_dir / "metrics" / "baseline_summary.csv", index=False)
    write_json(run_dir / "metrics" / "anomaly_ablation.json", summary["anomaly_ablation"])
    write_json(run_dir / "state" / "dataset_manifest.json", manifest)
    write_json(run_dir / "state" / "graph_declaration.json", graph)
    write_json(run_dir / "state" / "thresholds.json", thresholds)
    write_json(run_dir / "state" / "experiment_budget.json", budget.as_dict())
    write_json(run_dir / "state" / "final_test_access_ledger.json", {
        "access_count": 1, "mode": "single_pass_read_only", "post_test_tuning": False
    })
    write_wounds(run_dir / "ledgers" / "wounds.jsonl", wounds)
    write_json(run_dir / "certificates" / "dataset_transfer_certificate.json", certificate)
    write_plots(test_rows, run_dir / "visuals")
    artifacts = {
        "timeseries": "metrics/tessera_timeseries.csv",
        "replay_timeseries": "metrics/replay_timeseries.csv",
        "model_summary": "metrics/model_summary.csv",
        "baseline_summary": "metrics/baseline_summary.csv",
        "manifest": "state/dataset_manifest.json",
        "certificate": "certificates/dataset_transfer_certificate.json",
    }
    write_evidence(
        run_dir / "evidence" / "evidence_package.json",
        make_evidence_package(run_id, manifest, certificate, artifacts),
    )
    (run_dir / "reports" / "transfer_summary.md").write_text(
        "# NASA SMAP P-1 Diagnostic\n\n"
        f"```json\n{json.dumps(summary, indent=2)}\n```\n\n"
        "Inherited test-based scaling blocks clean T1 promotion.\n",
        encoding="utf-8",
    )
    return run_dir
