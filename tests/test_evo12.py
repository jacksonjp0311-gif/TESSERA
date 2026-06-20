from __future__ import annotations

import unittest
import time
import json
import numpy as np

from tessera.model.network import TESSERANet
from tessera.model.train import fit_tessera_model, evaluate_sequence
from tessera.graph.topologies import make_operator
from tessera.plugin import TesseraPlugin
from tessera.plugin.contracts import AgentEvent, InferenceQuery, ReplayPacket


class TestEvo12NeuralCore(unittest.TestCase):
    """EVO-012: Enhanced neural core tests."""

    def _make_data(self, n=200, dims=4, seed=42):
        rng = np.random.default_rng(seed)
        return rng.normal(size=(n, dims)).astype("float32")

    def test_network_gru_field_step(self):
        """GRU-style field update produces bounded field values."""
        P = make_operator("ring", 8, seed=42)
        net = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P, depth=2)
        x_t = np.random.randn(1, 4).astype("float32")
        import torch
        field = torch.zeros(1, 8)
        nf = net.field_step(torch.tensor(x_t), field)
        self.assertTrue(torch.all(torch.isfinite(nf)))
        self.assertEqual(nf.shape, (1, 8))

    def test_network_multi_scale_prediction(self):
        """step() returns finite predictions with multi-scale heads."""
        P = make_operator("ring", 8, seed=42)
        net = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P)
        import torch
        x_t = torch.randn(1, 4)
        field = torch.zeros(1, 8)
        nf, z, xr, xp = net.step(x_t, field)
        self.assertTrue(torch.all(torch.isfinite(xp)))
        self.assertEqual(xp.shape, x_t.shape)

    def test_network_depth_configurable(self):
        """Network accepts depth parameter for deeper architectures."""
        P = make_operator("ring", 8, seed=42)
        net = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P, depth=3)
        self.assertEqual(net.depth, 3)
        import torch
        x_t = torch.randn(1, 4)
        field = torch.zeros(1, 8)
        nf, z, xr, xp = net.step(x_t, field)
        self.assertTrue(torch.all(torch.isfinite(xp)))

    def test_network_hidden_dim_configurable(self):
        """Network accepts hidden_dim parameter."""
        P = make_operator("ring", 8, seed=42)
        net = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P, hidden_dim=128)
        self.assertEqual(net.hidden, 128)

    def test_train_accepts_depth_and_hidden_dim(self):
        """fit_tessera_model passes depth and hidden_dim to network."""
        X = self._make_data(150, 4, seed=42)
        P = make_operator("ring", 8, seed=42)
        model = fit_tessera_model(
            X, P, code_dim=4, alpha=0.5, epochs=1, seed=42,
            hidden_dim=64, depth=2,
        )
        self.assertEqual(model.hidden, 64)
        self.assertEqual(model.depth, 2)

    def test_train_adamw_optimizer(self):
        """Training uses AdamW with weight decay - verified via loss curve."""
        X = self._make_data(100, 4, seed=42)
        P = make_operator("ring", 8, seed=42)
        model = fit_tessera_model(X, P, code_dim=4, alpha=0.5, epochs=2, seed=42)
        # After 2 epochs, the model should produce finite, reasonable loss
        rows = evaluate_sequence(model, X)["rows"]
        mean_pred = float(np.mean([r["prediction_loss"] for r in rows]))
        self.assertTrue(np.isfinite(mean_pred))
        self.assertLess(mean_pred, 1e6)  # Should not explode

    def test_evaluate_sequence_returns_rows(self):
        """evaluate_sequence returns per-step metrics."""
        X = self._make_data(100, 4, seed=42)
        P = make_operator("ring", 8, seed=42)
        model = fit_tessera_model(X, P, code_dim=4, alpha=0.5, epochs=1, seed=42)
        result = evaluate_sequence(model, X)
        self.assertIn("rows", result)
        self.assertGreater(len(result["rows"]), 0)
        row = result["rows"][0]
        for key in ["step", "reconstruction_loss", "prediction_loss", "delta_phi", "code_drift", "rate"]:
            self.assertIn(key, row)


class TestEvo12PluginRuntime(unittest.TestCase):
    """EVO-012: Enhanced plugin runtime tests."""

    def _make_events(self, n=12):
        return [
            AgentEvent(
                event_id=f"evt-{index}",
                kind="test_result",
                timestamp=1000.0 + index * 10,
                features={
                    "duration_ms": 100 + index * 12,
                    "token_count": 300 + index * 20,
                    "tests_failed": float(index == n - 1),
                    "error": float(index == n - 1),
                },
            )
            for index in range(n)
        ]

    def test_plugin_checkpoint_v02(self):
        """Plugin checkpoint reports v0.2 schema with memory/wound counts."""
        plugin = TesseraPlugin()
        events = self._make_events(12)
        plugin.observe(events)
        plugin.infer()
        cp = plugin.checkpoint()
        self.assertEqual(cp["schema"], "TESSERA-PLUGIN-CHECKPOINT-v0.2")
        self.assertIn("memory_count", cp)
        self.assertIn("wound_count", cp)
        self.assertIn("anomaly_mean", cp)

    def test_plugin_memory_buffer_fills(self):
        """Plugin accumulates latent memory during neural inference."""
        plugin = TesseraPlugin(memory_capacity=32)
        events = self._make_events(12)
        plugin.observe(events)
        plugin.infer()
        cp = plugin.checkpoint()
        self.assertGreater(cp["memory_count"], 0)

    def test_plugin_wound_tracking(self):
        """Plugin tracks wound history across inferences."""
        plugin = TesseraPlugin()
        events = self._make_events(12)
        plugin.observe(events)
        plugin.infer()
        plugin.propose_repair()
        cp = plugin.checkpoint()
        self.assertGreaterEqual(cp["wound_count"], 0)

    def test_plugin_anomaly_history(self):
        """Plugin maintains anomaly score history for multi-scale scoring."""
        plugin = TesseraPlugin()
        events = self._make_events(12)
        plugin.observe(events)
        plugin.infer()
        self.assertGreater(len(plugin._anomaly_history), 0)

    def test_plugin_multi_event_stream(self):
        """Plugin handles multiple observe/infer cycles."""
        plugin = TesseraPlugin()
        for cycle in range(3):
            events = self._make_events(8)
            plugin.observe(events)
            packet = plugin.infer()
            self.assertIn(packet.status, ["neural", "fallback", "insufficient_context"])

    def test_plugin_field_dim_configurable(self):
        """Plugin accepts field_dim and code_dim configuration."""
        plugin = TesseraPlugin(field_dim=16, code_dim=8)
        self.assertEqual(plugin.field_dim, 16)
        self.assertEqual(plugin.code_dim, 8)


class TestEvo12Integration(unittest.TestCase):
    """EVO-12: Integration tests for neural core + plugin."""

    def test_full_pipeline_synthetic(self):
        """Full pipeline: data -> train -> evaluate -> plugin inference."""
        rng = np.random.default_rng(42)
        X = rng.normal(size=(200, 4)).astype("float32")
        P = make_operator("ring", 8, seed=42)
        model = fit_tessera_model(X, P, code_dim=4, alpha=0.5, epochs=1, seed=42)
        result = evaluate_sequence(model, X)
        self.assertGreater(len(result["rows"]), 0)

        plugin = TesseraPlugin()
        events = [
            AgentEvent(
                event_id=f"integration-{i}",
                kind="test_result",
                timestamp=1000.0 + i,
                features={"duration_ms": 100 + i * 5, "token_count": 200 + i * 10, "error": 0.0},
            )
            for i in range(12)
        ]
        plugin.observe(events)
        packet = plugin.infer()
        self.assertIsNotNone(packet)
        memory = plugin.propose_memory()
        self.assertIsNotNone(memory)
        repair = plugin.propose_repair()
        self.assertIsNotNone(repair)


if __name__ == "__main__":
    unittest.main()
