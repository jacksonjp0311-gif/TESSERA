"""Fix the extra closing paren and truncated import in cli.py"""
with open('src/tessera/cli.py', 'r') as f:
    content = f.read()

# Fix the smap function - replace the entire broken block
old_smap = '''def cmd_transfer_smap(args):
    from tessera.experiments.run_smap_transfer import run

    run_dir = run(
        root=args.root,
        out=args.out,
        channel_id=args.channel,
        epochs=args.epochs,
        seed=args.seed,
    )
    certificate = json.loads(
        (run_dir / "certificates" / "dataset_transfer_certificate.json").read_text(
            encoding="utf-8"
        )
    )
    print(json.dumps({
        "run": str(run_dir),
        "claim_ceiling": certificate["claim_ceiling"],
        "transfer_level": certificate["transfer_level"],
        "dataset_scoped_transfer_supported": certificate[
            "dataset_scoped_transfer_supported"
        ],
        "transfer_gates": certificate["transfer_gates"],
        "metrics": certificate["metrics"],
    }, indent=2))'''

new_smap = '''def cmd_transfer_smap(args):
    from tessera.experiments.run_smap_transfer import run_smap_transfer

    run_dir = run_smap_transfer(
        root=args.root,
        out=args.out,
        channel_id=args.channel,
        epochs=args.epochs,
        seed=args.seed,
    )
    certificate = json.loads(
        (run_dir / "certificates" / "dataset_transfer_certificate.json").read_text(
            encoding="utf-8"
        )
    )
    print(json.dumps({
        "run": str(run_dir),
        "claim_ceiling": certificate["claim_ceiling"],
        "transfer_level": certificate["transfer_level"],
        "dataset_scoped_transfer_supported": certificate[
            "dataset_scoped_transfer_supported"
        ],
        "transfer_gates": certificate["transfer_gates"],
        "metrics": certificate["metrics"],
    }, indent=2))'''

if old_smap in content:
    content = content.replace(old_smap, new_smap)
    print("Fixed smap function")
else:
    print("Smap pattern not found, trying line-by-line...")
    # Fix line by line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'from tessera.experiments.run_smap_transfer import run' in line and line.strip().endswith('run'):
            lines[i] = '    from tessera.experiments.run_smap_transfer import run_smap_transfer'
            print("Fixed smap import at line", i+1)
        if line.strip() == 'run_dir = run(' and i > 0 and 'run_smap_transfer' in lines[i-1]:
            lines[i] = '    run_dir = run_smap_transfer('
            print("Fixed smap call at line", i+1)
    content = '\n'.join(lines)

# Fix ucr function similarly
old_ucr = '''def cmd_transfer_ucr(args):
    from tessera.experiments.run_ucr_transfer import run

    run_dir = run('''

new_ucr = '''def cmd_transfer_ucr(args):
    from tessera.experiments.run_ucr_transfer import run_ucr_transfer

    run_dir = run_ucr_transfer('''

if old_ucr in content:
    content = content.replace(old_ucr, new_ucr)
    print("Fixed ucr function")
else:
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'from tessera.experiments.run_ucr_transfer import run' in line and line.strip().endswith('run'):
            lines[i] = '    from tessera.experiments.run_ucr_transfer import run_ucr_transfer'
            print("Fixed ucr import at line", i+1)
        if line.strip() == 'run_dir = run(' and i > 0 and 'run_ucr_transfer' in lines[i-1]:
            lines[i] = '    run_dir = run_ucr_transfer('
            print("Fixed ucr call at line", i+1)
    content = '\n'.join(lines)

# Ensure json is imported
lines = content.split('\n')
has_json = any(l.strip() == 'import json' for l in lines[:15])
if not has_json:
    for i, l in enumerate(lines):
        if l.startswith('import ') or l.startswith('from '):
            lines.insert(i, 'import json')
            break
    content = '\n'.join(lines)
    print("Added json import")

with open('src/tessera/cli.py', 'w') as f:
    f.write(content)

# Verify
import subprocess
r = subprocess.run(['python', '-c', 'import ast; ast.parse(open("src/tessera/cli.py").read()); print("Syntax OK")'],
                   capture_output=True, text=True, cwd='.')
print(r.stdout.strip() or r.stderr.strip())
