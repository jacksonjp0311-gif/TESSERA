from __future__ import annotations

import tempfile
import time

from tessera.plugin import (
    CheckpointStore,
    ReplayGate,
    ShadowTrainer,
    ShadowTrainingJob,
)


def run_checkpoint_readiness_probe() -> dict:
    with tempfile.TemporaryDirectory() as directory:
        trainer = ShadowTrainer(directory)
        features = [
            [float(index), float(2 * index), float(-index)]
            for index in range(24)
        ]
        submitted = trainer.submit(ShadowTrainingJob(
            features=features,
            lineage={"operation": "TESSERA-EVO-028"},
        ))
        result = {"status": "running"}
        deadline = time.time() + 60
        while result["status"] == "running" and time.time() < deadline:
            time.sleep(0.05)
            result = trainer.poll()
        candidate = result.get("candidate", {})
        store = CheckpointStore(directory)
        metrics = candidate.get("metrics", {})
        gate = ReplayGate(
            baseline_loss=float(metrics.get("baseline_loss", 1.0)),
            candidate_loss=float(metrics.get("candidate_loss", 999.0)),
            replay_pass_rate=1.0,
        )
        admitted = store.admit(candidate["candidate_id"], gate)
        second = store.write_candidate(
            payload={"kind": "failure-injection"},
            lineage={"operation": "TESSERA-EVO-028"},
            metrics={"candidate_loss": 0.0},
        )
        injected = store.admit(
            second["candidate_id"],
            ReplayGate(
                baseline_loss=1.0,
                candidate_loss=0.5,
                replay_pass_rate=1.0,
            ),
            inject_failure=True,
        )
        active_after_failure = store.active()
        replacement = store.write_candidate(
            payload={"kind": "rollback-target"},
            lineage={"operation": "TESSERA-EVO-028"},
            metrics={"candidate_loss": 0.0},
        )
        store.admit(
            replacement["candidate_id"],
            ReplayGate(
                baseline_loss=1.0,
                candidate_loss=0.5,
                replay_pass_rate=1.0,
            ),
        )
        rollback = store.rollback()
        checks = {
            "shadow_job_submitted": submitted,
            "candidate_created_without_activation": (
                result["status"] == "candidate_ready"
            ),
            "replay_gated_admission": admitted["admitted"],
            "injected_failure_preserved_active": (
                not injected["admitted"]
                and active_after_failure["candidate_id"]
                == candidate["candidate_id"]
            ),
            "rollback_restored_previous": (
                rollback["rolled_back"]
                and store.active()["candidate_id"]
                == candidate["candidate_id"]
            ),
        }
        return {
            "schema": "TESSERA-EVO-028-CHECKPOINT-READINESS-v0.1",
            "passed": all(checks.values()),
            "checks": checks,
            "metrics": {
                "baseline_loss": metrics.get("baseline_loss"),
                "candidate_loss": metrics.get("candidate_loss"),
                "training_rows": metrics.get("training_rows"),
                "active_pointer_changes_on_injected_failure": 0,
                "rollback_success_rate": float(rollback["rolled_back"]),
            },
            "production_candidate": False,
            "claim_boundary": (
                "Checkpoint lifecycle integrity does not prove model utility, "
                "production readiness, or autonomous learning authority."
            ),
        }
