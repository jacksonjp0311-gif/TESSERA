from __future__ import annotations

import unittest

from tessera.experiments.restart_state_readiness import (
    run_restart_state_readiness,
)


class TestRestartStateReadiness(unittest.TestCase):
    def test_evo042_restores_only_integrity_bound_state(self):
        result = run_restart_state_readiness()
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["metrics"]["packet_parity"], 1.0)
        self.assertEqual(result["metrics"]["row_parity"], 1.0)


if __name__ == "__main__":
    unittest.main()
