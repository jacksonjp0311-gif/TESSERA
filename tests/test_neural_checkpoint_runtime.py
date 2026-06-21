from __future__ import annotations

import tempfile
import time
import unittest

import numpy as np

from tessera.plugin import (
    CheckpointStore,
    PluginSupervisor,
    ReplayGate,
    train_neural_checkpoint,
)
from tessera.plugin.contracts import AgentEvent
from tessera.plugin.trajectory import vectorize_events


def _events(count=60):
    return [
        AgentEvent(
            event_id=f"neural-{index}",
            kind="test_result",
            timestamp=1000.0 + index,
            features={
                "duration_ms": 10.0 + index,
                "token_count": 20.0 + 2 * index,
                "tests_failed": 0.0,
            },
        )
        for index in range(count)
    ]


class TestNeuralCheckpointRuntime(unittest.TestCase):
    def test_real_checkpoint_trains_admits_and_serves(self):
        events = _events()
        payload, metrics = train_neural_checkpoint(vectorize_events(events))
        self.assertEqual(payload["kind"], "tessera-neural-checkpoint")
        with tempfile.TemporaryDirectory() as directory:
            store = CheckpointStore(directory)
            candidate = store.write_candidate(
                payload=payload,
                lineage={"test": "neural"},
                metrics=metrics,
            )
            gate = ReplayGate(
                baseline_loss=metrics["baseline_loss"],
                candidate_loss=metrics["candidate_loss"],
                replay_pass_rate=metrics["replay_pass_rate"],
            )
            self.assertTrue(store.admit(candidate["candidate_id"], gate)["admitted"])
            supervisor = PluginSupervisor(plugin_options={
                "neural_min_events": 8,
                "checkpoint_payload": payload,
            })
            supervisor.warmup()
            supervisor.observe(events[:12])
            result = supervisor.infer()
            supervisor.unload()
            self.assertEqual(result.status, "ok")
            self.assertEqual(
                result.packet.status,
                "admitted_neural_checkpoint",
            )
            self.assertLess(result.latency_ms, 250.0)

    def test_checkpoint_model_changes_neural_awareness(self):
        events = _events()
        matrix = vectorize_events(events)
        payload, metrics = train_neural_checkpoint(matrix)
        self.assertTrue(np.isfinite(metrics["neural_awareness_loss"]))
        self.assertIn("model_state_base64", payload)


if __name__ == "__main__":
    unittest.main()
