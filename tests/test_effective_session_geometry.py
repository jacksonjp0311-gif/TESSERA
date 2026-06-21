from __future__ import annotations

import unittest

import numpy as np

from tessera.plugin.host_adapters import effective_session_feature_indices


class TestEffectiveSessionGeometry(unittest.TestCase):
    def test_constant_float32_coordinates_do_not_create_rank(self):
        values = np.asarray([
            [float(index), 5.6666665, float(index * 2), 2.2110832, 2.5819888]
            for index in range(100)
        ], dtype="float32")
        selected = effective_session_feature_indices(values)
        self.assertEqual(selected, (0, 2))


if __name__ == "__main__":
    unittest.main()
