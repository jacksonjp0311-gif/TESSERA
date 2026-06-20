from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np

from .contracts import AgentEvent


DEFAULT_FEATURES = (
    "duration_ms",
    "token_count",
    "error",
    "retry",
    "files_changed",
    "tests_failed",
    "tool_latency_ms",
    "resource_cost",
    "system_cpu_percent",
    "memory_available_ratio",
    "process_count",
    "subprocess_spawn_ms",
    "disk_read_bytes_delta",
    "disk_write_bytes_delta",
    "disk_read_time_ms_delta",
    "disk_write_time_ms_delta",
)


class EventAdapter(Protocol):
    """Protocol for typed event adapters."""
    kind: str
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]: ...
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]: ...


@dataclass(frozen=True)
class PromptMetadataAdapter:
    kind: str = "prompt_metadata"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "token_count": float(raw.get("token_count", 0)),
            "prompt_length": float(raw.get("prompt_length", 0)),
            "system_prompt_ratio": float(raw.get("system_tokens", 0) / max(1, raw.get("token_count", 1))),
            "history_turns": float(raw.get("history_turns", 0)),
            "tool_count": float(raw.get("tool_count", 0)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        if "token_count" not in raw:
            return False, "missing token_count"
        return True, ""


@dataclass(frozen=True)
class ResponseMetadataAdapter:
    kind: str = "response_metadata"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "token_count": float(raw.get("token_count", 0)),
            "duration_ms": float(raw.get("duration_ms", 0)),
            "finish_reason_length": float(len(raw.get("finish_reason", ""))),
            "has_tool_call": float(raw.get("has_tool_call", False)),
            "reasoning_tokens": float(raw.get("reasoning_tokens", 0)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        if "duration_ms" not in raw:
            return False, "missing duration_ms"
        return True, ""


@dataclass(frozen=True)
class ToolCallAdapter:
    kind: str = "tool_call"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "tool_latency_ms": float(raw.get("latency_ms", 0)),
            "token_count": float(raw.get("input_tokens", 0)),
            "error": float(raw.get("error", False)),
            "retry": float(raw.get("retry_count", 0)),
            "files_changed": float(raw.get("files_changed", 0)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        if "tool_name" not in raw:
            return False, "missing tool_name"
        return True, ""


@dataclass(frozen=True)
class ToolResultAdapter:
    kind: str = "tool_result"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "tool_latency_ms": float(raw.get("latency_ms", 0)),
            "token_count": float(raw.get("output_tokens", 0)),
            "error": float(raw.get("error", False)),
            "retry": float(raw.get("retry_count", 0)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        return True, ""


@dataclass(frozen=True)
class FileChangeAdapter:
    kind: str = "file_change"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "files_changed": float(raw.get("files_changed", 1)),
            "lines_added": float(raw.get("lines_added", 0)),
            "lines_removed": float(raw.get("lines_removed", 0)),
            "token_count": float(raw.get("diff_tokens", 0)),
            "error": float(raw.get("conflict", False)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        if "files_changed" not in raw:
            return False, "missing files_changed"
        return True, ""


@dataclass(frozen=True)
class TestResultAdapter:
    kind: str = "test_result"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "duration_ms": float(raw.get("duration_ms", 0)),
            "tests_failed": float(raw.get("tests_failed", 0)),
            "tests_passed": float(raw.get("tests_passed", 0)),
            "error": float(raw.get("tests_failed", 0) > 0),
            "token_count": float(raw.get("output_tokens", 0)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        return True, ""


@dataclass(frozen=True)
class PlanTransitionAdapter:
    kind: str = "plan_transition"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "token_count": float(raw.get("reasoning_tokens", 0)),
            "duration_ms": float(raw.get("duration_ms", 0)),
            "history_turns": float(raw.get("step_number", 0)),
            "error": float(raw.get("blocked", False)),
            "retry": float(raw.get("revision_count", 0)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        return True, ""


@dataclass(frozen=True)
class ErrorAdapter:
    kind: str = "error"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "error": 1.0,
            "retry": float(raw.get("retry_count", 0)),
            "duration_ms": float(raw.get("duration_ms", 0)),
            "token_count": float(raw.get("error_tokens", 0)),
            "tests_failed": float(raw.get("is_test_failure", False)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        if "error_type" not in raw:
            return False, "missing error_type"
        return True, ""


@dataclass(frozen=True)
class RetryAdapter:
    kind: str = "retry"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "retry": float(raw.get("retry_count", 1)),
            "error": float(raw.get("previous_error", True)),
            "duration_ms": float(raw.get("duration_ms", 0)),
            "token_count": float(raw.get("token_count", 0)),
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        if "retry_count" not in raw:
            return False, "missing retry_count"
        return True, ""


@dataclass(frozen=True)
class ResourceAdapter:
    kind: str = "resource"
    def to_features(self, raw: dict[str, Any]) -> dict[str, float]:
        return {
            "duration_ms": float(raw.get("duration_ms", 0)),
            "token_count": float(raw.get("token_count", 0)),
            "resource_cost": float(raw.get("cost_usd", 0)),
            "error": float(raw.get("rate_limited", False)),
            "retry": float(raw.get("retry_after_ms", 0)) / 1000.0,
        }
    def validate(self, raw: dict[str, Any]) -> tuple[bool, str]:
        return True, ""


# Registry of all typed adapters
ADAPTER_REGISTRY: dict[str, EventAdapter] = {
    "prompt_metadata": PromptMetadataAdapter(),
    "response_metadata": ResponseMetadataAdapter(),
    "tool_call": ToolCallAdapter(),
    "tool_result": ToolResultAdapter(),
    "file_change": FileChangeAdapter(),
    "test_result": TestResultAdapter(),
    "plan_transition": PlanTransitionAdapter(),
    "error": ErrorAdapter(),
    "retry": RetryAdapter(),
    "resource": ResourceAdapter(),
}

# Unified feature dimension across all adapters
TRAJECTORY_FEATURES = (
    "duration_ms",
    "token_count",
    "error",
    "retry",
    "files_changed",
    "tests_failed",
    "tool_latency_ms",
    "resource_cost",
    "prompt_length",
    "system_prompt_ratio",
    "history_turns",
    "tool_count",
    "finish_reason_length",
    "has_tool_call",
    "reasoning_tokens",
    "lines_added",
    "lines_removed",
    "diff_tokens",
    "tests_passed",
    "step_number",
    "blocked",
    "revision_count",
    "error_tokens",
    "is_test_failure",
    "previous_error",
    "cost_usd",
    "rate_limited",
    "retry_after_ms",
)


def vectorize_events(
    events: list[AgentEvent],
    feature_names: tuple[str, ...] = TRAJECTORY_FEATURES,
) -> np.ndarray:
    """Convert agent events to a fixed-dimension feature matrix.

    Uses the unified TRAJECTORY_FEATURES space so that events of different
    kinds are comparable in the same latent space.
    """
    rows = [
        [float(event.features.get(feature, 0.0)) for feature in feature_names]
        for event in events
    ]
    if not rows:
        return np.empty((0, len(feature_names)), dtype="float32")
    return np.asarray(rows, dtype="float32")


def adapt_raw_event(kind: str, raw: dict[str, Any]) -> dict[str, float]:
    """Adapt a raw event dict using the typed adapter for its kind."""
    adapter = ADAPTER_REGISTRY.get(kind)
    if adapter is None:
        return {}
    valid, reason = adapter.validate(raw)
    if not valid:
        return {}
    return adapter.to_features(raw)


def create_agent_event(
    event_id: str,
    kind: str,
    raw: dict[str, Any],
    timestamp: float | None = None,
    metadata: dict[str, str] | None = None,
) -> AgentEvent:
    """Create an AgentEvent from a raw event dict using the typed adapter."""
    features = adapt_raw_event(kind, raw)
    return AgentEvent(
        event_id=event_id,
        kind=kind,
        timestamp=timestamp or time.time(),
        features=features,
        metadata=metadata or {},
    )


def trajectory_hash(events: list[AgentEvent]) -> str:
    """Compute a deterministic hash of an event trajectory."""
    content = json.dumps(
        [{"id": e.event_id, "kind": e.kind, "ts": e.timestamp} for e in events],
        sort_keys=True,
    )
    return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class TrajectorySummary:
    """Summary statistics for an agent trajectory."""
    event_count: int
    kinds: dict[str, int]
    total_duration_ms: float
    error_count: int
    retry_count: float
    total_tokens: float
    trajectory_hash: str
    adapter_coverage: float  # fraction of events with typed adapters


def summarize_trajectory(events: list[AgentEvent]) -> TrajectorySummary:
    """Compute summary statistics for an agent trajectory."""
    kinds: dict[str, int] = {}
    total_duration = 0.0
    error_count = 0
    retry_count = 0.0
    total_tokens = 0.0
    adapted = 0
    for event in events:
        kinds[event.kind] = kinds.get(event.kind, 0) + 1
        total_duration += event.features.get("duration_ms", 0.0)
        error_count += int(event.features.get("error", 0.0))
        retry_count += event.features.get("retry", 0.0)
        total_tokens += event.features.get("token_count", 0.0)
        if event.kind in ADAPTER_REGISTRY:
            adapted += 1
    return TrajectorySummary(
        event_count=len(events),
        kinds=kinds,
        total_duration_ms=total_duration,
        error_count=error_count,
        retry_count=retry_count,
        total_tokens=total_tokens,
        trajectory_hash=trajectory_hash(events),
        adapter_coverage=adapted / max(1, len(events)),
    )
