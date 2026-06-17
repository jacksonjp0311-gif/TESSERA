from __future__ import annotations

import argparse
from tessera import loop_runtime


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="tessera loop")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ascii").set_defaults(func=lambda args: print(loop_runtime.loop_chart_markdown()))
    sub.add_parser("manifest").set_defaults(func=lambda args: print(loop_runtime.json.dumps(loop_runtime.manifest(loop_runtime.root_path()), indent=2)))
    c = sub.add_parser("compile")
    c.add_argument("--out", default="reports/runtime_loop")
    c.set_defaults(func=lambda args: loop_runtime.compile_launchers(loop_runtime.root_path()))
    args = p.parse_args(argv)
    args.func(args)