from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np

from .manifold_monitor import ManifoldContract


@dataclass(frozen=True)
class SequentialGeometryContract:
    manifold_fingerprint: str
    residual_center: float
    residual_scale: float
    reference_allowance: float = 0.75
    evidence_clip: float = 3.0
    alarm_threshold: float = 5.0
    schema: str = "TESSERA-SEQUENTIAL-GEOMETRY-CONTRACT-v0.1"

    @property
    def fingerprint(self) -> str:
        encoded = json.dumps(
            asdict(self),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class SequentialGeometryState:
    evidence: float = 0.0
    observations: int = 0
    alarmed: bool = False
    first_alarm_index: int | None = None


@dataclass(frozen=True)
class SequentialGeometryUpdate:
    state: SequentialGeometryState
    orthogonal_residual: float
    nonconformity: float
    bounded_evidence: float
    route: str
    memory_candidate: bool
    reason: str


def _orthogonal_axis(contract: ManifoldContract) -> np.ndarray:
    axis = np.asarray(contract.principal_axis, dtype="float64")
    if len(axis) != 2:
        raise ValueError("sequential_geometry_requires_rank_one_plane")
    return np.asarray([-axis[1], axis[0]], dtype="float64")


def fit_sequential_geometry_contract(
    manifold: ManifoldContract,
    calibration_summaries: np.ndarray,
    *,
    reference_allowance: float = 0.75,
    evidence_clip: float = 3.0,
    alarm_threshold: float = 5.0,
) -> SequentialGeometryContract:
    values = np.asarray(calibration_summaries, dtype="float64")
    selected = np.asarray(manifold.selected_indices, dtype=int)
    normalized = (
        values[:, selected] - np.asarray(manifold.center)
    ) / np.asarray(manifold.scale)
    residual = np.abs(normalized @ _orthogonal_axis(manifold))
    center = float(np.median(residual))
    scale = float(1.4826 * np.median(np.abs(residual - center)))
    if scale <= 1e-12:
        scale = float(np.std(residual))
    if scale <= 1e-12:
        raise ValueError("sequential_geometry_requires_residual_variation")
    return SequentialGeometryContract(
        manifold_fingerprint=manifold.fingerprint,
        residual_center=center,
        residual_scale=scale,
        reference_allowance=reference_allowance,
        evidence_clip=evidence_clip,
        alarm_threshold=alarm_threshold,
    )


def update_sequential_geometry(
    contract: SequentialGeometryContract,
    manifold: ManifoldContract,
    summary: np.ndarray,
    state: SequentialGeometryState | None = None,
    *,
    neural_route: str = "trusted",
    neural_memory_candidate: bool = True,
) -> SequentialGeometryUpdate:
    if contract.manifold_fingerprint != manifold.fingerprint:
        raise ValueError("sequential_manifold_contract_mismatch")
    previous = state or SequentialGeometryState()
    values = np.asarray(summary, dtype="float64").reshape(-1)
    selected = np.asarray(manifold.selected_indices, dtype=int)
    normalized = (
        values[selected] - np.asarray(manifold.center)
    ) / np.asarray(manifold.scale)
    residual = float(abs(normalized @ _orthogonal_axis(manifold)))
    nonconformity = max(
        0.0,
        (residual - contract.residual_center) / contract.residual_scale,
    )
    bounded = min(contract.evidence_clip, nonconformity)
    evidence = max(
        0.0,
        previous.evidence + bounded - contract.reference_allowance,
    )
    observations = previous.observations + 1
    crossed = evidence > contract.alarm_threshold
    alarmed = previous.alarmed or crossed
    first_alarm = previous.first_alarm_index
    if first_alarm is None and crossed:
        first_alarm = observations - 1
    next_state = SequentialGeometryState(
        evidence=evidence,
        observations=observations,
        alarmed=alarmed,
        first_alarm_index=first_alarm,
    )
    if alarmed:
        route = "abstain"
        memory_candidate = False
        reason = "persistent_geometric_evidence_latched"
    else:
        route = neural_route
        memory_candidate = bool(
            neural_route == "trusted" and neural_memory_candidate
        )
        reason = "sequential_geometry_stable"
    return SequentialGeometryUpdate(
        state=next_state,
        orthogonal_residual=residual,
        nonconformity=nonconformity,
        bounded_evidence=bounded,
        route=route,
        memory_candidate=memory_candidate,
        reason=reason,
    )
