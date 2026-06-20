from __future__ import annotations

import time
import unittest

from tessera.plugin import TesseraPlugin
from tessera.plugin.contracts import AgentEvent, ReplayPacket


class TestTesseraPlugin(unittest.TestCase):
    def make_events(self, count=8):
        return [
            AgentEvent(
                event_id=f"e-{index}",
                kind="test_result",
                timestamp=time.time() + index,
                features={
                    "duration_ms": 100.0 + index,
                    "token_count": 200.0 + index * 2,
                    "tests_failed": float(index == count - 1),
                },
            )
            for index in range(count)
        ]

    def test_permissions_are_write_denied_by_default(self):
        permissions = TesseraPlugin().describe().permissions
        self.assertFalse(permissions.host_memory_write)
        self.assertFalse(permissions.tool_invocation)
        self.assertFalse(permissions.prompt_mutation)
        self.assertFalse(permissions.live_codec_replacement)
        self.assertFalse(permissions.topology_mutation)
        self.assertFalse(permissions.external_api_calls)

    def test_sensitive_events_are_rejected(self):
        plugin = TesseraPlugin()
        event = AgentEvent(
            event_id="secret",
            kind="tool_result",
            timestamp=time.time(),
            features={},
            contains_sensitive_data=True,
        )
        receipt = plugin.observe([event])
        self.assertEqual(receipt.accepted, 0)
        self.assertEqual(receipt.rejected, 1)

    def test_inference_proposals_and_replay_remain_host_gated(self):
        plugin = TesseraPlugin()
        plugin.observe(self.make_events())
        packet = plugin.infer()
        self.assertEqual(packet.status, "neural")
        self.assertNotEqual(packet.selected_prediction_expert, "not_selected")
        self.assertEqual(
            plugin.checkpoint()["selected_prediction_expert"],
            packet.selected_prediction_expert,
        )
        self.assertTrue(plugin.propose_memory().requires_host_authorization)
        repair = plugin.propose_repair()
        self.assertTrue(repair.shadow_only)
        self.assertTrue(repair.requires_host_authorization)
        certificate = plugin.replay(ReplayPacket(expected_max_prediction_loss=1e9))
        self.assertTrue(certificate.passed)
        self.assertFalse(certificate.memory_promotion_authorized)
        self.assertFalse(certificate.live_repair_authorized)


if __name__ == "__main__":
    unittest.main()
