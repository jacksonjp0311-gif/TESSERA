from __future__ import annotations

import unittest

from tessera.experiments.effective_geometry_readiness import (
    run_effective_geometry_readiness,
)


class TestEffectiveGeometryReadiness(unittest.TestCase):
    def test_evo038_removes_phantom_dimensions(self):
        result = run_effective_geometry_readiness(
            "docs/research/EVO032_NEURAL_UNCERTAINTY_ROUTER_PREREGISTRATION.json"
        )
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["geometry"]["effective_rank"], 2)
        self.assertEqual(
            result["geometry"]["selected_features"],
            ["mean_duration_ms", "std_duration_ms"],
        )


if __name__ == "__main__":
    unittest.main()
