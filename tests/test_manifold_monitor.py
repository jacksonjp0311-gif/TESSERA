from __future__ import annotations

import unittest

import numpy as np

from tessera.plugin.manifold_monitor import (
    audit_manifold_window,
    fit_manifold_contract,
    govern_manifold_audit,
)


class TestManifoldMonitor(unittest.TestCase):
    def setUp(self):
        x = np.linspace(1.0, 20.0, 20)
        self.values = np.zeros((20, 4), dtype=float)
        self.values[:, 0] = x
        self.values[:, 2] = 2.0 * x + np.sin(x) * 0.05
        self.contract = fit_manifold_contract(
            self.values,
            (0, 2),
        )

    def test_stable_filament_is_accepted(self):
        audit = audit_manifold_window(self.contract, self.values)
        self.assertTrue(audit.accepted, audit)
        self.assertEqual(audit.status, "stable")
        self.assertEqual(audit.intrinsic_rank, 1)

    def test_support_collapse_is_rejected(self):
        collapsed = self.values.copy()
        collapsed[:, 2] = collapsed[0, 2]
        audit = audit_manifold_window(self.contract, collapsed)
        self.assertFalse(audit.accepted)
        self.assertEqual(audit.status, "support_collapse")

    def test_support_expansion_is_rejected(self):
        expanded = self.values.copy()
        expanded[:, 1] = np.arange(len(expanded))
        audit = audit_manifold_window(self.contract, expanded)
        self.assertFalse(audit.accepted)
        self.assertEqual(audit.status, "support_expansion")

    def test_rotation_is_rejected(self):
        rotated = self.values.copy()
        rotated[:, 2] = -2.0 * rotated[:, 0]
        audit = audit_manifold_window(self.contract, rotated)
        self.assertFalse(audit.accepted)
        self.assertEqual(audit.status, "manifold_rotation")
        governed = govern_manifold_audit(
            audit,
            "trusted",
            neural_memory_candidate=True,
        )
        self.assertEqual(governed.route, "abstain")
        self.assertFalse(governed.memory_candidate)


if __name__ == "__main__":
    unittest.main()
