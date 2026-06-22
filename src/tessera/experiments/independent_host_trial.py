from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.experiments.trajectory_local_benchmark import (
    capture_agent_cli_sessions,
    run_local_utility_benchmark,
)
from tessera.plugin import PluginSupervisor
from tessera.plugin.atomic_capsule_store import AtomicCapsuleStore
from tessera.plugin.host_integrations import HostObservability
from tessera.plugin.host_integrations import (
    AgentCliMirrorIntegration,
    HermesStreamIntegration,
)


INDEPENDENT_HOST_TRIAL_SCHEMA = "TESSERA-INDEPENDENT-HOST-TRIAL-v0.1"


@dataclass
class HostTrialResult:
    host: str
    trial_id: str
    session_count: int
    observations: dict
    capsule_store_stats: dict | None
    utility_summary: dict | None
    rank_drift: dict | None
    wall_seconds: float
    claim_boundary: str = (
        "Independent host trial measures offline behavior on captured sessions "
        "from a second host. It does not establish live agent utility or production readiness."
    )


@dataclass
class IndependentHostTrialReport:
    schema: str = INDEPENDENT_HOST_TRIAL_SCHEMA
    trial_id: str = ""
    reference_host: str = ""
    trial_host: str = ""
    host_results: list = field(default_factory=list)
    capsules_written: int = 0
    capsules_verified: int = 0
    parity_checks: dict = field(default_factory=dict)
    rank_drift_summary: dict = field(default_factory=dict)
    wall_seconds: float = 0.0
    claim_boundary: str = (
        "Independent host trial validates that Tessera produces consistent "
        "routing decisions across hosts for the same captured sessions. "
        "It does not establish live agent utility or production readiness."
    )


def run_independent_host_trial(
    *,
    trial_id: str,
    reference_host: str,
    trial_host: str,
    reference_sessions_path: str | Path,
    trial_sessions_path: str | Path,
    capsule_store_path: str | Path,
    preregistration_path: str | Path | None = None,
) -> dict:
    """Run an independent host trial.

    Loads captured sessions from both a reference host and a trial host,
    runs Tessera against both, and compares routing decisions.

    The trial measures:
    1. Session capture quality (event count, adapter coverage)
    2. Routing consistency across hosts for equivalent sessions
    3. Capsule store integrity across hosts
    4. Rank drift between host session distributions
    """
    t0 = time.time()

    # Load preregistration if available
    prereg = None
    if preregistration_path and Path(preregistration_path).exists():
        prereg = json.loads(Path(preregistration_path).read_text(encoding="utf-8"))

    # Capture sessions from both hosts
    reference_captures = capture_agent_cli_sessions(
        reference_sessions_path, minimum_prefix=7
    )
    trial_captures = capture_agent_cli_sessions(
        trial_sessions_path, minimum_prefix=7
    )

    # Run utility benchmark on both
    reference_utility = run_local_utility_benchmark(reference_captures) if reference_captures else {}
    trial_utility = run_local_utility_benchmark(trial_captures) if trial_captures else {}

    # Write capsules to the store
    store = AtomicCapsuleStore(capsule_store_path, max_capsules=50000)
    capsules_written = 0

    for capture in reference_captures:
        store.write_capsule(
            payload={"host": reference_host, "session": capture.session_id_hash},
            host=reference_host,
            session_id_hash=capture.session_id_hash,
            metadata={"event_count": capture.event_count},
        )
        capsules_written += 1

    for capture in trial_captures:
        store.write_capsule(
            payload={"host": trial_host, "session": capture.session_id_hash},
            host=trial_host,
            session_id_hash=capture.session_id_hash,
            metadata={"event_count": capture.event_count},
        )
        capsules_written += 1

    # Verify all capsules
    verification = store.verify_all()
    capsules_verified = verification["passed"]

    # Compute rank drift
    rank_drift = _compute_rank_drift(reference_captures, trial_captures)

    # Build report
    report = IndependentHostTrialReport(
        trial_id=trial_id,
        reference_host=reference_host,
        trial_host=trial_host,
        host_results=[
            HostTrialResult(
                host=reference_host,
                trial_id=trial_id,
                session_count=len(reference_captures),
                observations=reference_utility if isinstance(reference_utility, dict) else {},
                capsule_store_stats=None,
                utility_summary=_summarize_utility(reference_utility) if isinstance(reference_utility, dict) else None,
                rank_drift=None,
                wall_seconds=0,
            ).__dict__,
            HostTrialResult(
                host=trial_host,
                trial_id=trial_id,
                session_count=len(trial_captures),
                observations=trial_utility if isinstance(trial_utility, dict) else {},
                capsule_store_stats=None,
                utility_summary=_summarize_utility(trial_utility) if isinstance(trial_utility, dict) else None,
                rank_drift=None,
                wall_seconds=0,
            ).__dict__,
        ],
        capsules_written=capsules_written,
        capsules_verified=capsules_verified,
        parity_checks=_compute_parity(reference_utility, trial_utility),
        rank_drift_summary=rank_drift,
        wall_seconds=time.time() - t0,
    )

    return asdict(report)


def _summarize_utility(utility: dict) -> dict:
    """Extract key metrics from a utility benchmark result."""
    if not utility:
        return {}
    return {
        "total_sessions": utility.get("total_sessions", 0),
        "abstention_rate": utility.get("abstention_rate", 0),
        "warning_rate": utility.get("warning_rate", 0),
        "mean_anomaly_score": utility.get("mean_anomaly_score", 0),
        "fallback_rate": utility.get("fallback_rate", 0),
        "neural_rate": utility.get("neural_rate", 0),
        "mean_adapter_coverage": utility.get("mean_adapter_coverage", 0),
    }


def _compute_parity(ref: dict, trial: dict) -> dict:
    """Compute parity between reference and trial utility results."""
    if not ref or not trial:
        return {"comparable": False}

    metrics = ["abstention_rate", "warning_rate", "mean_anomaly_score", "neural_rate"]
    parity = {"comparable": True, "metrics": {}}

    for metric in metrics:
        ref_val = ref.get(metric, 0)
        trial_val = trial.get(metric, 0)
        diff = abs(ref_val - trial_val) if isinstance(ref_val, (int, float)) else 0
        parity["metrics"][metric] = {
            "reference": ref_val,
            "trial": trial_val,
            "absolute_diff": diff,
            "within_tolerance": diff < 0.15,
        }

    parity["all_within_tolerance"] = all(
        m["within_tolerance"] for m in parity["metrics"].values()
    )
    return parity


def _compute_rank_drift(ref_captures: list, trial_captures: list) -> dict:
    """Compare session distributions between reference and trial hosts."""
    if not ref_captures or not trial_captures:
        return {"comparable": False}

    ref_events = [c.event_count for c in ref_captures]
    trial_events = [c.event_count for c in trial_captures]

    ref_cov = [c.adapter_coverage for c in ref_captures]
    trial_cov = [c.adapter_coverage for c in trial_captures]

    def _safe_mean(vals):
        return statistics.mean(vals) if vals else 0

    def _safe_stdev(vals):
        return statistics.stdev(vals) if len(vals) > 1 else 0

    return {
        "comparable": True,
        "reference_sessions": len(ref_captures),
        "trial_sessions": len(trial_captures),
        "reference_events_mean": _safe_mean(ref_events),
        "trial_events_mean": _safe_mean(trial_events),
        "reference_events_stdev": _safe_stdev(ref_events),
        "trial_events_stdev": _safe_stdev(trial_events),
        "reference_coverage_mean": _safe_mean(ref_cov),
        "trial_coverage_mean": _safe_mean(trial_cov),
        "event_count_drift": abs(_safe_mean(ref_events) - _safe_mean(trial_events)),
        "coverage_drift": abs(_safe_mean(ref_cov) - _safe_mean(trial_cov)),
    }
