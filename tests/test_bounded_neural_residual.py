from __future__ import annotations

import unittest

from tessera.experiments.bounded_neural_residual import (
    run_bounded_neural_residual,
)


class TestBoundedNeuralResidual(unittest.TestCase):
    def test_failed_residual_collapses_authority_to_zero(self):
        result = run_bounded_neural_residual(
            "docs/research/"
            "EVO031_BOUNDED_NEURAL_RESIDUAL_PREREGISTRATION.json"
        )
        self.assertFalse(result["bounded_residual_supported"])
        self.assertEqual(result["validation"]["selected"]["gain"], 0.0)
        self.assertFalse(result["replay"]["gate_passed"])
        self.assertTrue(result["authority"]["collapsed_to_zero"])
        self.assertEqual(result["authority"]["deployed_gain"], 0.0)
        self.assertEqual(result["final_test"]["loss_ratio"], 1.0)


if __name__ == "__main__":
    unittest.main()
