from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.plugin.host_adapters import (
    full_session_feature_names,
    full_session_summary,
)
from tessera.plugin.manifold_monitor import (
    audit_manifold_window,
    fit_manifold_contract,
)


def run_manifold_stability_readiness(
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
    selected = tuple(plan["selected_indices"])
    split = plan["splits"]
    contract = fit_manifold_contract(
        summaries[slice(*split["calibration"])],
        selected,
        trim_quantile=float(plan["trim_quantile"]),
    )
    audits = {
        name: audit_manifold_window(contract, summaries[slice(*bounds)])
        for name, bounds in split.items()
        if name != "calibration"
    }

    collapse = summaries[slice(*split["final"])].copy()
    collapse[:, selected[1]] = collapse[0, selected[1]]
    expansion = summaries[slice(*split["final"])].copy()
    expansion[:, 7] = np.arange(len(expansion), dtype=float)
    rotation = summaries[slice(*split["final"])].copy()
    mean_values = rotation[:, selected[0]].copy()
    rotation[:, selected[1]] = (
        np.mean(rotation[:, selected[1]])
        - 2.0 * (mean_values - np.mean(mean_values))
    )
    translation = summaries[slice(*split["final"])].copy()
    translation[:, selected] += 8.0 * np.asarray(contract.scale)
    injections = {
        "support_collapse": audit_manifold_window(contract, collapse),
        "support_expansion": audit_manifold_window(contract, expansion),
        "manifold_rotation": audit_manifold_window(contract, rotation),
        "location_drift": audit_manifold_window(contract, translation),
    }
    checks = {
        "calibration_intrinsic_rank_is_one": contract.intrinsic_rank == 1,
        "calibration_first_axis_explains_at_least_98_percent": (
            contract.explained_variance >= 0.98
        ),
        "chronological_windows_stable": all(
            audit.accepted for audit in audits.values()
        ),
        "support_collapse_rejected": (
            injections["support_collapse"].status == "support_collapse"
        ),
        "support_expansion_rejected": (
            injections["support_expansion"].status == "support_expansion"
        ),
        "rotation_rejected": (
            injections["manifold_rotation"].status == "manifold_rotation"
        ),
        "translation_rejected": (
            injections["location_drift"].status == "location_drift"
        ),
    }
    names = full_session_feature_names()
    return {
        "schema": "TESSERA-EVO-039-MANIFOLD-STABILITY-v0.1",
        "passed": all(checks.values()),
        "checks": checks,
        "contract": {
            **asdict(contract),
            "fingerprint": contract.fingerprint,
            "selected_features": [names[index] for index in selected],
        },
        "chronological_audits": {
            name: asdict(audit) for name, audit in audits.items()
        },
        "fault_injections": {
            name: asdict(audit) for name, audit in injections.items()
        },
        "mathematical_interpretation": (
            "The two-coordinate duration support contains a stable "
            "approximately one-dimensional filament. Mean duration and "
            "duration dispersion co-move, so support rank, intrinsic rank, "
            "principal angle, location, and scale are separate invariants."
        ),
        "decision": (
            "promote_manifold_drift_gate"
            if all(checks.values())
            else "reject_manifold_drift_gate"
        ),
        "claim_boundary": (
            "Reference-cohort manifold stability and injected-fault "
            "sensitivity do not establish independent production-host "
            "stability, causal failure prediction, or autonomous authority."
        ),
    }
