from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass
class SplitBundle:
    calibration: pd.DataFrame
    train: pd.DataFrame
    validation: pd.DataFrame
    replay: pd.DataFrame
    final_test: pd.DataFrame


def chronological_splits(df: pd.DataFrame) -> SplitBundle:
    n = len(df)
    # Keep windows chronological. Train/calibration intentionally begin before main anomaly windows.
    # Keep calibration/train before the first synthetic anomaly (first anomaly begins near 22%).
    # This preserves the v1.7 rule: fit normal operating envelope before testing transfer.
    a,b,c,d = int(.12*n), int(.20*n), int(.52*n), int(.74*n)
    return SplitBundle(
        calibration=df.iloc[:a].copy(),
        train=df.iloc[a:b].copy(),
        validation=df.iloc[b:c].copy(),
        replay=df.iloc[c:d].copy(),
        final_test=df.iloc[d:].copy(),
    )


def fixed_index_splits(
    df: pd.DataFrame,
    *,
    calibration_end: int,
    train_end: int,
    validation_end: int,
    replay_end: int,
) -> SplitBundle:
    boundaries = (0, calibration_end, train_end, validation_end, replay_end, len(df))
    if tuple(sorted(boundaries)) != boundaries or len(set(boundaries)) != len(boundaries):
        raise ValueError("split boundaries must be strictly increasing")
    return SplitBundle(
        calibration=df.iloc[:calibration_end].copy(),
        train=df.iloc[calibration_end:train_end].copy(),
        validation=df.iloc[train_end:validation_end].copy(),
        replay=df.iloc[validation_end:replay_end].copy(),
        final_test=df.iloc[replay_end:].copy(),
    )


def features_labels(df: pd.DataFrame):
    X = df.drop(columns=['label', 'timestamp'], errors='ignore').to_numpy(dtype='float32')
    y = df['label'].to_numpy(dtype=int)
    return X, y
