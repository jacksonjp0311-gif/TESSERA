"""Directly fix lines 75-85 in cli.py"""
with open('src/tessera/cli.py', 'r') as f:
    lines = f.readlines()

# Replace lines 75-84 (0-indexed: 74-83) with correct versions
# Line 75 (idx 74): def cmd_transfer_smap(args):
# Line 76 (idx 75):     from tessera.experiments.run_smap_transfer import run_smap_transfer
# Line 77 (idx 76): (blank)
# Line 78 (idx 77):     run_dir = run_smap_transfer(
# Line 79-83: same indentation
# Line 84 (idx 83): )

new_lines = [
    'def cmd_transfer_smap(args):\n',
    '    from tessera.experiments.run_smap_transfer import run_smap_transfer\n',
    '\n',
    '    run_dir = run_smap_transfer(\n',
    '        root=args.root,\n',
    '        out=args.out,\n',
    '        channel_id=args.channel,\n',
    '        epochs=args.epochs,\n',
    '        seed=args.seed,\n',
    '    )\n',
]

# Replace lines 74-83 (inclusive)
lines[74:84] = new_lines

# Also fix the ucr import around line 102
for i, line in enumerate(lines):
    if 'from tessera.experiments.run_ucr_transfer import' in line and line.strip().endswith('run'):
        lines[i] = '    from tessera.experiments.run_ucr_transfer import run_ucr_transfer\n'
        # Fix the run_dir line after it
        if i+2 < len(lines) and lines[i+2].strip() == 'run_dir = run(':
            lines[i+2] = '    run_dir = run_ucr_transfer(\n'
        break

# Check json import
has_json = any(l.strip() == 'import json' for l in lines[:15])
if not has_json:
    for i, l in enumerate(lines):
        if l.startswith('import ') or l.startswith('from '):
            lines.insert(i, 'import json\n')
            break

with open('src/tessera/cli.py', 'w') as f:
    f.writelines(lines)

# Verify
import subprocess
r = subprocess.run(['python', '-c', 'import ast; ast.parse(open("src/tessera/cli.py").read()); print("Syntax OK")'],
                   capture_output=True, text=True, cwd='.')
print(r.stdout.strip() or r.stderr.strip())
