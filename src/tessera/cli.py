from __future__ import annotations

import argparse
import json
from pathlib import Path

from tessera.experiments.run_synthetic import run as run_synthetic
from tessera import loop_compiler

def cmd_init(args):
    out = Path(args.out)
    for sub in ["runs", "datasets", "reports", "ledgers"]:
        (out / sub).mkdir(parents=True, exist_ok=True)
    print(f"TESSERA workspace initialized at {out}")

def cmd_run(args):
    run_synthetic(out=args.out, steps=args.steps, channels=args.channels, seed=args.seed, topology=args.topology, field_dim=args.field_dim, code_dim=args.code_dim, alpha=args.alpha, epochs=args.epochs)

def cmd_validate(args):
    run_dir = Path(args.run)
    cert_path = run_dir / "certificates" / "transfer_certificate.json"
    ev_path = run_dir / "evidence" / "evidence_package.json"
    missing = []
    for p in [cert_path, ev_path, run_dir / "metrics" / "tessera_timeseries.csv", run_dir / "ledgers" / "wounds.jsonl"]:
        if not p.exists():
            missing.append(str(p))
    if missing:
        print("TESSERA validation failed")
        for m in missing:
            print(f"missing: {m}")
        raise SystemExit(1)
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    print("TESSERA validation passed")
    print(f"claim_ceiling: {cert.get('claim_ceiling')}")
    print(f"certificate_hash: {cert.get('certificate_hash')}")

def cmd_loop(args):
    loop_compiler.main(args.loop_args)

def main(argv=None):
    p = argparse.ArgumentParser(prog="tessera", description="TESSERA Engine")
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("init"); q.add_argument("--out", default="outputs"); q.set_defaults(func=cmd_init)
    r = sub.add_parser("run")
    r.add_argument("--out", default="outputs")
    r.add_argument("--steps", type=int, default=900)
    r.add_argument("--channels", type=int, default=6)
    r.add_argument("--seed", type=int, default=42)
    r.add_argument("--topology", default="q4", choices=["q4", "ring", "random_sparse", "dense"])
    r.add_argument("--field-dim", type=int, default=16)
    r.add_argument("--code-dim", type=int, default=8)
    r.add_argument("--alpha", type=float, default=0.618)
    r.add_argument("--epochs", type=int, default=6)
    r.set_defaults(func=cmd_run)
    v = sub.add_parser("validate"); v.add_argument("--run", required=True); v.set_defaults(func=cmd_validate)
    loop = sub.add_parser("loop", help="Compile runtime loop surfaces.")
    loop.add_argument("loop_args", nargs=argparse.REMAINDER)
    loop.set_defaults(func=cmd_loop)
    args = p.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()