from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    build_version_summary,
    build_zero_context_packet,
    read_json,
    validate_repository,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tessera.rhp")
    parser.add_argument(
        "command",
        choices=[
            "rehydrate",
            "validate",
            "summary",
            "nexus",
            "geometry",
            "lessons",
        ],
    )
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if args.command == "rehydrate":
        data = build_zero_context_packet(root)
        print(json.dumps(data, indent=2))
        return 0 if data["ok"] else 1
    if args.command == "validate":
        data = validate_repository(root)
        print(json.dumps(data, indent=2))
        return 0 if data["passed"] else 1
    if args.command == "summary":
        print(json.dumps(build_version_summary(root), indent=2))
        return 0
    paths = {
        "nexus": "docs/context/nexus/surface_registry.json",
        "geometry": "docs/geometry/repository_geometry.json",
        "lessons": "docs/lessons/lesson_chart.json",
    }
    print(json.dumps(read_json(root / paths[args.command]), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
