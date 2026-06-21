from __future__ import annotations

import json
import unittest
from pathlib import Path

from tessera.plugin.host_integrations import (
    AgentCliMirrorIntegration,
    HermesStreamIntegration,
)


class TestHostIntegrations(unittest.TestCase):
    def fixture(self, name: str):
        return json.loads(
            Path(
                f"tests/fixtures/host_integrations/{name}.json"
            ).read_text(encoding="utf-8")
        )

    def test_agent_cli_payload_is_not_retained(self):
        session = AgentCliMirrorIntegration().adapt(
            self.fixture("agent_cli_session")
        )
        rendered = repr(session.events)
        self.assertNotIn("must not cross adapter", rendered)
        self.assertNotIn("C:\\private", rendered)
        self.assertTrue(session.terminal_ok)

    def test_hermes_payload_is_not_retained(self):
        session = HermesStreamIntegration().adapt(
            "fixture",
            self.fixture("hermes_session"),
        )
        rendered = repr(session.events)
        self.assertNotIn("must not cross adapter", rendered)
        self.assertNotIn("terminal", rendered)
        self.assertTrue(session.terminal_ok)

    def test_malformed_records_fail_closed(self):
        agent = AgentCliMirrorIntegration().adapt([{"bad": True}])
        hermes = HermesStreamIntegration().adapt(
            "bad",
            [{"type": "message_chunk", "text": "private"}],
        )
        self.assertEqual(agent.rejected_records, 1)
        self.assertEqual(hermes.rejected_records, 1)
        self.assertEqual(agent.events, ())
        self.assertEqual(hermes.events, ())


if __name__ == "__main__":
    unittest.main()
