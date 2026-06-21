from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tessera.experiments.neural_uncertainty_router import (
    run_neural_uncertainty_router,
)
from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.plugin.host_adapters import (
    effective_session_feature_indices,
    full_session_feature_names,
    full_session_summary,
)


def run_effective_geometry_readiness(
    preregistration_path: str | Path,
    *,
    root: str | Path = ".",
) -> dict:
    root = Path(root)
    plan = json.loads(Path(preregistration_path).read_text(encoding="utf-8"))
    trajectories = []
    for cohort in plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(str(root / cohort)))
    raw = np.asarray(
        [full_session_summary(events) for events, _ in trajectories],
        dtype="float64",
    )
    names = full_session_feature_names()
    indices = effective_session_feature_indices(raw[:100])
    legacy = [0, 7, 28, 35, 38]
    phantom = [index for index in legacy if index not in indices]
    router = run_neural_uncertainty_router(str(preregistration_path))
    final = router["final_test"]
    full_risk = float(final["full_risk"])
    neural_risk = float(final["neural"]["retained_risk"])
    simple_risk = float(final["simple"]["retained_risk"])
    checks = {
        "effective_rank_is_two": indices == (0, 28),
        "phantom_dimensions_are_constant": all(
            float(np.ptp(raw[:100, index])) == 0.0
            for index in phantom
        ),
        "router_replay_gate_passed": router["replay"]["gate_passed"],
        "router_final_gate_passed": final["gate_passed"],
        "forecast_remains_unmutated": not router["forecast_mutated"],
    }
    return {
        "schema": "TESSERA-EVO-038-EFFECTIVE-GEOMETRY-v0.1",
        "passed": all(checks.values()),
        "checks": checks,
        "geometry": {
            "ambient_summary_dimension": int(raw.shape[1]),
            "legacy_declared_router_dimension": len(legacy),
            "effective_rank": len(indices),
            "selected_indices": list(indices),
            "selected_features": [names[index] for index in indices],
            "phantom_indices": phantom,
            "phantom_features": [names[index] for index in phantom],
            "selection_rule": (
                "range_j > 1e-6 * max(max_abs_j, 1)"
            ),
        },
        "router": {
            "threshold": router["validation"]["neural_selected"]["threshold"],
            "final_coverage": final["neural"]["coverage"],
            "final_retained_risk": neural_risk,
            "final_full_risk": full_risk,
            "final_simple_risk": simple_risk,
            "risk_reduction_vs_full": 1.0 - neural_risk / full_risk,
            "risk_reduction_vs_simple": 1.0 - neural_risk / simple_risk,
            "decision": router["decision"],
        },
        "mathematical_interpretation": (
            "The calibrated host manifold is a two-dimensional duration "
            "plane embedded in an 84-dimensional summary space. Three legacy "
            "coordinates were constant axes selected by finite-precision "
            "variance noise. Trust must be gated by effective rank, not tensor "
            "width."
        ),
        "claim_boundary": (
            "Effective-rank repair preserves this cohort's selective routing "
            "result but does not establish general host transfer or failure "
            "prediction."
        ),
    }
