from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

CAPSULE_STORE_SCHEMA = "TESSERA-HOST-CAPSULE-STORE-v0.1"


class CapsuleIntegrityError(Exception):
    """Raised when a capsule fails integrity verification."""
    pass


class CapsuleStoreFullError(Exception):
    """Raised when the store has reached its maximum capacity."""
    pass


@dataclass(frozen=True)
class CapsuleRecord:
    capsule_id: str
    host: str
    session_id_hash: str
    created_at: float
    payload_sha256: str
    payload: dict
    metadata: dict = field(default_factory=dict)

    def verify_integrity(self) -> bool:
        """Verify the capsule's SHA-256 integrity."""
        canonical = json.dumps(self.payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        observed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return observed == self.payload_sha256


@dataclass
class CapsuleStoreStats:
    total_capsules: int
    hosts: dict[str, int]
    sessions: int
    oldest_timestamp: float | None
    newest_timestamp: float | None
    store_path: str
    max_capsules: int
    store_full: bool


class AtomicCapsuleStore:
    """Host-owned durable capsule store with SHA-256 integrity.

    The store is append-only. Capsules are written atomically (write to temp, then rename).
    Each capsule is bound to a host and session. The store enforces a maximum capacity.
    On overflow, the oldest capsules are evicted (FIFO).

    The host owns this store — the plugin can request writes but cannot directly mutate store files.
    """

    def __init__(
        self,
        store_path: str | Path,
        *,
        max_capsules: int = 10000,
        host_key: str | None = None,
    ):
        self._store_path = Path(store_path)
        self._max_capsules = max_capsules
        self._host_key = host_key
        self._store_path.mkdir(parents=True, exist_ok=True)
        self._index_path = self._store_path / "index.json"
        self._load_index()

    def _load_index(self) -> None:
        if self._index_path.exists():
            data = json.loads(self._index_path.read_text(encoding="utf-8"))
            self._index = data.get("capsules", [])
        else:
            self._index = []

    def _save_index(self) -> None:
        data = {
            "schema": CAPSULE_STORE_SCHEMA,
            "max_capsules": self._max_capsules,
            "host_key": self._host_key,
            "capsules": self._index,
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        # Atomic write: write to temp, then rename
        temp_path = self._index_path.with_suffix(".tmp")
        temp_path.write_text(canonical, encoding="utf-8")
        temp_path.replace(self._index_path)

    def _capsule_path(self, capsule_id: str) -> Path:
        # Shard by first 2 chars of capsule_id for filesystem efficiency
        shard = capsule_id[:2]
        shard_dir = self._store_path / "capsules" / shard
        shard_dir.mkdir(parents=True, exist_ok=True)
        return shard_dir / f"{capsule_id}.json"

    def _write_capsule_file(self, record: CapsuleRecord) -> None:
        """Write a capsule file atomically."""
        capsule_data = {
            "schema": CAPSULE_STORE_SCHEMA,
            "capsule_id": record.capsule_id,
            "host": record.host,
            "session_id_hash": record.session_id_hash,
            "created_at": record.created_at,
            "payload_sha256": record.payload_sha256,
            "payload": record.payload,
            "metadata": record.metadata,
        }
        canonical = json.dumps(capsule_data, sort_keys=True, separators=(",", ":"), indent=2)
        target = self._capsule_path(record.capsule_id)
        temp = target.with_suffix(".tmp")
        temp.write_text(canonical, encoding="utf-8")
        temp.replace(target)

    def _evict_oldest(self) -> None:
        """Evict oldest capsules until we're under max_capsules."""
        while len(self._index) >= self._max_capsules:
            oldest = self._index.pop(0)
            capsule_file = self._capsule_path(oldest["capsule_id"])
            if capsule_file.exists():
                capsule_file.unlink()

    def write_capsule(
        self,
        payload: dict,
        *,
        host: str,
        session_id_hash: str,
        metadata: dict | None = None,
    ) -> CapsuleRecord:
        """Write a capsule to the store. Returns the CapsuleRecord."""
        if self._host_key is not None and host != self._host_key:
            raise CapsuleIntegrityError(f"host mismatch: expected {self._host_key}, got {host}")

        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        payload_sha256 = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        capsule_id = hashlib.sha256(
            f"{host}:{session_id_hash}:{time.time_ns()}".encode()
        ).hexdigest()[:32]

        record = CapsuleRecord(
            capsule_id=capsule_id,
            host=host,
            session_id_hash=session_id_hash,
            created_at=time.time(),
            payload_sha256=payload_sha256,
            payload=payload,
            metadata=metadata or {},
        )

        # Evict if necessary before writing
        self._evict_oldest()

        # Write capsule file atomically
        self._write_capsule_file(record)

        # Update index
        self._index.append({
            "capsule_id": capsule_id,
            "host": host,
            "session_id_hash": session_id_hash,
            "created_at": record.created_at,
            "payload_sha256": payload_sha256,
        })
        self._save_index()

        return record

    def read_capsule(self, capsule_id: str) -> CapsuleRecord:
        """Read and verify a capsule from the store."""
        capsule_file = self._capsule_path(capsule_id)
        if not capsule_file.exists():
            raise FileNotFoundError(f"capsule not found: {capsule_id}")

        data = json.loads(capsule_file.read_text(encoding="utf-8"))
        record = CapsuleRecord(
            capsule_id=data["capsule_id"],
            host=data["host"],
            session_id_hash=data["session_id_hash"],
            created_at=data["created_at"],
            payload_sha256=data["payload_sha256"],
            payload=data["payload"],
            metadata=data.get("metadata", {}),
        )

        if not record.verify_integrity():
            raise CapsuleIntegrityError(f"capsule integrity check failed: {capsule_id}")

        return record

    def list_capsules(
        self,
        *,
        host: str | None = None,
        session_id_hash: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """List capsules, optionally filtered by host or session."""
        results = []
        for entry in reversed(self._index):  # newest first
            if host is not None and entry["host"] != host:
                continue
            if session_id_hash is not None and entry["session_id_hash"] != session_id_hash:
                continue
            results.append(entry)
            if limit is not None and len(results) >= limit:
                break
        return results

    def stats(self) -> CapsuleStoreStats:
        """Return store statistics."""
        hosts: dict[str, int] = {}
        timestamps = []
        for entry in self._index:
            h = entry.get("host", "unknown")
            hosts[h] = hosts.get(h, 0) + 1
            if "created_at" in entry:
                timestamps.append(entry["created_at"])

        sessions = len(set(e.get("session_id_hash", "") for e in self._index))

        return CapsuleStoreStats(
            total_capsules=len(self._index),
            hosts=hosts,
            sessions=sessions,
            oldest_timestamp=min(timestamps) if timestamps else None,
            newest_timestamp=max(timestamps) if timestamps else None,
            store_path=str(self._store_path),
            max_capsules=self._max_capsules,
            store_full=len(self._index) >= self._max_capsules,
        )

    def verify_all(self) -> dict:
        """Verify integrity of all capsules in the store."""
        passed = 0
        failed = 0
        errors = []
        for entry in self._index:
            try:
                self.read_capsule(entry["capsule_id"])
                passed += 1
            except (CapsuleIntegrityError, FileNotFoundError) as e:
                failed += 1
                errors.append({"capsule_id": entry["capsule_id"], "error": str(e)})
        return {
            "total": len(self._index),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        }
