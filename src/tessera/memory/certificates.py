from __future__ import annotations
import json
from pathlib import Path
from tessera.utils.hashing import sha256_json


def make_transfer_certificate(run_id: str, manifest: dict, graph: dict, codec: dict, metrics: dict, baselines: list[dict], wounds: list[dict]) -> dict:
    baseline_best = min([b.get('mean_prediction_loss', float('inf')) for b in baselines]) if baselines else None
    claim_ceiling = 'diagnostic'
    if metrics.get('false_memory_rate', 1.0) <= 0.01 and metrics.get('replay_pass_rate', 0.0) > 0.05:
        claim_ceiling = 'synthetic_reference_supported'
    if baseline_best is not None and metrics.get('mean_prediction_loss', float('inf')) > baseline_best:
        claim_ceiling = 'diagnostic_baseline_limited'
    cert = {
        'schema': 'TESSERA-v0.1-engine-transfer-certificate',
        'system': 'Tessera',
        'version': 'engine-v0.1',
        'run_id': run_id,
        'dataset_manifest_hash': manifest.get('manifest_hash'),
        'graph': graph,
        'codec': codec,
        'metrics': metrics,
        'baselines': baselines,
        'wound_count': len(wounds),
        'claim_ceiling': claim_ceiling,
        'non_claim_locks': {
            'synthetic_success_is_not_transfer': True,
            'low_loss_is_not_truth': True,
            'memory_is_certified_compression': True,
            'repair_requires_shadow_testing': True,
        },
    }
    cert['certificate_hash'] = sha256_json(cert)
    return cert


def write_json(path: str | Path, obj: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding='utf-8')
