"""
EVO-049: AGNT Bridge Integration Test
======================================
Self-contained test that starts the bridge, tests all endpoints,
measures latency, and produces results for the dashboard.
"""
from __future__ import annotations

import json
import sys
import os
import time
import socket
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from urllib.request import urlopen, Request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tessera.agnt_bridge import AGNTBridgeHandler, HANDLERS, TESSERA_VERSION

# Find a free port
def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

PORT = _free_port()
BRIDGE_BASE = f"http://127.0.0.1:{PORT}"


def _get(path):
    resp = urlopen(f"{BRIDGE_BASE}{path}", timeout=5)
    return json.loads(resp.read())


def _post(path, data=None):
    body = json.dumps(data).encode("utf-8") if data else b""
    req = Request(f"{BRIDGE_BASE}{path}", data=body, headers={"Content-Type": "application/json"})
    resp = urlopen(req, timeout=30)
    return json.loads(resp.read())


class TestBridgeIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._server = HTTPServer(("127.0.0.1", PORT), AGNTBridgeHandler)
        cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
        cls._thread.start()
        for _ in range(30):
            try:
                urlopen(f"{BRIDGE_BASE}/health", timeout=1)
                return
            except Exception:
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls._server.shutdown()

    def test_01_health(self):
        resp = _get("/health")
        self.assertEqual(resp["status"], "healthy")
        self.assertEqual(resp["version"], TESSERA_VERSION)

    def test_02_tools_list(self):
        resp = _get("/tools")
        self.assertEqual(resp["count"], 5)
        names = [t["type"] for t in resp["tools"]]
        for expected in HANDLERS:
            self.assertIn(expected, names)

    def test_03_analyze(self):
        events = [{"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i} for i in range(10)]
        resp = _post("/tools/tessera-analyze", {"events": events})
        self.assertEqual(resp["status"], "analyzed")
        self.assertEqual(resp["event_count"], 10)
        self.assertIn("version", resp)
        self.assertIn("claim_boundary", resp)

    def test_04_trust(self):
        resp = _post("/tools/tessera-trust", {"trust_route": "trusted", "anomaly_score": 0.1})
        self.assertEqual(resp["status"], "trust_decision")
        self.assertIn("Continue", resp["decision"])

    def test_05_memory(self):
        events = [{"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i} for i in range(12)]
        resp = _post("/tools/tessera-memory", {"events": events})
        self.assertEqual(resp["status"], "proposals_ready")

    def test_06_status(self):
        resp = _post("/tools/tessera-status", {})
        self.assertEqual(resp["status"], "complete")
        self.assertIn("summary", resp)
        self.assertIn("telemetry", resp)

    def test_07_latency(self):
        events = [{"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i} for i in range(10)]
        for _ in range(3):
            _post("/tools/tessera-health", {})
        for tool in ["tessera-analyze", "tessera-trust", "tessera-health", "tessera-status"]:
            start = time.time()
            _post(f"/tools/{tool}", {"events": events} if tool in ["tessera-analyze", "tessera-memory"] else {})
            ms = (time.time() - start) * 1000
            self.assertLess(ms, 3000, f"{tool} took {ms:.0f}ms")

    def test_08_anomaly_detection(self):
        events = [{"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i} for i in range(20)]
        events.append({"phase": "CHECK", "state": "FAIL", "elapsed_ms": 9999, "timestamp": 20})
        resp = _post("/tools/tessera-analyze", {"events": events})
        self.assertGreater(resp["metrics"]["anomaly_events"], 0)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.TestLoader().loadTestsFromTestCase(TestBridgeIntegration)
    )
    results = {
        "test": "EVO-049", "version": TESSERA_VERSION,
        "tests_run": result.testsRun, "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures), "errors": len(result.errors),
        "all_passed": result.wasSuccessful(), "timestamp": time.time(),
    }
    out = Path(__file__).resolve().parent.parent / "outputs" / "benchmarks" / "evo049_bridge_integration.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults: {out}")
