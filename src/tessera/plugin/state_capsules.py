from __future__ import annotations

import hashlib
import json
from typing import Any


STATE_CAPSULE_SCHEMA = "TESSERA-PREFIX-STATE-CAPSULE-v0.1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def seal_state_capsule(payload: dict) -> dict:
    return {
        "schema": STATE_CAPSULE_SCHEMA,
        "payload_sha256": sha256_json(payload),
        "payload": payload,
    }


def open_state_capsule(capsule: dict) -> dict:
    if capsule.get("schema") != STATE_CAPSULE_SCHEMA:
        raise ValueError("unsupported_state_capsule_schema")
    payload = capsule.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("state_capsule_payload_missing")
    if sha256_json(payload) != capsule.get("payload_sha256"):
        raise ValueError("state_capsule_hash_mismatch")
    return payload
