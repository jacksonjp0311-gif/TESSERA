from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from .contracts import AgentEvent
from .host_adapters import (
    AgentEventSessionAdapter,
    SessionSummaryContract,
)


HOST_INTEGRATION_SCHEMA = "TESSERA-HOST-INTEGRATION-v0.1"


def _timestamp(value: Any, fallback: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return fallback


def _safe_id(host: str, session_id: str, index: int) -> str:
    digest = hashlib.sha256(
        f"{host}:{session_id}:{index}".encode("utf-8")
    ).hexdigest()[:16]
    return f"{host}:{digest}"


@dataclass(frozen=True)
class HostSession:
    host: str
    session_id_hash: str
    events: tuple[AgentEvent, ...]
    failed: bool
    terminal_ok: bool
    rejected_records: int
    schema: str = HOST_INTEGRATION_SCHEMA

    def summary_event(
        self,
        contract: SessionSummaryContract,
    ) -> AgentEvent:
        return AgentEventSessionAdapter(contract).adapt(
            self.session_id_hash,
            list(self.events),
        )


class AgentCliMirrorIntegration:
    """Privacy-safe adapter for Agent CLI Mirror JSONL records."""

    name = "agent-cli-mirror"
    source_schema = "AGENT-CLI-MIRROR-v0.3.9"

    def adapt(self, records: Iterable[dict[str, Any]]) -> HostSession:
        values = list(records)
        session_id = str(
            next(
                (
                    value.get("session_id")
                    for value in values
                    if value.get("session_id")
                ),
                "unknown",
            )
        )
        events = []
        rejected = 0
        failed = False
        terminal_ok = False
        for index, record in enumerate(values):
            phase = str(record.get("phase", "")).upper()
            state = str(record.get("state", "")).upper()
            if not phase or state not in {"RUN", "OK", "FAIL", "SKIP"}:
                rejected += 1
                continue
            failed = failed or state == "FAIL"
            terminal_ok = terminal_ok or (
                phase == "ROOT" and state == "OK"
            )
            events.append(AgentEvent(
                event_id=_safe_id(self.name, session_id, index),
                kind=(
                    "error" if state == "FAIL"
                    else "plan_transition"
                ),
                timestamp=_timestamp(record.get("timestamp"), float(index)),
                features={
                    "duration_ms": float(record.get("elapsed_ms") or 0.0),
                    "error": float(state == "FAIL"),
                    "blocked": float(state in {"FAIL", "SKIP"}),
                    "history_turns": float(record.get("event_index") or index + 1),
                    "system_cpu_percent": float(
                        record.get("system_cpu_percent") or 0.0
                    ),
                    "memory_available_ratio": float(
                        record.get("memory_available_ratio") or 0.0
                    ),
                    "process_count": float(record.get("process_count") or 0.0),
                    "subprocess_spawn_ms": float(
                        record.get("subprocess_spawn_ms") or 0.0
                    ),
                    "disk_read_bytes_delta": float(
                        record.get("disk_read_bytes_delta") or 0.0
                    ),
                    "disk_write_bytes_delta": float(
                        record.get("disk_write_bytes_delta") or 0.0
                    ),
                    "disk_read_time_ms_delta": float(
                        record.get("disk_read_time_ms_delta") or 0.0
                    ),
                    "disk_write_time_ms_delta": float(
                        record.get("disk_write_time_ms_delta") or 0.0
                    ),
                },
                metadata={
                    "host": self.name,
                    "phase": phase,
                    "state": state,
                },
            ))
        return HostSession(
            host=self.name,
            session_id_hash=hashlib.sha256(
                session_id.encode("utf-8")
            ).hexdigest()[:16],
            events=tuple(events),
            failed=failed,
            terminal_ok=terminal_ok and not failed,
            rejected_records=rejected,
        )


class HermesStreamIntegration:
    """Metadata-only adapter for Hermes gateway stream/session events."""

    name = "hermes-agent"
    source_schema = "HERMES-STREAM-EVENTS-v1"
    allowed_types = {
        "tool_call_chunk",
        "tool_call_finished",
        "message_stop",
        "gateway_notice",
        "session_summary",
    }

    def adapt(
        self,
        session_id: str,
        records: Iterable[dict[str, Any]],
    ) -> HostSession:
        events = []
        rejected = 0
        failed = False
        terminal_ok = False
        for index, record in enumerate(records):
            event_type = str(record.get("type", "")).lower()
            if event_type not in self.allowed_types:
                rejected += 1
                continue
            timestamp = _timestamp(record.get("timestamp"), float(index))
            if event_type == "tool_call_chunk":
                kind = "tool_call"
                features = {
                    "tool_count": 1.0,
                    "history_turns": float(index + 1),
                }
            elif event_type == "tool_call_finished":
                ok = bool(record.get("ok", True))
                failed = failed or not ok
                kind = "tool_result" if ok else "error"
                features = {
                    "tool_latency_ms": float(record.get("duration") or 0.0)
                    * 1000.0,
                    "error": float(not ok),
                    "history_turns": float(index + 1),
                }
            elif event_type == "message_stop":
                terminal_ok = terminal_ok or bool(record.get("final", False))
                kind = "response_metadata"
                features = {
                    "history_turns": float(index + 1),
                }
            elif event_type == "gateway_notice":
                notice = str(record.get("kind", "")).lower()
                notice_failed = notice in {"error", "failed", "offline"}
                failed = failed or notice_failed
                kind = "error" if notice_failed else "plan_transition"
                features = {
                    "error": float(notice_failed),
                    "blocked": float(notice_failed),
                    "history_turns": float(index + 1),
                }
            else:
                end_reason = str(record.get("end_reason", "")).lower()
                summary_failed = end_reason in {
                    "error", "failed", "timeout", "cancelled",
                }
                failed = failed or summary_failed
                terminal_ok = terminal_ok or (
                    bool(record.get("ended_at")) and not summary_failed
                )
                kind = "resource"
                features = {
                    "token_count": float(
                        (record.get("input_tokens") or 0)
                        + (record.get("output_tokens") or 0)
                    ),
                    "tool_count": float(record.get("tool_call_count") or 0),
                    "history_turns": float(record.get("message_count") or 0),
                    "error": float(summary_failed),
                }
            events.append(AgentEvent(
                event_id=_safe_id(self.name, session_id, index),
                kind=kind,
                timestamp=timestamp,
                features=features,
                metadata={
                    "host": self.name,
                    "event_type": event_type,
                },
            ))
        return HostSession(
            host=self.name,
            session_id_hash=hashlib.sha256(
                session_id.encode("utf-8")
            ).hexdigest()[:16],
            events=tuple(events),
            failed=failed,
            terminal_ok=terminal_ok and not failed,
            rejected_records=rejected,
        )
