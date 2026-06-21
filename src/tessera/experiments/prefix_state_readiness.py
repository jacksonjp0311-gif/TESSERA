from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from tessera.experiments.neural_uncertainty_router import _select_router
from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.model.prediction_experts import predict_with_expert
from tessera.plugin.host_adapters import (
    AgentEventSessionAdapter,
    SessionSummaryContract,
    effective_session_feature_indices,
    full_session_summary,
)
from tessera.plugin.neural_checkpoints import (
    deserialize_expert,
    neural_awareness_features,
    train_neural_checkpoint,
)
from tessera.plugin.runtime import TesseraPlugin


def run_prefix_state_readiness(*, root: str | Path = ".") -> dict:
    root = Path(root)
    plan = json.loads(
        (
            root
            / "docs/research/EVO032_NEURAL_UNCERTAINTY_ROUTER_PREREGISTRATION.json"
        ).read_text(encoding="utf-8")
    )
    trajectories = []
    for cohort in plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(str(root / cohort)))
    raw = np.asarray(
        [full_session_summary(events) for events, _ in trajectories],
        dtype="float32",
    )
    selected = effective_session_feature_indices(raw[:100])
    contract = SessionSummaryContract(selected)
    adapter = AgentEventSessionAdapter(contract)
    events = [
        adapter.adapt(str(index), session)
        for index, (session, _) in enumerate(trajectories)
    ]
    sequence = raw[:, selected]
    payload, _ = train_neural_checkpoint(sequence[:100])
    mean = np.asarray(payload["normalization"]["mean"], dtype=float)
    scale = np.asarray(payload["normalization"]["scale"], dtype=float)
    normalized = (sequence - mean) / scale
    expert = deserialize_expert(payload["prediction_expert"])
    predictions = predict_with_expert(expert, normalized)
    awareness = neural_awareness_features(payload, normalized, predictions)
    errors = np.mean((predictions - normalized[1:]) ** 2, axis=1)
    router, _ = _select_router(
        awareness,
        errors,
        59,
        79,
        [0.6, 0.8, 0.9],
    )
    options = {
        "neural_min_events": 8,
        "checkpoint_payload": payload,
        "uncertainty_router": {
            "score": "latent_drift",
            "threshold": float(router["threshold"]),
        },
        "feature_names": list(contract.feature_names),
    }

    incremental = TesseraPlugin(**options)
    packet_parity = []
    row_parity = []
    incremental_ms = []
    full_replay_ms = []
    modes = []
    for end in range(101, 121):
        incremental.replace_events(events[:end])
        started = time.perf_counter()
        packet = incremental.infer()
        incremental_ms.append((time.perf_counter() - started) * 1000.0)
        modes.append(incremental._checkpoint_cache_mode)
        cached_rows = list(incremental._checkpoint_cache_rows)

        replay = TesseraPlugin(**options)
        replay.observe(events[:end])
        started = time.perf_counter()
        expected = replay.infer()
        full_replay_ms.append((time.perf_counter() - started) * 1000.0)
        packet_parity.append(packet == expected)
        row_parity.append(cached_rows == replay._checkpoint_cache_rows)

    mismatch = list(events[:121])
    mismatch[50] = mismatch[49]
    incremental.replace_events(mismatch)
    incremental.infer()
    mismatch_mode = incremental._checkpoint_cache_mode
    checks = {
        "all_packets_match_full_replay": all(packet_parity),
        "all_metric_rows_match_full_replay": all(row_parity),
        "first_prefix_uses_full_replay": modes[0] == "full_replay",
        "remaining_prefixes_extend_state": (
            modes[1:] == ["prefix_extended"] * 19
        ),
        "prefix_mismatch_forces_full_replay": (
            mismatch_mode == "full_replay"
        ),
        "incremental_p95_below_full_replay_p95": (
            float(np.percentile(incremental_ms[1:], 95))
            < float(np.percentile(full_replay_ms[1:], 95))
        ),
    }
    incremental_p95 = float(np.percentile(incremental_ms[1:], 95))
    replay_p95 = float(np.percentile(full_replay_ms[1:], 95))
    return {
        "schema": "TESSERA-EVO-041-PREFIX-STATE-v0.1",
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "prefixes_compared": len(packet_parity),
            "packet_parity_rate": float(np.mean(packet_parity)),
            "row_parity_rate": float(np.mean(row_parity)),
            "prefix_extensions": modes.count("prefix_extended"),
            "full_replays": modes.count("full_replay"),
            "incremental_latency_ms_p95": incremental_p95,
            "full_replay_latency_ms_p95": replay_p95,
            "p95_speedup": replay_p95 / max(incremental_p95, 1e-12),
            "mismatch_mode": mismatch_mode,
        },
        "decision": (
            "promote_exact_prefix_state_continuation"
            if all(checks.values())
            else "reject_prefix_state_continuation"
        ),
        "mathematical_interpretation": (
            "A validated recurrent prefix is a sufficient computational "
            "state for its next transition when the normalized historical "
            "prefix is byte-identical. Extension is associative over that "
            "state; any prefix mismatch destroys the equivalence and forces "
            "full replay."
        ),
        "claim_boundary": (
            "Exact parity on one reference chronology does not establish "
            "cross-platform floating-point identity or independent-host "
            "latency."
        ),
    }
