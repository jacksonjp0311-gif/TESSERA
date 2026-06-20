from __future__ import annotations

import numpy as np
import torch
from torch import nn


def evaluate_dense_autoencoder(
    X_train: np.ndarray,
    X_test: np.ndarray,
    code_dim: int,
    *,
    epochs: int = 20,
    seed: int = 42,
) -> dict:
    torch.manual_seed(seed)
    input_dim = X_train.shape[1]
    hidden = max(16, input_dim * 2)
    model = nn.Sequential(
        nn.Linear(input_dim, hidden),
        nn.Tanh(),
        nn.Linear(hidden, code_dim),
        nn.Tanh(),
        nn.Linear(code_dim, hidden),
        nn.Tanh(),
        nn.Linear(hidden, input_dim),
    )
    train = torch.tensor(X_train, dtype=torch.float32)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    for _ in range(epochs):
        reconstruction = model(train)
        loss = torch.mean((reconstruction - train) ** 2)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        test = torch.tensor(X_test, dtype=torch.float32)
        reconstruction = model(test)
        reconstruction_loss = torch.mean((reconstruction - test) ** 2, dim=1).numpy()
        prediction_loss = torch.mean((reconstruction[:-1] - test[1:]) ** 2, dim=1).numpy()
    return {
        "model": "dense_autoencoder",
        "mean_prediction_loss": float(prediction_loss.mean()),
        "mean_reconstruction_loss": float(reconstruction_loss.mean()),
        "parameter_count": int(sum(parameter.numel() for parameter in model.parameters())),
    }
