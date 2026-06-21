from __future__ import annotations

from pathlib import Path

from tessera.experiments.production_candidate import (
    run_production_candidate,
)
from tessera.experiments.release_readiness import run_release_readiness


def run_launch_readiness(root: str | Path = ".") -> dict:
    """Run latency-sensitive runtime checks before release construction."""
    production = run_production_candidate(root)
    release = run_release_readiness(root)
    passed = bool(production["passed"] and release["passed"])
    return {
        "schema": "TESSERA-EVO-035-LAUNCH-READINESS-v0.1",
        "passed": passed,
        "status": (
            "repository_launch_candidate"
            if passed
            else "repository_launch_candidate_rejected"
        ),
        "certification_order": [
            "runtime_semantic_latency_restart_rollback_soak",
            "wheel_build_integrity_install_smoke",
        ],
        "production_candidate": {
            "passed": production["passed"],
            "checks": production["checks"],
            "metrics": production["metrics"],
        },
        "release_readiness": {
            "passed": release["passed"],
            "checks": release["checks"],
            "version": release["version"],
            "wheel": release["wheel"],
        },
        "external_launch_gates": release["remaining_external_gates"],
        "claim_boundary": (
            "Repository launch candidacy certifies local runtime and package "
            "gates in a non-contending order. External host, security, "
            "failure-recovery, clean-environment, and cross-platform gates "
            "remain open."
        ),
    }
