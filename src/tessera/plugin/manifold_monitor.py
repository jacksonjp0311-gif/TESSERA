from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np

from .host_adapters import effective_session_feature_indices


@dataclass(frozen=True)
class ManifoldContract:
    selected_indices: tuple[int, ...]
    center: tuple[float, ...]
    scale: tuple[float, ...]
    principal_axis: tuple[float, ...]
    principal_scale: float
    explained_variance: float
    intrinsic_rank: int
    relative_tolerance: float = 1e-6
    trim_quantile: float = 0.9
    maximum_angle_degrees: float = 10.0
    maximum_center_shift: float = 2.0
    minimum_scale_ratio: float = 0.2
    maximum_scale_ratio: float = 3.0
    minimum_explained_variance: float = 0.95
    schema: str = "TESSERA-MANIFOLD-CONTRACT-v0.1"

    @property
    def fingerprint(self) -> str:
        encoded = json.dumps(
            asdict(self),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ManifoldAudit:
    accepted: bool
    status: str
    observed_indices: tuple[int, ...]
    missing_indices: tuple[int, ...]
    unexpected_indices: tuple[int, ...]
    principal_angle_degrees: float | None
    center_shift: float | None
    scale_ratio: float | None
    explained_variance: float
    intrinsic_rank: int
    contract_fingerprint: str


@dataclass(frozen=True)
class ManifoldRoute:
    route: str
    memory_candidate: bool
    audit_status: str
    reason: str


def govern_manifold_audit(
    audit: ManifoldAudit,
    neural_route: str,
    *,
    neural_memory_candidate: bool,
) -> ManifoldRoute:
    if not audit.accepted:
        return ManifoldRoute(
            route="abstain",
            memory_candidate=False,
            audit_status=audit.status,
            reason="manifold_drift_forces_abstention",
        )
    return ManifoldRoute(
        route=neural_route,
        memory_candidate=bool(
            neural_route == "trusted" and neural_memory_candidate
        ),
        audit_status=audit.status,
        reason="manifold_stable",
    )


def _robust_location_scale(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    center = np.median(values, axis=0)
    scale = 1.4826 * np.median(np.abs(values - center), axis=0)
    fallback = np.std(values, axis=0)
    scale = np.where(scale > 1e-12, scale, fallback)
    if np.any(scale <= 1e-12):
        raise ValueError("manifold_contract_requires_varying_coordinates")
    return center, scale


def _trimmed_axis(
    normalized: np.ndarray,
    trim_quantile: float,
) -> tuple[np.ndarray, float, int]:
    if len(normalized) < 4:
        raise ValueError("manifold_audit_requires_four_samples")
    local_center = np.median(normalized, axis=0)
    radius = np.linalg.norm(normalized - local_center, axis=1)
    cutoff = float(np.quantile(radius, trim_quantile))
    trimmed = normalized[radius <= cutoff]
    centered = trimmed - np.mean(trimmed, axis=0)
    _, singular, vectors = np.linalg.svd(centered, full_matrices=False)
    variance = singular ** 2
    total = float(np.sum(variance))
    if total <= 0.0:
        raise ValueError("manifold_audit_requires_nonzero_variance")
    axis = vectors[0]
    first_nonzero = int(np.flatnonzero(np.abs(axis) > 1e-12)[0])
    if axis[first_nonzero] < 0.0:
        axis = -axis
    explained = float(variance[0] / total)
    cumulative = np.cumsum(variance / total)
    intrinsic_rank = int(np.searchsorted(cumulative, 0.98) + 1)
    return axis, explained, intrinsic_rank


def fit_manifold_contract(
    summaries: np.ndarray,
    selected_indices: tuple[int, ...],
    *,
    relative_tolerance: float = 1e-6,
    trim_quantile: float = 0.9,
) -> ManifoldContract:
    values = np.asarray(summaries, dtype="float64")
    observed = effective_session_feature_indices(
        values,
        relative_tolerance=relative_tolerance,
    )
    if observed != tuple(selected_indices):
        raise ValueError("calibration_support_does_not_match_contract")
    projected = values[:, np.asarray(selected_indices, dtype=int)]
    center, scale = _robust_location_scale(projected)
    normalized = (projected - center) / scale
    axis, explained, intrinsic_rank = _trimmed_axis(
        normalized,
        trim_quantile,
    )
    principal_scale = float(np.std(normalized @ axis))
    return ManifoldContract(
        selected_indices=tuple(selected_indices),
        center=tuple(float(item) for item in center),
        scale=tuple(float(item) for item in scale),
        principal_axis=tuple(float(item) for item in axis),
        principal_scale=principal_scale,
        explained_variance=explained,
        intrinsic_rank=intrinsic_rank,
        relative_tolerance=relative_tolerance,
        trim_quantile=trim_quantile,
    )


def audit_manifold_window(
    contract: ManifoldContract,
    summaries: np.ndarray,
) -> ManifoldAudit:
    values = np.asarray(summaries, dtype="float64")
    observed = effective_session_feature_indices(
        values,
        relative_tolerance=contract.relative_tolerance,
    )
    expected = set(contract.selected_indices)
    actual = set(observed)
    missing = tuple(sorted(expected - actual))
    unexpected = tuple(sorted(actual - expected))
    if missing or unexpected:
        return ManifoldAudit(
            accepted=False,
            status=(
                "support_collapse" if missing and not unexpected
                else "support_expansion" if unexpected and not missing
                else "support_replacement"
            ),
            observed_indices=observed,
            missing_indices=missing,
            unexpected_indices=unexpected,
            principal_angle_degrees=None,
            center_shift=None,
            scale_ratio=None,
            explained_variance=0.0,
            intrinsic_rank=len(observed),
            contract_fingerprint=contract.fingerprint,
        )

    selected = np.asarray(contract.selected_indices, dtype=int)
    center = np.asarray(contract.center, dtype="float64")
    scale = np.asarray(contract.scale, dtype="float64")
    normalized = (values[:, selected] - center) / scale
    axis, explained, intrinsic_rank = _trimmed_axis(
        normalized,
        contract.trim_quantile,
    )
    reference_axis = np.asarray(contract.principal_axis, dtype="float64")
    cosine = float(np.clip(abs(np.dot(axis, reference_axis)), 0.0, 1.0))
    angle = float(np.degrees(np.arccos(cosine)))
    center_shift = float(np.linalg.norm(np.median(normalized, axis=0)))
    reference_projection = (
        (values[:, selected] - np.median(values[:, selected], axis=0))
        / scale
    ) @ reference_axis
    observed_scale = float(np.std(reference_projection))
    scale_ratio = observed_scale / max(contract.principal_scale, 1e-12)
    checks = {
        "angle": angle <= contract.maximum_angle_degrees,
        "center": center_shift <= contract.maximum_center_shift,
        "scale": (
            contract.minimum_scale_ratio
            <= scale_ratio
            <= contract.maximum_scale_ratio
        ),
        "shape": explained >= contract.minimum_explained_variance,
        "rank": intrinsic_rank == contract.intrinsic_rank,
    }
    if all(checks.values()):
        status = "stable"
    elif not checks["angle"]:
        status = "manifold_rotation"
    elif not checks["center"]:
        status = "location_drift"
    elif not checks["scale"]:
        status = "scale_drift"
    elif not checks["rank"] or not checks["shape"]:
        status = "intrinsic_rank_drift"
    else:
        status = "manifold_drift"
    return ManifoldAudit(
        accepted=all(checks.values()),
        status=status,
        observed_indices=observed,
        missing_indices=(),
        unexpected_indices=(),
        principal_angle_degrees=angle,
        center_shift=center_shift,
        scale_ratio=scale_ratio,
        explained_variance=explained,
        intrinsic_rank=intrinsic_rank,
        contract_fingerprint=contract.fingerprint,
    )
