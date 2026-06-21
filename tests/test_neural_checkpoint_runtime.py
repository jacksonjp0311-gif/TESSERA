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
    TesseraPlugin,
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

    def test_identical_checkpoint_query_reuses_exact_packet(self):
        events = _events()
        payload, _ = train_neural_checkpoint(vectorize_events(events))
        plugin = TesseraPlugin(
            neural_min_events=8,
            checkpoint_payload=payload,
        )
        plugin.observe(events[:20])
        first = plugin.infer()
        first_key = plugin._checkpoint_cache_key
        second = plugin.infer()
        self.assertEqual(first, second)
        self.assertEqual(first_key, plugin._checkpoint_cache_key)
        plugin.observe([events[20]])
        third = plugin.infer()
        self.assertNotEqual(first_key, plugin._checkpoint_cache_key)
        self.assertEqual(third.status, "admitted_neural_checkpoint")
        self.assertEqual(plugin._checkpoint_cache_mode, "prefix_extended")

    def test_changed_prefix_packet_matches_full_replay_exactly(self):
        events = _events()
        payload, _ = train_neural_checkpoint(vectorize_events(events))
        incremental = TesseraPlugin(
            neural_min_events=8,
            checkpoint_payload=payload,
        )
        incremental.observe(events[:20])
        incremental.infer()
        incremental.observe([events[20]])
        continued = incremental.infer()

        replay = TesseraPlugin(
            neural_min_events=8,
            checkpoint_payload=payload,
        )
        replay.observe(events[:21])
        expected = replay.infer()
        self.assertEqual(continued, expected)
        self.assertEqual(
            incremental._checkpoint_cache_rows,
            replay._checkpoint_cache_rows,
        )

    def test_prefix_mismatch_falls_back_to_full_replay(self):
        events = _events()
        payload, _ = train_neural_checkpoint(vectorize_events(events))
        plugin = TesseraPlugin(
            neural_min_events=8,
            checkpoint_payload=payload,
        )
        plugin.observe(events[:20])
        plugin.infer()
        changed = list(events[:21])
        changed[5] = AgentEvent(
            event_id="changed-prefix",
            kind="test_result",
            timestamp=changed[5].timestamp,
            features={"duration_ms": 999.0},
        )
        plugin.replace_events(changed)
        plugin.infer()
        self.assertEqual(plugin._checkpoint_cache_mode, "full_replay")

    def test_state_capsule_restores_exact_prefix(self):
        events = _events()
        payload, _ = train_neural_checkpoint(vectorize_events(events))
        source = TesseraPlugin(
            neural_min_events=8,
            checkpoint_payload=payload,
        )
        source.observe(events[:20])
        source.infer()
        capsule = source.export_state_capsule()
        restored = TesseraPlugin(
            neural_min_events=8,
            checkpoint_payload=payload,
            state_capsule=capsule,
        )
        restored.observe(events[:21])
        packet = restored.infer()
        self.assertEqual(restored._checkpoint_cache_mode, "prefix_extended")
        self.assertEqual(packet.status, "admitted_neural_checkpoint")


if __name__ == "__main__":
    unittest.main()
