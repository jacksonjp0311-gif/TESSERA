from __future__ import annotations
import torch
from torch import nn


class TESSERANet(nn.Module):
    """Sparse spectral compressive memory network - EVO-012."""
    def __init__(self, input_dim, field_dim, code_dim, P, alpha=0.618, level_alpha=0.2, hidden_dim=None, depth=2):
        super().__init__()
        self.input_dim = input_dim
        self.field_dim = field_dim
        self.code_dim = code_dim
        self.alpha = alpha
        self.level_alpha = level_alpha
        self.correction_gain = 1.0
        self.depth = depth
        self.register_buffer("P", torch.tensor(P, dtype=torch.float32))
        hidden = hidden_dim or max(64, 2 * field_dim)
        self.hidden = hidden
        self.B = nn.Linear(input_dim, field_dim, bias=False)
        self.field_update = nn.Linear(field_dim, field_dim, bias=False)
        self.field_reset = nn.Linear(field_dim, field_dim, bias=False)
        el = []
        i = input_dim + field_dim
        for d in range(depth):
            o = hidden if d < depth - 1 else code_dim
            el.append(nn.Linear(i, o))
            if d < depth - 1:
                el.append(nn.LayerNorm(o))
                el.append(nn.GELU())
            i = hidden
        self.encoder = nn.Sequential(*el)
        dl = []
        i = code_dim
        for d in range(depth):
            o = hidden if d < depth - 1 else input_dim
            dl.append(nn.Linear(i, o))
            if d < depth - 1:
                dl.append(nn.LayerNorm(o))
                dl.append(nn.GELU())
            i = hidden
        self.decoder = nn.Sequential(*dl)
        self.predictor_instant = nn.Sequential(nn.Linear(code_dim, hidden), nn.GELU(), nn.Linear(hidden, input_dim))
        self.predictor_short = nn.Sequential(nn.Linear(code_dim + input_dim, hidden), nn.GELU(), nn.Linear(hidden, input_dim))
        self.prediction_scale = nn.Parameter(torch.tensor(0.1))
        for h in [self.predictor_instant, self.predictor_short]:
            nn.init.zeros_(h[-1].weight)
            nn.init.zeros_(h[-1].bias)
        self.field_norm = nn.LayerNorm(field_dim)

    def field_step(self, x_t, field):
        proj = self.B(x_t)
        ug = torch.sigmoid(self.field_update(field))
        rg = torch.sigmoid(self.field_reset(field))
        cand = torch.tanh(self.alpha * (rg * field) @ self.P.T + proj)
        return self.field_norm((1 - ug) * field + ug * cand)

    def step(self, x_t, field, level=None):
        nf = self.field_step(x_t, field)
        z = self.encoder(torch.cat([x_t, nf], dim=-1))
        xr = self.decoder(z)
        sc = torch.tanh(self.prediction_scale) * self.correction_gain
        anchor = x_t if level is None else level
        xp = anchor + sc * torch.tanh(self.predictor_instant(z))
        return nf, z, xr, xp

    def update_level(self, observed, level):
        return self.level_alpha * observed + (1.0 - self.level_alpha) * level
