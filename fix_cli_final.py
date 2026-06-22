"""Fix truncated imports and indentation in cli.py"""
with open('src/tessera/cli.py', 'r') as f:
    lines = f.readlines()

fixed = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix truncated smap import
    if line.strip() == 'from tessera.experiments.run_smap_transfer import run' and i+1 < len(lines) and lines[i+1].strip() == '':
        fixed.append('    from tessera.experiments.run_smap_transfer import run_smap_transfer\n')
        fixed.append('\n')
        i += 2  # Skip the blank line after
        continue
    
    # Fix truncated ucr import
    if line.strip() == 'from tessera.experiments.run_ucr_transfer import run' and i+1 < len(lines) and lines[i+1].strip() == '':
        fixed.append('    from tessera.experiments.run_ucr_transfer import run_ucr_transfer\n')
        fixed.append('\n')
        i += 2
        continue
    
    # Fix indentation: "    run_dir = run(" should be "    run_dir = run_smap_transfer("
    if line.strip() == 'run_dir = run(' and i > 0 and 'run_smap_transfer' in lines[i-1]:
        fixed.append(line.replace('run_dir = run(', 'run_dir = run_smap_transfer('))
        i += 1
        continue
    
    if line.strip() == 'run_dir = run(' and i > 0 and 'run_ucr_transfer' in lines[i-1]:
        fixed.append(line.replace('run_dir = run(', 'run_dir = run_ucr_transfer('))
        i += 1
        continue
    
    fixed.append(line)
    i += 1

# Check json import
has_json = any(l.strip() == 'import json' for l in fixed[:15])
if not has_json:
    for i, l in enumerate(fixed):
        if l.startswith('import ') or l.startswith('from '):
            fixed.insert(i, 'import json\n')
            break

with open('src/tessera/cli.py', 'w') as f:
    f.writelines(fixed)

# Verify
import subprocess
r = subprocess.run(['python', '-c', 'import ast; ast.parse(open("src/tessera/cli.py").read()); print("Syntax OK")'],
                   capture_output=True, text=True, cwd='.')
print(r.stdout.strip() or r.stderr.strip())
