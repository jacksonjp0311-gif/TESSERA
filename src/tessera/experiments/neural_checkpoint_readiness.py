from __future__ import annotations

import tempfile

import numpy as np

from tessera.plugin import (
    CheckpointStore,
    PluginSupervisor,
    ReplayGate,
    train_neural_checkpoint,
)
from tessera.plugin.contracts import AgentEvent
from tessera.plugin.trajectory import vectorize_events


def _events(count=72):
    return [
        AgentEvent(
            event_id=f"evo029-{index}",
            kind="test_result",
            timestamp=1000.0 + index,
            features={
                "duration_ms": 25.0 + index,
                "token_count": 100.0 + 3 * index,
                "tests_failed": 0.0,
            },
        )
        for index in range(count)
    ]


def run_neural_checkpoint_readiness() -> dict:
    events = _events()
    payload, metrics = train_neural_checkpoint(vectorize_events(events))
    with tempfile.TemporaryDirectory() as directory:
        store = CheckpointStore(directory)
        candidate = store.write_candidate(
            payload=payload,
            lineage={"operation": "TESSERA-EVO-029"},
            metrics=metrics,
        )
        gate = ReplayGate(
            baseline_loss=metrics["baseline_loss"],
            candidate_loss=metrics["candidate_loss"],
            replay_pass_rate=metrics["replay_pass_rate"],
        )
        admission = store.admit(candidate["candidate_id"], gate)
        supervisor = PluginSupervisor(plugin_options={
            "neural_min_events": 8,
            "checkpoint_payload": payload,
        })
        cold = supervisor.warmup()
        supervisor.observe(events[:16])
        latencies = []
        statuses = []
        for _ in range(20):
            result = supervisor.infer()
            latencies.append(result.latency_ms)
            statuses.append(
                result.packet is not None
                and result.packet.status == "admitted_neural_checkpoint"
            )
        supervisor.unload()
        warm_p95 = float(np.percentile(latencies, 95))
        checks = {
            "real_tessera_model_serialized": (
                payload["kind"] == "tessera-neural-checkpoint"
            ),
            "held_out_replay_gate_passed": gate.passed,
            "checkpoint_admitted": admission["admitted"],
            "isolated_worker_loaded_checkpoint": all(statuses),
            "warm_latency_gate_passed": warm_p95 <= 250.0,
        }
        return {
            "schema": "TESSERA-EVO-029-NEURAL-CHECKPOINT-v0.1",
            "passed": all(checks.values()),
            "checks": checks,
            "metrics": {
                **metrics,
                "cold_start_latency_ms": cold.latency_ms,
                "warm_latency_ms_p50": float(np.percentile(latencies, 50)),
                "warm_latency_ms_p95": warm_p95,
                "warm_latency_ms_max": float(max(latencies)),
                "latency_budget_ms": 250.0,
            },
            "production_candidate": False,
            "claim_boundary": (
                "Admitted neural inference on a controlled trajectory does "
                "not establish natural agent utility or production readiness."
            ),
        }
