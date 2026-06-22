from __future__ import annotations

import time
import unittest

from tessera.plugin import PluginSupervisor
from tessera.plugin.contracts import AgentEvent, RuntimeBudget


def _crash_worker(events, plugin_options, output_queue):
    raise RuntimeError("simulated worker crash")


def _hang_worker(events, plugin_options, output_queue):
    time.sleep(5)


class TestPluginSupervisor(unittest.TestCase):
    def event(self, **overrides):
        values = {
            "event_id": "event-1",
            "kind": "test_result",
            "timestamp": 1000.0,
            "features": {"duration_ms": 10.0},
        }
        values.update(overrides)
        return AgentEvent(**values)

    def test_invalid_events_fail_closed_before_worker(self):
        supervisor = PluginSupervisor()
        receipt = supervisor.observe([
            self.event(features={"duration_ms": float("nan")}),
            self.event(
                event_id="sensitive",
                contains_sensitive_data=True,
            ),
        ])
        self.assertEqual(receipt.accepted, 0)
        self.assertEqual(receipt.rejected, 2)
        self.assertEqual(receipt.buffer_size, 0)

    def test_worker_crash_is_contained_and_opens_circuit(self):
        supervisor = PluginSupervisor(
            budget=RuntimeBudget(
                timeout_ms=1000,
                max_consecutive_failures=2,
            ),
            process_target=_crash_worker,
        )
        first = supervisor.infer()
        second = supervisor.infer()
        third = supervisor.infer()
        self.assertEqual(first.status, "contained_failure")
        self.assertEqual(second.status, "contained_failure")
        self.assertEqual(third.status, "unavailable")
        self.assertEqual(third.error_code, "circuit_open")
        self.assertTrue(supervisor.health().circuit_open)
        self.assertTrue(supervisor.reset_circuit())
        self.assertFalse(supervisor.health().circuit_open)

    def test_hard_timeout_terminates_worker(self):
        supervisor = PluginSupervisor(
            budget=RuntimeBudget(timeout_ms=50),
            process_target=_hang_worker,
        )
        result = supervisor.infer()
        self.assertEqual(result.status, "contained_failure")
        self.assertEqual(result.error_code, "hard_timeout")
        self.assertTrue(result.host_contained)
        self.assertEqual(supervisor.health().timed_out_requests, 1)

    def test_unload_clears_state_and_fails_closed(self):
        supervisor = PluginSupervisor()
        receipt = supervisor.observe([self.event()])
        self.assertEqual(receipt.accepted, 1)
        supervisor.unload()
        result = supervisor.infer()
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.error_code, "runtime_unloaded")
        self.assertEqual(supervisor.health().status, "unloaded")
        rejected = supervisor.observe([self.event(event_id="later")])
        self.assertEqual(rejected.accepted, 0)

    def test_manifest_declares_enforced_runtime_boundary(self):
        from tessera.plugin import TesseraPlugin

        manifest = TesseraPlugin().describe()
        self.assertEqual(manifest.schema, "TESSERA-PLUGIN-MANIFEST-v0.3")
        self.assertEqual(manifest.version, "0.4.1")
        self.assertTrue(manifest.supports_host_observability_gate)
        self.assertTrue(manifest.supports_manifold_drift_gate)
        self.assertTrue(manifest.supports_sequential_geometry_gate)
        self.assertTrue(manifest.supports_exact_prefix_state)
        self.assertTrue(manifest.supports_integrity_bound_restart_state)
        self.assertEqual(
            manifest.session_summary_schema,
            "TESSERA-SESSION-SUMMARY-v0.1",
        )
        self.assertEqual(
            manifest.execution_model,
            "host-supervised-local-subprocess",
        )
        self.assertTrue(manifest.supports_hard_timeout)
        self.assertTrue(manifest.supports_unload)

    def test_supervisor_disables_inline_training_by_default(self):
        supervisor = PluginSupervisor()
        self.assertEqual(supervisor.health().status, "starting")
        events = [
            self.event(
                event_id=f"event-{index}",
                timestamp=1000.0 + index,
            )
            for index in range(8)
        ]
        supervisor.observe(events)
        result = supervisor.infer()
        supervisor.unload()
        self.assertEqual(result.status, "ok")
        self.assertEqual(supervisor.health().status, "unloaded")
        self.assertEqual(
            result.packet.status,
            "fast_path_shadow_training_required",
        )

    def test_warmup_transitions_health_to_ready(self):
        supervisor = PluginSupervisor(
            budget=RuntimeBudget(worker_cpu_threads=1)
        )
        self.assertEqual(supervisor.budget.worker_cpu_threads, 1)
        self.assertEqual(supervisor.health().status, "starting")
        result = supervisor.warmup()
        self.assertEqual(result.status, "ok")
        self.assertEqual(supervisor.health().status, "ready")
        supervisor.unload()

    def test_direct_plugin_keeps_research_neural_path(self):
        from tessera.plugin import TesseraPlugin

        plugin = TesseraPlugin(neural_min_events=100)
        self.assertTrue(plugin.inline_neural_training)
        self.assertFalse(plugin.checkpoint()["shadow_training_required"])


if __name__ == "__main__":
    unittest.main()
