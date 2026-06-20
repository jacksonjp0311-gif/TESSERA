from __future__ import annotations
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge


def evaluate_pca_codec(X_train: np.ndarray, X_test: np.ndarray, code_dim: int) -> dict:
    k = min(code_dim, X_train.shape[1])
    pca = PCA(n_components=k, random_state=0).fit(X_train)
    Z_train = pca.transform(X_train[:-1])
    reg = Ridge(alpha=1.0).fit(Z_train, X_train[1:])
    Z = pca.transform(X_test[:-1])
    rec = np.asarray(pca.inverse_transform(Z)).reshape(
        len(Z), X_test.shape[1]
    )
    pred = np.asarray(reg.predict(Z)).reshape(
        len(Z), X_test.shape[1]
    )
    rec_loss = np.mean((rec-X_test[:-1])**2, axis=1)
    pred_loss = np.mean((pred-X_test[1:])**2, axis=1)
    return {'model':'pca_codec','mean_prediction_loss':float(pred_loss.mean()),'mean_reconstruction_loss':float(rec_loss.mean())}
