from __future__ import annotations

import math
import multiprocessing as mp
import queue
import time
from dataclasses import asdict
from typing import Callable

from .contracts import (
    AgentEvent,
    ObservationReceipt,
    RuntimeBudget,
    RuntimeHealth,
    RuntimeResult,
)
from .runtime import TesseraPlugin


def _infer_worker(
    events: list[AgentEvent],
    plugin_options: dict,
    output_queue,
) -> None:
    try:
        plugin = TesseraPlugin(**plugin_options)
        receipt = plugin.observe(events)
        if receipt.rejected:
            output_queue.put({
                "status": "rejected",
                "error_code": "worker_event_rejection",
            })
            return
        output_queue.put({
            "status": "ok",
            "packet": asdict(plugin.infer()),
        })
    except BaseException:
        output_queue.put({
            "status": "failed",
            "error_code": "worker_inference_failure",
        })


def _persistent_worker(request_queue, output_queue, plugin_options) -> None:
    while True:
        request = request_queue.get()
        if request is None:
            return
        try:
            plugin = TesseraPlugin(**plugin_options)
            receipt = plugin.observe(request["events"])
            if receipt.rejected:
                output_queue.put({
                    "request_id": request["request_id"],
                    "status": "rejected",
                    "error_code": "worker_event_rejection",
                })
                continue
            output_queue.put({
                "request_id": request["request_id"],
                "status": "ok",
                "packet": asdict(plugin.infer()),
            })
        except BaseException:
            output_queue.put({
                "request_id": request["request_id"],
                "status": "failed",
                "error_code": "worker_inference_failure",
            })


class PluginSupervisor:
    """Fail-closed host boundary for Tessera inference.

    Each inference runs in a disposable local subprocess. A timeout or crash is
    contained, returns no proposal, and contributes to a circuit breaker.
    """

    def __init__(
        self,
        *,
        budget: RuntimeBudget | None = None,
        plugin_options: dict | None = None,
        process_target: Callable | None = None,
    ):
        self.budget = budget or RuntimeBudget()
        self.plugin_options = {
            "inline_neural_training": False,
            **dict(plugin_options or {}),
        }
        self._process_target = process_target
        self._events: list[AgentEvent] = []
        self._lifecycle = "created"
        self._warmed = False
        self._consecutive_failures = 0
        self._total_requests = 0
        self._successful_requests = 0
        self._timed_out_requests = 0
        self._failed_requests = 0
        self._last_latency_ms = 0.0
        self._process = None
        self._request_queue = None
        self._output_queue = None
        self._request_id = 0

    def observe(self, events: list[AgentEvent]):
        if self._lifecycle == "unloaded":
            return ObservationReceipt(
                accepted=0,
                rejected=len(events),
                reasons=("runtime_unloaded",),
                buffer_size=0,
            )
        reasons: list[str] = []
        accepted = 0
        for event in events:
            reason = self._validate_event(event)
            if reason:
                reasons.append(f"{reason}:{event.event_id}")
                continue
            self._events.append(event)
            accepted += 1
        if len(self._events) > self.budget.max_events:
            self._events = self._events[-self.budget.max_events :]
        return ObservationReceipt(
            accepted=accepted,
            rejected=len(events) - accepted,
            reasons=tuple(reasons),
            buffer_size=len(self._events),
        )

    def infer(self) -> RuntimeResult:
        if self._lifecycle == "unloaded":
            return self._closed_result("runtime_unloaded")
        if self._circuit_open:
            return self._closed_result("circuit_open")

        self._total_requests += 1
        started = time.perf_counter()
        if self._process_target is not None:
            payload = self._run_one_shot(started)
            if isinstance(payload, RuntimeResult):
                return payload
        else:
            self._ensure_worker()
            self._request_id += 1
            self._request_queue.put({
                "request_id": self._request_id,
                "events": list(self._events),
            })
            try:
                payload = self._output_queue.get(
                    timeout=self.budget.timeout_ms / 1000.0
                )
            except queue.Empty:
                self._timed_out_requests += 1
                self._stop_worker()
                return self._failure_result(started, "hard_timeout")
            if payload.get("request_id") != self._request_id:
                self._failed_requests += 1
                self._stop_worker()
                return self._failure_result(started, "worker_protocol_error")

        if payload.get("status") != "ok":
            self._failed_requests += 1
            return self._failure_result(
                started,
                str(payload.get("error_code", "worker_failure")),
            )

        from .contracts import InferencePacket

        packet = InferencePacket(**payload["packet"])
        self._last_latency_ms = (time.perf_counter() - started) * 1000.0
        self._successful_requests += 1
        self._consecutive_failures = 0
        self._warmed = True
        self._lifecycle = "ready"
        return RuntimeResult(
            status="ok",
            packet=packet,
            latency_ms=self._last_latency_ms,
            error_code=None,
            host_contained=True,
            claim_boundary=(
                "Successful supervised inference is not production readiness "
                "or authority to mutate the host."
            ),
        )

    def warmup(self) -> RuntimeResult:
        """Start the isolated worker before host traffic reaches the plugin."""
        return self.infer()

    def reset_circuit(self) -> bool:
        if self._lifecycle == "unloaded":
            return False
        self._consecutive_failures = 0
        return True

    def unload(self) -> None:
        self._stop_worker(graceful=True)
        self._events.clear()
        self._lifecycle = "unloaded"

    def health(self) -> RuntimeHealth:
        if self._lifecycle == "unloaded":
            status = "unloaded"
        elif self._circuit_open:
            status = "degraded"
        elif not self._warmed:
            status = "starting"
        else:
            status = "ready"
        return RuntimeHealth(
            schema="TESSERA-PLUGIN-HEALTH-v0.1",
            status=status,
            lifecycle=self._lifecycle,
            consecutive_failures=self._consecutive_failures,
            total_requests=self._total_requests,
            successful_requests=self._successful_requests,
            timed_out_requests=self._timed_out_requests,
            failed_requests=self._failed_requests,
            last_latency_ms=self._last_latency_ms,
            circuit_open=self._circuit_open,
            claim_boundary=(
                "Runtime health reports local containment state only; it does "
                "not prove capability, safety, or production readiness."
            ),
        )

    @property
    def _circuit_open(self) -> bool:
        return (
            self._consecutive_failures
            >= self.budget.max_consecutive_failures
        )

    def _failure_result(
        self,
        started: float,
        error_code: str,
    ) -> RuntimeResult:
        self._last_latency_ms = (time.perf_counter() - started) * 1000.0
        self._consecutive_failures += 1
        return RuntimeResult(
            status="contained_failure",
            packet=None,
            latency_ms=self._last_latency_ms,
            error_code=error_code,
            host_contained=True,
            claim_boundary=(
                "Contained plugin failure emits no warning, memory, repair, "
                "tool, or host-mutation authority."
            ),
        )

    def _closed_result(self, error_code: str) -> RuntimeResult:
        return RuntimeResult(
            status="unavailable",
            packet=None,
            latency_ms=0.0,
            error_code=error_code,
            host_contained=True,
            claim_boundary=(
                "Unavailable runtime fails closed and emits no proposal or "
                "host-mutation authority."
            ),
        )

    def _validate_event(self, event: AgentEvent) -> str | None:
        if event.kind not in TesseraPlugin.ALLOWED_EVENT_KINDS:
            return "event_kind_blocked"
        if event.contains_sensitive_data:
            return "sensitive_event_blocked"
        if len(event.features) > self.budget.max_feature_count:
            return "feature_budget_exceeded"
        if len(event.metadata) > self.budget.max_metadata_count:
            return "metadata_budget_exceeded"
        if not math.isfinite(float(event.timestamp)):
            return "invalid_timestamp"
        for value in event.features.values():
            try:
                if not math.isfinite(float(value)):
                    return "nonfinite_feature"
            except (TypeError, ValueError):
                return "nonnumeric_feature"
        return None

    def _ensure_worker(self) -> None:
        if self._process is not None and self._process.is_alive():
            return
        context = mp.get_context("spawn")
        self._request_queue = context.Queue(maxsize=1)
        self._output_queue = context.Queue(maxsize=1)
        self._process = context.Process(
            target=_persistent_worker,
            args=(
                self._request_queue,
                self._output_queue,
                self.plugin_options,
            ),
        )
        self._process.start()

    def _stop_worker(self, *, graceful: bool = False) -> None:
        if self._process is None:
            return
        if graceful and self._process.is_alive():
            self._request_queue.put(None)
            self._process.join(timeout=2.0)
        if self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=2.0)
        for channel in (self._request_queue, self._output_queue):
            if channel is not None:
                channel.close()
        self._process = None
        self._request_queue = None
        self._output_queue = None

    def _run_one_shot(self, started: float):
        context = mp.get_context("spawn")
        output_queue = context.Queue(maxsize=1)
        process = context.Process(
            target=self._process_target,
            args=(list(self._events), self.plugin_options, output_queue),
        )
        process.start()
        process.join(self.budget.timeout_ms / 1000.0)
        if process.is_alive():
            process.terminate()
            process.join(timeout=2.0)
            output_queue.close()
            self._timed_out_requests += 1
            return self._failure_result(started, "hard_timeout")
        try:
            return output_queue.get(timeout=1.0)
        except queue.Empty:
            self._failed_requests += 1
            return self._failure_result(started, "worker_no_result")
        finally:
            output_queue.close()
