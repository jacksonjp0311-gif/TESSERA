from __future__ import annotations
import pandas as pd


def calibrate_thresholds(cal_df: pd.DataFrame) -> dict:
    return {
        'warn_J_RD': float(cal_df['J_RD'].quantile(0.90)),
        'block_J_RD': float(cal_df['J_RD'].quantile(0.975)),
        'memory_J_RD': float(cal_df['J_RD'].quantile(0.70)),
        'block_delta_phi': float(cal_df['delta_phi'].quantile(0.975)),
        'block_code_drift': float(cal_df['code_drift'].quantile(0.975)),
    }


def apply_triadic_gates(df: pd.DataFrame, thresholds: dict, labels=None) -> pd.DataFrame:
    out = df.copy()
    out['warn'] = (out['J_RD'] > thresholds['warn_J_RD']).astype(int)
    out['block'] = ((out['J_RD'] > thresholds['block_J_RD']) | (out['delta_phi'] > thresholds['block_delta_phi']) | (out['code_drift'] > thresholds['block_code_drift'])).astype(int)
    out['memory_candidate'] = ((out['J_RD'] <= thresholds['memory_J_RD']) & (out['block'] == 0)).astype(int)
    if labels is not None:
        lab = labels[:len(out)]
        out['label'] = lab
        out['replay_pass'] = ((out['memory_candidate'] == 1) & (out['label'] == 0)).astype(int)
        out['promoted_memory'] = out['replay_pass']
        out['false_memory_candidate'] = ((out['memory_candidate'] == 1) & (out['label'] == 1)).astype(int)
    else:
        out['replay_pass'] = 0
        out['promoted_memory'] = 0
        out['false_memory_candidate'] = 0
    return out
