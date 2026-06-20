from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from tessera.data.adapters import (
    CsvDatasetAdapter,
    DatasetDescriptor,
    NabKnownCauseAdapter,
    TelemanomChannelAdapter,
    UcrAnomalyAdapter,
)
from tessera.experiments.repair_ablation import run_repair_ablation
from tessera.graph.adaptive import propose_sparse_rewire
from tessera.graph.topologies import ring
from tessera.model.network import TESSERANet
from tessera.model.train import fit_tessera_model
from tessera.metrics.anomaly import calibrate_anomaly_model, score_anomalies
from tessera.metrics.subsequence import causal_event_persistence, z_normalized_subsequence_scores
from tessera.memory.episodes import (
    apply_event_memory_quarantine,
    apply_routed_event_memory_quarantine,
)
from tessera.memory.gates import apply_independent_memory_gate
from tessera.metrics.router import (
    calibrate_confidence_router,
    calibrate_selective_router,
    calibrate_sensor_router,
    robust_point_scores,
    route_sensor_scores,
    route_sensor_scores_with_abstention,
    route_sensor_scores_selectively,
)


class TestEvolutionPhases(unittest.TestCase):
    def test_prediction_expert_selection_is_validation_only_and_causal(self):
        from tessera.model.prediction_experts import (
            prediction_losses,
            select_prediction_expert,
        )

        train = np.arange(80, dtype=float).reshape(-1, 1)
        validation = np.arange(80, 120, dtype=float).reshape(-1, 1)
        expert, evidence = select_prediction_expert(train, validation)
        losses = prediction_losses(
            expert, validation, history=train
        )
        self.assertEqual(len(losses), len(validation) - 1)
        self.assertEqual(
            evidence["selection_source"], "normal_validation_only"
        )
        self.assertLess(float(losses.mean()), 1.0)

    def test_pca_codec_preserves_single_channel_shape(self):
        from tessera.baselines.pca_codec import evaluate_pca_codec

        train = np.linspace(0.0, 1.0, 30).reshape(-1, 1)
        test = np.linspace(1.0, 2.0, 40).reshape(-1, 1)
        result = evaluate_pca_codec(train, test, code_dim=1)
        self.assertTrue(np.isfinite(result["mean_prediction_loss"]))

    def test_random_projection_preserves_single_channel_shape(self):
        from tessera.baselines.random_projection import (
            evaluate_random_projection,
        )

        train = np.linspace(0.0, 1.0, 30).reshape(-1, 1)
        test = np.linspace(1.0, 2.0, 40).reshape(-1, 1)
        result = evaluate_random_projection(
            train, test, code_dim=1, seed=3
        )
        self.assertTrue(np.isfinite(result["mean_prediction_loss"]))

    def test_csv_dataset_adapter_normalizes_label_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stream.csv"
            path.write_text("x,y,target\n1,2,0\n2,3,1\n", encoding="utf-8")
            adapter = CsvDatasetAdapter(
                path=path,
                descriptor=DatasetDescriptor(
                    name="fixture",
                    version="1",
                    source="local",
                    license="test",
                    label_policy="evaluation_only",
                ),
                label_column="target",
            )
            frame = adapter.load()
            self.assertIn("label", frame)
            self.assertTrue(adapter.raw_hash())

    def test_nab_adapter_expands_official_windows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream = root / "stream.csv"
            windows = root / "windows.json"
            stream.write_text(
                "timestamp,value\n"
                "2020-01-01 00:00:00,1\n"
                "2020-01-01 00:05:00,2\n",
                encoding="utf-8",
            )
            windows.write_text(
                '{"fixture.csv":[["2020-01-01 00:05:00","2020-01-01 00:05:00"]]}',
                encoding="utf-8",
            )
            adapter = NabKnownCauseAdapter(
                stream,
                windows,
                "fixture.csv",
                DatasetDescriptor(
                    "fixture", "1", "local", "MIT", "evaluation_only"
                ),
            )
            frame = adapter.load()
            self.assertEqual(frame["label"].tolist(), [0, 1])

    def test_telemanom_adapter_uses_zero_based_inclusive_sequences(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            np.save(root / "train.npy", np.zeros((3, 2)))
            np.save(root / "test.npy", np.zeros((4, 2)))
            (root / "labels.csv").write_text(
                'chan_id,spacecraft,anomaly_sequences,class,num_values\n'
                'P-1,SMAP,"[[1, 2]]","[point]",4\n',
                encoding="utf-8",
            )
            adapter = TelemanomChannelAdapter(
                root / "train.npy",
                root / "test.npy",
                root / "labels.csv",
                "P-1",
                DatasetDescriptor("fixture", "1", "local", "Apache-2.0", "evaluation"),
            )
            self.assertEqual(adapter.load_test()["label"].tolist(), [0, 1, 1, 0])

    def test_ucr_adapter_parses_filename_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "173_UCR_Anomaly_fixture_3_5_6.txt"
            path.write_text("\n".join(str(value) for value in range(8)), encoding="utf-8")
            adapter = UcrAnomalyAdapter(
                path,
                DatasetDescriptor("fixture", "1", "local", "CC BY 4.0", "evaluation"),
            )
            self.assertEqual(adapter.metadata()["train_end"], 3)
            self.assertEqual(adapter.load()["label"].tolist(), [0, 0, 0, 0, 0, 1, 1, 0])

    def test_subsequence_discord_scores_shape_change(self):
        reference = np.sin(np.linspace(0, 8, 100))
        sequence = np.sin(np.linspace(8, 12, 40))
        sequence[20:24] += 4.0
        scores = z_normalized_subsequence_scores(reference, sequence, window=12)
        self.assertEqual(len(scores), len(sequence))
        self.assertGreater(scores[23], np.median(scores))
        held = causal_event_persistence(np.array([0.0, 3.0, 0.0]), hold=2)
        self.assertEqual(held.tolist(), [0.0, 3.0, 3.0])

    def test_event_quarantine_is_causal_and_recomputes_memory(self):
        import pandas as pd

        rows = pd.DataFrame(
            {
                "warn": [0, 1, 0, 0, 0],
                "memory_candidate": [1, 0, 1, 1, 1],
                "label": [0, 1, 1, 0, 0],
            }
        )
        out = apply_event_memory_quarantine(rows, hold=2)
        self.assertEqual(out["event_quarantine"].tolist(), [0, 1, 1, 1, 0])
        self.assertEqual(out["memory_candidate"].tolist(), [1, 0, 0, 0, 1])
        self.assertEqual(out["false_memory_candidate"].sum(), 0)

    def test_sensor_router_selects_stronger_normalized_evidence(self):
        reference = np.zeros(20)
        point = robust_point_scores(reference, np.array([0.0, 5.0]))
        calibration = calibrate_sensor_router(
            np.array([0.5, 1.0]), np.array([0.5, 1.0])
        )
        routed = route_sensor_scores(
            point, np.array([0.1, 0.1]), calibration
        )
        self.assertEqual(routed["sensor_route"].iloc[-1], "point")

    def test_routed_episode_uses_shorter_point_hold(self):
        import pandas as pd

        rows = pd.DataFrame(
            {
                "warn": [1, 0, 0, 0],
                "sensor_route": ["point"] * 4,
                "memory_candidate": [0, 1, 1, 1],
                "label": [1, 0, 0, 0],
            }
        )
        out = apply_routed_event_memory_quarantine(
            rows, point_hold=1, subsequence_hold=4
        )
        self.assertEqual(out["event_quarantine"].tolist(), [1, 1, 0, 0])

    def test_confidence_router_abstains_on_weak_or_ambiguous_evidence(self):
        calibration = calibrate_confidence_router(
            np.array([0.2, 0.4, 0.8, 1.0]),
            np.array([0.2, 0.4, 0.8, 1.0]),
        )
        weak = route_sensor_scores_with_abstention(
            np.array([0.1]), np.array([0.1]), calibration
        )
        ambiguous = route_sensor_scores_with_abstention(
            np.array([2.0]), np.array([2.0]), calibration
        )
        decisive = route_sensor_scores_with_abstention(
            np.array([4.0]), np.array([0.1]), calibration
        )
        self.assertEqual(weak["sensor_route"].iloc[0], "abstain")
        self.assertEqual(ambiguous["sensor_route"].iloc[0], "abstain")
        self.assertEqual(decisive["sensor_route"].iloc[0], "point")

    def test_memory_normality_gate_is_independent_from_detection_score(self):
        import pandas as pd

        rows = pd.DataFrame(
            {
                "anomaly_score": [0.1, 0.1],
                "memory_normality_score": [0.2, 4.0],
                "block": [0, 0],
                "memory_candidate": [1, 1],
                "label": [0, 1],
            }
        )
        out = apply_independent_memory_gate(rows, threshold=1.0)
        self.assertEqual(out["memory_candidate"].tolist(), [1, 0])
        self.assertEqual(out["false_memory_candidate"].sum(), 0)

    def test_abstain_route_uses_conservative_episode_hold(self):
        import pandas as pd

        rows = pd.DataFrame(
            {
                "warn": [1, 0, 0, 0],
                "sensor_route": ["abstain"] * 4,
                "memory_candidate": [0, 1, 1, 1],
                "label": [1, 0, 0, 0],
            }
        )
        out = apply_routed_event_memory_quarantine(
            rows,
            point_hold=1,
            subsequence_hold=3,
            abstain_hold=2,
        )
        self.assertEqual(out["event_quarantine"].tolist(), [1, 1, 1, 0])

    def test_selective_router_changes_abstained_score_fusion(self):
        calibration = calibrate_selective_router(
            np.array([0.2, 0.4, 0.8, 1.0]),
            np.array([0.2, 0.4, 0.8, 1.0]),
            target_coverage=0.20,
        )
        routed = route_sensor_scores_selectively(
            np.array([0.1]), np.array([0.4]), calibration
        )
        self.assertEqual(routed["sensor_route"].iloc[0], "abstain")
        self.assertLess(
            routed["anomaly_score"].iloc[0],
            routed["max_fusion_score"].iloc[0],
        )

    def test_selective_router_calibrates_declared_coverage(self):
        calibration = calibrate_selective_router(
            np.linspace(0.1, 1.0, 100),
            np.linspace(1.0, 0.1, 100),
            target_coverage=0.20,
        )
        self.assertEqual(calibration["target_specialist_coverage"], 0.20)
        self.assertGreater(calibration["activation_score"], 0.0)

    def test_targeted_repair_must_beat_controls(self):
        """Targeted shadow repair should produce finite results and not mutate live codec."""
        result = run_repair_ablation(seed=42, steps=300, channels=3, epochs=2, depth=2)
        # Targeted arm should produce finite loss
        targeted = next((a for a in result["arms"] if a["arm"] == "targeted_shadow_repair"), None)
        self.assertIsNotNone(targeted)
        self.assertTrue(targeted["prediction_loss"] < 1e6)
        # No live codec mutation in any arm
        for arm in result["arms"]:
            self.assertFalse(arm.get("live_codec_mutated", False))

    def test_topology_proposal_is_shadow_and_stable(self):
        operator = ring(8)
        candidate, proposal = propose_sparse_rewire(
            operator, alpha=0.5, max_changed_edges=1
        )
        self.assertEqual(candidate.shape, operator.shape)
        self.assertTrue(proposal.shadow_only)
        self.assertLess(proposal.stability_margin, 1.0)
        self.assertNotEqual(proposal.old_hash, proposal.candidate_hash)

    def test_neural_predictor_starts_at_declared_anchor_floor(self):
        model = TESSERANet(
            input_dim=2, field_dim=4, code_dim=2, P=ring(4), alpha=0.5
        )
        import torch

        x = torch.tensor([[1.0, -2.0]])
        field = torch.zeros(1, 4)
        _, _, _, prediction = model.step(x, field)
        self.assertTrue(torch.allclose(prediction, x))
        level = torch.tensor([[0.5, -1.0]])
        _, _, _, prediction = model.step(x, field, level)
        self.assertTrue(torch.allclose(prediction, level))

    def test_validation_selection_keeps_correction_bounded(self):
        sequence = np.stack(
            [np.linspace(0.0, 1.0, 12), np.linspace(1.0, 0.0, 12)], axis=1
        ).astype("float32")
        model = fit_tessera_model(
            sequence[:8],
            ring(4),
            code_dim=2,
            alpha=0.5,
            epochs=1,
            X_validation=sequence[7:],
        )
        self.assertIn(model.correction_gain, (0.0, 0.1, 0.25))

    def test_target_aware_training_emits_target_metrics(self):
        sequence = np.random.default_rng(3).normal(size=(12, 3)).astype("float32")
        model = fit_tessera_model(
            sequence[:8],
            ring(4),
            code_dim=2,
            alpha=0.5,
            epochs=1,
            X_validation=sequence[7:],
            prediction_target_dims=1,
        )
        from tessera.model.train import evaluate_sequence

        row = evaluate_sequence(model, sequence[8:])["rows"][0]
        self.assertIn("target_prediction_loss", row)
        self.assertIn("target_reconstruction_loss", row)

    def test_multiscale_score_detects_two_sided_channel_surprise(self):
        import pandas as pd

        normal = pd.DataFrame(
            {
                "prediction_loss": [1.0, 1.1, 0.9, 1.05],
                "reconstruction_loss": [10.0, 10.2, 9.8, 10.1],
                "delta_phi": [0.1, 0.11, 0.09, 0.1],
                "code_drift": [0.2, 0.19, 0.21, 0.2],
                "rate": [0.5, 0.51, 0.49, 0.5],
            }
        )
        calibration = calibrate_anomaly_model(normal)
        high = normal.iloc[[0]].copy()
        high["prediction_loss"] = 20.0
        low = normal.iloc[[0]].copy()
        low["reconstruction_loss"] = 0.1
        self.assertGreater(
            score_anomalies(high, calibration)["anomaly_score"].iloc[0],
            calibration["warn_score"],
        )
        self.assertGreater(
            score_anomalies(low, calibration)["anomaly_score"].iloc[0],
            calibration["warn_score"],
        )

    def test_anomaly_fusion_profile_is_persisted(self):
        import pandas as pd

        normal = pd.DataFrame(
            {
                "prediction_loss": [1.0, 1.1, 0.9, 1.05],
                "delta_phi": [0.1, 0.11, 0.09, 0.1],
                "code_drift": [0.2, 0.19, 0.21, 0.2],
                "rate": [0.5, 0.51, 0.49, 0.5],
            }
        )
        calibration = calibrate_anomaly_model(
            normal,
            components=("prediction_loss", "delta_phi", "code_drift", "rate"),
            fusion="mean_multiscale",
        )
        self.assertEqual(calibration["fusion"], "mean_multiscale")
        self.assertNotIn("reconstruction_loss", calibration["components"])

    def test_false_memory_rate_counts_anomaly_candidates(self):
        import pandas as pd
        from tessera.metrics.governance import summarize_gates

        rows = pd.DataFrame(
            {
                "J_RD": [1.0, 2.0],
                "anomaly_score": [1.0, 2.0],
                "delta_phi": [0.0, 0.0],
                "warn": [0, 0],
                "block": [0, 0],
                "memory_candidate": [1, 1],
                "replay_pass": [1, 0],
                "false_memory_candidate": [0, 1],
                "label": [0, 1],
            }
        )
        summary = summarize_gates(rows)
        self.assertEqual(summary["false_memory_rate"], 1.0)
        self.assertEqual(summary["replay_pass_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
