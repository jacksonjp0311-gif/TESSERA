from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import Ridge


@dataclass
class PredictionExpert:
    name: str
    kind: str
    alpha: float | None = None
    lag: int | None = None
    model: Ridge | None = None


def _prediction_loss(predictions: np.ndarray, targets: np.ndarray) -> float:
    return float(np.mean((predictions - targets) ** 2))


def _fit_autoregression(
    train: np.ndarray, *, lag: int, ridge: float = 1e-3
) -> PredictionExpert | None:
    if len(train) <= lag:
        return None
    design = np.asarray(
        [train[index - lag : index].reshape(-1) for index in range(lag, len(train))]
    )
    targets = train[lag:]
    model = Ridge(alpha=ridge).fit(design, targets)
    return PredictionExpert(
        name=f"ridge_ar_lag_{lag}",
        kind="ridge_ar",
        lag=lag,
        model=model,
    )


def predict_with_expert(
    expert: PredictionExpert,
    sequence: np.ndarray,
    *,
    history: np.ndarray | None = None,
) -> np.ndarray:
    """Predict each next row causally using observed history only."""
    sequence = np.asarray(sequence, dtype=float)
    if len(sequence) < 2:
        return np.empty((0, sequence.shape[1]), dtype=float)
    if expert.kind == "persistence":
        return sequence[:-1].copy()
    if expert.kind == "ewma":
        state = (
            np.asarray(history[-1], dtype=float).copy()
            if history is not None and len(history)
            else sequence[0].copy()
        )
        predictions = []
        alpha = float(expert.alpha)
        for current in sequence[:-1]:
            state = alpha * current + (1.0 - alpha) * state
            predictions.append(state.copy())
        return np.asarray(predictions)
    if expert.kind == "ridge_ar":
        lag = int(expert.lag)
        observed = []
        if history is not None:
            observed.extend(np.asarray(history, dtype=float).tolist())
        observed.append(sequence[0].tolist())
        predictions = []
        for next_row in sequence[1:]:
            window = np.asarray(observed[-lag:], dtype=float)
            if len(window) < lag:
                predictions.append(np.asarray(observed[-1], dtype=float))
            else:
                prediction = np.asarray(
                    expert.model.predict(window.reshape(1, -1))
                ).reshape(sequence.shape[1])
                predictions.append(prediction)
            observed.append(next_row.tolist())
        return np.asarray(predictions)
    raise ValueError(f"unknown prediction expert kind: {expert.kind}")


def select_prediction_expert(
    train: np.ndarray,
    validation: np.ndarray,
) -> tuple[PredictionExpert, dict]:
    """Select a causal expert using normal validation prediction loss only."""
    train = np.asarray(train, dtype=float)
    validation = np.asarray(validation, dtype=float)
    candidates = [PredictionExpert("persistence", "persistence")]
    candidates.extend(
        PredictionExpert(f"ewma_{alpha:g}", "ewma", alpha=alpha)
        for alpha in (0.05, 0.1, 0.2, 0.5, 0.8)
    )
    for lag in (2, 4, 8, 16, 32):
        expert = _fit_autoregression(train, lag=lag)
        if expert is not None:
            candidates.append(expert)
    scores = []
    for expert in candidates:
        predictions = predict_with_expert(
            expert, validation, history=train
        )
        loss = _prediction_loss(predictions, validation[1:])
        scores.append({"expert": expert.name, "validation_loss": loss})
    winner_name = min(scores, key=lambda row: row["validation_loss"])["expert"]
    winner = next(expert for expert in candidates if expert.name == winner_name)
    return winner, {
        "schema": "TESSERA-PREDICTION-EXPERT-SELECTION-v0.1",
        "selection_source": "normal_validation_only",
        "selected_expert": winner.name,
        "candidate_scores": scores,
    }


def prediction_losses(
    expert: PredictionExpert,
    sequence: np.ndarray,
    *,
    history: np.ndarray,
) -> np.ndarray:
    predictions = predict_with_expert(expert, sequence, history=history)
    return np.mean((predictions - np.asarray(sequence)[1:]) ** 2, axis=1)
