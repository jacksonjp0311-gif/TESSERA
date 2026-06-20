from __future__ import annotations

import numpy as np
from sklearn.neighbors import NearestNeighbors


def evaluate_matrix_profile(
    X_train: np.ndarray, X_test: np.ndarray, *, window: int = 3
) -> dict:
    if len(X_train) <= window or len(X_test) <= window:
        return {
            "model": "matrix_profile_neighbor",
            "mean_prediction_loss": float("inf"),
            "mean_reconstruction_loss": 0.0,
        }
    train_windows = np.asarray(
        [X_train[index : index + window].reshape(-1) for index in range(len(X_train) - window)]
    )
    train_targets = X_train[window:]
    test_windows = np.asarray(
        [
            X_test[index : index + window].reshape(-1)
            for index in range(len(X_test) - window)
        ]
    )
    neighbors = NearestNeighbors(n_neighbors=1)
    neighbors.fit(train_windows)
    _, indices = neighbors.kneighbors(test_windows)
    predictions = train_targets[indices[:, 0]]
    losses = np.mean(
        (predictions - X_test[window:]) ** 2, axis=1
    )
    return {
        "model": "matrix_profile_neighbor",
        "mean_prediction_loss": float(losses.mean()),
        "mean_reconstruction_loss": 0.0,
    }
