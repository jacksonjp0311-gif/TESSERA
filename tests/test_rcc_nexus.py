import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TestRCCNexus(unittest.TestCase):
    def test_route_map_exists_and_targets_exist(self):
        route = json.loads((ROOT / 'rcc/nexus/route_map.json').read_text(encoding='utf-8'))
        self.assertEqual(route['repository'], 'Tessera')
        self.assertIn('navigation_is_not_validation', route['non_claim_locks'])
        for item in route['routes']:
            self.assertTrue((ROOT / item['path']).exists(), item)

    def test_context_indexes_exist(self):
        self.assertTrue((ROOT / 'docs/context/repository_context_index.json').exists())
        self.assertTrue((ROOT / 'docs/context/rcc_nexus_index.json').exists())

if __name__ == '__main__':
    unittest.main()
