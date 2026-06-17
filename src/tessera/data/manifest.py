from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any
import json
from pathlib import Path
from tessera.utils.hashing import sha256_json

@dataclass
class DatasetManifest:
    schema: str
    dataset_name: str
    dataset_version: str
    raw_data_hash: str
    split_policy: Dict[str, str]
    label_policy: str
    leakage_controls: Dict[str, bool]
    claim_boundary: str = 'synthetic_or_dataset_scoped_evidence_only'

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['manifest_hash'] = sha256_json(d)
        return d


def make_manifest(dataset_name: str, rows: int, channels: int) -> DatasetManifest:
    raw = {'dataset_name': dataset_name, 'rows': rows, 'channels': channels}
    return DatasetManifest(
        schema='TESSERA-v0.1-dataset-manifest',
        dataset_name=dataset_name,
        dataset_version='synthetic-v0.1',
        raw_data_hash=sha256_json(raw),
        split_policy={
            'calibration':'first 16 percent chronological window',
            'train':'first 38 percent chronological window',
            'validation':'38-58 percent chronological window',
            'replay':'58-76 percent chronological window',
            'final_test':'76-100 percent chronological window',
        },
        label_policy='labels are used for evaluation and replay validation, not for training codec thresholds',
        leakage_controls={
            'future_statistics_blocked': True,
            'test_labels_blocked_from_tuning': True,
            'preprocessing_fit_on_train_only': True,
            'time_order_preserved': True,
        },
    )
