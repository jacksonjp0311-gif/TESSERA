from __future__ import annotations
import numpy as np


def row_normalize(A: np.ndarray) -> np.ndarray:
    rows = A.sum(axis=1, keepdims=True)
    rows[rows == 0] = 1.0
    return A / rows


def ring(n: int) -> np.ndarray:
    A = np.zeros((n,n), dtype='float32')
    for i in range(n):
        A[i,(i-1)%n] = 1
        A[i,(i+1)%n] = 1
    return row_normalize(A)


def dense(n: int) -> np.ndarray:
    A = np.ones((n,n), dtype='float32') - np.eye(n, dtype='float32')
    return row_normalize(A)


def random_sparse(n: int, degree: int = 3, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    A = np.zeros((n,n), dtype='float32')
    for i in range(n):
        js = rng.choice([j for j in range(n) if j != i], size=min(degree, n-1), replace=False)
        A[i, js] = 1
    # symmetrize for stability
    A = np.maximum(A, A.T)
    return row_normalize(A)


def q_hypercube(dim: int = 4) -> np.ndarray:
    n = 2**dim
    A = np.zeros((n,n), dtype='float32')
    for i in range(n):
        for b in range(dim):
            j = i ^ (1 << b)
            A[i,j] = 1
    return row_normalize(A)


def make_operator(topology: str, n: int, seed: int = 42) -> np.ndarray:
    topology = topology.lower()
    if topology == 'ring': return ring(n)
    if topology == 'dense': return dense(n)
    if topology == 'random_sparse': return random_sparse(n, seed=seed)
    if topology == 'q4':
        if n != 16:
            raise ValueError('q4 topology requires field_dim=16')
        return q_hypercube(4)
    raise ValueError(f'unknown topology: {topology}')
