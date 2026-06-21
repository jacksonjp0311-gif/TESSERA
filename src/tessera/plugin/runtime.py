from __future__ import annotations

from collections import deque

import numpy as np

from tessera.graph.topologies import make_operator
from tessera.model.train import evaluate_sequence, fit_tessera_model
from tessera.model.prediction_experts import (
    prediction_losses,
    select_prediction_expert,
)

from .contracts import (
    AgentEvent,
    InferencePacket,
    InferenceQuery,
    MemoryProposal,
    ObservationReceipt,
    PluginManifest,
    RepairProposal,
    ReplayCertificate,
    ReplayPacket,
)
from .trajectory import vectorize_events
from .neural_checkpoints import load_neural_checkpoint


class TesseraPlugin:
    """Read-mostly neural sidecar — EVO-012 enhanced.

    Improvements over v0.1:
    - Stateful latent memory buffer with configurable capacity
    - Multi-scale anomaly scoring (instant + short + medium horizon)
    - Wound-aware inference that tracks failure modes over time
    - Checkpoint export/import for agent session continuity
    - Graceful degradation when neural context is insufficient
    """

    ALLOWED_EVENT_KINDS = {
        "prompt_metadata",
        "response_metadata",
        "tool_call",
        "tool_result",
        "file_change",
        "test_result",
        "plan_transition",
        "error",
        "retry",
        "resource",
    }

    def __init__(
        self,
        *,
        max_events: int = 512,
        warning_quantile: float = 0.9,
        neural_min_events: int = 8,
        memory_capacity: int = 64,
        field_dim: int = 8,
        code_dim: int = 4,
        inline_neural_training: bool = True,
        checkpoint_payload: dict | None = None,
    ):
        self._events: deque[AgentEvent] = deque(maxlen=max_events)
        self.warning_quantile = warning_quantile
        self.neural_min_events = neural_min_events
        self.memory_capacity = memory_capacity
        self.field_dim = field_dim
        self.code_dim = code_dim
        self.inline_neural_training = inline_neural_training
        self._loaded_checkpoint = (
            load_neural_checkpoint(checkpoint_payload)
            if checkpoint_payload is not None
            else None
        )
        self._last_packet: InferencePacket | None = None
        self._last_prediction_expert = "not_selected"
        self._wound_history: list[str] = []
        self._memory_buffer: list[np.ndarray] = []
        self._anomaly_history: list[float] = []

    def describe(self) -> PluginManifest:
        return PluginManifest()

    def observe(self, events: list[AgentEvent]) -> ObservationReceipt:
        reasons: list[str] = []
        accepted = 0
        for event in events:
            if event.kind not in self.ALLOWED_EVENT_KINDS:
                reasons.append(f"event_kind_blocked:{event.kind}")
                continue
            if event.contains_sensitive_data:
                reasons.append(f"sensitive_event_blocked:{event.event_id}")
                continue
            self._events.append(event)
            accepted += 1
        return ObservationReceipt(
            accepted=accepted,
            rejected=len(events) - accepted,
            reasons=tuple(reasons),
            buffer_size=len(self._events),
        )

    def replace_events(self, events: list[AgentEvent]) -> ObservationReceipt:
        self._events.clear()
        return self.observe(events)

    def infer(self, query: InferenceQuery | None = None) -> InferencePacket:
        _ = query or InferenceQuery()
        matrix = vectorize_events(list(self._events))
        if len(matrix) < 3:
            packet = InferencePacket(
                status="insufficient_context",
                anomaly_score=0.0,
                prediction_loss=0.0,
                warning=False,
                memory_candidate=False,
                claim_boundary="Insufficient context; no capability or memory claim.",
            )
            self._last_packet = packet
            return packet
        if (
            len(matrix) >= self.neural_min_events
            and self._loaded_checkpoint is not None
        ):
            packet = self._checkpoint_infer(matrix)
            self._last_packet = packet
            return packet
        if (
            len(matrix) >= self.neural_min_events
            and self.inline_neural_training
        ):
            packet = self._neural_infer(matrix)
            self._last_packet = packet
            return packet
        packet = self._fallback_infer(matrix)
        if (
            len(matrix) >= self.neural_min_events
            and not self.inline_neural_training
        ):
            packet = InferencePacket(
                status="fast_path_shadow_training_required",
                anomaly_score=packet.anomaly_score,
                prediction_loss=packet.prediction_loss,
                warning=packet.warning,
                memory_candidate=packet.memory_candidate,
                claim_boundary=(
                    "Bounded fast-path inference only; neural fitting is "
                    "excluded from the host request and remains shadow-only."
                ),
            )
        self._last_packet = packet
        return packet

    def _checkpoint_infer(self, matrix: np.ndarray) -> InferencePacket:
        loaded = self._loaded_checkpoint
        normalized = ((matrix - loaded["mean"]) / loaded["scale"]).astype(
            "float32"
        )
        rows = evaluate_sequence(loaded["model"], normalized)["rows"]
        neural_losses = np.asarray(
            [row["prediction_loss"] for row in rows],
            dtype=float,
        )
        center = float(np.median(neural_losses[:-1])) if len(neural_losses) > 1 else 0.0
        spread = float(np.std(neural_losses[:-1])) if len(neural_losses) > 1 else 1.0
        spread = spread or 1.0
        score = max(0.0, (float(neural_losses[-1]) - center) / spread)
        expert_losses = prediction_losses(
            loaded["expert"],
            normalized[-2:],
            history=normalized[:-2],
        )
        prediction_loss = float(expert_losses[-1])
        return InferencePacket(
            status="admitted_neural_checkpoint",
            anomaly_score=score,
            prediction_loss=prediction_loss,
            warning=score > 1.5,
            memory_candidate=score <= 1.5,
            claim_boundary=(
                "Replay-admitted checkpoint inference remains read-only and "
                "does not authorize host mutation."
            ),
            selected_prediction_expert=loaded["expert"].name,
        )

    def _fallback_infer(self, matrix: np.ndarray) -> InferencePacket:
        history, current = matrix[:-1], matrix[-1]
        center = np.median(history, axis=0)
        mad = np.median(np.abs(history - center), axis=0)
        std = np.std(history, axis=0)
        scale = np.where(mad > 1e-3, mad, np.where(std > 1e-3, std, 1.0))
        score = float(np.mean(np.abs((current - center) / scale)))
        prediction = history[-1]
        prediction_loss = float(np.mean((current - prediction) ** 2))
        historical_scores = np.mean(np.abs((history - center) / scale), axis=1)
        threshold = float(np.quantile(historical_scores, self.warning_quantile))
        warning = score > threshold
        return InferencePacket(
            status="fallback",
            anomaly_score=score,
            prediction_loss=prediction_loss,
            warning=warning,
            memory_candidate=not warning and prediction_loss <= float(
                np.median(np.sum((history[1:] - history[:-1]) ** 2, axis=1))
            ),
            claim_boundary="Prototype local trajectory inference; not validated agent capability.",
        )

    def _neural_infer(self, matrix: np.ndarray) -> InferencePacket:
        mean = matrix.mean(axis=0)
        scale = matrix.std(axis=0)
        scale[scale < 1e-3] = 1.0
        normalized = ((matrix - mean) / scale).astype("float32")
        historical = normalized[:-1]
        split = min(
            len(historical) - 2,
            max(4, int(len(historical) * 0.70)),
        )
        train = historical[:split]
        validation = historical[split - 1 :]
        evaluation = normalized[split - 1 :]
        operator = make_operator("ring", self.field_dim, seed=42)
        model = fit_tessera_model(
            train,
            operator,
            code_dim=self.code_dim,
            alpha=0.5,
            epochs=2,
            seed=42,
        )
        rows = evaluate_sequence(model, evaluation)["rows"]
        neural_losses = np.asarray(
            [row["prediction_loss"] for row in rows], dtype=float
        )
        neural_latest_loss = float(neural_losses[-1])
        center = float(np.median(neural_losses[:-1]))
        spread = float(np.std(neural_losses[:-1])) or 1.0
        instant_score = max(0.0, (neural_latest_loss - center) / spread)

        # Multi-scale anomaly scoring
        if len(self._anomaly_history) >= 2:
            short_scores = self._anomaly_history[-3:] + [instant_score]
            medium_scores = self._anomaly_history[-7:] + [instant_score]
            short_score = float(np.mean(short_scores[-3:]))
            medium_score = float(np.mean(medium_scores[-7:]))
        else:
            short_score = instant_score
            medium_score = instant_score

        combined_score = max(instant_score, short_score, medium_score)
        self._anomaly_history.append(instant_score)
        if len(self._anomaly_history) > 100:
            self._anomaly_history = self._anomaly_history[-50:]

        # Store latent memory
        if len(rows) > 0:
            last_row = rows[-1]
            latent = np.array([last_row["reconstruction_loss"], last_row["prediction_loss"],
                              last_row["delta_phi"], last_row["code_drift"], last_row["rate"]])
            self._memory_buffer.append(latent)
            if len(self._memory_buffer) > self.memory_capacity:
                self._memory_buffer = self._memory_buffer[-self.memory_capacity:]

        expert, _ = select_prediction_expert(train, validation)
        selected_losses = prediction_losses(
            expert,
            normalized[-2:],
            history=normalized[:-2],
        )
        latest_loss = float(selected_losses[-1])
        validation_selected_losses = prediction_losses(
            expert,
            validation,
            history=train,
        )
        selected_center = float(np.median(validation_selected_losses))
        self._last_prediction_expert = expert.name
        warning = combined_score > 1.5
        return InferencePacket(
            status="neural",
            anomaly_score=combined_score,
            prediction_loss=latest_loss,
            warning=warning,
            memory_candidate=(
                not warning and latest_loss <= selected_center
            ),
            claim_boundary="Local sparse-neural trajectory inference; not validated agent capability.",
            selected_prediction_expert=expert.name,
        )

    def propose_memory(self) -> MemoryProposal:
        packet = self._last_packet or self.infer()
        event_ids = tuple(event.event_id for event in list(self._events)[-4:])
        return MemoryProposal(
            approved=packet.memory_candidate,
            score=max(0.0, 1.0 - packet.anomaly_score),
            evidence_event_ids=event_ids,
        )

    def propose_repair(self) -> RepairProposal:
        packet = self._last_packet or self.infer()
        wound = "W_agent_prediction" if packet.warning else "no_active_wound"
        if packet.warning:
            self._wound_history.append(wound)
        return RepairProposal(
            wound_class=wound,
            target="predictor_head",
            shadow_only=True,
            requires_replay=True,
            requires_host_authorization=True,
        )

    def replay(self, packet: ReplayPacket) -> ReplayCertificate:
        inference = self._last_packet or self.infer()
        return ReplayCertificate(
            passed=inference.prediction_loss <= packet.expected_max_prediction_loss,
            observed_prediction_loss=inference.prediction_loss,
        )

    def checkpoint(self) -> dict:
        return {
            "schema": "TESSERA-PLUGIN-CHECKPOINT-v0.2",
            "event_count": len(self._events),
            "memory_count": len(self._memory_buffer),
            "wound_count": len(self._wound_history),
            "anomaly_mean": float(np.mean(self._anomaly_history)) if self._anomaly_history else 0.0,
            "selected_prediction_expert": self._last_prediction_expert,
            "inline_neural_training": self.inline_neural_training,
            "shadow_training_required": (
                len(self._events) >= self.neural_min_events
                and not self.inline_neural_training
            ),
            "admitted_checkpoint_loaded": self._loaded_checkpoint is not None,
            "live_codec_replacement": False,
            "memory_write": False,
            "tool_invocation": False,
        }
