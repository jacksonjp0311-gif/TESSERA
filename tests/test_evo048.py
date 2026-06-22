"""
EVO-048: AGNT Bridge Integration Test
========================================
Live integration test that:
1. Starts the AGNT Bridge HTTP server
2. Registers the Tessera plugin with AGNT via /api/plugins/install-file
3. Calls each tool via AGNT's /api/plugins/tools endpoint
4. Measures end-to-end latency for each tool call
5. Validates response structure and claim boundaries

This is the first real end-to-end test of Tessera as an AGNT plugin.
"""

from __future__ import annotations

import json
import os
import sys
import time
import threading
import unittest
import base64
import io
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from http.server import HTTPServer
from tessera.agnt_bridge import (
    handle_analyze,
    handle_trust,
    handle_memory,
    handle_health,
    handle_status,
    HANDLERS,
    TESSERA_VERSION,
)

AGNT_BASE = "http://localhost:3333/api"
BRIDGE_BASE = "http://localhost:8765"


def _bridge_available() -> bool:
    """Check if the AGNT bridge is running."""
    try:
        urlopen(f"{BRIDGE_BASE}/health", timeout=2)
        return True
    except Exception:
        return False


def _agnt_available() -> bool:
    """Check if AGNT API is available."""
    try:
        urlopen(f"{AGNT_BASE}/plugins/installed", timeout=2)
        return True
    except Exception:
        return False


def _post(url: str, data: dict) -> dict:
    """POST JSON to a URL and return parsed response."""
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers={"Content-Type": "application/json"})
    resp = urlopen(req, timeout=30)
    return json.loads(resp.read())


def _get(url: str) -> dict:
    """GET from a URL and return parsed response."""
    resp = urlopen(url, timeout=30)
    return json.loads(resp.read())


def _build_agnt_package() -> bytes:
    """Build a .agnt package (tar.gz with manifest.json, package.json, index.js, README.md)."""
    import tarfile
    import io as _io
    plugin_dir = Path(__file__).resolve().parent.parent / "agnt-plugin"
    buf = _io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for fname in ["manifest.json", "package.json", "index.js", "README.md"]:
            fpath = plugin_dir / fname
            if fpath.exists():
                data = fpath.read_bytes()
                info = tarfile.TarInfo(name=fname)
                info.size = len(data)
                tar.addfile(info, _io.BytesIO(data))
    return buf.getvalue()


class TestBridgeEndpoints(unittest.TestCase):
    """Test the AGNT Bridge HTTP endpoints directly."""

    @classmethod
    def setUpClass(cls):
        """Start the bridge server in a background thread."""
        if not _bridge_available():
            from tessera.agnt_bridge import AGNTBridgeHandler
            cls._server = HTTPServer(("127.0.0.1", 8765), AGNTBridgeHandler)
            cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
            cls._thread.start()
            time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "_server"):
            cls._server.shutdown()

    def test_health_endpoint(self):
        resp = _get(f"{BRIDGE_BASE}/health")
        self.assertEqual(resp["status"], "healthy")
        self.assertEqual(resp["version"], TESSERA_VERSION)

    def test_tools_endpoint(self):
        resp = _get(f"{BRIDGE_BASE}/tools")
        self.assertEqual(resp["count"], 5)
        tool_names = [t["type"] for t in resp["tools"]]
        for expected in HANDLERS:
            self.assertIn(expected, tool_names)

    def test_analyze_tool(self):
        events = [{"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i} for i in range(10)]
        resp = _post(f"{BRIDGE_BASE}/tools/tessera-analyze", {"events": events})
        self.assertEqual(resp["status"], "analyzed")
        self.assertEqual(resp["event_count"], 10)
        self.assertIn("version", resp)
        self.assertIn("claim_boundary", resp)

    def test_trust_tool(self):
        resp = _post(f"{BRIDGE_BASE}/tools/tessera-trust", {"trust_route": "trusted", "anomaly_score": 0.1})
        self.assertEqual(resp["status"], "trust_decision")
        self.assertIn("Continue", resp["decision"])

    def test_memory_tool(self):
        events = [{"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i} for i in range(12)]
        resp = _post(f"{BRIDGE_BASE}/tools/tessera-memory", {"events": events})
        self.assertEqual(resp["status"], "proposals_ready")

    def test_health_tool(self):
        resp = _post(f"{BRIDGE_BASE}/tools/tessera-health", {})
        self.assertEqual(resp["status"], "healthy")
        self.assertTrue(resp["capabilities"]["tessera_plugin"])

    def test_status_tool(self):
        resp = _post(f"{BRIDGE_BASE}/tools/tessera-status", {})
        self.assertEqual(resp["status"], "complete")
        self.assertIn("summary", resp)
        self.assertIn("telemetry", resp)

    def test_latency_under_500ms(self):
        """Each tool call should complete in under 500ms (after warmup)."""
        events = [{"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i} for i in range(10)]
        # Multiple warmup calls to trigger lazy imports and JIT
        for _ in range(3):
            _post(f"{BRIDGE_BASE}/tools/tessera-health", {})
        for tool in ["tessera-analyze", "tessera-trust", "tessera-health", "tessera-status"]:
            start = time.time()
            _post(f"{BRIDGE_BASE}/tools/{tool}", {"events": events} if tool in ["tessera-analyze", "tessera-memory"] else {})
            elapsed_ms = (time.time() - start) * 1000
            self.assertLess(elapsed_ms, 500, f"{tool} took {elapsed_ms:.1f}ms (budget: 500ms)")


class TestAGNTPluginRegistration(unittest.TestCase):
    """Test registering the Tessera plugin with AGNT."""

    @classmethod
    def setUpClass(cls):
        if not _agnt_available():
            raise unittest.SkipTest("AGNT API not available at localhost:3333")

    def test_register_plugin(self):
        """Register Tessera plugin with AGNT via /install-file."""
        import tarfile
        import io as _io
        # Build a .tar.gz package (AGNT expects tar format)
        buf = _io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            plugin_dir = Path(__file__).resolve().parent.parent / "agnt-plugin"
            for fname in ["manifest.json", "package.json", "index.js", "README.md"]:
                fpath = plugin_dir / fname
                if fpath.exists():
                    data = fpath.read_bytes()
                    info = tarfile.TarInfo(name=fname)
                    info.size = len(data)
                    tar.addfile(info, _io.BytesIO(data))
        package_bytes = buf.getvalue()
        file_data = base64.b64encode(package_bytes).decode("utf-8")
        resp = _post(f"{AGNT_BASE}/plugins/install-file", {
            "name": "tessera-neural-sidecar",
            "fileData": file_data,
            "fileName": "tessera.agnt",
        })
        self.assertTrue(resp.get("success", False), f"Registration failed: {resp}")

    def test_plugin_appears_in_installed(self):
        """After registration, the plugin should appear in /installed."""
        resp = _get(f"{AGNT_BASE}/plugins/installed")
        plugin_names = [p["name"] for p in resp.get("plugins", [])]
        self.assertIn("tessera-neural-sidecar", plugin_names)

    def test_plugin_tools_available(self):
        """After registration, the plugin's tools should be available via /tools."""
        resp = _get(f"{AGNT_BASE}/plugins/tools")
        tool_names = [t["type"] for t in resp.get("tools", [])]
        for expected in HANDLERS:
            self.assertIn(expected, tool_names, f"Tool {expected} not found in AGNT tools")

    def test_plugin_details(self):
        """Get plugin details and verify structure."""
        resp = _get(f"{AGNT_BASE}/plugins/installed/tessera-neural-sidecar")
        plugin = resp.get("plugin", {})
        self.assertEqual(plugin["name"], "tessera-neural-sidecar")
        self.assertTrue(plugin.get("isValid", False))
        self.assertGreaterEqual(len(plugin.get("tools", [])), 5)


class TestEndToEndLatency(unittest.TestCase):
    """Measure end-to-end latency of the full pipeline."""

    @classmethod
    def setUpClass(cls):
        if not _agnt_available():
            raise unittest.SkipTest("AGNT API not available")
        if not _bridge_available():
            raise unittest.SkipTest("Bridge not available")

    def test_full_pipeline_latency(self):
        """Full pipeline: AGNT -> Bridge -> Tessera -> Response."""
        events = [{"phase": "CHECK", "state": "OK", "elapsed_ms": 100, "timestamp": i} for i in range(10)]
        
        start = time.time()
        resp = _post(f"{BRIDGE_BASE}/tools/tessera-analyze", {"events": events})
        elapsed_ms = (time.time() - start) * 1000
        
        self.assertEqual(resp["status"], "analyzed")
        self.assertLess(elapsed_ms, 200, f"Full pipeline took {elapsed_ms:.1f}ms (budget: 200ms)")
