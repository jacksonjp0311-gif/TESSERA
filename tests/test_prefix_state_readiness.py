from __future__ import annotations

import unittest

from tessera.experiments.prefix_state_readiness import (
    run_prefix_state_readiness,
)


class TestPrefixStateReadiness(unittest.TestCase):
    def test_evo041_prefix_state_matches_full_replay(self):
        result = run_prefix_state_readiness()
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["metrics"]["packet_parity_rate"], 1.0)
        self.assertEqual(result["metrics"]["row_parity_rate"], 1.0)
        self.assertEqual(result["metrics"]["prefix_extensions"], 19)


if __name__ == "__main__":
    unittest.main()
