from __future__ import annotations

import json
import unittest
from unittest.mock import patch, MagicMock

from tessera.agnt_bridge import (
    handle_analyze,
    handle_trust,
    handle_memory,
    handle_health,
    handle_status,
    HANDLERS,
)


class TestAGNTBridge(unittest.TestCase):
    """EVO-047: AGNT integration bridge tests."""

    def test_analyze_sufficient_events(self):
        events = [
            {"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i}
            for i in range(10)
        ]
        result = handle_analyze({"events": events})
        self.assertEqual(result["status"], "analyzed")
        self.assertEqual(result["event_count"], 10)
        self.assertEqual(result["error_count"], 0)
        self.assertIn("metrics", result)

    def test_analyze_insufficient_events(self):
        result = handle_analyze({"events": [{"phase": "CHECK"}]})
        self.assertEqual(result["status"], "insufficient_context")

    def test_analyze_detects_anomalies(self):
        events = [
            {"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i}
            for i in range(20)
        ]
        # Add an anomaly
        events.append({"phase": "CHECK", "state": "FAIL", "elapsed_ms": 9999, "timestamp": 20})
        result = handle_analyze({"events": events})
        self.assertGreater(result["metrics"]["anomaly_events"], 0)

    def test_trust_trusted(self):
        result = handle_trust({"trust_route": "trusted", "anomaly_score": 0.1})
        self.assertEqual(result["trust_route"], "trusted")
        self.assertIn("Continue", result["decision"])

    def test_trust_abstain(self):
        result = handle_trust({"trust_route": "abstain", "anomaly_score": 0.9})
        self.assertEqual(result["trust_route"], "abstain")
        self.assertIn("Abstain", result["decision"])

    def test_trust_not_routed(self):
        result = handle_trust({})
        self.assertEqual(result["trust_route"], "not_routed")

    def test_memory_sufficient_events(self):
        events = [
            {"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i}
            for i in range(12)
        ]
        result = handle_memory({"events": events})
        self.assertEqual(result["status"], "proposals_ready")
        self.assertGreater(result["proposal_count"], 0)

    def test_memory_insufficient_events(self):
        result = handle_memory({"events": [{"phase": "CHECK"}]})
        self.assertEqual(result["status"], "insufficient_context")

    def test_health(self):
        result = handle_health({})
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["version"], "0.4.2")
        self.assertIn("capabilities", result)
        self.assertTrue(result["capabilities"]["tessera_plugin"])

    def test_status(self):
        result = handle_status({})
        self.assertEqual(result["status"], "complete")
        self.assertIn("summary", result)
        self.assertIn("telemetry", result)
        self.assertIn("production", result)

    def test_all_handlers_registered(self):
        expected = ["tessera-analyze", "tessera-trust", "tessera-memory", "tessera-health", "tessera-status"]
        for name in expected:
            self.assertIn(name, HANDLERS)

    def test_handlers_return_version(self):
        for name, handler in HANDLERS.items():
            result = handler({})
            self.assertIn("version", result, f"{name} missing version")

    def test_handlers_return_claim_boundary(self):
        for name, handler in HANDLERS.items():
            if name == "tessera-health":
                continue
            result = handler({})
            self.assertIn("claim_boundary", result, f"{name} missing claim_boundary")


if __name__ == "__main__":
    unittest.main()
