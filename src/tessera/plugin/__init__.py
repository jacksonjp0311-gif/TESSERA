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
    HostSession,
)

__all__ = [
    "CheckpointStore",
    "AgentEventSessionAdapter",
    "JsonSessionAdapter",
    "GovernedRoute",
    "IncidentGovernor",
    "AgentCliMirrorIntegration",
    "HermesStreamIntegration",
    "HostSession",
    "PluginSupervisor",
    "ReplayGate",
    "ShadowTrainer",
    "ShadowTrainingJob",
    "SessionSummaryContract",
    "TesseraPlugin",
    "train_neural_checkpoint",
]
