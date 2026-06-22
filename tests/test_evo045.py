from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tessera.experiments.run_yahoo_s5_transfer import (
    load_yahoo_s5_stream,
    run_yahoo_s5_transfer,
)


def _create_yahoo_csv(path: Path, n: int = 500, anomaly_windows: list[list[int]] | None = None) -> None:
    """Create a synthetic Yahoo S5-format CSV for testing."""
    rng = np.random.default_rng(42)
    timestamps = np.arange(n)
    values = rng.normal(100, 10, n).astype(float)
    labels = np.zeros(n, dtype=int)

    if anomaly_windows:
        for start, end in anomaly_windows:
            values[start:end] += rng.normal(50, 15, end - start)
            labels[start:end] = 1

    with open(path, "w") as f:
        f.write("timestamp,value,anomaly\n")
        for t, v, l in zip(timestamps, values.flatten(), labels):
            f.write(f"{t},{v},{l}\n")


class TestYahooS5Transfer(unittest.TestCase):
    """EVO-045: Third dataset family evaluation."""

    def _temp_data_dir(self) -> Path:
        d = Path(tempfile.mkdtemp())
        _create_yahoo_csv(d / "A1Benchmark_real_1.csv", n=600, anomaly_windows=[[287, 307], [490, 513]])
        _create_yahoo_csv(d / "A2Benchmark_synthetic_1.csv", n=400, anomaly_windows=[])
        return d

    def test_load_stream(self):
        d = self._temp_data_dir()
        values, labels = load_yahoo_s5_stream(d / "A1Benchmark_real_1.csv")
        self.assertEqual(values.shape[0], 600)
        self.assertEqual(values.shape[1], 1)
        self.assertEqual(len(labels), 600)
        self.assertGreater(labels.sum(), 0)

    def test_load_stream_no_windows(self):
        d = self._temp_data_dir()
        values, labels = load_yahoo_s5_stream(d / "A2Benchmark_synthetic_1.csv")
        self.assertEqual(values.shape[0], 400)
        self.assertEqual(labels.sum(), 0)

    def test_transfer_returns_results(self):
        d = self._temp_data_dir()
        result = run_yahoo_s5_transfer(
            data_dir=d,
            stream_name="A1Benchmark_real_1.csv",
            epochs=2,
            field_dim=8,
            code_dim=4,
            hidden_dim=32,
            depth=2,
        )
        self.assertEqual(result["status"], "evaluated")
        self.assertIn("auc", result)
        self.assertIn("recall", result)
        self.assertIn("t1_supported", result)
        self.assertIn("t1_supported", result)  # T1 support is determined by AUC > 0.9

    def test_transfer_clean_stream(self):
        d = self._temp_data_dir()
        result = run_yahoo_s5_transfer(
            data_dir=d,
            stream_name="A2Benchmark_synthetic_1.csv",
            epochs=1,
            field_dim=8,
            code_dim=4,
            hidden_dim=32,
            depth=2,
        )
        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(result["recall"], 0.0)  # No anomalies

    def test_data_not_found(self):
        d = Path(tempfile.mkdtemp())
        result = run_yahoo_s5_transfer(
            data_dir=d,
            stream_name="nonexistent.csv",
            epochs=1,
        )
        self.assertEqual(result["status"], "data_not_found")

    def test_result_structure(self):
        d = self._temp_data_dir()
        result = run_yahoo_s5_transfer(
            data_dir=d,
            stream_name="A1Benchmark_real_1.csv",
            epochs=1,
            field_dim=8,
            code_dim=4,
            hidden_dim=32,
            depth=2,
        )
        required_keys = [
            "status", "stream", "n_samples", "auc", "recall",
            "false_memory_rate", "replay_pass_rate", "neural_prediction_loss",
            "best_baseline_loss", "baseline_gap", "selected_expert",
            "t1_supported", "parameter_count", "depth", "hidden_dim",
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")


if __name__ == "__main__":
    unittest.main()
