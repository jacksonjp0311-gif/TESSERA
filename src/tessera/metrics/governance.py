from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score


def summarize_gates(df: pd.DataFrame) -> dict:
    y = df.get('label')
    score_column = 'anomaly_score' if 'anomaly_score' in df else 'J_RD'
    score = df[score_column].to_numpy()
    pred = df['warn'].to_numpy()
    out = {
        'mean_J_RD': float(df['J_RD'].mean()),
        'mean_anomaly_score': float(df[score_column].mean()),
        'mean_delta_phi': float(df['delta_phi'].mean()),
        'warn_rate': float(df['warn'].mean()),
        'block_rate': float(df['block'].mean()),
        'memory_candidate_rate': float(df['memory_candidate'].mean()),
        'replay_pass_rate': float(df['replay_pass'].mean()),
        'false_memory_rate': float(df['false_memory_candidate'].mean()),
    }
    if y is not None:
        y = y.to_numpy(dtype=int)
        if len(set(y.tolist())) > 1:
            out['auc'] = float(roc_auc_score(y, score))
        else:
            out['auc'] = None
        out['f1_warn'] = float(f1_score(y, pred, zero_division=0))
        out['precision_warn'] = float(precision_score(y, pred, zero_division=0))
        out['recall_warn'] = float(recall_score(y, pred, zero_division=0))
        normal = df[df['label']==0]
        anomaly = df[df['label']==1]
        out['replay_pass_rate'] = float(normal['memory_candidate'].mean()) if len(normal) else 0.0
        out['false_memory_candidate_rate'] = float(anomaly['false_memory_candidate'].mean()) if len(anomaly) else 0.0
        out['false_memory_rate'] = out['false_memory_candidate_rate']
        out['memory_selectivity'] = float(normal['memory_candidate'].mean() - anomaly['memory_candidate'].mean()) if len(normal) and len(anomaly) else 0.0
        out['block_false_positive'] = float(normal['block'].mean()) if len(normal) else 0.0
        out['missed_warning'] = float((anomaly['warn']==0).mean()) if len(anomaly) else 0.0
        out['governance_harm'] = float(0.35*out['false_memory_rate'] + 0.35*out['block_false_positive'] + 0.30*out['missed_warning'])
    return out
