from __future__ import annotations

import unittest

from tessera.plugin.incident_governor import IncidentGovernor


class TestIncidentGovernor(unittest.TestCase):
    def test_failure_latches_and_clean_terminal_releases(self):
        governor = IncidentGovernor(recovery_sessions_required=1)
        governor.record_outcome(failed=True, terminal_ok=False)
        blocked = governor.govern(
            "trusted",
            neural_memory_candidate=True,
        )
        self.assertEqual(blocked.route, "abstain")
        self.assertFalse(blocked.memory_candidate)
        governor.record_outcome(failed=False, terminal_ok=True)
        released = governor.govern(
            "trusted",
            neural_memory_candidate=True,
        )
        self.assertEqual(released.route, "trusted")
        self.assertTrue(released.memory_candidate)

    def test_incomplete_recovery_resets_streak(self):
        governor = IncidentGovernor(recovery_sessions_required=2)
        governor.record_outcome(failed=True, terminal_ok=False)
        governor.record_outcome(failed=False, terminal_ok=True)
        governor.record_outcome(failed=False, terminal_ok=False)
        self.assertTrue(governor.incident_latched)


if __name__ == "__main__":
    unittest.main()
