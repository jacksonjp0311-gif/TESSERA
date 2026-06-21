from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np

from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.model.prediction_experts import predict_with_expert
from tessera.plugin.checkpoints import CheckpointStore, ReplayGate
from tessera.plugin.contracts import RuntimeBudget
from tessera.plugin.host_adapters import (
    AgentEventSessionAdapter,
    JsonSessionAdapter,
    SessionSummaryContract,
    full_session_summary,
    effective_session_feature_indices,
)
from tessera.plugin.neural_checkpoints import (
    deserialize_expert,
    neural_awareness_features,
    train_neural_checkpoint,
)
from tessera.plugin.supervisor import PluginSupervisor


def _crash_worker(events, plugin_options, output_queue):
    raise RuntimeError("evo034_injected_worker_crash")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_production_candidate(root: str | Path = ".") -> dict:
    root = Path(root)
    plan = json.loads(
        (root / "docs/research/EVO032_NEURAL_UNCERTAINTY_ROUTER_PREREGISTRATION.json")
        .read_text(encoding="utf-8")
    )
    prior = json.loads(
        (root / "outputs/evidence/evo032/neural_uncertainty_router.json")
        .read_text(encoding="utf-8")
    )
    trajectories = []
    for cohort in plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(str(root / cohort)))
    if len(trajectories) != 120 or any(label for _, label in trajectories):
        raise ValueError("production_candidate_requires_120_clean_sessions")

    raw = np.asarray(
        [full_session_summary(events) for events, _ in trajectories],
        dtype="float32",
    )
    selected_indices = effective_session_feature_indices(raw[:100])
    contract = SessionSummaryContract(selected_indices)
    direct = AgentEventSessionAdapter(contract)
    json_adapter = JsonSessionAdapter(contract)
    direct_events = []
    json_events = []
    for index, (events, _) in enumerate(trajectories):
        direct_events.append(direct.adapt(str(index), events))
        json_events.append(json_adapter.adapt(
            str(index),
            JsonSessionAdapter.serialize(events),
        ))
    direct_matrix = np.asarray([
        [event.features[name] for name in contract.feature_names]
        for event in direct_events
    ], dtype="float32")
    json_matrix = np.asarray([
        [event.features[name] for name in contract.feature_names]
        for event in json_events
    ], dtype="float32")
    sequence = raw[:, selected_indices]
    payload, checkpoint_metrics = train_neural_checkpoint(sequence[:100])
    mean = np.asarray(payload["normalization"]["mean"], dtype=float)
    scale = np.asarray(payload["normalization"]["scale"], dtype=float)
    normalized = (sequence - mean) / scale
    expert = deserialize_expert(payload["prediction_expert"])
    predictions = predict_with_expert(expert, normalized)
    awareness = neural_awareness_features(payload, normalized, predictions)
    from tessera.experiments.neural_uncertainty_router import _select_router

    errors = np.mean((predictions - normalized[1:]) ** 2, axis=1)
    selected_router, _ = _select_router(
        awareness,
        errors,
        59,
        79,
        [0.6, 0.8, 0.9],
    )
    threshold = float(selected_router["threshold"])
    expected_routes = [
        "trusted" if score <= threshold else "abstain"
        for score in awareness["latent_drift"][99:119]
    ]

    options = {
        "neural_min_events": 8,
        "checkpoint_payload": payload,
        "uncertainty_router": {
            "score": "latent_drift",
            "threshold": threshold,
        },
        "feature_names": list(contract.feature_names),
    }
    supervisor = PluginSupervisor(
        budget=RuntimeBudget(timeout_ms=30_000),
        plugin_options=options,
    )
    cold = supervisor.warmup()
    routes = []
    latencies = []
    packets = []
    for end in range(101, 121):
        supervisor.replace_events(direct_events[:end])
        result = supervisor.infer()
        latencies.append(result.latency_ms)
        packets.append(result.packet)
        routes.append(result.packet.trust_route)

    supervisor.unload()
    restarted = PluginSupervisor(
        budget=RuntimeBudget(timeout_ms=30_000),
        plugin_options=options,
    )
    restarted.replace_events(direct_events)
    restart_first = restarted.infer()
    restart_second = restarted.infer()
    soak_latencies = []
    soak_failures = 0
    for _ in range(100):
        result = restarted.infer()
        soak_latencies.append(result.latency_ms)
        soak_failures += int(result.status != "ok")
    restart_health = restarted.health()
    restarted.unload()

    failure = PluginSupervisor(
        budget=RuntimeBudget(
            timeout_ms=1000,
            max_consecutive_failures=2,
        ),
        process_target=_crash_worker,
    )
    failure_results = [failure.infer(), failure.infer(), failure.infer()]

    with tempfile.TemporaryDirectory() as directory:
        store = CheckpointStore(directory)
        lifecycle_replay = ReplayGate(
            baseline_loss=1.0,
            candidate_loss=0.5,
            replay_pass_rate=1.0,
        )
        first = store.write_candidate(
            payload=payload,
            lineage={"operation": "TESSERA-EVO-034", "slot": "stable"},
            metrics={"probe": "rollback_transaction_only"},
        )
        second = store.write_candidate(
            payload=payload,
            lineage={"operation": "TESSERA-EVO-034", "slot": "candidate"},
            metrics={"probe": "rollback_transaction_only"},
        )
        first_admission = store.admit(
            first["candidate_id"],
            lifecycle_replay,
        )
        second_admission = store.admit(
            second["candidate_id"],
            lifecycle_replay,
        )
        rollback = store.rollback()

    critical_paths = [
        "pyproject.toml",
        "src/tessera/plugin/contracts.py",
        "src/tessera/plugin/runtime.py",
        "src/tessera/plugin/supervisor.py",
        "src/tessera/plugin/host_adapters.py",
        "src/tessera/plugin/neural_checkpoints.py",
        "src/tessera/plugin/checkpoints.py",
        "configs/production.json",
    ]
    integrity = {
        path: _sha256(root / path)
        for path in critical_paths
        if (root / path).exists()
    }
    checks = {
        "semantic_adapter_matches_calibration": bool(
            np.array_equal(direct_matrix, sequence)
        ),
        "json_adapter_matches_direct_adapter": bool(
            np.array_equal(json_matrix, direct_matrix)
        ),
        "selected_feature_contract_stable": (
            len(selected_indices) == 2
            and list(selected_indices) == [0, 28]
        ),
        "runtime_routes_match_offline_final_test": routes == expected_routes,
        "abstention_blocks_memory_candidate": all(
            not packet.memory_candidate
            for packet in packets if packet.abstained
        ),
        "forecast_status_preserved": all(
            packet.status == "admitted_neural_checkpoint"
            for packet in packets
        ),
        "warm_latency_gate_passed": (
            float(np.percentile(latencies, 95)) <= 250.0
        ),
        "restart_is_deterministic": (
            restart_first.status == "ok"
            and restart_second.status == "ok"
            and restart_first.packet.trust_route
            == restart_second.packet.trust_route
            == expected_routes[-1]
        ),
        "soak_passed": (
            soak_failures == 0
            and restart_health.successful_requests >= 102
            and float(np.percentile(soak_latencies, 99)) <= 250.0
        ),
        "failure_isolation_passed": (
            [item.status for item in failure_results]
            == ["contained_failure", "contained_failure", "unavailable"]
            and failure_results[-1].error_code == "circuit_open"
        ),
        "checkpoint_rollback_passed": (
            first_admission["admitted"]
            and second_admission["admitted"]
            and rollback["rolled_back"]
            and rollback["active"]["candidate_id"]
            == first["candidate_id"]
        ),
        "release_integrity_manifest_complete": (
            len(integrity) == len(critical_paths)
        ),
    }
    return {
        "schema": "TESSERA-EVO-034-PRODUCTION-CANDIDATE-v0.1",
        "passed": all(checks.values()),
        "status": (
            "local_production_candidate"
            if all(checks.values())
            else "production_candidate_rejected"
        ),
        "checks": checks,
        "session_contract": contract.as_dict(),
        "metrics": {
            **checkpoint_metrics,
            "sessions": len(trajectories),
            "selected_session_features": len(selected_indices),
            "final_route_count": len(routes),
            "trusted_count": routes.count("trusted"),
            "abstain_count": routes.count("abstain"),
            "route_parity_rate": float(np.mean(
                np.asarray(routes) == np.asarray(expected_routes)
            )),
            "cold_start_latency_ms": cold.latency_ms,
            "warm_latency_ms_p50": float(np.percentile(latencies, 50)),
            "warm_latency_ms_p95": float(np.percentile(latencies, 95)),
            "warm_latency_ms_max": float(max(latencies)),
            "soak_requests": len(soak_latencies),
            "soak_failures": soak_failures,
            "soak_latency_ms_p99": float(
                np.percentile(soak_latencies, 99)
            ),
            "latency_budget_ms": 250.0,
        },
        "integrity": {
            "algorithm": "sha256",
            "files": integrity,
        },
        "external_launch_blockers": [
            "untouched natural failure-and-recovery cohort",
            "two genuinely independent external host integrations",
            "independent security review and dependency vulnerability scan",
            "independent reproducibility run in a clean environment",
        ],
        "claim_boundary": (
            "Local production candidacy proves the checked repository and "
            "runtime properties only; it does not establish general safety, "
            "natural failure sensitivity, or authorization for host mutation."
        ),
    }
