from __future__ import annotations

import unittest

from tessera import __version__
from tessera.experiments.release_readiness import run_release_readiness
from tessera.plugin.contracts import PluginManifest


class TestReleaseReadiness(unittest.TestCase):
    def test_version_surfaces_match(self):
        self.assertEqual(__version__, "0.3.2")
        self.assertEqual(PluginManifest().version, __version__)

    def test_release_wheel_is_reproducibly_installable(self):
        result = run_release_readiness()
        self.assertTrue(result["passed"], result)
        self.assertTrue(result["checks"]["wheel_record_integrity_passed"])
        self.assertTrue(
            result["checks"]["isolated_import_and_inference_passed"]
        )


if __name__ == "__main__":
    unittest.main()
