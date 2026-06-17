from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from tessera.data.synthetic import generate_synthetic_telemetry
from tessera.data.splits import chronological_splits, features_labels
from tessera.data.manifest import make_manifest
from tessera.data.leakage_guard import validate_manifest
from tessera.graph.topologies import make_operator
from tessera.graph.spectral import graph_declaration
from tessera.model.train import fit_tessera_model, evaluate_sequence
from tessera.metrics.rate_distortion import add_rate_distortion
from tessera.memory.gates import calibrate_thresholds, apply_triadic_gates
from tessera.metrics.governance import summarize_gates
from tessera.baselines.persistence import evaluate_persistence
from tessera.baselines.pca_codec import evaluate_pca_codec
from tessera.baselines.random_projection import evaluate_random_projection
from tessera.baselines.ewma import evaluate_ewma
from tessera.memory.wound_ledger import classify_wounds, write_wounds
from tessera.memory.certificates import make_transfer_certificate, write_json
from tessera.evidence.package import make_evidence_package, write_evidence
from tessera.visuals.plots import write_plots
from tessera.utils.paths import make_run_dir, publish_latest_run, publish_latest_run, publish_latest_run, publish_latest_run


def run(out='outputs', steps=900, channels=6, seed=42, topology='q4', field_dim=16, code_dim=8, alpha=0.618, epochs=6):
    run_dir = make_run_dir(out)
    run_id = run_dir.name
    df, labels = generate_synthetic_telemetry(steps=steps, channels=channels, seed=seed)
    manifest = make_manifest('tessera_synthetic_telemetry', rows=len(df), channels=channels).to_dict()
    ok, reasons = validate_manifest(manifest)
    if not ok:
        raise RuntimeError(f'leakage guard failed: {reasons}')
    splits = chronological_splits(df)
    X_cal, y_cal = features_labels(splits.calibration)
    X_train, y_train = features_labels(splits.train)
    X_val, y_val = features_labels(splits.validation)
    X_replay, y_replay = features_labels(splits.replay)
    X_test, y_test = features_labels(splits.final_test)

    scaler = StandardScaler().fit(X_train)
    X_cal_s = scaler.transform(X_cal).astype('float32')
    X_train_s = scaler.transform(X_train).astype('float32')
    X_val_s = scaler.transform(X_val).astype('float32')
    X_test_s = scaler.transform(X_test).astype('float32')

    P = make_operator(topology, field_dim, seed=seed)
    graph = graph_declaration(P, topology, alpha)
    if not graph['stability_condition_alpha_rho_lt_1']:
        raise RuntimeError('unstable graph declaration: alpha*rho(P) must be < 1')
    model = fit_tessera_model(X_train_s, P, code_dim=code_dim, alpha=alpha, epochs=epochs, seed=seed)

    cal_rows = pd.DataFrame(evaluate_sequence(model, X_cal_s)['rows'])
    val_rows = pd.DataFrame(evaluate_sequence(model, X_val_s)['rows'])
    cal_rows = add_rate_distortion(pd.concat([cal_rows, val_rows], ignore_index=True))
    thresholds = calibrate_thresholds(cal_rows)

    test_rows = pd.DataFrame(evaluate_sequence(model, X_test_s)['rows'])
    test_rows = add_rate_distortion(test_rows)
    # labels align to x_t steps, length len(X_test)-1
    test_rows = apply_triadic_gates(test_rows, thresholds, labels=y_test[:-1])
    summary = summarize_gates(test_rows)
    summary['mean_prediction_loss'] = float(test_rows['prediction_loss'].mean())
    summary['code_dim'] = int(code_dim)
    summary['field_dim'] = int(field_dim)
    summary['topology'] = topology

    baselines = [
        evaluate_persistence(X_test_s),
        evaluate_pca_codec(X_train_s, X_test_s, code_dim),
        evaluate_random_projection(X_train_s, X_test_s, code_dim, seed),
        evaluate_ewma(X_test_s),
    ]
    wounds = classify_wounds(test_rows, thresholds)

    codec = {
        'encoder': 'torch_small_mlp',
        'decoder': 'torch_small_mlp',
        'predictor': 'torch_small_mlp',
        'field_dim': field_dim,
        'code_dim': code_dim,
        'training_epochs': epochs,
        'live_repair_enabled': False,
        'shadow_repair_required': True,
    }
    cert = make_transfer_certificate(run_id, manifest, graph, codec, summary, baselines, wounds)

    # Write artifacts.
    test_rows.to_csv(run_dir/'metrics'/'tessera_timeseries.csv', index=False)
    pd.DataFrame([summary]).to_csv(run_dir/'metrics'/'model_summary.csv', index=False)
    pd.DataFrame(baselines).to_csv(run_dir/'metrics'/'baseline_summary.csv', index=False)
    write_wounds(run_dir/'ledgers'/'wounds.jsonl', wounds)
    write_json(run_dir/'certificates'/'transfer_certificate.json', cert)
    write_json(run_dir/'state'/'dataset_manifest.json', manifest)
    write_json(run_dir/'state'/'graph_declaration.json', graph)
    write_json(run_dir/'state'/'thresholds.json', thresholds)
    write_plots(test_rows, run_dir/'visuals')
    artifacts = {
        'timeseries': 'metrics/tessera_timeseries.csv',
        'model_summary': 'metrics/model_summary.csv',
        'baseline_summary': 'metrics/baseline_summary.csv',
        'wounds': 'ledgers/wounds.jsonl',
        'certificate': 'certificates/transfer_certificate.json',
    }
    evidence = make_evidence_package(run_id, manifest, cert, artifacts)
    write_evidence(run_dir/'evidence'/'evidence_package.json', evidence)
    summary_md = f"""# TESSERA Engine v0.1 Run Summary\n\nrun_id: `{run_id}`\n\n## Claim ceiling\n\n`{cert['claim_ceiling']}`\n\n## Core metrics\n\n```json\n{json.dumps(summary, indent=2)}\n```\n\n## Baselines\n\n```json\n{json.dumps(baselines, indent=2)}\n```\n\n## Non-claim lock\n\nSynthetic success is not transfer. Low loss is not truth. Memory is certified compression.\n"""
    (run_dir/'reports'/'tessera_run_summary.md').write_text(summary_md, encoding='utf-8')
    publish_latest_run(run_dir)
    print(f'TESSERA Engine v0.1 run complete: {run_dir}')
    print(f"claim_ceiling: {cert['claim_ceiling']}")
    print(f"auc: {summary.get('auc')}, memory_selectivity: {summary.get('memory_selectivity')}, false_memory_rate: {summary.get('false_memory_rate')}")
    return run_dir
