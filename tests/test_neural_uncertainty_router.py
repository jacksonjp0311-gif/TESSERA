from __future__ import annotations

import unittest

from tessera.experiments.neural_uncertainty_router import (
    run_neural_uncertainty_router,
)


class TestNeuralUncertaintyRouter(unittest.TestCase):
    def test_latent_drift_router_passes_without_forecast_mutation(self):
        result = run_neural_uncertainty_router(
            "docs/research/"
            "EVO032_NEURAL_UNCERTAINTY_ROUTER_PREREGISTRATION.json"
        )
        self.assertTrue(result["neural_uncertainty_routing_supported"])
        self.assertFalse(result["forecast_mutated"])
        self.assertEqual(
            result["validation"]["neural_selected"]["score"],
            "latent_drift",
        )
        self.assertTrue(result["replay"]["gate_passed"])
        self.assertTrue(result["final_test"]["gate_passed"])
        self.assertLess(
            result["final_test"]["neural"]["retained_risk"],
            result["final_test"]["full_risk"],
        )
        self.assertLess(
            result["final_test"]["neural"]["retained_risk"],
            result["final_test"]["simple"]["retained_risk"],
        )
        self.assertGreater(
            result["final_test"]["neural"]["coverage"],
            result["final_test"]["simple"]["coverage"],
        )


if __name__ == "__main__":
    unittest.main()
