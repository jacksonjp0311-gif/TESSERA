from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.plugin.host_adapters import full_session_summary
from tessera.plugin.manifold_monitor import fit_manifold_contract
from tessera.plugin.sequential_geometry import (
    SequentialGeometryState,
    fit_sequential_geometry_contract,
    update_sequential_geometry,
)


def _run_stream(contract, manifold, summaries):
    state = SequentialGeometryState()
    maximum_evidence = 0.0
    final = None
    for summary in summaries:
        final = update_sequential_geometry(
            contract,
            manifold,
            summary,
            state,
        )
        state = final.state
        maximum_evidence = max(maximum_evidence, state.evidence)
    return final, maximum_evidence


def run_sequential_geometry_readiness(
    preregistration_path: str | Path,
    *,
    root: str | Path = ".",
) -> dict:
    root = Path(root)
    plan = json.loads(Path(preregistration_path).read_text(encoding="utf-8"))
    trajectories = []
    for cohort in plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(str(root / cohort)))
    summaries = np.asarray(
        [full_session_summary(events) for events, _ in trajectories],
        dtype="float64",
    )
    calibration = summaries[slice(*plan["calibration"])]
    monitoring = summaries[slice(*plan["monitoring"])]
    manifold = fit_manifold_contract(
        calibration,
        tuple(plan["selected_indices"]),
    )
    sequential = fit_sequential_geometry_contract(
        manifold,
        calibration,
        **plan["sequential_parameters"],
    )
    stable_final, stable_max = _run_stream(
        sequential,
        manifold,
        monitoring,
    )

    selected = np.asarray(manifold.selected_indices, dtype=int)
    center = np.asarray(manifold.center)
    scale = np.asarray(manifold.scale)
    axis = np.asarray(manifold.principal_axis)
    normal = np.asarray([-axis[1], axis[0]])
    normalized = (monitoring[:, selected] - center) / scale

    impulse = normalized.copy()
    impulse[10] += float(plan["impulse_magnitude"]) * normal
    impulse_summaries = monitoring.copy()
    impulse_summaries[:, selected] = impulse * scale + center
    impulse_final, impulse_max = _run_stream(
        sequential,
        manifold,
        impulse_summaries,
    )

    persistent = normalized.copy()
    change_index = int(plan["persistent_change_index"])
    persistent[change_index:] += (
        float(plan["persistent_shift"]) * normal
    )
    persistent_summaries = monitoring.copy()
    persistent_summaries[:, selected] = persistent * scale + center
    persistent_final, persistent_max = _run_stream(
        sequential,
        manifold,
        persistent_summaries,
    )
    alarm_delay = (
        persistent_final.state.first_alarm_index - change_index
        if persistent_final.state.first_alarm_index is not None
        else None
    )
    checks = {
        "untouched_stream_has_no_alarm": not stable_final.state.alarmed,
        "untouched_evidence_below_threshold": (
            stable_max <= sequential.alarm_threshold
        ),
        "single_impulse_does_not_latch": not impulse_final.state.alarmed,
        "persistent_small_shift_latches": persistent_final.state.alarmed,
        "persistent_alarm_within_ten_samples": (
            alarm_delay is not None and alarm_delay <= 10
        ),
        "alarm_forces_abstention": persistent_final.route == "abstain",
        "alarm_suppresses_memory": not persistent_final.memory_candidate,
    }
    return {
        "schema": "TESSERA-EVO-040-SEQUENTIAL-GEOMETRY-v0.1",
        "passed": all(checks.values()),
        "checks": checks,
        "contract": {
            **asdict(sequential),
            "fingerprint": sequential.fingerprint,
        },
        "metrics": {
            "calibration_sessions": len(calibration),
            "monitoring_sessions": len(monitoring),
            "untouched_maximum_evidence": stable_max,
            "single_impulse_maximum_evidence": impulse_max,
            "persistent_shift_maximum_evidence": persistent_max,
            "persistent_change_index": change_index,
            "persistent_first_alarm_index": (
                persistent_final.state.first_alarm_index
            ),
            "persistent_alarm_delay": alarm_delay,
        },
        "decision": (
            "promote_dual_timescale_geometry_sentinel"
            if all(checks.values())
            else "reject_sequential_geometry_sentinel"
        ),
        "mathematical_interpretation": (
            "The window manifold gate is a geometric Shewhart surface for "
            "large changes. Bounded one-sided cumulative evidence along the "
            "orthogonal residual adds a CUSUM-like timescale for persistent "
            "small departures while preventing one impulse from acquiring "
            "authority."
        ),
        "claim_boundary": (
            "Controlled sequential sensitivity does not establish calibrated "
            "false-alarm guarantees on independent hosts or causal failure "
            "prediction."
        ),
    }
