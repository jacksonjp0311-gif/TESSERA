from __future__ import annotations

import unittest

from tessera.experiments.runtime_uncertainty_readiness import (
    run_runtime_uncertainty_readiness,
)
from tessera.plugin.contracts import InferencePacket


class TestRuntimeUncertainty(unittest.TestCase):
    def test_packet_defaults_remain_backward_compatible(self):
        packet = InferencePacket(
            status="test",
            anomaly_score=0.0,
            prediction_loss=0.0,
            warning=False,
            memory_candidate=False,
            claim_boundary="test",
        )
        self.assertEqual(packet.trust_route, "not_routed")
        self.assertFalse(packet.abstained)
        self.assertEqual(packet.uncertainty_score, 0.0)

    def test_runtime_router_is_explicit_and_fail_closed(self):
        result = run_runtime_uncertainty_readiness()
        self.assertTrue(result["passed"])
        self.assertTrue(result["checks"]["host_route_is_explicit"])
        self.assertTrue(
            result["checks"]["abstention_blocks_memory_candidate"]
        )
        self.assertTrue(result["checks"]["both_routes_observed"])
        self.assertTrue(result["checks"]["warm_latency_gate_passed"])
        self.assertFalse(result["semantic_transfer_validated"])


if __name__ == "__main__":
    unittest.main()
