from __future__ import annotations

import tempfile
import unittest

from tessera.experiments.natural_checkpoint_utility import (
    run_natural_checkpoint_utility,
)


class TestNaturalCheckpointUtility(unittest.TestCase):
    def test_natural_checkpoint_rejection_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_natural_checkpoint_utility(
                "docs/research/"
                "EVO030_NATURAL_CHECKPOINT_UTILITY_PREREGISTRATION.json",
                directory,
            )
        self.assertEqual(result["session_count"], 120)
        self.assertFalse(result["admission"]["admitted"])
        self.assertFalse(result["natural_checkpoint_utility_supported"])
        self.assertEqual(
            result["decision"],
            "reject_natural_checkpoint_admission_preserve_fast_path",
        )
        self.assertLess(
            result["checkpoint_metrics"]["replay_pass_rate"],
            0.60,
        )
        self.assertGreater(
            result["final_test"]["checkpoint_loss_ratio_to_best_control"],
            1.0,
        )
        self.assertEqual(
            result["final_test"]["best_control"],
            "validation_selected_ewma",
        )


if __name__ == "__main__":
    unittest.main()
