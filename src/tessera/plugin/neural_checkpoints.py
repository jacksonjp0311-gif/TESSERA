from __future__ import annotations

import base64
import io
from typing import Any

import numpy as np
import torch

from tessera.graph.topologies import make_operator
from tessera.model.network import TESSERANet
from tessera.model.prediction_experts import (
    PredictionExpert,
    prediction_losses,
    select_prediction_expert,
)
from tessera.model.train import evaluate_sequence, fit_tessera_model


def _serialize_expert(expert: PredictionExpert) -> dict:
    value = {
        "name": expert.name,
        "kind": expert.kind,
        "alpha": expert.alpha,
        "lag": expert.lag,
    }
    if expert.model is not None:
        value["coef"] = np.asarray(expert.model.coef_).tolist()
        value["intercept"] = np.asarray(expert.model.intercept_).tolist()
    return value


def deserialize_expert(value: dict) -> PredictionExpert:
    expert = PredictionExpert(
        name=value["name"],
        kind=value["kind"],
        alpha=value.get("alpha"),
        lag=value.get("lag"),
    )
    if expert.kind == "ridge_ar":
        from sklearn.linear_model import Ridge

        model = Ridge(alpha=1e-3)
        model.coef_ = np.asarray(value["coef"], dtype=float)
        model.intercept_ = np.asarray(value["intercept"], dtype=float)
        model.n_features_in_ = model.coef_.shape[1]
        expert.model = model
    return expert


def train_neural_checkpoint(matrix: np.ndarray) -> tuple[dict, dict]:
    matrix = np.asarray(matrix, dtype="float32")
    if matrix.ndim != 2 or len(matrix) < 36:
        raise ValueError("neural_checkpoint_requires_36_rows")
    train_end = int(len(matrix) * 0.60)
    validation_end = int(len(matrix) * 0.80)
    train_raw = matrix[:train_end]
    validation_raw = matrix[train_end:validation_end]
    replay_raw = matrix[validation_end:]
    mean = train_raw.mean(axis=0)
    scale = train_raw.std(axis=0)
    scale[scale < 1e-3] = 1.0
    train = ((train_raw - mean) / scale).astype("float32")
    validation = ((validation_raw - mean) / scale).astype("float32")
    replay = ((replay_raw - mean) / scale).astype("float32")

    field_dim = 8
    code_dim = 4
    operator = make_operator("ring", field_dim, seed=42)
    model = fit_tessera_model(
        train,
        operator,
        code_dim=code_dim,
        alpha=0.5,
        epochs=2,
        seed=42,
        X_validation=validation,
    )
    expert, selection = select_prediction_expert(train, validation)
    candidate_losses = prediction_losses(
        expert,
        replay,
        history=np.concatenate([train, validation], axis=0),
    )
    baseline_losses = np.mean((replay[1:] - replay[:-1]) ** 2, axis=1)
    neural_rows = evaluate_sequence(model, replay)["rows"]
    buffer = io.BytesIO()
    torch.save(model.state_dict(), buffer)
    payload = {
        "kind": "tessera-neural-checkpoint",
        "architecture": {
            "input_dim": int(matrix.shape[1]),
            "field_dim": field_dim,
            "code_dim": code_dim,
            "alpha": 0.5,
            "hidden_dim": int(model.hidden),
            "depth": int(model.depth),
            "topology": "ring",
            "seed": 42,
        },
        "normalization": {
            "mean": mean.tolist(),
            "scale": scale.tolist(),
        },
        "model_state_base64": base64.b64encode(buffer.getvalue()).decode("ascii"),
        "prediction_expert": _serialize_expert(expert),
        "selection": selection,
    }
    metrics = {
        "baseline_loss": float(np.mean(baseline_losses)),
        "candidate_loss": float(np.mean(candidate_losses)),
        "replay_pass_rate": float(
            np.mean(candidate_losses <= baseline_losses * 1.02 + 1e-12)
        ),
        "neural_awareness_loss": float(np.mean([
            row["prediction_loss"] for row in neural_rows
        ])),
        "train_rows": len(train),
        "validation_rows": len(validation),
        "replay_rows": len(replay),
        "selected_prediction_expert": expert.name,
    }
    return payload, metrics


def load_neural_checkpoint(payload: dict) -> dict[str, Any]:
    if payload.get("kind") != "tessera-neural-checkpoint":
        raise ValueError("unsupported_neural_checkpoint_kind")
    architecture = payload["architecture"]
    operator = make_operator(
        architecture["topology"],
        int(architecture["field_dim"]),
        seed=int(architecture["seed"]),
    )
    model = TESSERANet(
        input_dim=int(architecture["input_dim"]),
        field_dim=int(architecture["field_dim"]),
        code_dim=int(architecture["code_dim"]),
        P=operator,
        alpha=float(architecture["alpha"]),
        hidden_dim=int(architecture["hidden_dim"]),
        depth=int(architecture["depth"]),
    )
    state = torch.load(
        io.BytesIO(base64.b64decode(payload["model_state_base64"])),
        map_location="cpu",
        weights_only=True,
    )
    model.load_state_dict(state)
    model.eval()
    return {
        "model": model,
        "expert": deserialize_expert(payload["prediction_expert"]),
        "mean": np.asarray(payload["normalization"]["mean"], dtype=float),
        "scale": np.asarray(payload["normalization"]["scale"], dtype=float),
    }


def neural_sequence_predictions(
    payload: dict,
    sequence: np.ndarray,
) -> np.ndarray:
    loaded = load_neural_checkpoint(payload)
    model = loaded["model"]
    values = torch.tensor(np.asarray(sequence), dtype=torch.float32)
    field = torch.zeros(1, model.field_dim)
    level = values[0:1]
    predictions = []
    with torch.no_grad():
        for index in range(len(values) - 1):
            next_field, _, _, prediction = model.step(
                values[index : index + 1],
                field,
                level,
            )
            predictions.append(prediction.numpy().reshape(-1))
            level = model.update_level(
                values[index + 1 : index + 2],
                level,
            )
            field = next_field
    return np.asarray(predictions)


def neural_awareness_features(
    payload: dict,
    sequence: np.ndarray,
    stable_predictions: np.ndarray,
) -> dict[str, np.ndarray]:
    loaded = load_neural_checkpoint(payload)
    model = loaded["model"]
    values = torch.tensor(np.asarray(sequence), dtype=torch.float32)
    field = torch.zeros(1, model.field_dim)
    level = values[0:1]
    previous_code = torch.zeros(1, model.code_dim)
    scores = {
        "reconstruction_surprise": [],
        "latent_drift": [],
        "field_movement": [],
        "neural_expert_disagreement": [],
    }
    with torch.no_grad():
        for index in range(len(values) - 1):
            next_field, code, reconstruction, prediction = model.step(
                values[index : index + 1],
                field,
                level,
            )
            scores["reconstruction_surprise"].append(
                torch.mean(
                    (reconstruction - values[index : index + 1]) ** 2
                ).item()
            )
            scores["latent_drift"].append(
                torch.mean(torch.abs(code - previous_code)).item()
            )
            scores["field_movement"].append(
                torch.mean(torch.abs(next_field - field)).item()
            )
            scores["neural_expert_disagreement"].append(
                float(np.mean(
                    (
                        prediction.numpy().reshape(-1)
                        - stable_predictions[index]
                    ) ** 2
                ))
            )
            level = model.update_level(
                values[index + 1 : index + 2],
                level,
            )
            field = next_field
            previous_code = code
    return {
        name: np.asarray(values, dtype=float)
        for name, values in scores.items()
    }
