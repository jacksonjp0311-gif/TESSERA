from __future__ import annotations
import numpy as np


def evaluate_persistence(X: np.ndarray) -> dict:
    pred_loss = np.mean((X[1:] - X[:-1])**2, axis=1)
    return {'model':'persistence','mean_prediction_loss':float(pred_loss.mean()),'mean_reconstruction_loss':0.0}
