from __future__ import annotations

import unittest

from tessera.experiments.sequential_geometry_readiness import (
    run_sequential_geometry_readiness,
)


class TestSequentialGeometryReadiness(unittest.TestCase):
    def test_evo040_separates_impulse_from_persistent_drift(self):
        result = run_sequential_geometry_readiness(
            "docs/research/EVO040_SEQUENTIAL_GEOMETRY_PREREGISTRATION.json"
        )
        self.assertTrue(result["passed"], result)
        self.assertLessEqual(
            result["metrics"]["persistent_alarm_delay"],
            10,
        )


if __name__ == "__main__":
    unittest.main()
