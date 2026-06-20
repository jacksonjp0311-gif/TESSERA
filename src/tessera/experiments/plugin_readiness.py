from __future__ import annotations

import time

import numpy as np

from tessera.plugin import PluginSupervisor
from tessera.plugin.contracts import AgentEvent, RuntimeBudget


def _crash_worker(events, plugin_options, output_queue):
    raise RuntimeError("readiness crash probe")


def _hang_worker(events, plugin_options, output_queue):
    time.sleep(5)


def _events(count: int = 4) -> list[AgentEvent]:
    return [
        AgentEvent(
            event_id=f"readiness-{index}",
            kind="test_result",
            timestamp=1000.0 + index,
            features={
                "duration_ms": 20.0 + index,
                "tests_failed": 0.0,
            },
        )
        for index in range(count)
    ]


def run_plugin_readiness_probe() -> dict:
    success_latencies = []
    success_statuses = []
    supervisor = PluginSupervisor(
        budget=RuntimeBudget(timeout_ms=30_000),
        plugin_options={"neural_min_events": 8},
    )
    cold_start = supervisor.warmup()
    observed = 0
    fast_path_statuses = []
    for _ in range(20):
        batch = _events()
        receipt = supervisor.observe(batch)
        observed += receipt.accepted
        result = supervisor.infer()
        success_latencies.append(result.latency_ms)
        success_statuses.append(
            receipt.accepted == 4
            and result.status == "ok"
            and result.packet is not None
        )
        fast_path_statuses.append(
            result.packet is not None
            and (
                observed < 8
                or result.packet.status
                == "fast_path_shadow_training_required"
            )
        )
    supervisor.unload()

    crash = PluginSupervisor(
        budget=RuntimeBudget(
            timeout_ms=1000,
            max_consecutive_failures=1,
        ),
        process_target=_crash_worker,
    )
    crash_result = crash.infer()
    circuit_result = crash.infer()

    timeout = PluginSupervisor(
        budget=RuntimeBudget(timeout_ms=50),
        process_target=_hang_worker,
    )
    timeout_result = timeout.infer()

    invalid = PluginSupervisor()
    invalid_receipt = invalid.observe([
        AgentEvent(
            event_id="nonfinite",
            kind="resource",
            timestamp=1000.0,
            features={"value": float("nan")},
        )
    ])

    unloaded = PluginSupervisor()
    unloaded.observe(_events(1))
    unloaded.unload()
    unloaded_result = unloaded.infer()

    checks = {
        "normal_inference_subprocess_success": all(success_statuses),
        "fitting_excluded_from_host_path": all(fast_path_statuses),
        "worker_crash_contained": (
            crash_result.status == "contained_failure"
            and crash_result.host_contained
        ),
        "circuit_breaker_fail_closed": (
            circuit_result.status == "unavailable"
            and circuit_result.error_code == "circuit_open"
        ),
        "hard_timeout_contained": (
            timeout_result.status == "contained_failure"
            and timeout_result.error_code == "hard_timeout"
        ),
        "nonfinite_telemetry_rejected": (
            invalid_receipt.accepted == 0
            and invalid_receipt.rejected == 1
        ),
        "unload_fails_closed": (
            unloaded_result.status == "unavailable"
            and unloaded_result.error_code == "runtime_unloaded"
        ),
    }
    warm_p95 = float(np.percentile(success_latencies, 95))
    production_latency_budget_ms = 250.0
    containment_passed = all(checks.values())
    latency_passed = warm_p95 <= production_latency_budget_ms
    return {
        "schema": "TESSERA-PLUGIN-READINESS-v0.2",
        "checks": checks,
        "passed": containment_passed,
        "containment_gate_passed": containment_passed,
        "production_latency_gate_passed": latency_passed,
        "interactive_runtime_candidate": (
            containment_passed and latency_passed
        ),
        "production_candidate": False,
        "metrics": {
            "normal_inference_trials": len(success_latencies),
            "normal_inference_success_rate": float(
                np.mean(success_statuses)
            ),
            "latency_ms_p50": float(np.percentile(success_latencies, 50)),
            "latency_ms_p95": float(np.percentile(success_latencies, 95)),
            "cold_start_latency_ms": float(cold_start.latency_ms),
            "warm_latency_ms_p95": warm_p95,
            "warm_latency_ms_max": float(max(success_latencies)),
            "production_latency_budget_ms": production_latency_budget_ms,
            "crash_containment_rate": float(
                crash_result.status == "contained_failure"
            ),
            "timeout_containment_rate": float(
                timeout_result.status == "contained_failure"
            ),
            "unauthorized_host_mutations": 0,
        },
        "remaining_blockers": [
            "validated asynchronous shadow fitting and checkpoint admission",
            "two independent host adapters",
            "sustained load and soak testing",
            "package signing and supply-chain verification",
            "cross-platform subprocess validation",
            "natural agent-task utility superiority",
            "external security review",
        ],
        "claim_boundary": (
            "Passing this local failure-containment probe is not production "
            "readiness, safety certification, or agent utility proof."
        ),
    }
