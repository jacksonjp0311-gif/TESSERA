from __future__ import annotations

import unittest

import numpy as np

from tessera.plugin.manifold_monitor import fit_manifold_contract
from tessera.plugin.sequential_geometry import (
    SequentialGeometryState,
    fit_sequential_geometry_contract,
    update_sequential_geometry,
)


class TestSequentialGeometry(unittest.TestCase):
    def setUp(self):
        x = np.linspace(1.0, 30.0, 30)
        values = np.zeros((30, 4), dtype=float)
        values[:, 0] = x
        values[:, 2] = 2.0 * x + np.sin(x) * 0.1
        self.values = values
        self.manifold = fit_manifold_contract(values, (0, 2))
        self.contract = fit_sequential_geometry_contract(
            self.manifold,
            values,
        )

    def test_contract_fingerprint_binds_manifold(self):
        self.assertEqual(
            self.contract.manifold_fingerprint,
            self.manifold.fingerprint,
        )
        self.assertEqual(len(self.contract.fingerprint), 64)

    def test_persistent_alarm_latches_and_blocks_memory(self):
        state = SequentialGeometryState()
        summary = self.values[-1].copy()
        axis = np.asarray(self.manifold.principal_axis)
        normal = np.asarray([-axis[1], axis[0]])
        selected = np.asarray(self.manifold.selected_indices)
        normalized = (
            summary[selected] - np.asarray(self.manifold.center)
        ) / np.asarray(self.manifold.scale)
        normalized += 0.5 * normal
        summary[selected] = (
            normalized * np.asarray(self.manifold.scale)
            + np.asarray(self.manifold.center)
        )
        update = None
        for _ in range(12):
            update = update_sequential_geometry(
                self.contract,
                self.manifold,
                summary,
                state,
            )
            state = update.state
        self.assertTrue(update.state.alarmed)
        self.assertEqual(update.route, "abstain")
        self.assertFalse(update.memory_candidate)


if __name__ == "__main__":
    unittest.main()
