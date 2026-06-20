from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable, Sequence

AUTHORITY_LOCKS = (
    "provider_call_executed",
    "model_call_executed",
    "tool_use_executed",
    "runtime_source_mutation",
    "memory_write",
    "memory_promotion",
    "api_write",
    "dependency_mutation_committed",
    "external_ingestion",
    "autonomous_authority",
    "self_authorization",
)

VALID_PROFILES = {"full", "compact", "pointer"}
VALID_NODE_KINDS = {
    "truth",
    "route",
    "readme",
    "runtime",
    "validator",
    "evidence",
    "lesson",
    "boundary",
    "operator",
}
VALID_EDGE_KINDS = {
    "reads",
    "validates",
    "emits",
    "routes_to",
    "governed_by",
    "documented_by",
    "learns_from",
    "blocks",
    "promotes",
}
LESSON_FIELDS = {
    "id",
    "observed_event",
    "evidence_path",
    "wound_class",
    "diagnosis",
    "lesson",
    "future_behavior_change",
    "validation_gate",
    "authority_boundary",
    "status",
}


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def authority_locks_false(data: dict[str, Any]) -> tuple[bool, list[str]]:
    failures = []
    for key in AUTHORITY_LOCKS:
        if data.get(key) is False:
            continue
        if (
            key == "external_ingestion"
            and data.get("external_ingestion") is True
            and data.get("external_ingestion_authorized_by_user") is True
        ):
            continue
        failures.append(key)
    return not failures, failures


def ordered_sequence_report(
    expected: Sequence[str], observed: Sequence[str]
) -> dict[str, Any]:
    """Compare complete sequences without deduplicating repeated stages."""
    mismatch_index = None
    for index, (left, right) in enumerate(zip(expected, observed)):
        if left != right:
            mismatch_index = index
            break
    if mismatch_index is None and len(expected) != len(observed):
        mismatch_index = min(len(expected), len(observed))
    return {
        "ok": tuple(expected) == tuple(observed),
        "expected": list(expected),
        "observed": list(observed),
        "mismatch_index": mismatch_index,
    }


def validate_lineage(
    root: Path, pointer: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    checks = {
        "operation_alignment": pointer.get("latest_operation")
        == evidence.get("operation"),
        "evidence_path_alignment": bool(pointer.get("latest_evidence")),
        "state_alignment": pointer.get("state")
        == evidence.get("state_after_validation"),
        "next_operation_alignment": pointer.get("next_operation")
        == evidence.get("next_recommended_operation"),
        "source_commit_alignment": pointer.get("source_commit")
        == evidence.get("source_commit"),
        "authority_ok": authority_locks_false(evidence)[0],
        "current_head_observed": bool(git_head(root)),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "failures": [name for name, ok in checks.items() if not ok],
    }


def validate_origin(
    root: Path, pointer: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    required = [str(path) for path in manifest.get("required_surfaces", [])]
    missing = [path for path in required if not (root / path).exists()]
    checks = {
        "source_commit_alignment": manifest.get("source_lineage", {}).get("commit")
        == pointer.get("source_commit"),
        "history_not_copied": manifest.get("source_lineage", {}).get("history_copied")
        is False,
        "context_default_disabled": manifest.get("context_default_enabled") is False,
        "compounding_permission_disabled": manifest.get("compounding_permission")
        is False,
        "required_surfaces_present": not missing,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "missing_surfaces": missing,
    }


def _readme_tokens(profile: str) -> tuple[str, ...]:
    if profile == "full":
        return ("Specification", "Hooks", "Artifacts", "Invariants", "Claim Boundary")
    if profile == "compact":
        return ("Specification", "Claim Boundary")
    return ("#",)


def validate_surface_registry(
    root: Path, registry: dict[str, Any], profile_map: dict[str, Any]
) -> dict[str, Any]:
    surfaces = registry.get("surfaces", [])
    profiles = profile_map.get("profiles", {})
    ids: set[str] = set()
    paths: set[str] = set()
    findings: list[dict[str, str]] = []
    counts = {profile: 0 for profile in VALID_PROFILES}

    for surface in surfaces:
        surface_id = str(surface.get("id", ""))
        rel = str(surface.get("path", ""))
        profile = str(surface.get("profile", ""))
        readme = str(surface.get("readme", ""))
        if not surface_id or surface_id in ids:
            findings.append({"surface": surface_id, "error": "duplicate_or_missing_id"})
        ids.add(surface_id)
        if not rel or rel in paths:
            findings.append({"surface": surface_id, "error": "duplicate_or_missing_path"})
        paths.add(rel)
        if profile not in VALID_PROFILES:
            findings.append({"surface": surface_id, "error": "invalid_profile"})
            continue
        counts[profile] += 1
        if profile not in profiles:
            findings.append({"surface": surface_id, "error": "profile_not_declared"})
        target = root / rel
        if not target.exists():
            findings.append({"surface": surface_id, "error": "missing_surface"})
        readme_path = root / readme
        if not readme_path.is_file():
            findings.append({"surface": surface_id, "error": "missing_mini_readme"})
            continue
        text = readme_path.read_text(encoding="utf-8", errors="replace")
        for token in _readme_tokens(profile):
            if token not in text:
                findings.append(
                    {"surface": surface_id, "error": f"readme_missing:{token}"}
                )
        if not surface.get("claim_boundary"):
            findings.append({"surface": surface_id, "error": "missing_claim_boundary"})
        if not surface.get("validation"):
            findings.append({"surface": surface_id, "error": "missing_validation"})

    return {
        "ok": not findings,
        "surface_count": len(surfaces),
        "profile_counts": counts,
        "findings": findings,
    }


def validate_lessons(root: Path, chart: dict[str, Any]) -> dict[str, Any]:
    lessons = chart.get("lessons", [])
    findings: list[dict[str, str]] = []
    seen: set[str] = set()
    for lesson in lessons:
        lesson_id = str(lesson.get("id", ""))
        if not lesson_id or lesson_id in seen:
            findings.append({"lesson": lesson_id, "error": "duplicate_or_missing_id"})
        seen.add(lesson_id)
        missing = sorted(field for field in LESSON_FIELDS if not lesson.get(field))
        for field in missing:
            findings.append({"lesson": lesson_id, "error": f"missing:{field}"})
        evidence_path = root / str(lesson.get("evidence_path", ""))
        if not evidence_path.exists():
            findings.append({"lesson": lesson_id, "error": "missing_evidence_path"})
        gate = str(lesson.get("validation_gate", ""))
        if gate and not (root / gate.split(" ")[0]).exists():
            findings.append({"lesson": lesson_id, "error": "missing_validation_gate"})
        if lesson.get("status") not in {"proposed", "validated", "promoted", "retired"}:
            findings.append({"lesson": lesson_id, "error": "invalid_status"})
    return {"ok": not findings, "lesson_count": len(lessons), "findings": findings}


def _edges_for(
    edges: Iterable[dict[str, Any]], source: str, kind: str
) -> list[dict[str, Any]]:
    return [
        edge
        for edge in edges
        if edge.get("source") == source and edge.get("kind") == kind
    ]


def validate_geometry(root: Path, geometry: dict[str, Any]) -> dict[str, Any]:
    nodes = geometry.get("nodes", [])
    edges = geometry.get("edges", [])
    findings: list[dict[str, str]] = []
    node_ids = [str(node.get("id", "")) for node in nodes]
    node_set = set(node_ids)
    if len(node_ids) != len(node_set) or "" in node_set:
        findings.append({"geometry": "nodes", "error": "duplicate_or_missing_node_id"})
    for node in nodes:
        node_id = str(node.get("id", ""))
        kind = str(node.get("kind", ""))
        if kind not in VALID_NODE_KINDS:
            findings.append({"geometry": node_id, "error": "invalid_node_kind"})
        path = str(node.get("path", ""))
        if path and not (root / path).exists():
            findings.append({"geometry": node_id, "error": "missing_node_path"})
        if kind == "runtime":
            if not _edges_for(edges, node_id, "documented_by"):
                findings.append({"geometry": node_id, "error": "runtime_not_documented"})
            if not any(
                edge.get("target") == node_id and edge.get("kind") == "validates"
                for edge in edges
            ):
                findings.append({"geometry": node_id, "error": "runtime_not_validated"})
    for edge in edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        kind = str(edge.get("kind", ""))
        if source not in node_set or target not in node_set:
            findings.append({"geometry": f"{source}->{target}", "error": "broken_edge"})
        if kind not in VALID_EDGE_KINDS:
            findings.append({"geometry": f"{source}->{target}", "error": "invalid_edge_kind"})
    sequence = geometry.get("canonical_loop", [])
    expected = geometry.get("expected_loop", [])
    sequence_report = ordered_sequence_report(expected, sequence)
    if not sequence_report["ok"]:
        findings.append({"geometry": "canonical_loop", "error": "loop_order_mismatch"})
    return {
        "ok": not findings,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "sequence": sequence_report,
        "findings": findings,
    }


def validate_route_echoes(root: Path) -> dict[str, Any]:
    canonical = (
        "docs/context/rhp/latest-rhp.json",
        "docs/context/nexus/surface_registry.json",
        "docs/geometry/repository_geometry.json",
        "docs/lessons/lesson_chart.json",
    )
    route_paths = (
        "docs/context/repository_context_index.json",
        "docs/context/rcc_nexus_index.json",
        "rcc/nexus/route_map.json",
    )
    findings: list[dict[str, str]] = []
    for route_path in route_paths:
        text = (root / route_path).read_text(encoding="utf-8-sig")
        for canonical_path in canonical:
            if canonical_path not in text:
                findings.append(
                    {"route": route_path, "error": f"missing_echo:{canonical_path}"}
                )
    return {"ok": not findings, "route_count": len(route_paths), "findings": findings}


def validate_governance_hygiene(root: Path) -> dict[str, Any]:
    paths = (
        "AGENTS.md",
        "README.md",
        "docs/context/rhp/latest-rhp.json",
        "docs/context/nexus/surface_registry.json",
        "docs/geometry/repository_geometry.json",
        "docs/lessons/lesson_chart.json",
    )
    findings: list[dict[str, Any]] = []
    for rel in paths:
        path = root / rel
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            findings.append({"path": rel, "error": "utf8_bom"})
        if len(data) > 1_000_000:
            findings.append(
                {"path": rel, "error": "governance_file_over_1mb", "bytes": len(data)}
            )
    return {"ok": not findings, "checked_count": len(paths), "findings": findings}


def build_zero_context_packet(root: Path) -> dict[str, Any]:
    pointer_path = root / "docs/context/rhp/latest-rhp.json"
    pointer = read_json(pointer_path)
    evidence_path = root / str(pointer["latest_evidence"])
    evidence = read_json(evidence_path)
    locks_ok, lock_failures = authority_locks_false(evidence)
    return {
        "schema": "TESSERA-RHP-ZERO-CONTEXT-v0.1",
        "ok": locks_ok,
        "latest_operation": pointer.get("latest_operation"),
        "latest_evidence": pointer.get("latest_evidence"),
        "state": pointer.get("state"),
        "next_operation": pointer.get("next_operation"),
        "current_head": git_head(root),
        "required_read_order": [
            "README.md",
            "AGENTS.md",
            "README_90_SECONDS.md",
            "docs/context/rhp/latest-rhp.json",
            str(pointer.get("latest_evidence")),
            "docs/context/nexus/surface_registry.json",
            "docs/geometry/repository_geometry.json",
            "docs/lessons/lesson_chart.json",
        ],
        "authority_locks": {key: evidence.get(key) for key in AUTHORITY_LOCKS},
        "authority_failures": lock_failures,
        "roles": {
            "RHP": "current truth, evidence lineage, and zero-context reconstruction",
            "Nexus": "repository routing, profiles, hooks, and validation obligations",
            "Geometry": "interconnection and ordered-loop validation",
            "Lessons": "evidence-backed future behavior changes",
            "Agent CLI": "registered execution surface",
            "Human": "promotion and external-action boundary",
        },
        "non_claim_lock": "Rehydration reconstructs bounded repository state only; it grants no runtime, model, memory, API, autonomous, or self-authorization authority.",
    }


def build_version_summary(root: Path) -> dict[str, Any]:
    pointer = read_json(root / "docs/context/rhp/latest-rhp.json")
    evidence = read_json(root / str(pointer["latest_evidence"]))
    changed = evidence.get("implemented") or list(
        evidence.get("changes", {}).keys()
    )
    findings = []
    for key in ("finding", "diagnosis", "decision", "non_claim_lock"):
        if evidence.get(key):
            findings.append(str(evidence[key]))
    metrics = evidence.get("metrics", {})
    return {
        "schema": "TESSERA-VERSION-SUMMARY-v0.1",
        "version": pointer.get("latest_operation"),
        "state": pointer.get("state"),
        "what_changed": changed,
        "what_we_found": findings,
        "current_metrics": metrics,
        "what_remains_bounded": evidence.get("non_claim_lock"),
        "next_best_move": pointer.get("next_operation"),
        "evidence": pointer.get("latest_evidence"),
    }


def validate_repository(root: Path) -> dict[str, Any]:
    pointer_path = root / "docs/context/rhp/latest-rhp.json"
    pointer = read_json(pointer_path)
    evidence = read_json(root / str(pointer["latest_evidence"]))
    manifest = read_json(root / "docs/context/rhp/origin_manifest.json")
    registry = read_json(root / "docs/context/nexus/surface_registry.json")
    profiles = read_json(root / "docs/context/nexus/mini_readme_profiles.json")
    lessons = read_json(root / "docs/lessons/lesson_chart.json")
    geometry = read_json(root / "docs/geometry/repository_geometry.json")

    sections = {
        "origin": validate_origin(root, pointer, manifest),
        "lineage": validate_lineage(root, pointer, evidence),
        "nexus": validate_surface_registry(root, registry, profiles),
        "route_echoes": validate_route_echoes(root),
        "lessons": validate_lessons(root, lessons),
        "geometry": validate_geometry(root, geometry),
        "hygiene": validate_governance_hygiene(root),
    }
    return {
        "schema": "TESSERA-RHP-NEXUS-VALIDATION-v0.1",
        "passed": all(section["ok"] for section in sections.values()),
        "latest_operation": pointer.get("latest_operation"),
        "sections": sections,
        "claim_boundary": "RHP-Nexus validation proves local contract coherence only; it does not prove model capability, correctness, safety, production readiness, or transfer.",
    }
