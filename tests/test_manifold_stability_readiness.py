from __future__ import annotations

import unittest

from tessera.experiments.manifold_stability_readiness import (
    run_manifold_stability_readiness,
)


class TestManifoldStabilityReadiness(unittest.TestCase):
    def test_evo039_detects_filament_and_injected_drift(self):
        result = run_manifold_stability_readiness(
            "docs/research/EVO039_MANIFOLD_STABILITY_PREREGISTRATION.json"
        )
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["contract"]["intrinsic_rank"], 1)
        self.assertGreater(
            result["contract"]["explained_variance"],
            0.98,
        )


if __name__ == "__main__":
    unittest.main()
