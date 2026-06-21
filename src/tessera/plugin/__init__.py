"""Host-neutral permission-bounded Tessera neural plugin."""

from .runtime import TesseraPlugin
from .supervisor import PluginSupervisor
from .checkpoints import CheckpointStore, ReplayGate
from .shadow_training import ShadowTrainer, ShadowTrainingJob
from .neural_checkpoints import train_neural_checkpoint
from .host_adapters import (
    AgentEventSessionAdapter,
    JsonSessionAdapter,
    SessionSummaryContract,
)
from .incident_governor import GovernedRoute, IncidentGovernor
from .host_integrations import (
    AgentCliMirrorIntegration,
    HermesStreamIntegration,
    HostObservability,
    ObservabilityRoute,
    HostSession,
)
from .manifold_monitor import (
    ManifoldAudit,
    ManifoldContract,
    ManifoldRoute,
    audit_manifold_window,
    fit_manifold_contract,
    govern_manifold_audit,
)
from .sequential_geometry import (
    SequentialGeometryContract,
    SequentialGeometryState,
    SequentialGeometryUpdate,
    fit_sequential_geometry_contract,
    update_sequential_geometry,
)

__all__ = [
    "CheckpointStore",
    "AgentEventSessionAdapter",
    "JsonSessionAdapter",
    "GovernedRoute",
    "IncidentGovernor",
    "AgentCliMirrorIntegration",
    "HermesStreamIntegration",
    "HostObservability",
    "ObservabilityRoute",
    "HostSession",
    "ManifoldAudit",
    "ManifoldContract",
    "ManifoldRoute",
    "PluginSupervisor",
    "ReplayGate",
    "ShadowTrainer",
    "ShadowTrainingJob",
    "SessionSummaryContract",
    "SequentialGeometryContract",
    "SequentialGeometryState",
    "SequentialGeometryUpdate",
    "TesseraPlugin",
    "audit_manifold_window",
    "fit_manifold_contract",
    "fit_sequential_geometry_contract",
    "govern_manifold_audit",
    "train_neural_checkpoint",
    "update_sequential_geometry",
]
