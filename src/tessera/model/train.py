from __future__ import annotations
import numpy as np
import torch
from torch import nn
from .network import TESSERANet


def fit_tessera_model(X_train: np.ndarray, P: np.ndarray, code_dim: int, alpha: float, epochs: int = 6, lr: float = 1e-3, seed: int = 42) -> TESSERANet:
    torch.manual_seed(seed)
    model = TESSERANet(input_dim=X_train.shape[1], field_dim=P.shape[0], code_dim=code_dim, P=P, alpha=alpha)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    X = torch.tensor(X_train, dtype=torch.float32)
    for _ in range(epochs):
        field = torch.zeros(1, P.shape[0])
        prev_z = torch.zeros(1, code_dim)
        for i in range(len(X)-1):
            x_t = X[i:i+1]
            x_next = X[i+1:i+2]
            next_field, z, x_rec, x_pred = model.step(x_t, field.detach())
            rec_loss = loss_fn(x_rec, x_t)
            pred_loss = loss_fn(x_pred, x_next)
            dphi = torch.mean(torch.abs(next_field - field.detach()))
            dz = torch.mean(torch.abs(z - prev_z.detach()))
            rate = torch.mean(z*z)
            loss = rec_loss + pred_loss + 0.01*dphi + 0.001*dz + 0.0005*rate
            opt.zero_grad(); loss.backward(); opt.step()
            field = next_field.detach()
            prev_z = z.detach()
    return model


def evaluate_sequence(model: TESSERANet, X: np.ndarray) -> dict:
    model.eval()
    X_t = torch.tensor(X, dtype=torch.float32)
    field = torch.zeros(1, model.field_dim)
    prev_z = torch.zeros(1, model.code_dim)
    rows=[]
    with torch.no_grad():
        for i in range(len(X_t)-1):
            x = X_t[i:i+1]
            x_next = X_t[i+1:i+2]
            next_field,z,x_rec,x_pred = model.step(x, field)
            rec = torch.mean((x_rec-x)**2).item()
            pred = torch.mean((x_pred-x_next)**2).item()
            dphi = torch.mean(torch.abs(next_field-field)).item()
            dz = torch.mean(torch.abs(z-prev_z)).item()
            rate = torch.mean(z*z).item()
            rows.append({'step':i,'reconstruction_loss':rec,'prediction_loss':pred,'delta_phi':dphi,'code_drift':dz,'rate':rate})
            field = next_field
            prev_z = z
    return {'rows': rows}
