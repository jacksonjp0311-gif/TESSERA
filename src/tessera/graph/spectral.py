from __future__ import annotations
import numpy as np


def spectral_radius(P: np.ndarray) -> float:
    vals = np.linalg.eigvals(P)
    return float(np.max(np.abs(vals)))


def graph_declaration(P: np.ndarray, topology: str, alpha: float) -> dict:
    rho = spectral_radius(P)
    return {
        'topology': topology,
        'nodes': int(P.shape[0]),
        'normalization': 'row',
        'spectral_radius': rho,
        'damping_alpha': alpha,
        'stability_margin_alpha_rho': float(alpha * rho),
        'stability_condition_alpha_rho_lt_1': bool(alpha * rho < 1.0),
    }
