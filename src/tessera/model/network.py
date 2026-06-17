from __future__ import annotations
import torch
from torch import nn


class TESSERANet(nn.Module):
    """Sparse spectral compressive memory network."""
    def __init__(self, input_dim: int, field_dim: int, code_dim: int, P, alpha: float = 0.618):
        super().__init__()
        self.input_dim = input_dim
        self.field_dim = field_dim
        self.code_dim = code_dim
        self.alpha = alpha
        P_tensor = torch.tensor(P, dtype=torch.float32)
        self.register_buffer('P', P_tensor)
        self.B = nn.Linear(input_dim, field_dim, bias=False)
        hidden = max(32, 2*field_dim)
        self.encoder = nn.Sequential(
            nn.Linear(input_dim + field_dim, hidden), nn.Tanh(), nn.Linear(hidden, code_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(code_dim, hidden), nn.Tanh(), nn.Linear(hidden, input_dim)
        )
        self.predictor = nn.Sequential(
            nn.Linear(code_dim, hidden), nn.Tanh(), nn.Linear(hidden, input_dim)
        )

    def step(self, x_t: torch.Tensor, field: torch.Tensor):
        next_field = torch.tanh(self.alpha * (field @ self.P.T) + self.B(x_t))
        z = self.encoder(torch.cat([x_t, next_field], dim=-1))
        x_rec = self.decoder(z)
        x_pred = self.predictor(z)
        return next_field, z, x_rec, x_pred
