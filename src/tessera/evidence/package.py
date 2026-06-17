from __future__ import annotations
import json
from pathlib import Path
from tessera.utils.hashing import sha256_json


def make_evidence_package(run_id, manifest, certificate, artifacts):
    pkg = {
        'schema': 'TESSERA-v0.1-evidence-package',
        'run_id': run_id,
        'manifest': manifest,
        'certificate_hash': certificate.get('certificate_hash'),
        'artifacts': artifacts,
        'claim_boundary': certificate.get('claim_ceiling'),
        'non_claim_locks_preserved': True,
    }
    pkg['evidence_hash'] = sha256_json(pkg)
    return pkg


def write_evidence(path, pkg):
    Path(path).write_text(json.dumps(pkg, indent=2), encoding='utf-8')
