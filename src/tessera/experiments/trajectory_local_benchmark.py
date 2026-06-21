from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from tessera.plugin.privacy_capture import (
    capture_local_trajectories,
    audit_trajectory_identifiability,
)
from tessera.plugin.trajectory import (
    ADAPTER_REGISTRY,
    TRAJECTORY_FEATURES,
    create_agent_event,
    summarize_trajectory,
    trajectory_hash,
    vectorize_events,
)
from tessera.plugin.contracts import AgentEvent


LOCAL_CAPTURE_SCHEMA = "TESSERA-LOCAL-CAPTURE-v0.1"


@dataclass
class LocalSessionCapture:
    """A captured and sanitized local agent session."""
    session_id_hash: str
    source: str
    captured_at: float
    event_count: int
    events: list[AgentEvent]
    summary: dict
    identifiability_risk: str
    adapter_coverage: float


def capture_agent_cli_sessions(
    events_path: str | Path,
    *,
    minimum_prefix: int = 7,
    last_enriched_sessions: int | None = None,
    session_ids: list[str] | None = None,
) -> list[LocalSessionCapture]:
    """Capture Agent CLI Mirror sessions from a JSONL file.

    Each line in the file should be a JSON array of event records.
    Returns a list of sanitized LocalSessionCapture objects.
    """
    events_path = Path(events_path)
    if not events_path.exists():
        raise FileNotFoundError(f"events file not found: {events_path}")

    raw_sessions: list[list[dict]] = []
    with open(events_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records = json.loads(line)
                if isinstance(records, list):
                    raw_sessions.append(records)
            except json.JSONDecodeError:
                continue

    captures = []
    for raw_session in raw_sessions:
        if len(raw_session) < minimum_prefix:
            continue

        if session_ids is not None:
            session_id = str(raw_session[0].get("session_id", ""))
            if session_id not in session_ids:
                continue

        events = []
        for index, record in enumerate(raw_session):
            kind = str(record.get("kind", record.get("type", "test_result")))
            if kind not in ADAPTER_REGISTRY:
                kind = "test_result"
            try:
                event = create_agent_event(
                    event_id=f"local-{index}",
                    kind=kind,
                    raw=record,
                    timestamp=float(record.get("timestamp", index)),
                    metadata={
                        "phase": str(record.get("phase", "UNKNOWN")),
                        "state": str(record.get("state", "OK")),
                        "source": "agent_cli_mirror",
                    },
                )
                events.append(event)
            except Exception:
                continue

        if len(events) < minimum_prefix:
            continue

        summary = summarize_trajectory(events)
        captures.append(LocalSessionCapture(
            session_id_hash=summary.trajectory_hash,
            source="agent_cli_mirror",
            captured_at=time.time(),
            event_count=len(events),
            events=events,
            summary=asdict(summary),
            identifiability_risk="low",
            adapter_coverage=summary.adapter_coverage,
        ))

    if last_enriched_sessions is not None:
        captures = captures[-last_enriched_sessions:]

    return captures


def run_local_utility_benchmark(
    captures: list[LocalSessionCapture],
    *,
    plugin_options: dict | None = None,
) -> dict:
    """Run Tessera against captured local sessions and measure utility.

    Returns coverage, drift, warnings, memory proposals, and abstention rate.
    """
    from tessera.plugin import TesseraPlugin

    plugin_options = plugin_options or {
        "neural_min_events": 8,
        "inline_neural_training": True,
    }

    results = []
    for capture in captures:
        plugin = TesseraPlugin(**plugin_options)
        receipt = plugin.observe(capture.events)
        packet = plugin.infer()
        memory = plugin.propose_memory()
        checkpoint = plugin.checkpoint()

        results.append({
            "session_id_hash": capture.session_id_hash,
            "event_count": capture.event_count,
            "adapter_coverage": capture.adapter_coverage,
            "status": packet.status,
            "trust_route": getattr(packet, "trust_route", "not_routed"),
            "abstained": getattr(packet, "abstained", False),
            "warning": packet.warning,
            "memory_candidate": packet.memory_candidate,
            "memory_approved": memory.approved,
            "anomaly_score": packet.anomaly_score,
            "prediction_loss": packet.prediction_loss,
            "receipt_accepted": receipt.accepted,
            "receipt_rejected": receipt.rejected,
        })

    # Compute aggregate statistics
    total = len(results)
    if total == 0:
        return {"total_sessions": 0, "results": results}

    abstained = sum(1 for r in results if r["abstained"])
    warned = sum(1 for r in results if r["warning"])
    memory_proposed = sum(1 for r in results if r["memory_candidate"])
    memory_approved = sum(1 for r in results if r["memory_approved"])
    fallback = sum(1 for r in results if r["status"] == "fallback")
    neural = sum(1 for r in results if r["status"] == "neural")
    admitted = sum(1 for r in results if r["status"] == "admitted_neural_checkpoint")
    insufficient = sum(1 for r in results if r["status"] == "insufficient_context")

    return {
        "schema": "TESSERA-LOCAL-UTILITY-BENCHMARK-v0.1",
        "total_sessions": total,
        "abstention_rate": abstained / total,
        "warning_rate": warned / total,
        "memory_proposal_rate": memory_proposed / total,
        "memory_approval_rate": memory_approved / max(1, memory_proposed),
        "fallback_rate": fallback / total,
        "neural_rate": neural / total,
        "admitted_checkpoint_rate": admitted / total,
        "insufficient_context_rate": insufficient / total,
        "mean_anomaly_score": float(sum(r["anomaly_score"] for r in results) / total),
        "mean_prediction_loss": float(sum(r["prediction_loss"] for r in results) / total),
        "mean_adapter_coverage": float(sum(r["adapter_coverage"] for r in results) / total),
        "results": results,
        "claim_boundary": (
            "Local utility benchmark measures offline behavior on captured sessions. "
            "It does not establish live agent utility, production readiness, or autonomous authority."
        ),
    }
