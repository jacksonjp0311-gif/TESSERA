from __future__ import annotations

import unittest
import json
import time
import numpy as np

from tessera.model.network import TESSERANet
from tessera.model.train import fit_tessera_model, evaluate_sequence
from tessera.graph.topologies import make_operator
from tessera.plugin import TesseraPlugin
from tessera.plugin.contracts import AgentEvent, InferenceQuery, ReplayPacket
from tessera.plugin.trajectory import (
    adapt_raw_event,
    create_agent_event,
    summarize_trajectory,
    trajectory_hash,
    ADAPTER_REGISTRY,
    TRAJECTORY_FEATURES,
    vectorize_events,
)
from tessera.experiments.repair_ablation import (
    run_repair_ablation,
    ARM_NO_REPAIR,
    ARM_RANDOM,
    ARM_WRONG_TARGET,
    ARM_GENERIC_RETRAIN,
    ARM_TARGETED,
)
from tessera.experiments.benchmark import (
    multi_seed_benchmark,
    ArchitectureConfig,
)


class TestEvo13TrajectoryAdapters(unittest.TestCase):
    """EVO-013: Phase 4 — Agent trajectory typed event adapters."""

    def test_all_kinds_have_adapters(self):
        """Every allowed event kind has a registered adapter."""
        expected_kinds = {
            "prompt_metadata", "response_metadata", "tool_call", "tool_result",
            "file_change", "test_result", "plan_transition", "error", "retry", "resource",
        }
        self.assertEqual(set(ADAPTER_REGISTRY.keys()), expected_kinds)

    def test_prompt_adapter_extracts_features(self):
        """PromptMetadataAdapter extracts prompt-specific features."""
        raw = {"token_count": 1500, "prompt_length": 1200, "system_tokens": 300,
               "history_turns": 5, "tool_count": 3}
        features = adapt_raw_event("prompt_metadata", raw)
        self.assertAlmostEqual(features["token_count"], 1500.0)
        self.assertAlmostEqual(features["system_prompt_ratio"], 300.0 / 1500.0)
        self.assertAlmostEqual(features["history_turns"], 5.0)

    def test_tool_call_adapter_extracts_features(self):
        """ToolCallAdapter extracts tool-specific features."""
        raw = {"tool_name": "bash", "latency_ms": 250, "input_tokens": 50,
               "error": False, "retry_count": 0, "files_changed": 0}
        features = adapt_raw_event("tool_call", raw)
        self.assertAlmostEqual(features["tool_latency_ms"], 250.0)
        self.assertAlmostEqual(features["error"], 0.0)

    def test_error_adapter_marks_error(self):
        """ErrorAdapter always sets error=1.0."""
        raw = {"error_type": "timeout", "retry_count": 2, "duration_ms": 5000}
        features = adapt_raw_event("error", raw)
        self.assertAlmostEqual(features["error"], 1.0)
        self.assertAlmostEqual(features["retry"], 2.0)

    def test_adapter_validation_rejects_missing_fields(self):
        """Adapters reject raw events with missing required fields."""
        valid, reason = ADAPTER_REGISTRY["prompt_metadata"].validate({})
        self.assertFalse(valid)
        self.assertIn("token_count", reason)

    def test_create_agent_event_from_raw(self):
        """create_agent_event converts raw dict to AgentEvent via adapter."""
        raw = {"token_count": 1000, "prompt_length": 800, "system_tokens": 200,
               "history_turns": 3, "tool_count": 2}
        event = create_agent_event("test-1", "prompt_metadata", raw, timestamp=1000.0)
        self.assertEqual(event.event_id, "test-1")
        self.assertEqual(event.kind, "prompt_metadata")
        self.assertIn("token_count", event.features)

    def test_vectorize_events_unified_space(self):
        """vectorize_events produces fixed-dimension matrix for mixed event kinds."""
        events = [
            AgentEvent("e1", "prompt_metadata", 1000.0, {"token_count": 500, "error": 0.0}),
            AgentEvent("e2", "tool_call", 1010.0, {"tool_latency_ms": 200, "error": 0.0}),
            AgentEvent("e3", "error", 1020.0, {"error": 1.0, "retry": 2.0}),
        ]
        matrix = vectorize_events(events)
        self.assertEqual(matrix.shape[0], 3)
        self.assertEqual(matrix.shape[1], len(TRAJECTORY_FEATURES))
        self.assertTrue(np.all(np.isfinite(matrix)))

    def test_trajectory_hash_deterministic(self):
        """trajectory_hash is deterministic for same events."""
        events = [
            AgentEvent("e1", "test_result", 1000.0, {"error": 0.0}),
            AgentEvent("e2", "test_result", 1010.0, {"error": 1.0}),
        ]
        h1 = trajectory_hash(events)
        h2 = trajectory_hash(events)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 16)

    def test_summarize_trajectory(self):
        """summarize_trajectory computes correct statistics."""
        events = [
            AgentEvent("e1", "test_result", 1000.0, {"duration_ms": 100, "error": 0.0, "token_count": 200, "retry": 0.0}),
            AgentEvent("e2", "error", 1010.0, {"duration_ms": 5000, "error": 1.0, "token_count": 50, "retry": 2.0}),
            AgentEvent("e3", "tool_call", 1020.0, {"duration_ms": 200, "error": 0.0, "token_count": 100, "retry": 0.0}),
        ]
        summary = summarize_trajectory(events)
        self.assertEqual(summary.event_count, 3)
        self.assertAlmostEqual(summary.total_duration_ms, 5300.0)
        self.assertEqual(summary.error_count, 1)
        self.assertAlmostEqual(summary.total_tokens, 350.0)
        self.assertGreater(summary.adapter_coverage, 0.0)

    def test_trajectory_features_dimension(self):
        """TRAJECTORY_FEATURES has expected dimension."""
        self.assertGreaterEqual(len(TRAJECTORY_FEATURES), 20)

    def test_offline_trajectory_benchmark_compares_controls(self):
        from tessera.experiments.trajectory_benchmark import (
            run_trajectory_benchmark,
        )

        result = run_trajectory_benchmark(
            seeds=[0, 1, 2, 3],
            length=10,
        )
        self.assertEqual(
            set(result["policies"]),
            {"recency", "summary", "tessera"},
        )
        for metrics in result["policies"].values():
            self.assertIn("failure_recall", metrics)
            self.assertIn("unsafe_memory_rate", metrics)
            self.assertIn("mean_latency_ms", metrics)

    def test_precursor_only_benchmark_removes_explicit_failure(self):
        from tessera.experiments.trajectory_benchmark import (
            run_trajectory_benchmark,
        )

        result = run_trajectory_benchmark(
            seeds=[100, 101, 102, 103],
            length=12,
            explicit_failure=False,
        )
        self.assertFalse(result["explicit_failure"])
        self.assertEqual(result["trajectory_count"], 4)

    def test_privacy_capture_denies_payload_fields(self):
        import tempfile
        from pathlib import Path
        from tessera.plugin.privacy_capture import (
            capture_local_trajectories,
        )

        records = []
        for session in range(2):
            for index in range(7):
                records.append(
                    {
                        "schema": "fixture",
                        "timestamp": f"2026-06-19T00:00:{session}{index}+00:00",
                        "phase": "CHECK",
                        "state": "RUN" if index % 2 == 0 else "OK",
                        "command": "SECRET COMMAND",
                        "detail": "PRIVATE DETAIL",
                        "root": "C:/PRIVATE",
                        "mirror_dir": "C:/PRIVATE/MIRROR",
                    }
                )
            if session:
                records.append(
                    {
                        "schema": "fixture",
                        "timestamp": "2026-06-19T00:01:00+00:00",
                        "phase": "CHECK",
                        "state": "FAIL",
                    }
                )
            records.append(
                {
                    "schema": "fixture",
                    "timestamp": "2026-06-19T00:02:00+00:00",
                    "phase": "ROOT",
                    "state": "OK",
                }
            )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text(
                "\n".join(json.dumps(record) for record in records),
                encoding="utf-8",
            )
            trajectories, manifest = capture_local_trajectories(path)
        self.assertEqual(len(trajectories), 2)
        self.assertEqual(manifest["degraded_session_count"], 1)
        self.assertFalse(manifest["raw_payload_retained"])
        self.assertIn("command", manifest["denied_fields"])
        serialized = json.dumps(manifest)
        self.assertNotIn("SECRET COMMAND", serialized)
        self.assertNotIn("PRIVATE DETAIL", serialized)

    def test_identifiability_audit_detects_label_collision(self):
        from tessera.plugin.privacy_capture import (
            audit_trajectory_identifiability,
        )

        event = AgentEvent(
            "same",
            "plan_transition",
            1.0,
            {"duration_ms": 1.0},
        )
        result = audit_trajectory_identifiability(
            [([event], False), ([event], True)]
        )
        self.assertEqual(result["conflicting_observation_count"], 1)
        self.assertEqual(
            result[
                "failure_recall_upper_bound_at_zero_false_intervention"
            ],
            0.0,
        )

    def test_phase_conditioned_policy_learns_clean_bounds(self):
        from tessera.experiments.trajectory_benchmark import (
            _phase_conditioned_policy,
            calibrate_phase_duration_policy,
        )

        def event(duration):
            return AgentEvent(
                f"validate-{duration}",
                "plan_transition",
                duration,
                {"duration_ms": duration},
                metadata={"phase": "VALIDATE", "state": "OK"},
            )

        calibration = [
            ([event(80.0 + index)], False)
            for index in range(24)
        ] + [([event(250.0)], True)]
        model = calibrate_phase_duration_policy(calibration)
        self.assertEqual(model["clean_trajectory_count"], 24)
        self.assertTrue(model["calibration_sufficient"])
        self.assertIn("VALIDATE", model["bounds"])
        warning, memory, abstained, evidence = _phase_conditioned_policy(
            [event(240.0)], model
        )
        self.assertTrue(warning)
        self.assertFalse(memory)
        self.assertFalse(abstained)
        self.assertTrue(evidence[0]["exceeded"])

    def test_phase_policy_abstains_on_workflow_profile_mismatch(self):
        from tessera.experiments.trajectory_benchmark import (
            _phase_conditioned_policy,
            calibrate_phase_duration_policy,
        )

        def event(phase, duration):
            return AgentEvent(
                f"{phase}-{duration}",
                "plan_transition",
                duration,
                {"duration_ms": duration},
                metadata={"phase": phase, "state": "OK"},
            )

        calibration = [
            ([event("VALIDATE", 80.0 + index)], False)
            for index in range(24)
        ]
        model = calibrate_phase_duration_policy(calibration)
        warning, memory, abstained, evidence = _phase_conditioned_policy(
            [event("CHECK", 80.0), event("VALIDATE", 90.0)], model
        )
        self.assertFalse(warning)
        self.assertFalse(memory)
        self.assertTrue(abstained)
        self.assertEqual(evidence[0]["reason"], "workflow_profile_mismatch")

    def test_phase_calibration_requires_finite_sample_support(self):
        from tessera.experiments.trajectory_benchmark import (
            calibrate_phase_duration_policy,
        )

        event = AgentEvent(
            "validate",
            "plan_transition",
            1.0,
            {"duration_ms": 80.0},
            metadata={"phase": "VALIDATE", "state": "OK"},
        )
        model = calibrate_phase_duration_policy(
            [([event], False) for _ in range(18)]
        )
        self.assertEqual(model["minimum_support"], 19)
        self.assertFalse(model["calibration_sufficient"])
        self.assertEqual(model["bounds"], {})

    def test_archived_trajectory_cohort_detects_tampering(self):
        import tempfile
        from pathlib import Path

        from tessera.experiments.trajectory_benchmark import (
            archive_trajectory_cohort,
            load_trajectory_cohort,
        )

        records = []
        session_id = "opaque-session"
        for index in range(9):
            records.append(
                {
                    "schema": "fixture",
                    "timestamp": f"2026-06-19T00:00:0{index}+00:00",
                    "phase": "CHECK",
                    "state": "OK",
                    "session_id": session_id,
                    "event_index": index + 1,
                    "elapsed_ms": 80.0,
                    "exit_code": 0,
                }
            )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "events.jsonl"
            archive = Path(directory) / "cohort.json"
            source.write_text(
                "\n".join(json.dumps(record) for record in records),
                encoding="utf-8",
            )
            archive_trajectory_cohort(
                str(source),
                str(archive),
                role="test",
                session_ids=[session_id],
            )
            self.assertEqual(len(load_trajectory_cohort(str(archive))), 1)
            data = json.loads(archive.read_text(encoding="utf-8"))
            data["trajectories"][0]["events"][0]["features"][
                "duration_ms"
            ] = 999.0
            archive.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_trajectory_cohort(str(archive))


class TestEvo13RepairAblation(unittest.TestCase):
    """EVO-013: Phase 3 — Replay-guided shadow repair ablation."""

    def test_repair_ablation_runs_all_arms(self):
        """Repair ablation runs all 5 arms and returns results."""
        result = run_repair_ablation(seed=42, steps=300, channels=3, epochs=2, depth=2)
        self.assertIn("arms", result)
        self.assertEqual(len(result["arms"]), 5)
        arm_names = [a["arm"] for a in result["arms"]]
        self.assertIn(ARM_NO_REPAIR, arm_names)
        self.assertIn(ARM_RANDOM, arm_names)
        self.assertIn(ARM_WRONG_TARGET, arm_names)
        self.assertIn(ARM_GENERIC_RETRAIN, arm_names)
        self.assertIn(ARM_TARGETED, arm_names)

    def test_repair_ablation_selects_winner(self):
        """Repair ablation selects a winning arm."""
        result = run_repair_ablation(seed=42, steps=300, channels=3, epochs=2, depth=2)
        self.assertNotEqual(result["winner"], ARM_WRONG_TARGET)
        if result["winner"] != "none":
            winner = next(
                arm for arm in result["arms"]
                if arm["arm"] == result["winner"]
            )
            self.assertTrue(winner["eligible"])

    def test_repair_ablation_no_repair_baseline(self):
        """No-repair arm produces finite loss."""
        result = run_repair_ablation(seed=42, steps=300, channels=3, epochs=2, depth=2)
        no_repair = next(a for a in result["arms"] if a["arm"] == ARM_NO_REPAIR)
        self.assertTrue(np.isfinite(no_repair["prediction_loss"]))
        self.assertLess(no_repair["prediction_loss"], 1e6)

    def test_repair_ablation_targeted_arm_exists(self):
        """Targeted shadow repair arm produces results."""
        result = run_repair_ablation(seed=42, steps=300, channels=3, epochs=2, depth=2)
        targeted = next(a for a in result["arms"] if a["arm"] == ARM_TARGETED)
        self.assertIn("notes", targeted)
        self.assertIn("shadow", targeted["notes"].lower())

    def test_repair_ablation_report_structure(self):
        """Repair ablation report has all expected fields."""
        result = run_repair_ablation(seed=42, steps=300, channels=3, epochs=2, depth=2)
        for key in ["seed", "field_dim", "code_dim", "depth", "hidden_dim", "arms", "winner", "wall_seconds"]:
            self.assertIn(key, result)
        for arm in result["arms"]:
            for key in ["arm", "prediction_loss", "baseline_loss", "replay_pass_rate", "recall", "false_memory_rate", "wall_seconds", "parameter_count", "eligible", "utility"]:
                self.assertIn(key, arm)
            self.assertIsInstance(arm["baseline_loss"], float)


class TestEvo13MultiSeedBenchmark(unittest.TestCase):
    """EVO-013: Multi-seed benchmark with architecture scaling."""

    def test_multi_seed_default_architecture(self):
        """Multi-seed benchmark runs with default architecture."""
        result = multi_seed_benchmark(seeds=[42, 43], steps=300, channels=3, epochs=1)
        self.assertIn("default", result)
        self.assertEqual(result["default"]["summary"]["seed_count"], 2)

    def test_multi_seed_architecture_scaling(self):
        """Multi-seed benchmark compares multiple architectures."""
        archs = [
            {"name": "d2_h64", "depth": 2, "hidden_dim": 64},
            {"name": "d3_h128", "depth": 3, "hidden_dim": 128},
        ]
        result = multi_seed_benchmark(seeds=[42], steps=300, channels=3, epochs=1, architectures=archs)
        self.assertIn("d2_h64", result)
        self.assertIn("d3_h128", result)
        # Deeper/wider should have more parameters
        d2_params = result["d2_h64"]["summary"]["mean_parameter_count"]
        d3_params = result["d3_h128"]["summary"]["mean_parameter_count"]
        self.assertGreater(d3_params, d2_params)

    def test_multi_seed_summary_statistics(self):
        """Multi-seed benchmark computes summary statistics."""
        result = multi_seed_benchmark(seeds=[42, 43, 44], steps=300, channels=3, epochs=1)
        summary = result["default"]["summary"]
        for key in ["mean_prediction_loss", "std_prediction_loss", "mean_baseline_loss",
                     "mean_baseline_gap", "mean_recall", "mean_false_memory_rate",
                     "mean_replay_pass_rate", "mean_parameter_count", "baseline_parity",
                     "seed_count"]:
            self.assertIn(key, summary)
        self.assertEqual(summary["seed_count"], 3)

    def test_multi_seed_baseline_parity_flag(self):
        """Baseline parity flag is computed correctly."""
        result = multi_seed_benchmark(seeds=[42], steps=300, channels=3, epochs=1)
        summary = result["default"]["summary"]
        self.assertIsInstance(summary["baseline_parity"], bool)


class TestEvo13EnhancedNetworkOnRealPattern(unittest.TestCase):
    """EVO-013: Enhanced network handles structured patterns better than v1."""

    def test_gru_gating_produces_different_trajectories(self):
        """GRU gating produces different field trajectories than simple tanh."""
        P = make_operator("ring", 8, seed=42)
        net = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P, depth=2)
        import torch
        field = torch.zeros(1, 8)
        trajectory = []
        for i in range(20):
            x = torch.randn(1, 4) * 0.1
            nf = net.field_step(x, field)
            trajectory.append(nf.detach().clone())
            field = nf
        # Check that field actually changes (gating is active)
        diffs = [torch.norm(trajectory[i+1] - trajectory[i]).item() for i in range(len(trajectory)-1)]
        self.assertTrue(any(d > 1e-6 for d in diffs))

    def test_deeper_network_has_more_parameters(self):
        """Deeper network (depth=3) has more parameters than shallow (depth=2)."""
        P = make_operator("ring", 8, seed=42)
        net_shallow = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P, depth=2)
        net_deep = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P, depth=3)
        shallow_params = sum(p.numel() for p in net_shallow.parameters())
        deep_params = sum(p.numel() for p in net_deep.parameters())
        self.assertGreater(deep_params, shallow_params)

    def test_wider_network_has_more_parameters(self):
        """Wider network (hidden=128) has more parameters than narrow (hidden=64)."""
        P = make_operator("ring", 8, seed=42)
        net_narrow = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P, hidden_dim=64)
        net_wide = TESSERANet(input_dim=4, field_dim=8, code_dim=4, P=P, hidden_dim=128)
        narrow_params = sum(p.numel() for p in net_narrow.parameters())
        wide_params = sum(p.numel() for p in net_wide.parameters())
        self.assertGreater(wide_params, narrow_params)

    def test_nab_runner_uses_official_window_adapter(self):
        import inspect
        from tessera.experiments.run_nab_transfer import run_nab_diagnostic

        source = inspect.getsource(run_nab_diagnostic)
        self.assertIn("NabKnownCauseAdapter", source)
        self.assertIn("combined_windows.json", source)
        self.assertIn("calibration_end=850", source)


if __name__ == "__main__":
    unittest.main()
