from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from tessera.utils.hashing import sha256_json


@dataclass(frozen=True)
class ExperimentBudget:
    epochs: int
    parameter_count: int
    train_rows: int
    latency_ms: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "epochs": self.epochs,
            "parameter_count": self.parameter_count,
            "train_rows": self.train_rows,
            "latency_ms": self.latency_ms,
        }


def model_parameter_count(model) -> int:
    return int(sum(parameter.numel() for parameter in model.parameters()))


def split_hashes(splits) -> dict[str, str]:
    return {
        name: sha256_json(getattr(splits, name).to_dict(orient="list"))
        for name in ("calibration", "train", "validation", "replay", "final_test")
    }


def preprocessing_hash(scaler) -> str:
    return sha256_json(
        {
            "class": scaler.__class__.__name__,
            "mean": np.asarray(scaler.mean_).tolist(),
            "scale": np.asarray(scaler.scale_).tolist(),
            "var": np.asarray(scaler.var_).tolist(),
        }
    )


class Timer:
    def __enter__(self):
        self.started = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.elapsed_ms = (time.perf_counter() - self.started) * 1000.0
