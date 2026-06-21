from __future__ import annotations

import numpy as np

from tessera.plugin import PluginSupervisor, train_neural_checkpoint
from tessera.plugin.contracts import AgentEvent, RuntimeBudget
from tessera.plugin.neural_checkpoints import neural_awareness_features
from tessera.plugin.trajectory import vectorize_events


def _events(count: int = 72) -> list[AgentEvent]:
    return [
        AgentEvent(
            event_id=f"evo033-{index}",
            kind="test_result",
            timestamp=1000.0 + index,
            features={
                "duration_ms": 30.0 + index + 2.0 * np.sin(index / 5),
                "token_count": 120.0 + 2.0 * index,
                "tests_failed": 0.0,
            },
        )
        for index in range(count)
    ]


def run_runtime_uncertainty_readiness() -> dict:
    events = _events()
    matrix = vectorize_events(events)
    payload, metrics = train_neural_checkpoint(matrix)
    mean = np.asarray(payload["normalization"]["mean"], dtype=float)
    scale = np.asarray(payload["normalization"]["scale"], dtype=float)
    normalized = (matrix - mean) / scale
    from tessera.plugin.neural_checkpoints import deserialize_expert
    from tessera.model.prediction_experts import predict_with_expert

    expert = deserialize_expert(payload["prediction_expert"])
    stable = predict_with_expert(expert, normalized)
    awareness = neural_awareness_features(payload, normalized, stable)
    calibration = awareness["latent_drift"][43:57]
    threshold = float(np.quantile(calibration, 0.60))
    options = {
        "neural_min_events": 8,
        "checkpoint_payload": payload,
        "uncertainty_router": {
            "score": "latent_drift",
            "threshold": threshold,
        },
    }
    supervisor = PluginSupervisor(
        budget=RuntimeBudget(timeout_ms=30_000),
        plugin_options=options,
    )
    cold = supervisor.warmup()
    latencies = []
    packets = []
    for end in range(58, 72):
        supervisor.replace_events(events[:end])
        result = supervisor.infer()
        latencies.append(result.latency_ms)
        packets.append(result.packet)
    supervisor.unload()
    routes = [packet.trust_route for packet in packets]
    checks = {
        "host_route_is_explicit": all(
            route in {"trusted", "abstain"} for route in routes
        ),
        "forecast_status_preserved": all(
            packet.status == "admitted_neural_checkpoint"
            for packet in packets
        ),
        "abstention_blocks_memory_candidate": all(
            not packet.memory_candidate
            for packet in packets if packet.abstained
        ),
        "both_routes_observed": set(routes) == {"trusted", "abstain"},
        "warm_latency_gate_passed": (
            float(np.percentile(latencies, 95)) <= 250.0
        ),
        "fail_closed_contract_preserved": all(
            packet.trust_route != "abstain" or packet.abstained
            for packet in packets
        ),
    }
    return {
        "schema": "TESSERA-EVO-033-RUNTIME-UNCERTAINTY-v0.1",
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            **metrics,
            "router_threshold": threshold,
            "trial_count": len(packets),
            "trusted_count": routes.count("trusted"),
            "abstain_count": routes.count("abstain"),
            "coverage": routes.count("trusted") / len(routes),
            "cold_start_latency_ms": cold.latency_ms,
            "warm_latency_ms_p50": float(np.percentile(latencies, 50)),
            "warm_latency_ms_p95": float(np.percentile(latencies, 95)),
            "warm_latency_ms_max": float(max(latencies)),
            "latency_budget_ms": 250.0,
        },
        "semantic_transfer_validated": False,
        "production_candidate": False,
        "claim_boundary": (
            "Runtime routing mechanics do not prove that a session-level "
            "threshold transfers to arbitrary host event streams."
        ),
    }
