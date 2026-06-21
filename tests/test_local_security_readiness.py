from __future__ import annotations

import unittest

from tessera.experiments.local_security_readiness import (
    run_local_security_readiness,
)


class TestLocalSecurityReadiness(unittest.TestCase):
    def test_local_security_gate_passes_without_overclaim(self):
        result = run_local_security_readiness()
        self.assertTrue(result["passed"], result)
        self.assertFalse(result["external_security_review_complete"])
        self.assertTrue(result["checks"]["tracked_secret_scan_clean"])


if __name__ == "__main__":
    unittest.main()
