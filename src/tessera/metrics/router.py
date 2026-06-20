from __future__ import annotations

import numpy as np
import pandas as pd


def robust_point_scores(reference: np.ndarray, sequence: np.ndarray) -> np.ndarray:
    """Point-scale evidence from level, velocity, and acceleration surprise."""
    reference = np.asarray(reference, dtype=float).reshape(-1)
    sequence = np.asarray(sequence, dtype=float).reshape(-1)

    def robust_z(train: np.ndarray, values: np.ndarray) -> np.ndarray:
        center = np.median(train)
        scale = 1.4826 * np.median(np.abs(train - center))
        if scale < 1e-8:
            scale = max(float(np.std(train)), 1e-8)
        return np.abs(values - center) / scale

    joined = np.concatenate([reference[-2:], sequence])
    ref_diff = np.diff(reference)
    ref_accel = np.diff(reference, n=2)
    level = robust_z(reference, sequence)
    velocity = robust_z(ref_diff, np.diff(joined)[-len(sequence) :])
    acceleration = robust_z(
        ref_accel, np.diff(joined, n=2)[-len(sequence) :]
    )
    return np.maximum.reduce([level, velocity, acceleration])


def calibrate_sensor_router(
    point_validation: np.ndarray,
    shape_validation: np.ndarray,
) -> dict:
    return {
        "schema": "TESSERA-SENSOR-ROUTER-v0.1",
        "point_scale": float(np.quantile(point_validation, 0.90)),
        "shape_scale": float(np.quantile(shape_validation, 0.90)),
        "warn_score": 1.0,
        "block_score": 1.5,
        "memory_score": 0.70,
        "calibration_source": "normal_validation_only",
    }


def calibrate_confidence_router(
    point_validation: np.ndarray,
    shape_validation: np.ndarray,
) -> dict:
    """Calibrate specialist activation, disagreement, and joint normality."""
    point_validation = np.asarray(point_validation, dtype=float)
    shape_validation = np.asarray(shape_validation, dtype=float)
    calibration = calibrate_sensor_router(
        point_validation, shape_validation
    )
    point = point_validation / max(calibration["point_scale"], 1e-8)
    shape = shape_validation / max(calibration["shape_scale"], 1e-8)
    disagreement = np.abs(point - shape)

    centers = np.array([np.median(point), np.median(shape)])
    values = np.column_stack([point, shape])
    scales = 1.4826 * np.median(np.abs(values - centers), axis=0)
    fallback = np.std(values, axis=0)
    scales = np.maximum(scales, np.maximum(fallback, 1e-8))
    normality = np.sqrt(
        np.sum(((values - centers) / scales) ** 2, axis=1)
    )
    calibration.update(
        {
            "schema": "TESSERA-CONFIDENCE-SENSOR-ROUTER-v0.2",
            "activation_score": 1.0,
            "disagreement_margin": float(
                max(0.25, np.quantile(disagreement, 0.90))
            ),
            "memory_normality_center": centers.tolist(),
            "memory_normality_scale": scales.tolist(),
            "memory_normality_threshold": float(
                np.quantile(normality, 0.70)
            ),
            "memory_calibration_source": (
                "joint_point_subsequence_normal_validation_only"
            ),
        }
    )
    return calibration


def calibrate_selective_router(
    point_validation: np.ndarray,
    shape_validation: np.ndarray,
    *,
    target_coverage: float = 0.20,
) -> dict:
    """Calibrate a bounded specialist-routing coverage on normal validation."""
    if not 0.0 < target_coverage < 1.0:
        raise ValueError("target_coverage must be between zero and one")
    calibration = calibrate_confidence_router(
        point_validation, shape_validation
    )
    point = np.asarray(point_validation, dtype=float) / max(
        calibration["point_scale"], 1e-8
    )
    shape = np.asarray(shape_validation, dtype=float) / max(
        calibration["shape_scale"], 1e-8
    )
    maximum = np.maximum(point, shape)
    calibration.update(
        {
            "schema": "TESSERA-SELECTIVE-SENSOR-ROUTER-v0.3",
            "target_specialist_coverage": float(target_coverage),
            "activation_score": float(
                np.quantile(maximum, 1.0 - target_coverage)
            ),
            "abstain_fusion": (
                "geometric_consensus_when_inactive_mean_when_ambiguous"
            ),
        }
    )
    return calibration


def score_memory_normality(
    point_scores: np.ndarray,
    shape_scores: np.ndarray,
    calibration: dict,
) -> np.ndarray:
    """Measure distance from the joint normal sensor manifold."""
    point = np.asarray(point_scores, dtype=float) / max(
        calibration["point_scale"], 1e-8
    )
    shape = np.asarray(shape_scores, dtype=float) / max(
        calibration["shape_scale"], 1e-8
    )
    values = np.column_stack([point, shape])
    centers = np.asarray(
        calibration["memory_normality_center"], dtype=float
    )
    scales = np.asarray(
        calibration["memory_normality_scale"], dtype=float
    )
    return np.sqrt(
        np.sum(((values - centers) / np.maximum(scales, 1e-8)) ** 2, axis=1)
    )


def route_sensor_scores(
    point_scores: np.ndarray,
    shape_scores: np.ndarray,
    calibration: dict,
) -> pd.DataFrame:
    point = np.asarray(point_scores, dtype=float) / max(
        calibration["point_scale"], 1e-8
    )
    shape = np.asarray(shape_scores, dtype=float) / max(
        calibration["shape_scale"], 1e-8
    )
    route = np.where(point >= shape, "point", "subsequence")
    return pd.DataFrame(
        {
            "point_router_score": point,
            "subsequence_router_score": shape,
            "sensor_route": route,
            "anomaly_score": np.maximum(point, shape),
        }
    )


def route_sensor_scores_with_abstention(
    point_scores: np.ndarray,
    shape_scores: np.ndarray,
    calibration: dict,
) -> pd.DataFrame:
    """Route only when a specialist has sufficient, distinct evidence."""
    point = np.asarray(point_scores, dtype=float) / max(
        calibration["point_scale"], 1e-8
    )
    shape = np.asarray(shape_scores, dtype=float) / max(
        calibration["shape_scale"], 1e-8
    )
    activation = float(calibration["activation_score"])
    margin_required = float(calibration["disagreement_margin"])
    point_active = point >= activation
    shape_active = shape >= activation
    margin = np.abs(point - shape)
    winner = np.where(point >= shape, "point", "subsequence")
    exclusive = np.logical_xor(point_active, shape_active)
    decisive = np.maximum(point, shape) >= activation
    decisive &= np.logical_or(exclusive, margin >= margin_required)
    route = np.where(decisive, winner, "abstain")
    reason = np.where(
        decisive,
        "decisive_specialist",
        np.where(
            np.maximum(point, shape) < activation,
            "insufficient_evidence",
            "sensor_disagreement",
        ),
    )
    maximum = np.maximum(point, shape)
    confidence = margin / np.maximum(maximum, 1e-8)
    return pd.DataFrame(
        {
            "point_router_score": point,
            "subsequence_router_score": shape,
            "sensor_route": route,
            "route_reason": reason,
            "route_confidence": confidence,
            "anomaly_score": maximum,
            "memory_normality_score": score_memory_normality(
                point_scores, shape_scores, calibration
            ),
        }
    )


def route_sensor_scores_selectively(
    point_scores: np.ndarray,
    shape_scores: np.ndarray,
    calibration: dict,
) -> pd.DataFrame:
    """Select a specialist within budget; otherwise fuse by consensus."""
    routed = route_sensor_scores_with_abstention(
        point_scores, shape_scores, calibration
    )
    point = routed["point_router_score"].to_numpy(dtype=float)
    shape = routed["subsequence_router_score"].to_numpy(dtype=float)
    routes = routed["sensor_route"].to_numpy(dtype=str)
    reasons = routed["route_reason"].to_numpy(dtype=str)
    geometric = np.sqrt(np.maximum(point, 0.0) * np.maximum(shape, 0.0))
    ambiguous = 0.5 * (point + shape)
    abstain_score = np.where(
        reasons == "sensor_disagreement", ambiguous, geometric
    )
    selected = np.where(
        routes == "point",
        point,
        np.where(routes == "subsequence", shape, abstain_score),
    )
    routed["max_fusion_score"] = np.maximum(point, shape)
    routed["consensus_fusion_score"] = abstain_score
    routed["anomaly_score"] = selected
    routed["fusion_mode"] = np.where(
        routes == "abstain", "consensus", "specialist"
    )
    return routed
