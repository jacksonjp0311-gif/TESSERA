from __future__ import annotations
import numpy as np
from sklearn.random_projection import GaussianRandomProjection
from sklearn.linear_model import Ridge


def evaluate_random_projection(X_train: np.ndarray, X_test: np.ndarray, code_dim: int, seed: int=42) -> dict:
    k = min(code_dim, X_train.shape[1])
    rp = GaussianRandomProjection(n_components=k, random_state=seed).fit(X_train)
    Z_train = rp.transform(X_train[:-1])
    dec = Ridge(alpha=1.0).fit(Z_train, X_train[:-1])
    pred_reg = Ridge(alpha=1.0).fit(Z_train, X_train[1:])
    Z = rp.transform(X_test[:-1])
    rec = np.asarray(dec.predict(Z)).reshape(len(Z), X_test.shape[1])
    pred = np.asarray(pred_reg.predict(Z)).reshape(
        len(Z), X_test.shape[1]
    )
    rec_loss = np.mean((rec-X_test[:-1])**2, axis=1)
    pred_loss = np.mean((pred-X_test[1:])**2, axis=1)
    return {'model':'random_projection','mean_prediction_loss':float(pred_loss.mean()),'mean_reconstruction_loss':float(rec_loss.mean())}
