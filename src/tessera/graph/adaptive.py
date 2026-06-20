from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tessera.graph.spectral import spectral_radius
from tessera.utils.hashing import sha256_json


@dataclass(frozen=True)
class TopologyProposal:
    old_hash: str
    candidate_hash: str
    changed_edges: int
    spectral_radius: float
    stability_margin: float
    shadow_only: bool = True

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def propose_sparse_rewire(
    operator: np.ndarray,
    *,
    alpha: float,
    max_changed_edges: int = 2,
    seed: int = 42,
) -> tuple[np.ndarray, TopologyProposal]:
    rng = np.random.default_rng(seed)
    candidate = operator.copy()
    n = candidate.shape[0]
    changed = 0
    while changed < max_changed_edges:
        source, target = rng.integers(0, n, size=2)
        if source == target:
            continue
        candidate[source, target] = 0.0 if candidate[source, target] else 1.0
        changed += 1
    rows = candidate.sum(axis=1, keepdims=True)
    rows[rows == 0] = 1.0
    candidate = candidate / rows
    rho = spectral_radius(candidate)
    proposal = TopologyProposal(
        old_hash=sha256_json(operator.tolist()),
        candidate_hash=sha256_json(candidate.tolist()),
        changed_edges=changed,
        spectral_radius=rho,
        stability_margin=alpha * rho,
    )
    return candidate.astype("float32"), proposal
