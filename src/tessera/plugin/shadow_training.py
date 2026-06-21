from __future__ import annotations

import multiprocessing as mp
import queue
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .checkpoints import CheckpointStore


@dataclass(frozen=True)
class ShadowTrainingJob:
    features: list[list[float]]
    lineage: dict
    timeout_seconds: float = 60.0


def _train_summary_worker(features, output_queue) -> None:
    matrix = np.asarray(features, dtype=float)
    if matrix.ndim != 2 or len(matrix) < 3:
        output_queue.put({"status": "failed", "reason": "insufficient_rows"})
        return
    history = matrix[:-1]
    deltas = matrix[1:] - matrix[:-1]
    payload = {
        "kind": "robust-fast-path-state",
        "feature_count": int(matrix.shape[1]),
        "center": np.median(history, axis=0).tolist(),
        "scale": np.maximum(
            np.median(np.abs(history - np.median(history, axis=0)), axis=0),
            1e-6,
        ).tolist(),
        "prediction_delta": np.median(deltas, axis=0).tolist(),
    }
    baseline = float(np.mean(deltas * deltas))
    centered = deltas - np.asarray(payload["prediction_delta"])
    candidate = float(np.mean(centered * centered))
    output_queue.put({
        "status": "ok",
        "payload": payload,
        "metrics": {
            "baseline_loss": baseline,
            "candidate_loss": candidate,
            "training_rows": int(len(matrix)),
        },
    })


class ShadowTrainer:
    """Asynchronous candidate builder; never activates checkpoints."""

    def __init__(self, store_root: str | Path):
        self.store = CheckpointStore(store_root)
        self._process = None
        self._output_queue = None
        self._lineage = None

    def submit(self, job: ShadowTrainingJob) -> bool:
        if self._process is not None and self._process.is_alive():
            return False
        context = mp.get_context("spawn")
        self._output_queue = context.Queue(maxsize=1)
        self._lineage = dict(job.lineage)
        self._process = context.Process(
            target=_train_summary_worker,
            args=(job.features, self._output_queue),
        )
        self._process.start()
        return True

    def poll(self) -> dict:
        if self._process is None:
            return {"status": "idle"}
        try:
            result = self._output_queue.get_nowait()
        except queue.Empty:
            if self._process.is_alive():
                return {"status": "running"}
            return {"status": "failed", "reason": "worker_no_result"}
        self._process.join(timeout=1.0)
        self._output_queue.close()
        self._process = None
        self._output_queue = None
        if result["status"] != "ok":
            return result
        candidate = self.store.write_candidate(
            payload=result["payload"],
            lineage=self._lineage or {},
            metrics=result["metrics"],
        )
        return {
            "status": "candidate_ready",
            "candidate": candidate,
        }

    def stop(self) -> None:
        if self._process is not None and self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=2.0)
        if self._output_queue is not None:
            self._output_queue.close()
        self._process = None
        self._output_queue = None
