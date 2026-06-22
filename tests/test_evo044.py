from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from tessera.experiments.trajectory_local_benchmark import (
    capture_agent_cli_sessions,
    run_local_utility_benchmark,
)
from tessera.experiments.independent_host_trial import (
    run_independent_host_trial,
    _compute_parity,
    _compute_rank_drift,
)


def _make_session_file(path: Path, sessions: list[list[dict]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for session in sessions:
            f.write(json.dumps(session) + "\n")


def _make_session(session_id: str, n_events: int = 10, degraded: bool = False) -> list[dict]:
    records = []
    for i in range(n_events):
        pressure = 0.5 if degraded and i >= n_events - 3 else 0.0
        records.append({
            "kind": "test_result" if i % 2 == 0 else "tool_call",
            "timestamp": float(i),
            "phase": "CHECK" if i < n_events - 1 else "ROOT",
            "state": "FAIL" if (degraded and i == n_events - 1) else "OK",
            "session_id": session_id,
            "duration_ms": 100.0 + 200.0 * pressure,
            "token_count": 300.0 + 100.0 * pressure,
            "error": float(degraded and i == n_events - 1),
            "retry": float(degraded and i == n_events - 2),
            "tests_failed": float(degraded and i == n_events - 1),
        })
    return records


class TestIndependentHostTrial(unittest.TestCase):
    """EVO-044: Independent host trial framework."""

    def _make_ref_trial_files(self):
        """Create reference and trial session files."""
        ref_sessions = [
            _make_session(f"ref-{i}", n_events=10, degraded=(i % 2 == 1))
            for i in range(6)
        ]
        trial_sessions = [
            _make_session(f"trial-{i}", n_events=10, degraded=(i % 3 == 0))
            for i in range(4)
        ]
        ref_path = Path(tempfile.mktemp(suffix=".jsonl"))
        trial_path = Path(tempfile.mktemp(suffix=".jsonl"))
        _make_session_file(ref_path, ref_sessions)
        _make_session_file(trial_path, trial_sessions)
        return ref_path, trial_path

    def test_trial_runs(self):
        ref_path, trial_path = self._make_ref_trial_files()
        store_path = tempfile.mkdtemp()
        try:
            result = run_independent_host_trial(
                trial_id="test-trial-1",
                reference_host="agent-cli-mirror",
                trial_host="hermes-agent",
                reference_sessions_path=ref_path,
                trial_sessions_path=trial_path,
                capsule_store_path=store_path,
            )
            self.assertEqual(result["trial_id"], "test-trial-1")
            self.assertEqual(result["reference_host"], "agent-cli-mirror")
            self.assertEqual(result["trial_host"], "hermes-agent")
            self.assertEqual(len(result["host_results"]), 2)
            self.assertGreater(result["capsules_written"], 0)
            self.assertEqual(result["capsules_verified"], result["capsules_written"])
        finally:
            ref_path.unlink(missing_ok=True)
            trial_path.unlink(missing_ok=True)

    def test_trial_parity(self):
        ref_path, trial_path = self._make_ref_trial_files()
        store_path = tempfile.mkdtemp()
        try:
            result = run_independent_host_trial(
                trial_id="test-trial-2",
                reference_host="ref-host",
                trial_host="trial-host",
                reference_sessions_path=ref_path,
                trial_sessions_path=trial_path,
                capsule_store_path=store_path,
            )
            self.assertIn("parity_checks", result)
            self.assertIn("rank_drift_summary", result)
        finally:
            ref_path.unlink(missing_ok=True)
            trial_path.unlink(missing_ok=True)

    def test_parity_computation(self):
        ref = {"abstention_rate": 0.2, "warning_rate": 0.5, "mean_anomaly_score": 1.0, "neural_rate": 0.8}
        trial = {"abstention_rate": 0.25, "warning_rate": 0.55, "mean_anomaly_score": 1.1, "neural_rate": 0.75}
        parity = _compute_parity(ref, trial)
        self.assertTrue(parity["comparable"])
        self.assertTrue(parity["all_within_tolerance"])

    def test_parity_outside_tolerance(self):
        ref = {"abstention_rate": 0.2, "warning_rate": 0.5, "mean_anomaly_score": 1.0, "neural_rate": 0.8}
        trial = {"abstention_rate": 0.9, "warning_rate": 0.5, "mean_anomaly_score": 1.0, "neural_rate": 0.8}
        parity = _compute_parity(ref, trial)
        self.assertFalse(parity["all_within_tolerance"])

    def test_rank_drift_computation(self):
        from tessera.experiments.trajectory_local_benchmark import LocalSessionCapture
        ref_caps = [
            type("C", (), {"session_id_hash": f"r{i}", "event_count": 10 + i, "adapter_coverage": 0.9})()
            for i in range(4)
        ]
        trial_caps = [
            type("C", (), {"session_id_hash": f"t{i}", "event_count": 12 + i, "adapter_coverage": 0.85})()
            for i in range(3)
        ]
        drift = _compute_rank_drift(ref_caps, trial_caps)
        self.assertTrue(drift["comparable"])
        self.assertEqual(drift["reference_sessions"], 4)
        self.assertEqual(drift["trial_sessions"], 3)
        self.assertGreater(drift["event_count_drift"], 0)


if __name__ == "__main__":
    unittest.main()
