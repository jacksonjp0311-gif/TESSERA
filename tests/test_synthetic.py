import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from tessera.data.synthetic import generate_synthetic_telemetry

class TestSynthetic(unittest.TestCase):
    def test_has_labels(self):
        df, labels = generate_synthetic_telemetry(steps=300, channels=4)
        self.assertEqual(len(df), 300)
        self.assertGreater(labels.sum(), 0)
        self.assertIn('label', df.columns)

if __name__ == '__main__':
    unittest.main()
