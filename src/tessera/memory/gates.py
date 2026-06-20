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
    score_column = 'anomaly_score' if 'anomaly_score' in out else 'J_RD'
    warn_threshold = thresholds.get('warn_score', thresholds.get('warn_J_RD'))
    block_threshold = thresholds.get('block_score', thresholds.get('block_J_RD'))
    memory_threshold = thresholds.get('memory_score', thresholds.get('memory_J_RD'))
    out['warn'] = (out[score_column] > warn_threshold).astype(int)
    out['block'] = (out[score_column] > block_threshold).astype(int)
    out['memory_candidate'] = (
        (out[score_column] <= memory_threshold) & (out['block'] == 0)
    ).astype(int)
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


def apply_independent_memory_gate(
    df: pd.DataFrame,
    *,
    threshold: float,
) -> pd.DataFrame:
    """Recompute memory eligibility from a separately calibrated normality model."""
    if "memory_normality_score" not in df:
        raise ValueError(
            "independent memory gate requires memory_normality_score"
        )
    out = df.copy()
    out["memory_candidate"] = (
        (out["memory_normality_score"] <= threshold)
        & (out["block"] == 0)
    ).astype(int)
    if "label" in out:
        out["replay_pass"] = (
            (out["memory_candidate"] == 1) & (out["label"] == 0)
        ).astype(int)
        out["promoted_memory"] = out["replay_pass"]
        out["false_memory_candidate"] = (
            (out["memory_candidate"] == 1) & (out["label"] == 1)
        ).astype(int)
    return out
