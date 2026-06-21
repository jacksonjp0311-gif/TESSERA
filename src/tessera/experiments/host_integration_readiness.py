from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from tessera.experiments.trajectory_benchmark import load_trajectory_cohort
from tessera.plugin.host_adapters import (
    SessionSummaryContract,
    full_session_summary,
)
from tessera.plugin.host_integrations import (
    AgentCliMirrorIntegration,
    HermesStreamIntegration,
)
from tessera.plugin.incident_governor import IncidentGovernor


FORBIDDEN_OUTPUT_TOKENS = (
    "must not cross adapter",
    "C:\\private",
    "terminal",
    "agent-cli-fixture",
    "hermes-fixture",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head(path: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=path,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def run_host_integration_readiness(
    *,
    root: str | Path = ".",
    hermes_root: str | Path,
) -> dict:
    root = Path(root).resolve()
    hermes_root = Path(hermes_root).resolve()
    agent_fixture = json.loads(
        (root / "tests/fixtures/host_integrations/agent_cli_session.json")
        .read_text(encoding="utf-8")
    )
    hermes_fixture = json.loads(
        (root / "tests/fixtures/host_integrations/hermes_session.json")
        .read_text(encoding="utf-8")
    )
    router_plan = json.loads(
        (root / "docs/research/EVO032_NEURAL_UNCERTAINTY_ROUTER_PREREGISTRATION.json")
        .read_text(encoding="utf-8")
    )
    trajectories = []
    for cohort in router_plan["cohorts"]:
        trajectories.extend(load_trajectory_cohort(str(root / cohort)))
    raw = np.asarray(
        [full_session_summary(events) for events, _ in trajectories],
        dtype="float32",
    )
    selected = tuple(
        int(index)
        for index in np.flatnonzero(raw[:100].std(axis=0) > 1e-6)
    )
    contract = SessionSummaryContract(selected)

    started = time.perf_counter()
    agent_session = AgentCliMirrorIntegration().adapt(agent_fixture)
    agent_latency = (time.perf_counter() - started) * 1000.0
    started = time.perf_counter()
    hermes_session = HermesStreamIntegration().adapt(
        "hermes-fixture",
        hermes_fixture,
    )
    hermes_latency = (time.perf_counter() - started) * 1000.0
    agent_summary = agent_session.summary_event(contract)
    hermes_summary = hermes_session.summary_event(contract)

    failed_hermes = HermesStreamIntegration().adapt(
        "hermes-failed",
        [
            {"type": "tool_call_finished", "duration": 0.2, "ok": False},
            {"type": "message_stop", "final": True},
        ],
    )
    governor = IncidentGovernor()
    governor.record_outcome(
        failed=failed_hermes.failed,
        terminal_ok=failed_hermes.terminal_ok,
    )
    governed = governor.govern(
        "trusted",
        neural_memory_candidate=True,
    )

    rendered = json.dumps({
        "agent": [
            {"features": event.features, "metadata": event.metadata}
            for event in agent_session.events
        ],
        "hermes": [
            {"features": event.features, "metadata": event.metadata}
            for event in hermes_session.events
        ],
    }, sort_keys=True)
    hermes_source = hermes_root / "gateway/stream_events.py"
    agent_source = root / "agent_cli_mirror/agent_mirror.py"
    checks = {
        "agent_cli_contract_adapted": (
            len(agent_session.events) == 3
            and agent_session.terminal_ok
            and not agent_session.failed
        ),
        "hermes_contract_adapted": (
            len(hermes_session.events) == 4
            and hermes_session.terminal_ok
            and not hermes_session.failed
        ),
        "privacy_denied_payloads_absent": not any(
            token in rendered for token in FORBIDDEN_OUTPUT_TOKENS
        ),
        "summary_contract_matches_calibration": (
            len(agent_summary.features)
            == len(hermes_summary.features)
            == len(contract.feature_names)
            == 5
        ),
        "malformed_records_fail_closed": (
            AgentCliMirrorIntegration().adapt([{"detail": "bad"}])
            .rejected_records == 1
            and HermesStreamIntegration().adapt(
                "bad",
                [{"type": "message_chunk", "text": "secret"}],
            ).rejected_records == 1
        ),
        "host_failure_triggers_incident_latch": (
            governed.route == "abstain"
            and not governed.memory_candidate
        ),
        "adapter_latency_below_10_ms": max(
            agent_latency,
            hermes_latency,
        ) < 10.0,
        "source_contracts_present": (
            agent_source.exists() and hermes_source.exists()
        ),
    }
    return {
        "schema": "TESSERA-EVO-037-HOST-INTEGRATION-v0.1",
        "passed": all(checks.values()),
        "status": (
            "two_host_reference_integration_candidate"
            if all(checks.values())
            else "host_integration_rejected"
        ),
        "checks": checks,
        "metrics": {
            "host_integrations": 2,
            "agent_cli_events": len(agent_session.events),
            "hermes_events": len(hermes_session.events),
            "summary_features": len(contract.feature_names),
            "agent_cli_adapter_latency_ms": agent_latency,
            "hermes_adapter_latency_ms": hermes_latency,
            "rejected_malformed_records": 2,
            "privacy_payload_leaks": 0 if checks[
                "privacy_denied_payloads_absent"
            ] else 1,
        },
        "sources": {
            "agent_cli_mirror": {
                "path": str(agent_source.relative_to(root)),
                "sha256": _sha256(agent_source),
                "repository_commit": _git_head(root),
            },
            "hermes_agent": {
                "path": "gateway/stream_events.py",
                "sha256": _sha256(hermes_source),
                "repository_commit": _git_head(hermes_root),
            },
        },
        "session_contract": contract.as_dict(),
        "independently_operated_production_hosts": 0,
        "claim_boundary": (
            "Two source-bound reference integrations prove adapter "
            "compatibility only. They are not independent production "
            "deployments or evidence of cross-host task utility."
        ),
    }
