from __future__ import annotations

import unittest

from tessera.experiments.production_candidate import (
    run_production_candidate,
)
from tessera.plugin.contracts import AgentEvent
from tessera.plugin.host_adapters import (
    AgentEventSessionAdapter,
    JsonSessionAdapter,
    SessionSummaryContract,
    full_session_summary,
)


class TestProductionCandidate(unittest.TestCase):
    def test_reference_adapters_preserve_session_semantics(self):
        events = [
            AgentEvent(
                event_id=f"e-{index}",
                kind="test_result",
                timestamp=float(index),
                features={
                    "duration_ms": float(index + 1),
                    "tests_failed": float(index % 2),
                },
            )
            for index in range(3)
        ]
        full = full_session_summary(events)
        contract = SessionSummaryContract((0, 28, 56))
        direct = AgentEventSessionAdapter(contract).adapt("a", events)
        encoded = JsonSessionAdapter.serialize(events)
        decoded = JsonSessionAdapter(contract).adapt("a", encoded)
        expected = full[list(contract.selected_indices)].tolist()
        self.assertEqual(
            [direct.features[name] for name in contract.feature_names],
            expected,
        )
        self.assertEqual(direct.features, decoded.features)

    def test_evo034_local_production_candidate_gate(self):
        result = run_production_candidate()
        self.assertTrue(result["passed"])
        self.assertEqual(result["metrics"]["route_parity_rate"], 1.0)
        self.assertTrue(result["checks"]["restart_is_deterministic"])
        self.assertTrue(result["checks"]["checkpoint_rollback_passed"])


if __name__ == "__main__":
    unittest.main()
