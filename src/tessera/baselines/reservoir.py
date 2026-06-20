from __future__ import annotations

import numpy as np


def evaluate_reservoir(
    X_train: np.ndarray,
    X_test: np.ndarray,
    *,
    reservoir_dim: int = 32,
    seed: int = 42,
    ridge: float = 1e-3,
) -> dict:
    rng = np.random.default_rng(seed)
    input_weights = rng.normal(0, 0.25, size=(X_train.shape[1], reservoir_dim))
    recurrent = rng.normal(0, 1, size=(reservoir_dim, reservoir_dim))
    radius = max(np.max(np.abs(np.linalg.eigvals(recurrent))), 1e-6)
    recurrent = recurrent * (0.85 / radius)

    def states(X):
        state = np.zeros(reservoir_dim)
        rows = []
        for row in X:
            state = np.tanh(row @ input_weights + state @ recurrent)
            rows.append(state.copy())
        return np.asarray(rows)

    train_states = states(X_train)
    design = train_states[:-1]
    target = X_train[1:]
    weights = np.linalg.solve(
        design.T @ design + ridge * np.eye(reservoir_dim),
        design.T @ target,
    )
    test_states = states(X_test)
    predictions = test_states[:-1] @ weights
    loss = np.mean((predictions - X_test[1:]) ** 2, axis=1)
    return {
        "model": "reservoir_esn",
        "mean_prediction_loss": float(loss.mean()),
        "mean_reconstruction_loss": 0.0,
        "parameter_count": int(input_weights.size + recurrent.size + weights.size),
    }
