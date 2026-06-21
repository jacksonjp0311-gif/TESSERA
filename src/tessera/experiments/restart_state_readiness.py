from __future__ import annotations

import copy
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


def run_restart_state_readiness(*, root: str | Path = ".") -> dict:
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
    checkpoint, _ = train_neural_checkpoint(sequence[:100])
    mean = np.asarray(checkpoint["normalization"]["mean"], dtype=float)
    scale = np.asarray(checkpoint["normalization"]["scale"], dtype=float)
    normalized = (sequence - mean) / scale
    expert = deserialize_expert(checkpoint["prediction_expert"])
    predictions = predict_with_expert(expert, normalized)
    awareness = neural_awareness_features(
        checkpoint,
        normalized,
        predictions,
    )
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
        "checkpoint_payload": checkpoint,
        "uncertainty_router": {
            "score": "latent_drift",
            "threshold": float(router["threshold"]),
        },
        "feature_names": list(contract.feature_names),
    }
    original = TesseraPlugin(**options)
    original.observe(events[:110])
    original.infer()
    capsule = original.export_state_capsule()

    restored = TesseraPlugin(**{**options, "state_capsule": capsule})
    restored.observe(events[:111])
    started = time.perf_counter()
    restored_packet = restored.infer()
    restored_latency = (time.perf_counter() - started) * 1000.0

    replay = TesseraPlugin(**options)
    replay.observe(events[:111])
    started = time.perf_counter()
    replay_packet = replay.infer()
    replay_latency = (time.perf_counter() - started) * 1000.0

    tampered = copy.deepcopy(capsule)
    tampered["payload"]["recurrent_state"]["transitions"] += 1
    tamper_rejected = False
    try:
        TesseraPlugin(**{**options, "state_capsule": tampered})
    except ValueError as error:
        tamper_rejected = str(error) == "state_capsule_hash_mismatch"

    wrong_checkpoint = copy.deepcopy(checkpoint)
    wrong_checkpoint["architecture"]["seed"] = 43
    checkpoint_mismatch_rejected = False
    try:
        TesseraPlugin(
            **{
                **options,
                "checkpoint_payload": wrong_checkpoint,
                "state_capsule": capsule,
            }
        )
    except ValueError as error:
        checkpoint_mismatch_rejected = (
            str(error) == "state_capsule_checkpoint_mismatch"
        )

    wrong_prefix = list(events[:111])
    wrong_prefix[20] = wrong_prefix[19]
    mismatch = TesseraPlugin(**{**options, "state_capsule": capsule})
    mismatch.observe(wrong_prefix)
    mismatch.infer()
    checks = {
        "restored_packet_matches_full_replay": (
            restored_packet == replay_packet
        ),
        "restored_rows_match_full_replay": (
            restored._checkpoint_cache_rows
            == replay._checkpoint_cache_rows
        ),
        "restored_state_extends_prefix": (
            restored._checkpoint_cache_mode == "prefix_extended"
        ),
        "tampered_capsule_rejected": tamper_rejected,
        "checkpoint_mismatch_rejected": checkpoint_mismatch_rejected,
        "historical_mismatch_forces_replay": (
            mismatch._checkpoint_cache_mode == "full_replay"
        ),
        "restored_continuation_faster_than_replay": (
            restored_latency < replay_latency
        ),
    }
    return {
        "schema": "TESSERA-EVO-042-RESTART-STATE-v0.1",
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "capsule_payload_sha256": capsule["payload_sha256"],
            "prefix_rows_restored": 110,
            "restored_continuation_latency_ms": restored_latency,
            "full_replay_latency_ms": replay_latency,
            "restart_speedup": replay_latency / max(
                restored_latency,
                1e-12,
            ),
            "packet_parity": float(restored_packet == replay_packet),
            "row_parity": float(
                restored._checkpoint_cache_rows
                == replay._checkpoint_cache_rows
            ),
        },
        "decision": (
            "promote_integrity_bound_restart_state"
            if all(checks.values())
            else "reject_restart_state_capsule"
        ),
        "mathematical_interpretation": (
            "A recurrent prefix witness can cross a process boundary only "
            "when its full serialized state, input lineage, checkpoint, "
            "feature contract, router, packet, and metric history share one "
            "verified integrity envelope."
        ),
        "claim_boundary": (
            "Local restart parity and SHA-256 integrity do not establish "
            "confidentiality, authenticity against a privileged attacker, "
            "cross-platform identity, or independent production safety."
        ),
    }
