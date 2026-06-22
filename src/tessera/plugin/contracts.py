from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


EventKind = Literal[
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
]


@dataclass(frozen=True)
class PluginPermissions:
    observe_allowlisted_events: bool = True
    local_neural_inference: bool = True
    warning_proposals: bool = True
    memory_proposals: bool = True
    repair_proposals: bool = True
    host_memory_write: bool = False
    tool_invocation: bool = False
    prompt_mutation: bool = False
    live_codec_replacement: bool = False
    topology_mutation: bool = False
    external_api_calls: bool = False


@dataclass(frozen=True)
class PluginManifest:
    schema: str = "TESSERA-PLUGIN-MANIFEST-v0.3"
    name: str = "tessera-neural-sidecar"
    version: str = "0.4.2"
    deterministic_mode: bool = True
    event_schema: str = "TESSERA-AGENT-EVENT-v0.1"
    execution_model: str = "host-supervised-local-subprocess"
    health_schema: str = "TESSERA-PLUGIN-HEALTH-v0.1"
    supports_hard_timeout: bool = True
    supports_unload: bool = True
    session_summary_schema: str = "TESSERA-SESSION-SUMMARY-v0.1"
    supports_host_observability_gate: bool = True
    supports_manifold_drift_gate: bool = True
    supports_sequential_geometry_gate: bool = True
    supports_exact_prefix_state: bool = True
    supports_integrity_bound_restart_state: bool = True
    permissions: PluginPermissions = field(default_factory=PluginPermissions)
    claim_boundary: str = (
        "The plugin provides local inference and proposals only; the host retains "
        "tool, memory-write, prompt, topology, codec, and external API authority."
    )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentEvent:
    event_id: str
    kind: EventKind
    timestamp: float
    features: dict[str, float]
    metadata: dict[str, str] = field(default_factory=dict)
    contains_sensitive_data: bool = False


@dataclass(frozen=True)
class ObservationReceipt:
    accepted: int
    rejected: int
    reasons: tuple[str, ...]
    buffer_size: int


@dataclass(frozen=True)
class InferenceQuery:
    horizon: int = 1


@dataclass(frozen=True)
class InferencePacket:
    status: str
    anomaly_score: float
    prediction_loss: float
    warning: bool
    memory_candidate: bool
    claim_boundary: str
    selected_prediction_expert: str = "not_selected"
    trust_route: str = "not_routed"
    abstained: bool = False
    uncertainty_score: float = 0.0


@dataclass(frozen=True)
class MemoryProposal:
    approved: bool
    score: float
    evidence_event_ids: tuple[str, ...]
    requires_host_authorization: bool = True


@dataclass(frozen=True)
class RepairProposal:
    wound_class: str
    target: str
    shadow_only: bool
    requires_replay: bool
    requires_host_authorization: bool


@dataclass(frozen=True)
class ReplayPacket:
    expected_max_prediction_loss: float


@dataclass(frozen=True)
class ReplayCertificate:
    passed: bool
    observed_prediction_loss: float
    memory_promotion_authorized: bool = False
    live_repair_authorized: bool = False


@dataclass(frozen=True)
class RuntimeBudget:
    timeout_ms: int = 30_000
    worker_cpu_threads: int = 1
    max_events: int = 512
    max_feature_count: int = 32
    max_metadata_count: int = 16
    max_consecutive_failures: int = 3


@dataclass(frozen=True)
class RuntimeHealth:
    schema: str
    status: str
    lifecycle: str
    consecutive_failures: int
    total_requests: int
    successful_requests: int
    timed_out_requests: int
    failed_requests: int
    last_latency_ms: float
    circuit_open: bool
    claim_boundary: str


@dataclass(frozen=True)
class RuntimeResult:
    status: str
    packet: InferencePacket | None
    latency_ms: float
    error_code: str | None
    host_contained: bool
    claim_boundary: str
