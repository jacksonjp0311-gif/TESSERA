from __future__ import annotations

import unittest

from tessera.experiments.failure_recovery_readiness import (
    run_failure_recovery_readiness,
)


class TestFailureRecoveryReadiness(unittest.TestCase):
    def test_evo036_preserves_minimum_support_gate(self):
        result = run_failure_recovery_readiness(
            "docs/research/EVO036_FAILURE_RECOVERY_PREREGISTRATION.json",
            "outputs/evidence/evo036/failure_prefix.json",
            "outputs/evidence/evo036/recovery_prefix.json",
        )
        self.assertFalse(result["checks"]["minimum_episode_support_met"])
        self.assertFalse(result["natural_failure_recovery_promoted"])
        self.assertTrue(result["passed"])
        self.assertTrue(
            result["checks"]["incident_latch_forces_abstention"]
        )
        self.assertTrue(
            result["checks"]["clean_terminal_session_releases_latch"]
        )
        self.assertEqual(
            result["decision"],
            "retain_router_reject_failure_recovery_claim",
        )


if __name__ == "__main__":
    unittest.main()
