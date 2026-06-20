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
from tessera.data.adapters import DatasetDescriptor, UcrAnomalyAdapter
from tessera.data.manifest import make_manifest
from tessera.data.splits import SplitBundle, features_labels
from tessera.evidence.package import make_evidence_package, write_evidence
from tessera.experiments.integrity import ExperimentBudget, Timer, model_parameter_count, preprocessing_hash, split_hashes
from tessera.graph.spectral import graph_declaration
from tessera.graph.topologies import make_operator
from tessera.memory.certificates import make_dataset_transfer_certificate, write_json
from tessera.memory.gates import (
    apply_independent_memory_gate,
    apply_triadic_gates,
)
from tessera.memory.episodes import (
    apply_event_memory_quarantine,
    apply_routed_event_memory_quarantine,
)
from tessera.memory.wound_ledger import classify_wounds, write_wounds
from tessera.metrics.anomaly import anomaly_ablation, calibrate_anomaly_model, score_anomalies
from tessera.metrics.governance import summarize_gates
from tessera.metrics.rate_distortion import add_rate_distortion
from tessera.metrics.subsequence import (
    causal_event_persistence,
    z_normalized_subsequence_scores,
)
from tessera.metrics.router import (
    calibrate_confidence_router,
    calibrate_selective_router,
    calibrate_sensor_router,
    robust_point_scores,
    route_sensor_scores,
    route_sensor_scores_with_abstention,
    route_sensor_scores_selectively,
)
from tessera.model.train import evaluate_sequence, fit_tessera_model
from tessera.model.prediction_experts import (
    prediction_losses,
    select_prediction_expert,
)
from tessera.utils.paths import make_run_dir
from tessera.visuals.plots import write_plots


def find_series(root: Path, filename: str) -> Path:
    matches = list((root / "datasets" / "ucr" / "extracted").rglob(filename))
    if len(matches) != 1:
        raise ValueError(f"expected one UCR series named {filename}, found {len(matches)}")
    return matches[0]


def run(
    *,
    root: str | Path = ".",
    filename: str,
    role: str,
    out: str | Path = "outputs/transfers/ucr",
    epochs: int = 5,
    seed: int = 42,
    episode_quarantine: int = 0,
    sensor_mode: str = "subsequence",
) -> Path:
    root = Path(root).resolve()
    path = find_series(root, filename)
    adapter = UcrAnomalyAdapter(
        path,
        DatasetDescriptor(
            name=f"ucr_{path.stem}",
            version="UCR-2021@figshare-26410744-v1",
            source="https://doi.org/10.6084/m9.figshare.26410744.v1",
            license="CC BY 4.0",
            label_policy="filename_encoded_single_anomaly_interval_evaluation_only",
            known_caveats=(
                "single univariate series",
                "one anomaly interval",
                f"preregistered role: {role}",
            ),
        ),
    )
    frame = adapter.load()
    meta = adapter.metadata()
    train_end = meta["train_end"]
    calibration_end = max(20, int(train_end * 0.15))
    fit_end = max(calibration_end + 20, int(train_end * 0.70))
    test_mid = train_end + (len(frame) - train_end) // 2
    if meta["anomaly_start"] < test_mid:
        raise ValueError("selected UCR anomaly must remain in final-test partition")
    splits = SplitBundle(
        calibration=frame.iloc[:calibration_end].copy(),
        train=frame.iloc[calibration_end:fit_end].copy(),
        validation=frame.iloc[fit_end:train_end].copy(),
        replay=frame.iloc[train_end:test_mid].copy(),
        final_test=frame.iloc[test_mid:].copy(),
    )
    parts = [features_labels(getattr(splits, name)) for name in (
        "calibration", "train", "validation", "replay", "final_test"
    )]
    (X_cal, _), (X_train, _), (X_val, _), (X_replay, y_replay), (X_test, y_test) = parts
    scaler = StandardScaler().fit(X_train)
    X_cal_s, X_train_s, X_val_s, X_replay_s, X_test_s = [
        scaler.transform(values).astype("float32")
        for values in (X_cal, X_train, X_val, X_replay, X_test)
    ]
    manifest = make_manifest(
        adapter.descriptor.name,
        rows=len(frame),
        channels=1,
        preprocess_hash=preprocessing_hash(scaler),
        split_hashes=split_hashes(splits),
        dataset_version=adapter.descriptor.version,
        raw_data_hash=adapter.raw_hash(),
        source=adapter.descriptor.source,
        license_name=adapter.descriptor.license,
        timebase="ordered samples; physical timebase dataset-specific",
        known_caveats=adapter.descriptor.known_caveats,
        split_policy={
            "calibration": f"normal prefix rows 0:{calibration_end}",
            "train": f"normal prefix rows {calibration_end}:{fit_end}",
            "validation": f"normal prefix rows {fit_end}:{train_end}",
            "replay": f"post-train normal rows {train_end}:{test_mid}",
            "final_test": f"single-pass rows {test_mid}:{len(frame)} containing anomaly {meta['anomaly_start']}:{meta['anomaly_end']}",
        },
    ).to_dict()
    operator = make_operator("q4", 16, seed=seed)
    graph = graph_declaration(operator, "q4", 0.618)
    with Timer() as timer:
        model = fit_tessera_model(
            X_train_s, operator, code_dim=8, alpha=0.618, epochs=epochs,
            seed=seed, X_validation=X_val_s, sequence_chunk_size=128,
        )
    prediction_expert, prediction_selection = select_prediction_expert(
        X_train_s, X_val_s
    )
    normal = np.concatenate([X_cal_s, X_train_s], axis=0)
    normal_rows = add_rate_distortion(pd.DataFrame(evaluate_sequence(model, normal)["rows"]))
    window = 24
    event_hold = 12
    validation_discord = causal_event_persistence(
        z_normalized_subsequence_scores(
            X_train_s[:, 0], X_val_s[1:, 0], window=window
        ),
        hold=event_hold,
    )
    if sensor_mode in {"router", "abstaining-router", "selective-router"}:
        validation_point = robust_point_scores(
            X_train_s[:, 0], X_val_s[1:, 0]
        )
        if sensor_mode == "selective-router":
            thresholds = calibrate_selective_router(
                validation_point, validation_discord
            )
        elif sensor_mode == "abstaining-router":
            thresholds = calibrate_confidence_router(
                validation_point, validation_discord
            )
        else:
            thresholds = calibrate_sensor_router(
                validation_point, validation_discord
            )
        thresholds.update({"window": window, "event_hold": event_hold})
    else:
        thresholds = {
            "schema": "TESSERA-UCR-SUBSEQUENCE-CALIBRATION-v0.1",
            "detector": "z_normalized_nearest_normal_subsequence",
            "window": window,
            "event_hold": event_hold,
            "warn_score": float(np.quantile(validation_discord, 0.90)),
            "block_score": float(np.quantile(validation_discord, 0.995)),
            "memory_score": float(np.quantile(validation_discord, 0.70)),
            "calibration_source": "normal_validation_only",
        }

    def evaluate(values, labels):
        rows = add_rate_distortion(pd.DataFrame(evaluate_sequence(model, values)["rows"]))
        rows["neural_prediction_loss"] = rows["prediction_loss"]
        rows["selected_prediction_loss"] = prediction_losses(
            prediction_expert,
            values,
            history=X_train_s,
        )
        rows["prediction_loss"] = rows["selected_prediction_loss"]
        discord = causal_event_persistence(
            z_normalized_subsequence_scores(
                X_train_s[:, 0], values[1:, 0], window=window
            ),
            hold=event_hold,
        )
        if sensor_mode in {
            "router",
            "abstaining-router",
            "selective-router",
        }:
            point = robust_point_scores(X_train_s[:, 0], values[1:, 0])
            if sensor_mode == "selective-router":
                routed = route_sensor_scores_selectively(
                    point, discord, thresholds
                )
            elif sensor_mode == "abstaining-router":
                routed = route_sensor_scores_with_abstention(
                    point, discord, thresholds
                )
            else:
                routed = route_sensor_scores(point, discord, thresholds)
            for column in routed:
                rows[column] = routed[column].to_numpy()
        else:
            rows["score_subsequence_discord"] = discord
            rows["anomaly_score"] = discord
        rows["instant_anomaly_score"] = rows["anomaly_score"]
        rows["short_anomaly_score"] = rows["anomaly_score"]
        rows["medium_anomaly_score"] = rows["anomaly_score"]
        rows = apply_triadic_gates(rows, thresholds, labels=labels[1:])
        if sensor_mode in {"abstaining-router", "selective-router"}:
            rows = apply_independent_memory_gate(
                rows,
                threshold=thresholds["memory_normality_threshold"],
            )
        if episode_quarantine > 0:
            if sensor_mode in {
                "router",
                "abstaining-router",
                "selective-router",
            }:
                rows = apply_routed_event_memory_quarantine(
                    rows,
                    point_hold=2,
                    subsequence_hold=episode_quarantine,
                    abstain_hold=episode_quarantine,
                )
            else:
                rows = apply_event_memory_quarantine(
                    rows, hold=episode_quarantine
                )
        return rows

    replay_rows = evaluate(X_replay_s, y_replay)
    test_rows = evaluate(X_test_s, y_test)
    replay_summary = summarize_gates(replay_rows)
    summary = summarize_gates(test_rows)
    summary["mean_prediction_loss"] = float(test_rows["prediction_loss"].mean())
    summary["mean_neural_prediction_loss"] = float(
        test_rows["neural_prediction_loss"].mean()
    )
    summary["selected_prediction_expert"] = prediction_expert.name
    summary["replay_pass_rate"] = replay_summary["replay_pass_rate"]
    summary["replay_false_memory_rate"] = replay_summary["false_memory_rate"]
    summary["anomaly_ablation"] = {
        "sensor_mode": sensor_mode,
        "routed_score": float(summary["auc"]),
        "window": window,
        "event_hold": event_hold,
    }
    if sensor_mode in {
        "router",
        "abstaining-router",
        "selective-router",
    }:
        summary["sensor_route_counts"] = (
            test_rows["sensor_route"].value_counts().to_dict()
        )
    if sensor_mode in {"abstaining-router", "selective-router"}:
        summary["abstention_rate"] = float(
            (test_rows["sensor_route"] == "abstain").mean()
        )
        summary["mean_memory_normality_score"] = float(
            test_rows["memory_normality_score"].mean()
        )
    if sensor_mode == "selective-router":
        summary["specialist_coverage"] = float(
            (test_rows["sensor_route"] != "abstain").mean()
        )
        summary["mean_max_fusion_score"] = float(
            test_rows["max_fusion_score"].mean()
        )
    baselines = [
        evaluate_persistence(X_test_s), evaluate_ewma(X_test_s),
        evaluate_pca_codec(X_train_s, X_test_s, 1),
        evaluate_random_projection(X_train_s, X_test_s, 1, seed),
        evaluate_dense_autoencoder(X_train_s, X_test_s, 1, seed=seed),
        evaluate_reservoir(X_train_s, X_test_s, seed=seed),
        evaluate_matrix_profile(X_train_s, X_test_s),
    ]
    best = min(row["mean_prediction_loss"] for row in baselines)
    summary["best_baseline_prediction_loss"] = float(best)
    summary["baseline_gap"] = float(best - summary["mean_prediction_loss"])
    run_dir = make_run_dir(Path(out) / role)
    run_id = run_dir.name
    budget = ExperimentBudget(epochs, model_parameter_count(model), len(X_train_s), timer.elapsed_ms)
    codec = {
        "predictor": "normal_validation_selected_causal_expert",
        "neural_predictor": "ewma_anchor_plus_sparse_neural_innovation",
        "prediction_expert_selection": prediction_selection,
        "anomaly_sensor": (
            "coverage_constrained_selective_specialist_router"
            if sensor_mode == "selective-router"
            else "confidence_aware_point_subsequence_abstain_router"
            if sensor_mode == "abstaining-router"
            else "normal_calibrated_point_subsequence_router"
            if sensor_mode == "router"
            else "z_normalized_nearest_normal_subsequence"
        ),
        "sensor_mode": sensor_mode,
        "subsequence_window": window,
        "event_persistence_hold": event_hold,
        "memory_episode_quarantine": episode_quarantine,
        "point_episode_quarantine": (
            2
            if sensor_mode
            in {"router", "abstaining-router", "selective-router"}
            else None
        ),
        "memory_eligibility": (
            "joint_sensor_normality_independent_of_detection_threshold"
            if sensor_mode in {"abstaining-router", "selective-router"}
            else "detection_score_threshold"
        ),
        "field_dim": 16, "code_dim": 8, "correction_gain": model.correction_gain,
        "training_epochs": epochs, "parameter_count": budget.parameter_count,
        "live_repair_enabled": False, "memory_promotion_enabled": False,
    }
    wounds = classify_wounds(test_rows, thresholds)
    cert = make_dataset_transfer_certificate(run_id, manifest, graph, codec, summary, baselines, wounds)
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
        "access_count": 1, "mode": "single_pass_read_only", "post_test_tuning": False, "role": role
    })
    write_wounds(run_dir / "ledgers" / "wounds.jsonl", wounds)
    write_json(run_dir / "certificates" / "dataset_transfer_certificate.json", cert)
    write_plots(test_rows, run_dir / "visuals")
    artifacts = {
        "timeseries": "metrics/tessera_timeseries.csv",
        "replay_timeseries": "metrics/replay_timeseries.csv",
        "model_summary": "metrics/model_summary.csv",
        "baseline_summary": "metrics/baseline_summary.csv",
        "manifest": "state/dataset_manifest.json",
        "certificate": "certificates/dataset_transfer_certificate.json",
    }
    write_evidence(run_dir / "evidence" / "evidence_package.json", make_evidence_package(run_id, manifest, cert, artifacts))
    (run_dir / "reports" / "transfer_summary.md").write_text(
        f"# UCR {role.title()} Trial\n\n```json\n{json.dumps(summary, indent=2)}\n```\n",
        encoding="utf-8",
    )
    return run_dir
