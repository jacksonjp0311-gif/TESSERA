from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tessera.plugin.atomic_capsule_store import (
    AtomicCapsuleStore,
    CapsuleIntegrityError,
    CapsuleRecord,
)
from tessera.plugin.contracts import AgentEvent
from tessera.experiments.trajectory_local_benchmark import (
    capture_agent_cli_sessions,
    run_local_utility_benchmark,
)


class TestAtomicCapsuleStore(unittest.TestCase):
    """EVO-043: Atomic host-owned capsule store."""

    def _temp_store(self):
        return AtomicCapsuleStore(tempfile.mkdtemp(), max_capsules=100)

    def test_write_and_read_capsule(self):
        store = self._temp_store()
        payload = {"state": "ok", "value": 42}
        record = store.write_capsule(payload, host="test", session_id_hash="abc123")
        self.assertIsNotNone(record.capsule_id)
        self.assertEqual(record.host, "test")
        self.assertEqual(record.session_id_hash, "abc123")

        read = store.read_capsule(record.capsule_id)
        self.assertEqual(read.payload, payload)
        self.assertTrue(read.verify_integrity())

    def test_host_key_enforcement(self):
        store = AtomicCapsuleStore(tempfile.mkdtemp(), max_capsules=100, host_key="my-host")
        store.write_capsule({"x": 1}, host="my-host", session_id_hash="s1")
        with self.assertRaises(CapsuleIntegrityError):
            store.write_capsule({"x": 2}, host="other-host", session_id_hash="s2")

    def test_list_capsules_by_host(self):
        store = self._temp_store()
        store.write_capsule({"x": 1}, host="host-a", session_id_hash="s1")
        store.write_capsule({"x": 2}, host="host-b", session_id_hash="s2")
        store.write_capsule({"x": 3}, host="host-a", session_id_hash="s3")

        host_a = store.list_capsules(host="host-a")
        self.assertEqual(len(host_a), 2)

        host_b = store.list_capsules(host="host-b")
        self.assertEqual(len(host_b), 1)

    def test_list_capsules_by_session(self):
        store = self._temp_store()
        store.write_capsule({"x": 1}, host="h", session_id_hash="session-1")
        store.write_capsule({"x": 2}, host="h", session_id_hash="session-2")
        store.write_capsule({"x": 3}, host="h", session_id_hash="session-1")

        results = store.list_capsules(session_id_hash="session-1")
        self.assertEqual(len(results), 2)

    def test_stats(self):
        store = self._temp_store()
        store.write_capsule({"x": 1}, host="h1", session_id_hash="s1")
        store.write_capsule({"x": 2}, host="h2", session_id_hash="s2")
        store.write_capsule({"x": 3}, host="h1", session_id_hash="s3")

        stats = store.stats()
        self.assertEqual(stats.total_capsules, 3)
        self.assertEqual(stats.hosts.get("h1"), 2)
        self.assertEqual(stats.hosts.get("h2"), 1)
        self.assertEqual(stats.sessions, 3)
        self.assertFalse(stats.store_full)

    def test_verify_all(self):
        store = self._temp_store()
        store.write_capsule({"x": 1}, host="h", session_id_hash="s1")
        store.write_capsule({"x": 2}, host="h", session_id_hash="s2")

        result = store.verify_all()
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["passed"], 2)
        self.assertEqual(result["failed"], 0)

    def test_eviction_on_overflow(self):
        store = AtomicCapsuleStore(tempfile.mkdtemp(), max_capsules=3)
        store.write_capsule({"x": 1}, host="h", session_id_hash="s1")
        store.write_capsule({"x": 2}, host="h", session_id_hash="s2")
        store.write_capsule({"x": 3}, host="h", session_id_hash="s3")
        # This should evict the oldest
        store.write_capsule({"x": 4}, host="h", session_id_hash="s4")

        stats = store.stats()
        self.assertEqual(stats.total_capsules, 3)

    def test_tamper_detection(self):
        store = self._temp_store()
        record = store.write_capsule({"x": 1}, host="h", session_id_hash="s1")

        # Tamper with the capsule file
        capsule_file = None
        for root, dirs, files in os.walk(store._store_path):
            for f in files:
                if f.startswith(record.capsule_id):
                    capsule_file = Path(root) / f
                    break

        if capsule_file and capsule_file.exists():
            data = json.loads(capsule_file.read_text())
            data["payload"]["x"] = 999
            capsule_file.write_text(json.dumps(data))
            with self.assertRaises(CapsuleIntegrityError):
                store.read_capsule(record.capsule_id)


class TestLocalUtilityBenchmark(unittest.TestCase):
    """EVO-043: Live agent utility benchmark on captured sessions."""

    def _make_events_file(self, path: Path, sessions: list[list[dict]]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for session in sessions:
                f.write(json.dumps(session) + "\n")

    def _make_session(self, session_id: str, n_events: int = 10, degraded: bool = False) -> list[dict]:
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

    def test_capture_sessions(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            sessions = [
                self._make_session("s1", n_events=10, degraded=False),
                self._make_session("s2", n_events=10, degraded=True),
            ]
            for s in sessions:
                f.write(json.dumps(s) + "\n")
            f.flush()
            path = f.name

        try:
            captures = capture_agent_cli_sessions(path, minimum_prefix=7)
            self.assertEqual(len(captures), 2)
            self.assertEqual(captures[0].source, "agent_cli_mirror")
            self.assertGreater(captures[0].adapter_coverage, 0.0)
        finally:
            os.unlink(path)

    def test_utility_benchmark_runs(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            sessions = [
                self._make_session(f"bench-{i}", n_events=10, degraded=(i % 2 == 1))
                for i in range(6)
            ]
            for s in sessions:
                f.write(json.dumps(s) + "\n")
            f.flush()
            path = f.name

        try:
            captures = capture_agent_cli_sessions(path, minimum_prefix=7)
            result = run_local_utility_benchmark(captures)

            self.assertEqual(result["total_sessions"], 6)
            self.assertIn("abstention_rate", result)
            self.assertIn("warning_rate", result)
            self.assertIn("mean_anomaly_score", result)
            self.assertIn("results", result)
            self.assertEqual(len(result["results"]), 6)
        finally:
            os.unlink(path)

    def test_utility_benchmark_empty(self):
        result = run_local_utility_benchmark([])
        self.assertEqual(result["total_sessions"], 0)

    def test_capture_filters_by_minimum_prefix(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            # One short session (should be filtered) and one long session
            short = self._make_session("short", n_events=3, degraded=False)
            long = self._make_session("long", n_events=12, degraded=False)
            f.write(json.dumps(short) + "\n")
            f.write(json.dumps(long) + "\n")
            f.flush()
            path = f.name

        try:
            captures = capture_agent_cli_sessions(path, minimum_prefix=7)
            self.assertEqual(len(captures), 1)
            self.assertEqual(captures[0].session_id_hash, captures[0].session_id_hash)
        finally:
            os.unlink(path)

    def test_capture_session_id_filter(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            sessions = [self._make_session(f"s{i}", n_events=10) for i in range(4)]
            for s in sessions:
                f.write(json.dumps(s) + "\n")
            f.flush()
            path = f.name

        try:
            captures = capture_agent_cli_sessions(
                path, minimum_prefix=7, session_ids=["s1", "s3"]
            )
            self.assertEqual(len(captures), 2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
