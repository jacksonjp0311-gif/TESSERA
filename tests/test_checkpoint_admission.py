from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from tessera.plugin import (
    CheckpointStore,
    ReplayGate,
    ShadowTrainer,
    ShadowTrainingJob,
)


class TestCheckpointAdmission(unittest.TestCase):
    def candidate(self, store, value):
        return store.write_candidate(
            payload={"weights": [value, value + 1]},
            lineage={"source": "test"},
            metrics={"loss": float(value)},
        )

    def test_candidate_integrity_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CheckpointStore(directory)
            candidate = self.candidate(store, 1)
            path = Path(candidate["path"])
            record = json.loads(path.read_text(encoding="utf-8"))
            record["payload"]["weights"][0] = 999
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(
                ValueError,
                "checkpoint_payload_hash_mismatch",
            ):
                store.load_candidate(candidate["candidate_id"])

    def test_failed_replay_does_not_change_active_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CheckpointStore(directory)
            candidate = self.candidate(store, 1)
            result = store.admit(
                candidate["candidate_id"],
                ReplayGate(
                    baseline_loss=1.0,
                    candidate_loss=2.0,
                    replay_pass_rate=1.0,
                ),
            )
            self.assertFalse(result["admitted"])
            self.assertIsNone(store.active())

    def test_atomic_admission_failure_preserves_previous(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CheckpointStore(directory)
            first = self.candidate(store, 1)
            gate = ReplayGate(
                baseline_loss=1.0,
                candidate_loss=0.9,
                replay_pass_rate=1.0,
            )
            self.assertTrue(store.admit(first["candidate_id"], gate)["admitted"])
            second = self.candidate(store, 2)
            failed = store.admit(
                second["candidate_id"],
                gate,
                inject_failure=True,
            )
            self.assertFalse(failed["admitted"])
            self.assertEqual(
                store.active()["candidate_id"],
                first["candidate_id"],
            )

    def test_rollback_restores_previous_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CheckpointStore(directory)
            gate = ReplayGate(
                baseline_loss=1.0,
                candidate_loss=0.9,
                replay_pass_rate=1.0,
            )
            first = self.candidate(store, 1)
            second = self.candidate(store, 2)
            store.admit(first["candidate_id"], gate)
            store.admit(second["candidate_id"], gate)
            result = store.rollback()
            self.assertTrue(result["rolled_back"])
            self.assertEqual(
                store.active()["candidate_id"],
                first["candidate_id"],
            )

    def test_shadow_trainer_only_emits_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            trainer = ShadowTrainer(directory)
            features = [
                [float(index), float(index % 3)]
                for index in range(12)
            ]
            self.assertTrue(trainer.submit(ShadowTrainingJob(
                features=features,
                lineage={"session": "test"},
            )))
            result = {"status": "running"}
            deadline = time.time() + 30
            while result["status"] == "running" and time.time() < deadline:
                time.sleep(0.05)
                result = trainer.poll()
            self.assertEqual(result["status"], "candidate_ready")
            self.assertIsNone(trainer.store.active())


if __name__ == "__main__":
    unittest.main()
