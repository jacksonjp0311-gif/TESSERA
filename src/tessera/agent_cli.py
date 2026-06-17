from __future__ import annotations

import argparse
from pathlib import Path

from tessera import operator_geometry


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="python -m tessera.agent_cli", description="Tessera universal Agent CLI entrypoint.")
    parser.add_argument("cmd", choices=["validate", "launch", "observe", "worker", "chart", "lessons", "commands"])
    parser.add_argument("--root", default=str(operator_geometry.DEFAULT_ROOT))
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--skip-run", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args(argv)

    root = operator_geometry.root_path(args.root)
    if args.cmd == "validate":
        raise SystemExit(0 if operator_geometry.validate(root) else 1)
    if args.cmd == "launch":
        operator_geometry.launch(root, no_push=args.no_push, skip_run=args.skip_run, skip_tests=args.skip_tests)
        return
    if args.cmd == "observe":
        operator_geometry.observer(root)
        return
    if args.cmd == "worker":
        operator_geometry.worker(root, no_push=args.no_push, skip_run=args.skip_run, skip_tests=args.skip_tests)
        return
    if args.cmd == "chart":
        operator_geometry.print_file(root, "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md")
        return
    if args.cmd == "lessons":
        operator_geometry.print_file(root, "docs/loop/TESSERA_FAILURE_LESSONS.md")
        return
    if args.cmd == "commands":
        operator_geometry.print_file(root, "docs/loop/TESSERA_COMMAND_REGISTRY.md")
        return


if __name__ == "__main__":
    main()