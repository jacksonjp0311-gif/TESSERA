from __future__ import annotations
import json
from pathlib import Path
import pandas as pd


def classify_wounds(df: pd.DataFrame, thresholds: dict) -> list[dict]:
    wounds=[]
    for _, r in df.iterrows():
        types=[]
        if r['reconstruction_loss'] > df['reconstruction_loss'].quantile(.95): types.append('W_reconstruct')
        if r['prediction_loss'] > df['prediction_loss'].quantile(.95): types.append('W_predict')
        if 'score_code_drift' in r:
            if r['score_code_drift'] > thresholds.get('block_score', float('inf')):
                types.append('W_codedrift')
        elif r['code_drift'] > thresholds.get('block_code_drift', float('inf')):
            types.append('W_codedrift')
        if r.get('false_memory_candidate',0) == 1: types.append('W_falsememory')
        if r.get('block',0) == 1 and r.get('label',0) == 0: types.append('W_block_false_positive')
        for t in types:
            wounds.append({'step': int(r['step']), 'wound_type': t, 'J_RD': float(r['J_RD']), 'claim_boundary': 'repair_evidence_not_training_permission'})
    return wounds


def write_wounds(path: str | Path, wounds: list[dict]) -> None:
    path = Path(path)
    with path.open('w', encoding='utf-8') as f:
        for w in wounds:
            f.write(json.dumps(w) + '\n')
