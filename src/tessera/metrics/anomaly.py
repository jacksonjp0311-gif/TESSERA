from __future__ import annotations

import numpy as np
import pandas as pd

COMPONENTS = (
    "prediction_loss",
    "reconstruction_loss",
    "delta_phi",
    "code_drift",
    "rate",
)
MAX_COMPONENT_SCORE = 12.0


def calibrate_anomaly_model(
    normal_rows: pd.DataFrame,
    *,
    warn_quantile: float = 0.95,
    block_quantile: float = 0.99,
    memory_quantile: float | None = None,
    components: tuple[str, ...] = COMPONENTS,
    fusion: str = "top_two_multiscale",
    adaptive: bool = True,
) -> dict:
    """Fit a robust, normal-only reference for independent awareness channels.

    Args:
        normal_rows: DataFrame with normal-only metric columns.
        warn_quantile: Quantile for warning threshold (default 0.95).
        block_quantile: Quantile for block threshold (default 0.99).
        memory_quantile: Quantile for memory threshold (defaults to warn_quantile).
        components: Which metric components to use.
        fusion: Fusion mode for combining component scores.
        adaptive: If True, use per-component adaptive thresholds.
    """
    channels = {}
    standardized = pd.DataFrame(index=normal_rows.index)
    for name in components:
        values = normal_rows[name].to_numpy(dtype=float)
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        scale = 1.4826 * mad
        if scale < 1e-8:
            scale = float(np.std(values))
        scale = max(scale, 1e-8)
        channels[name] = {"center": center, "scale": scale}
        standardized[name] = np.abs(values - center) / scale

    scored = _combine_scores(standardized, components=components, fusion=fusion)

    # Adaptive thresholds: use per-component multimax instead of single quantile
    if adaptive:
        component_columns = [c for c in scored.columns if c.startswith("score_")]
        all_component_scores = scored[component_columns].to_numpy()
        flat_scores = all_component_scores.flatten()
        warn_score = float(np.percentile(flat_scores, 95))
        block_score = float(np.percentile(flat_scores, 99))
        memory_score = float(np.percentile(flat_scores, 90))
    else:
        warn_score = float(scored["anomaly_score"].quantile(warn_quantile))
        block_score = float(scored["anomaly_score"].quantile(block_quantile))
        memory_score = float(scored["anomaly_score"].quantile(
            warn_quantile if memory_quantile is None else memory_quantile
        ))

    memory_quantile = warn_quantile if memory_quantile is None else memory_quantile
    return {
        "schema": "TESSERA-MULTISCALE-ANOMALY-CALIBRATION-v0.2",
        "channels": channels,
        "components": list(components),
        "fusion": fusion,
        "adaptive": adaptive,
        "warn_score": warn_score,
        "block_score": block_score,
        "memory_score": memory_score,
        "warn_quantile": warn_quantile,
        "block_quantile": block_quantile,
        "memory_quantile": memory_quantile,
        "max_component_score": MAX_COMPONENT_SCORE,
        "normal_rows": int(len(normal_rows)),
        "label_usage": "normal_only_calibration_no_anomaly_labels",
    }


def score_anomalies(rows: pd.DataFrame, calibration: dict) -> pd.DataFrame:
    """Score rows against a fitted calibration."""
    standardized = pd.DataFrame(index=rows.index)
    components = tuple(calibration.get("components", COMPONENTS))
    for name in components:
        reference = calibration["channels"][name]
        standardized[name] = np.minimum(
            np.abs(rows[name].to_numpy(dtype=float) - reference["center"])
            / reference["scale"],
            calibration.get("max_component_score", MAX_COMPONENT_SCORE),
        )
    combined = _combine_scores(
        standardized,
        components=components,
        fusion=calibration.get("fusion", "top_two_multiscale"),
    )
    return pd.concat([rows.reset_index(drop=True), combined], axis=1)


def _combine_scores(
    standardized: pd.DataFrame,
    *,
    components: tuple[str, ...] = COMPONENTS,
    fusion: str = "top_two_multiscale",
) -> pd.DataFrame:
    """Combine per-component standardized scores into anomaly scores."""
    out = pd.DataFrame(index=standardized.index)
    component_columns = []
    for name in components:
        column = f"score_{name}"
        out[column] = np.minimum(
            standardized[name].to_numpy(dtype=float), MAX_COMPONENT_SCORE
        )
        component_columns.append(column)

    values = out[component_columns].to_numpy(dtype=float)

    if fusion == "top_two_multiscale":
        top_two = np.partition(values, -2, axis=1)[:, -2:]
        out["instant_anomaly_score"] = top_two.mean(axis=1)
    elif fusion == "mean_multiscale":
        out["instant_anomaly_score"] = values.mean(axis=1)
    elif fusion == "mean_instant":
        out["instant_anomaly_score"] = values.mean(axis=1)
        out["short_anomaly_score"] = out["instant_anomaly_score"]
        out["medium_anomaly_score"] = out["instant_anomaly_score"]
        out["anomaly_score"] = out["instant_anomaly_score"]
        return out
    else:
        raise ValueError(f"unsupported anomaly fusion: {fusion}")

    # Apply multi-scale smoothing for top_two_multiscale and mean_multiscale
    out["short_anomaly_score"] = (
        out["instant_anomaly_score"].rolling(3, min_periods=1).mean()
    )
    out["medium_anomaly_score"] = (
        out["instant_anomaly_score"].rolling(7, min_periods=1).mean()
    )
    out["anomaly_score"] = out[
        ["instant_anomaly_score", "short_anomaly_score", "medium_anomaly_score"]
    ].max(axis=1)
    return out


def anomaly_ablation(rows: pd.DataFrame) -> dict:
    """Compute per-component AUC scores for ablation analysis."""
    from sklearn.metrics import roc_auc_score

    labels = rows["label"].to_numpy(dtype=int)
    scores = {}
    for name in COMPONENTS:
        column = f"score_{name}"
        if column in rows:
            scores[name] = float(roc_auc_score(labels, rows[column]))
    scores["combined_multiscale"] = float(
        roc_auc_score(labels, rows["anomaly_score"])
    )
    return scores
