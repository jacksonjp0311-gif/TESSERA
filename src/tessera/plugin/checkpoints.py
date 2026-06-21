from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class ReplayGate:
    baseline_loss: float
    candidate_loss: float
    max_regression_fraction: float = 0.02
    minimum_replay_pass_rate: float = 0.60
    replay_pass_rate: float = 0.0

    @property
    def passed(self) -> bool:
        loss_ok = self.candidate_loss <= (
            self.baseline_loss * (1.0 + self.max_regression_fraction)
        )
        return loss_ok and self.replay_pass_rate >= self.minimum_replay_pass_rate


class CheckpointStore:
    """Immutable candidate store with atomic activation and rollback."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.candidates = self.root / "candidates"
        self.pointers = self.root / "pointers"
        self.candidates.mkdir(parents=True, exist_ok=True)
        self.pointers.mkdir(parents=True, exist_ok=True)

    def write_candidate(
        self,
        *,
        payload: dict,
        lineage: dict,
        metrics: dict,
    ) -> dict:
        candidate_id = uuid.uuid4().hex
        payload_hash = _sha256(payload)
        record = {
            "schema": "TESSERA-PLUGIN-CHECKPOINT-v0.3",
            "candidate_id": candidate_id,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "payload_sha256": payload_hash,
            "payload": payload,
            "lineage": lineage,
            "metrics": metrics,
            "immutable": True,
            "admitted": False,
            "claim_boundary": (
                "A shadow checkpoint candidate has no live authority until "
                "integrity and replay admission pass."
            ),
        }
        path = self.candidates / f"{candidate_id}.json"
        path.write_bytes(_canonical_bytes(record))
        return {"candidate_id": candidate_id, "path": str(path), **record}

    def load_candidate(self, candidate_id: str) -> dict:
        path = self.candidates / f"{candidate_id}.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        if _sha256(record["payload"]) != record["payload_sha256"]:
            raise ValueError("checkpoint_payload_hash_mismatch")
        return record

    def admit(
        self,
        candidate_id: str,
        replay: ReplayGate,
        *,
        inject_failure: bool = False,
    ) -> dict:
        candidate = self.load_candidate(candidate_id)
        if not replay.passed:
            return {
                "admitted": False,
                "reason": "replay_gate_failed",
                "active": self.active(),
            }
        previous = self.active()
        pointer = {
            "schema": "TESSERA-ACTIVE-CHECKPOINT-v0.1",
            "candidate_id": candidate_id,
            "payload_sha256": candidate["payload_sha256"],
            "admitted_at_utc": datetime.now(timezone.utc).isoformat(),
            "replay": asdict(replay),
            "previous_candidate_id": (
                previous.get("candidate_id") if previous else None
            ),
        }
        self._atomic_write(self.pointers / "pending.json", pointer)
        if inject_failure:
            (self.pointers / "pending.json").unlink(missing_ok=True)
            return {
                "admitted": False,
                "reason": "injected_pre_activation_failure",
                "active": self.active(),
            }
        if previous:
            self._atomic_write(self.pointers / "previous.json", previous)
        os.replace(
            self.pointers / "pending.json",
            self.pointers / "active.json",
        )
        return {"admitted": True, "active": pointer}

    def rollback(self) -> dict:
        previous_path = self.pointers / "previous.json"
        if not previous_path.exists():
            return {"rolled_back": False, "reason": "no_previous_checkpoint"}
        previous = json.loads(previous_path.read_text(encoding="utf-8"))
        active = self.active()
        self._atomic_write(self.pointers / "rollback-pending.json", previous)
        os.replace(
            self.pointers / "rollback-pending.json",
            self.pointers / "active.json",
        )
        if active:
            self._atomic_write(self.pointers / "previous.json", active)
        return {"rolled_back": True, "active": previous}

    def active(self) -> dict | None:
        path = self.pointers / "active.json"
        if not path.exists():
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        candidate = self.load_candidate(value["candidate_id"])
        if value["payload_sha256"] != candidate["payload_sha256"]:
            raise ValueError("active_checkpoint_hash_mismatch")
        return value

    @staticmethod
    def _atomic_write(path: Path, value: dict) -> None:
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_bytes(_canonical_bytes(value))
        os.replace(temp, path)
