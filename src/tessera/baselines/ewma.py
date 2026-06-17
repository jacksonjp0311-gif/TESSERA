from __future__ import annotations
import numpy as np


def evaluate_ewma(X: np.ndarray, alpha: float = 0.2) -> dict:
    state = X[0].copy()
    losses=[]
    for i in range(1, len(X)):
        pred = state
        losses.append(np.mean((X[i]-pred)**2))
        state = alpha*X[i] + (1-alpha)*state
    return {'model':'ewma','mean_prediction_loss':float(np.mean(losses)),'mean_reconstruction_loss':0.0}
