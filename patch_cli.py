"""Patch cli.py to add transfer-yahoo-s5 command"""
import re

with open('src/tessera/cli.py', 'r') as f:
    content = f.read()

# Find the transfer-ucr section and add yahoo-s5 after it
# Look for the pattern after transfer-ucr's set_defaults
old = '''    ucr.set_defaults(func=cmd_transfer_ucr)

    repair = sub.add_parser("repair",'''

new = '''    ucr.set_defaults(func=cmd_transfer_ucr)

    yahoo = sub.add_parser(
        "transfer-yahoo-s5",
        help="Run Yahoo S5 third family evaluation.",
    )
    yahoo.add_argument("--root", default=".")
    yahoo.add_argument("--out", default="outputs/transfers/yahoo_s5")
    yahoo.add_argument("--stream", default="A1Benchmark_real_1.csv")
    yahoo.add_argument("--epochs", type=int, default=4)
    yahoo.add_argument("--seed", type=int, default=42)
    yahoo.add_argument("--field-dim", type=int, default=16)
    yahoo.add_argument("--code-dim", type=int, default=8)
    yahoo.add_argument("--hidden-dim", type=int, default=0)
    yahoo.add_argument("--depth", type=int, default=2)
    yahoo.set_defaults(func=cmd_transfer_yahoo_s5)

    repair = sub.add_parser("repair",'''

if old in content:
    content = content.replace(old, new)
    print("Patched cli.py to add transfer-yahoo-s5 command")
else:
    print("Pattern not found, trying alternative...")
    # Try to find just before "repair = sub.add_parser"
    idx = content.find('    repair = sub.add_parser("repair"')
    if idx > 0:
        insert = '''
    yahoo = sub.add_parser(
        "transfer-yahoo-s5",
        help="Run Yahoo S5 third family evaluation.",
    )
    yahoo.add_argument("--root", default=".")
    yahoo.add_argument("--out", default="outputs/transfers/yahoo_s5")
    yahoo.add_argument("--stream", default="A1Benchmark_real_1.csv")
    yahoo.add_argument("--epochs", type=int, default=4)
    yahoo.add_argument("--seed", type=int, default=42)
    yahoo.add_argument("--field-dim", type=int, default=16)
    yahoo.add_argument("--code-dim", type=int, default=8)
    yahoo.add_argument("--hidden-dim", type=int, default=0)
    yahoo.add_argument("--depth", type=int, default=2)
    yahoo.set_defaults(func=cmd_transfer_yahoo_s5)

'''
        content = content[:idx] + insert + content[idx:]
        print("Inserted transfer-yahoo-s5 command before repair")
    else:
        print("Could not find insertion point")

# Also add the import for cmd_transfer_yahoo_s5
if 'cmd_transfer_yahoo_s5' not in content and 'from tessera.experiments.run_yahoo_s5_transfer' not in content:
    # Add import after the existing transfer imports
    content = content.replace(
        'from tessera.experiments.run_smap_transfer import',
        'from tessera.experiments.run_smap_transfer import\nfrom tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer'
    )
    print("Added yahoo_s5 import")

# Add the command function before cmd_repair
yahoo_func = '''
def cmd_transfer_yahoo_s5(args):
    """Run Yahoo S5 third family evaluation."""
    from pathlib import Path
    root = Path(args.root)
    data_dir = root / "datasets" / "yahoo_s5"
    
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        print("Run: python download_yahoo_s5.js")
        raise SystemExit(1)
    
    csv_path = data_dir / args.stream
    if not csv_path.exists():
        print(f"Stream not found: {csv_path}")
        raise SystemExit(1)
    
    # Parse anomaly windows from filename
    anomaly_windows = None
    if "real_1" in args.stream:
        anomaly_windows = [[287, 307], [490, 513]]
    elif "real_2" in args.stream:
        anomaly_windows = [[400, 420]]
    elif "real_3" in args.stream:
        anomaly_windows = [[300, 320], [500, 520]]
    
    result = run_yahoo_s5_transfer(
        data_dir=str(data_dir),
        stream_name=args.stream,
        epochs=args.epochs,
        seed=args.seed,
        field_dim=args.field_dim,
        code_dim=args.code_dim,
        hidden_dim=args.hidden_dim if args.hidden_dim > 0 else None,
        depth=args.depth,
        anomaly_windows=anomaly_windows,
    )
    
    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)
    result_file = out_path / f"{args.stream.replace('.csv', '')}_result.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\\nYahoo S5 Transfer Evaluation: {args.stream}")
    print(f"  Status: {result.get('status', 'unknown')}")
    if result.get('status') == 'evaluated':
        print(f"  AUC: {result['auc']:.4f}")
        print(f"  Recall: {result['recall']:.4f}")
        print(f"  False Memory Rate: {result['false_memory_rate']:.4f}")
        print(f"  Replay Pass Rate: {result['replay_pass_rate']:.4f}")
        print(f"  Neural Loss: {result['neural_prediction_loss']:.4f}")
        print(f"  Best Baseline: {result['best_baseline_loss']:.4f}")
        print(f"  Baseline Gap: {result['baseline_gap']:.4f}")
        print(f"  Selected Expert: {result['selected_expert']}")
        print(f"  T1 Supported: {result['t1_supported']}")
        print(f"  Parameters: {result['parameter_count']}")
    print(f"\\nResults written to: {result_file}")

'''

# Insert before cmd_repair
if 'def cmd_transfer_yahoo_s5' not in content:
    idx = content.find('\ndef cmd_repair(args):')
    if idx > 0:
        content = content[:idx] + yahoo_func + content[idx:]
        print("Added cmd_transfer_yahoo_s5 function")
    else:
        # Try another pattern
        idx = content.find('def cmd_repair(args):')
        if idx > 0:
            content = content[:idx] + yahoo_func + '\n' + content[idx:]
            print("Added cmd_transfer_yahoo_s5 function (alt)")

with open('src/tessera/cli.py', 'w') as f:
    f.write(content)

print("Done patching cli.py")
