import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
import numpy as np
from tessera.graph.topologies import make_operator
from tessera.graph.spectral import spectral_radius

class TestGraphOperator(unittest.TestCase):
    def test_q4_row_normalized(self):
        P = make_operator('q4', 16)
        self.assertEqual(P.shape, (16,16))
        np.testing.assert_allclose(P.sum(axis=1), np.ones(16), atol=1e-6)
        self.assertLessEqual(spectral_radius(P), 1.00001)

if __name__ == '__main__':
    unittest.main()
