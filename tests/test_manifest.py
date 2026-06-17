import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from tessera.data.manifest import make_manifest
from tessera.data.leakage_guard import validate_manifest

class TestManifest(unittest.TestCase):
    def test_manifest_valid(self):
        m = make_manifest('x', 10, 3).to_dict()
        ok, reasons = validate_manifest(m)
        self.assertTrue(ok, reasons)
        self.assertIn('manifest_hash', m)

if __name__ == '__main__':
    unittest.main()
