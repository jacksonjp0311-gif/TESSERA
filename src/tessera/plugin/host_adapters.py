from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

import numpy as np

from .contracts import AgentEvent
from .trajectory import TRAJECTORY_FEATURES, vectorize_events


SESSION_SUMMARY_SCHEMA = "TESSERA-SESSION-SUMMARY-v0.1"


def full_session_summary(events: list[AgentEvent]) -> np.ndarray:
    """Return the calibrated mean/std/latest session representation."""
    matrix = vectorize_events(events)
    if len(matrix) == 0:
        raise ValueError("session_summary_requires_events")
    return np.concatenate(
        [matrix.mean(axis=0), matrix.std(axis=0), matrix[-1]],
        axis=0,
    ).astype("float32")


def full_session_feature_names() -> tuple[str, ...]:
    return tuple(
        f"{stat}_{feature}"
        for stat in ("mean", "std", "latest")
        for feature in TRAJECTORY_FEATURES
    )


def effective_session_feature_indices(
    summaries: np.ndarray,
    *,
    relative_tolerance: float = 1e-6,
) -> tuple[int, ...]:
    """Select genuinely varying coordinates without float32 variance ghosts."""
    values = np.asarray(summaries, dtype="float64")
    if values.ndim != 2 or len(values) == 0:
        raise ValueError("effective_feature_selection_requires_matrix")
    span = np.ptp(values, axis=0)
    scale = np.maximum(np.max(np.abs(values), axis=0), 1.0)
    return tuple(
        int(index)
        for index in np.flatnonzero(
            span > float(relative_tolerance) * scale
        )
    )


@dataclass(frozen=True)
class SessionSummaryContract:
    """Versioned projection of the 84-value calibrated session space."""

    selected_indices: tuple[int, ...]
    schema: str = SESSION_SUMMARY_SCHEMA

    @property
    def feature_names(self) -> tuple[str, ...]:
        names = full_session_feature_names()
        return tuple(names[index] for index in self.selected_indices)

    def project(self, events: list[AgentEvent]) -> np.ndarray:
        full = full_session_summary(events)
        return full[np.asarray(self.selected_indices, dtype=int)]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "source_event_schema": "TESSERA-AGENT-EVENT-v0.1",
            "aggregation": ["mean", "std", "latest"],
            "source_features": list(TRAJECTORY_FEATURES),
            "selected_indices": list(self.selected_indices),
            "feature_names": list(self.feature_names),
            "chronology": "one completed session per runtime event",
        }


def summary_event(
    session_id: str,
    timestamp: float,
    vector: np.ndarray,
    contract: SessionSummaryContract,
) -> AgentEvent:
    values = np.asarray(vector, dtype=float).reshape(-1)
    if len(values) != len(contract.feature_names):
        raise ValueError("session_summary_dimension_mismatch")
    return AgentEvent(
        event_id=f"session-summary:{session_id}",
        kind="resource",
        timestamp=float(timestamp),
        features=dict(zip(contract.feature_names, values.tolist())),
        metadata={
            "schema": contract.schema,
            "session_id": str(session_id),
        },
    )


class AgentEventSessionAdapter:
    """Reference adapter for hosts that already emit AgentEvent objects."""

    name = "agent-event-session-adapter"

    def __init__(self, contract: SessionSummaryContract):
        self.contract = contract

    def adapt(
        self,
        session_id: str,
        events: list[AgentEvent],
        *,
        timestamp: float | None = None,
    ) -> AgentEvent:
        vector = self.contract.project(events)
        end = timestamp if timestamp is not None else max(
            event.timestamp for event in events
        )
        return summary_event(session_id, end, vector, self.contract)


class JsonSessionAdapter:
    """Reference adapter for JSON-safe AgentEvent records."""

    name = "json-session-adapter"

    def __init__(self, contract: SessionSummaryContract):
        self.contract = contract

    def adapt(
        self,
        session_id: str,
        records: Iterable[dict[str, Any]],
        *,
        timestamp: float | None = None,
    ) -> AgentEvent:
        events = []
        for record in records:
            value = dict(record)
            value["features"] = {
                str(key): float(item)
                for key, item in value.get("features", {}).items()
            }
            value["metadata"] = {
                str(key): str(item)
                for key, item in value.get("metadata", {}).items()
            }
            events.append(AgentEvent(**value))
        return AgentEventSessionAdapter(self.contract).adapt(
            session_id,
            events,
            timestamp=timestamp,
        )

    @staticmethod
    def serialize(events: list[AgentEvent]) -> list[dict[str, Any]]:
        return [asdict(event) for event in events]
