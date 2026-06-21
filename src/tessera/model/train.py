from __future__ import annotations
import numpy as np
import torch
from torch import nn
from .network import TESSERANet


def fit_tessera_model(
    X_train: np.ndarray,
    P: np.ndarray,
    code_dim: int,
    alpha: float,
    epochs: int = 6,
    lr: float = 3e-3,
    seed: int = 42,
    X_validation: np.ndarray | None = None,
    sequence_chunk_size: int = 128,
    prediction_target_dims: int | None = None,
    hidden_dim: int | None = None,
    depth: int = 2,
) -> TESSERANet:
    torch.manual_seed(seed)
    model = TESSERANet(
        input_dim=X_train.shape[1],
        field_dim=P.shape[0],
        code_dim=code_dim,
        P=P,
        alpha=alpha,
        hidden_dim=hidden_dim,
        depth=depth,
    )
    model.prediction_target_dims = prediction_target_dims
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-5)
    loss_fn = nn.SmoothL1Loss(beta=0.5)
    X = torch.tensor(X_train, dtype=torch.float32)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        opt, T_max=max(1, epochs), eta_min=lr * 0.1
    )
    for epoch in range(epochs):
        model.train()
        field = torch.zeros(1, P.shape[0])
        level = X[0:1]
        prev_z = torch.zeros(1, code_dim)
        losses = []
        for i in range(len(X) - 1):
            x_t = X[i:i+1]
            x_next = X[i+1:i+2]
            next_field, z, x_rec, x_pred = model.step(x_t, field, level)
            rec_loss = loss_fn(x_rec, x_t)
            if prediction_target_dims is None:
                pred_loss = loss_fn(x_pred, x_next)
            else:
                pred_loss = loss_fn(
                    x_pred[:, :prediction_target_dims],
                    x_next[:, :prediction_target_dims],
                )
            dphi = torch.mean(torch.abs(next_field - field))
            dz = torch.mean(torch.abs(z - prev_z))
            rate = torch.mean(z * z)
            correction = x_pred - x_t
            correction_cost = torch.mean(correction * correction)
            loss = (
                0.25 * rec_loss
                + pred_loss
                + 0.01 * dphi
                + 0.001 * dz
                + 0.0005 * rate
                + 0.01 * correction_cost
            )
            losses.append(loss)
            field = next_field
            level = model.update_level(x_next, level)
            prev_z = z
            if len(losses) >= sequence_chunk_size or i == len(X) - 2:
                opt.zero_grad()
                torch.stack(losses).mean().backward()
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                opt.step()
                losses = []
                field = field.detach()
                level = level.detach()
                prev_z = prev_z.detach()
        scheduler.step()
    if X_validation is not None and len(X_validation) > 1:
        candidate_gains = (0.0, 0.1, 0.25)
        scored = []
        for gain in candidate_gains:
            model.correction_gain = gain
            rows = evaluate_sequence(model, X_validation)["rows"]
            metric = (
                "target_prediction_loss"
                if prediction_target_dims is not None
                else "prediction_loss"
            )
            scored.append(
                (float(np.mean([row[metric] for row in rows])), gain)
            )
        model.correction_gain = min(scored)[1]
    return model


def evaluate_sequence(model: TESSERANet, X: np.ndarray) -> dict:
    model.eval()
    X_t = torch.tensor(X, dtype=torch.float32)
    field = torch.zeros(1, model.field_dim)
    level = X_t[0:1]
    prev_z = torch.zeros(1, model.code_dim)
    rows = []
    with torch.no_grad():
        for i in range(len(X_t) - 1):
            x = X_t[i:i+1]
            x_next = X_t[i+1:i+2]
            next_field, z, x_rec, x_pred = model.step(x, field, level)
            rec = torch.mean((x_rec - x) ** 2).item()
            pred = torch.mean((x_pred - x_next) ** 2).item()
            target_dims = getattr(model, "prediction_target_dims", None)
            if target_dims is None:
                target_dims = model.input_dim
            target_rec = torch.mean(
                (x_rec[:, :target_dims] - x[:, :target_dims]) ** 2
            ).item()
            target_pred = torch.mean(
                (x_pred[:, :target_dims] - x_next[:, :target_dims]) ** 2
            ).item()
            dphi = torch.mean(torch.abs(next_field - field)).item()
            dz = torch.mean(torch.abs(z - prev_z)).item()
            rate = torch.mean(z * z).item()
            rows.append({
                "step": i,
                "reconstruction_loss": rec,
                "prediction_loss": pred,
                "target_reconstruction_loss": target_rec,
                "target_prediction_loss": target_pred,
                "delta_phi": dphi,
                "code_drift": dz,
                "rate": rate,
            })
            field = next_field
            level = model.update_level(x_next, level)
            prev_z = z
    return {
        "rows": rows,
        "state": {
            "field": field,
            "level": level,
            "previous_code": prev_z,
            "last_observation": X_t[-1:],
            "transitions": len(rows),
        },
    }


def extend_evaluated_sequence(
    model: TESSERANet,
    state: dict,
    new_rows: np.ndarray,
) -> dict:
    """Continue an evaluated prefix without replaying validated transitions."""
    model.eval()
    values = torch.tensor(np.asarray(new_rows), dtype=torch.float32)
    field = state["field"]
    level = state["level"]
    prev_z = state["previous_code"]
    current = state["last_observation"]
    step = int(state["transitions"])
    rows = []
    with torch.no_grad():
        for x_next in values:
            x_next = x_next.reshape(1, -1)
            next_field, z, x_rec, x_pred = model.step(
                current,
                field,
                level,
            )
            rec = torch.mean((x_rec - current) ** 2).item()
            pred = torch.mean((x_pred - x_next) ** 2).item()
            target_dims = getattr(model, "prediction_target_dims", None)
            if target_dims is None:
                target_dims = model.input_dim
            target_rec = torch.mean(
                (
                    x_rec[:, :target_dims]
                    - current[:, :target_dims]
                ) ** 2
            ).item()
            target_pred = torch.mean(
                (
                    x_pred[:, :target_dims]
                    - x_next[:, :target_dims]
                ) ** 2
            ).item()
            rows.append({
                "step": step,
                "reconstruction_loss": rec,
                "prediction_loss": pred,
                "target_reconstruction_loss": target_rec,
                "target_prediction_loss": target_pred,
                "delta_phi": torch.mean(
                    torch.abs(next_field - field)
                ).item(),
                "code_drift": torch.mean(
                    torch.abs(z - prev_z)
                ).item(),
                "rate": torch.mean(z * z).item(),
            })
            field = next_field
            level = model.update_level(x_next, level)
            prev_z = z
            current = x_next
            step += 1
    return {
        "rows": rows,
        "state": {
            "field": field,
            "level": level,
            "previous_code": prev_z,
            "last_observation": current,
            "transitions": step,
        },
    }
