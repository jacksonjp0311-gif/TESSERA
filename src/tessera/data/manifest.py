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
    preprocess_hash: str
    split_hashes: Dict[str, str]
    split_policy: Dict[str, str]
    label_policy: str
    leakage_controls: Dict[str, bool]
    source: str = "generated_local"
    license: str = "internal_generated"
    labels_hash: str | None = None
    timebase: str = "ordered_rows"
    known_caveats: tuple[str, ...] = ()
    claim_boundary: str = 'synthetic_or_dataset_scoped_evidence_only'

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['manifest_hash'] = sha256_json(d)
        return d


def make_manifest(
    dataset_name: str,
    rows: int,
    channels: int,
    *,
    preprocess_hash: str = "pending_until_fit",
    split_hashes: Dict[str, str] | None = None,
    dataset_version: str = "synthetic-v0.1",
    raw_data_hash: str | None = None,
    source: str = "generated_local",
    license_name: str = "internal_generated",
    labels_hash: str | None = None,
    timebase: str = "ordered_rows",
    known_caveats: tuple[str, ...] = (),
    split_policy: Dict[str, str] | None = None,
    leakage_overrides: Dict[str, bool] | None = None,
) -> DatasetManifest:
    raw = {'dataset_name': dataset_name, 'rows': rows, 'channels': channels}
    leakage_controls = {
        'future_statistics_blocked': True,
        'test_labels_blocked_from_tuning': True,
        'preprocessing_fit_on_train_only': True,
        'time_order_preserved': True,
        'replay_held_out_from_repair': True,
        'final_test_read_only': True,
    }
    leakage_controls.update(leakage_overrides or {})
    return DatasetManifest(
        schema='TESSERA-v1.7-dataset-manifest',
        dataset_name=dataset_name,
        dataset_version=dataset_version,
        raw_data_hash=raw_data_hash or sha256_json(raw),
        preprocess_hash=preprocess_hash,
        split_hashes=split_hashes or {
            name: sha256_json({"dataset": dataset_name, "window": name, "rows": rows})
            for name in ("calibration", "train", "validation", "replay", "final_test")
        },
        split_policy=split_policy or {
            'calibration':'0-12 percent chronological window',
            'train':'12-20 percent chronological window',
            'validation':'20-52 percent chronological window',
            'replay':'52-74 percent chronological window',
            'final_test':'74-100 percent chronological window',
        },
        label_policy='labels are used for evaluation and replay validation, not for training codec thresholds',
        leakage_controls=leakage_controls,
        source=source,
        license=license_name,
        labels_hash=labels_hash,
        timebase=timebase,
        known_caveats=known_caveats,
    )
