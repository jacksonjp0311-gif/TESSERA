from __future__ import annotations

import unittest
from pathlib import Path

from tessera.rhp.core import (
    build_version_summary,
    build_zero_context_packet,
    ordered_sequence_report,
    validate_repository,
)


ROOT = Path(__file__).resolve().parents[1]


class TestRhpNexus(unittest.TestCase):
    def test_repository_contract_is_coherent(self):
        report = validate_repository(ROOT)
        self.assertTrue(report["passed"], report)
        self.assertGreaterEqual(report["sections"]["lessons"]["lesson_count"], 13)
        self.assertGreaterEqual(report["sections"]["nexus"]["surface_count"], 18)
        self.assertTrue(report["sections"]["route_echoes"]["ok"])
        self.assertTrue(report["sections"]["hygiene"]["ok"])

    def test_zero_context_packet_keeps_authority_locked(self):
        packet = build_zero_context_packet(ROOT)
        self.assertTrue(packet["ok"], packet)
        self.assertEqual(packet["authority_failures"], [])
        for name, value in packet["authority_locks"].items():
            if name != "external_ingestion":
                self.assertFalse(value)

    def test_sequence_validation_preserves_duplicates(self):
        expected = ["RHPREADY", "LINEAGE", "RHPREADY"]
        self.assertTrue(ordered_sequence_report(expected, expected)["ok"])
        collapsed = ["RHPREADY", "LINEAGE"]
        self.assertFalse(ordered_sequence_report(expected, collapsed)["ok"])

    def test_version_summary_exposes_required_handoff_fields(self):
        summary = build_version_summary(ROOT)
        for field in (
            "version",
            "what_changed",
            "what_we_found",
            "what_remains_bounded",
            "next_best_move",
        ):
            self.assertIn(field, summary)


if __name__ == "__main__":
    unittest.main()
