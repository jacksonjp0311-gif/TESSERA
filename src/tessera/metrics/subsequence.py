from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


def z_normalized_subsequence_scores(
    reference: np.ndarray,
    sequence: np.ndarray,
    *,
    window: int,
) -> np.ndarray:
    """Score each sequence endpoint by its nearest normal subsequence."""
    reference = np.asarray(reference, dtype=float).reshape(-1)
    sequence = np.asarray(sequence, dtype=float).reshape(-1)
    if len(reference) < window or len(sequence) == 0:
        raise ValueError("subsequence score requires a full reference window")
    reference_windows = np.lib.stride_tricks.sliding_window_view(reference, window)
    prefix = reference[-(window - 1) :] if window > 1 else np.empty(0)
    sequence_windows = np.lib.stride_tricks.sliding_window_view(
        np.concatenate([prefix, sequence]), window
    )

    def normalize(rows: np.ndarray) -> np.ndarray:
        center = rows.mean(axis=1, keepdims=True)
        scale = rows.std(axis=1, keepdims=True)
        return (rows - center) / np.maximum(scale, 1e-8)

    neighbors = NearestNeighbors(n_neighbors=1)
    neighbors.fit(normalize(reference_windows))
    distances, _ = neighbors.kneighbors(normalize(sequence_windows))
    return distances[:, 0]


def causal_event_persistence(scores: np.ndarray, *, hold: int) -> np.ndarray:
    """Carry anomaly evidence forward without using future observations."""
    return (
        pd.Series(np.asarray(scores, dtype=float))
        .rolling(hold, min_periods=1)
        .max()
        .to_numpy()
    )
