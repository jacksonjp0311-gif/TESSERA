from __future__ import annotations

from pathlib import Path

from tessera.experiments.production_candidate import (
    run_production_candidate,
)
from tessera.experiments.release_readiness import run_release_readiness
from tessera.experiments.local_security_readiness import (
    run_local_security_readiness,
)


def run_launch_readiness(root: str | Path = ".") -> dict:
    """Run latency-sensitive runtime checks before release construction."""
    production = run_production_candidate(root)
    security = run_local_security_readiness(root)
    release = run_release_readiness(root)
    passed = bool(
        production["passed"]
        and security["passed"]
        and release["passed"]
    )
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
            "local_static_security_and_secret_scan",
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
        "local_security_readiness": {
            "passed": security["passed"],
            "checks": security["checks"],
            "metrics": security["metrics"],
            "external_security_review_complete": security[
                "external_security_review_complete"
            ],
        },
        "external_launch_gates": release["remaining_external_gates"],
        "claim_boundary": (
            "Repository launch candidacy certifies local runtime and package "
            "gates in a non-contending order. External host, security, "
            "failure-recovery, clean-environment, and cross-platform gates "
            "remain open."
        ),
    }
