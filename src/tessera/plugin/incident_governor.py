from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GovernedRoute:
    route: str
    incident_latched: bool
    memory_candidate: bool
    reason: str
    clean_recovery_streak: int


class IncidentGovernor:
    """Deterministic host-owned failure latch around neural trust routing."""

    def __init__(self, *, recovery_sessions_required: int = 1):
        if recovery_sessions_required < 1:
            raise ValueError("recovery_sessions_required_must_be_positive")
        self.recovery_sessions_required = recovery_sessions_required
        self._latched = False
        self._clean_recovery_streak = 0

    @property
    def incident_latched(self) -> bool:
        return self._latched

    def record_outcome(
        self,
        *,
        failed: bool,
        terminal_ok: bool,
    ) -> None:
        if failed:
            self._latched = True
            self._clean_recovery_streak = 0
            return
        if not self._latched:
            return
        if terminal_ok:
            self._clean_recovery_streak += 1
            if self._clean_recovery_streak >= self.recovery_sessions_required:
                self._latched = False
                self._clean_recovery_streak = 0
        else:
            self._clean_recovery_streak = 0

    def govern(
        self,
        neural_route: str,
        *,
        neural_memory_candidate: bool,
    ) -> GovernedRoute:
        if self._latched:
            return GovernedRoute(
                route="abstain",
                incident_latched=True,
                memory_candidate=False,
                reason="observed_failure_latched",
                clean_recovery_streak=self._clean_recovery_streak,
            )
        trusted = neural_route == "trusted"
        return GovernedRoute(
            route=neural_route,
            incident_latched=False,
            memory_candidate=bool(
                trusted and neural_memory_candidate
            ),
            reason="neural_route",
            clean_recovery_streak=0,
        )
