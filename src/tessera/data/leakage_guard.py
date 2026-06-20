from __future__ import annotations
from typing import Dict


def validate_manifest(manifest: Dict) -> tuple[bool, list[str]]:
    reasons = []
    controls = manifest.get('leakage_controls', {})
    for key in ['future_statistics_blocked','test_labels_blocked_from_tuning','preprocessing_fit_on_train_only','time_order_preserved','replay_held_out_from_repair','final_test_read_only']:
        if controls.get(key) is not True:
            reasons.append(f'leakage_control_failed:{key}')
    if not manifest.get('raw_data_hash'):
        reasons.append('missing_raw_data_hash')
    if not manifest.get('split_policy'):
        reasons.append('missing_split_policy')
    if not manifest.get('split_hashes'):
        reasons.append('missing_split_hashes')
    if not manifest.get('preprocess_hash'):
        reasons.append('missing_preprocess_hash')
    return len(reasons) == 0, reasons
