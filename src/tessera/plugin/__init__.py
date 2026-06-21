"""Host-neutral permission-bounded Tessera neural plugin."""

from .runtime import TesseraPlugin
from .supervisor import PluginSupervisor
from .checkpoints import CheckpointStore, ReplayGate
from .shadow_training import ShadowTrainer, ShadowTrainingJob
from .neural_checkpoints import train_neural_checkpoint

__all__ = [
    "CheckpointStore",
    "PluginSupervisor",
    "ReplayGate",
    "ShadowTrainer",
    "ShadowTrainingJob",
    "TesseraPlugin",
    "train_neural_checkpoint",
]
