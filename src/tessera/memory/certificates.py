from __future__ import annotations
import json
from pathlib import Path
from tessera.utils.hashing import sha256_json


def make_transfer_certificate(run_id: str, manifest: dict, graph: dict, codec: dict, metrics: dict, baselines: list[dict], wounds: list[dict]) -> dict:
    baseline_best = min([b.get('mean_prediction_loss', float('inf')) for b in baselines]) if baselines else None
    baseline_parity_tolerance = 0.001
    claim_ceiling = 'diagnostic'
    phase_1_run_supported = (
        metrics.get('auc', 0.0) > 0.60
        and metrics.get('replay_pass_rate', 0.0) >= 0.60
        and metrics.get('missed_warning', 1.0) < 0.35
        and metrics.get('false_memory_rate', 1.0) <= 0.05
    )
    if phase_1_run_supported:
        claim_ceiling = 'synthetic_phase_1_run_supported'
    if (
        baseline_best is not None
        and metrics.get('mean_prediction_loss', float('inf'))
        > baseline_best * (1.0 + baseline_parity_tolerance)
    ):
        claim_ceiling = 'diagnostic_baseline_limited'
    cert = {
        'schema': 'TESSERA-synthetic-diagnostic-certificate-v0.2',
        'system': 'Tessera',
        'version': 'engine-v0.2-diagnostic',
        'run_id': run_id,
        'dataset_manifest_hash': manifest.get('manifest_hash'),
        'graph': graph,
        'codec': codec,
        'metrics': metrics,
        'baselines': baselines,
        'wound_count': len(wounds),
        'claim_ceiling': claim_ceiling,
        'transfer_level': 'T0_synthetic',
        'real_telemetry_transfer': False,
        'baseline_parity_tolerance_fraction': baseline_parity_tolerance,
        'phase_1_run_supported': phase_1_run_supported,
        'non_claim_locks': {
            'synthetic_success_is_not_transfer': True,
            'low_loss_is_not_truth': True,
            'memory_is_certified_compression': True,
            'repair_requires_shadow_testing': True,
        },
    }
    cert['certificate_hash'] = sha256_json(cert)
    return cert


def make_dataset_transfer_certificate(
    run_id: str,
    manifest: dict,
    graph: dict,
    codec: dict,
    metrics: dict,
    baselines: list[dict],
    wounds: list[dict],
) -> dict:
    by_name = {row["model"]: row for row in baselines}
    strong_names = ("dense_autoencoder", "reservoir_esn", "matrix_profile_neighbor")
    simple_names = ("persistence", "ewma")
    strong_best = min(
        by_name[name]["mean_prediction_loss"]
        for name in strong_names
        if name in by_name
    )
    simple_worst = max(
        by_name[name]["mean_prediction_loss"]
        for name in simple_names
        if name in by_name
    )
    prediction_loss = metrics.get("mean_prediction_loss", float("inf"))
    gates = {
        "manifest_leakage_controls_clear": all(
            manifest.get("leakage_controls", {}).values()
        ),
        "auc_above_0_60": metrics.get("auc", 0.0) > 0.60,
        "replay_pass_at_least_0_60": metrics.get("replay_pass_rate", 0.0) >= 0.60,
        "missed_warning_below_0_35": metrics.get("missed_warning", 1.0) < 0.35,
        "false_memory_at_most_0_05": metrics.get("false_memory_rate", 1.0) <= 0.05,
        "beats_at_least_one_strong_baseline": prediction_loss < strong_best,
        "not_below_all_simple_baselines": prediction_loss <= simple_worst * 1.05,
    }
    supported = all(gates.values())
    cert = {
        "schema": "TESSERA-dataset-scoped-transfer-certificate-v0.1",
        "system": "Tessera",
        "version": "engine-v0.5-dataset-trial",
        "run_id": run_id,
        "dataset_name": manifest["dataset_name"],
        "dataset_version": manifest["dataset_version"],
        "dataset_manifest_hash": manifest["manifest_hash"],
        "graph": graph,
        "codec": codec,
        "metrics": metrics,
        "baselines": baselines,
        "wound_count": len(wounds),
        "transfer_level": "T1_dataset_scoped",
        "real_telemetry_evaluated": True,
        "dataset_scoped_transfer_supported": supported,
        "transfer_gates": gates,
        "claim_ceiling": (
            "dataset_scoped_T1_supported" if supported else "dataset_scoped_T1_diagnostic"
        ),
        "non_claim_locks": {
            "dataset_win_is_not_generalization": True,
            "single_stream_is_not_family_diversity": True,
            "replay_is_not_safety": True,
            "no_live_memory_or_repair_authority": True,
        },
    }
    cert["certificate_hash"] = sha256_json(cert)
    return cert


def write_json(path: str | Path, obj: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding='utf-8')
