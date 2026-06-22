"""Fix broken imports in cli.py by directly patching specific lines"""
with open('src/tessera/cli.py', 'r') as f:
    lines = f.readlines()

# Find and fix broken import lines
fixed = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix broken run_ucr_transfer import (truncated)
    if 'from tessera.experiments.run_ucr_transfer import run' in line and line.strip().endswith('run'):
        fixed.append('    from tessera.experiments.run_ucr_transfer import run_ucr_transfer\n')
        i += 1
        continue
    
    # Fix broken run_smap_transfer import (truncated)
    if 'from tessera.experiments.run_smap_transfer import run' in line and line.strip().endswith('run'):
        fixed.append('    from tessera.experiments.run_smap_transfer import run_smap_transfer\n')
        i += 1
        continue
    
    # Skip duplicate/malformed yahoo imports
    if 'from tessera.experiments.run_yahoo_s5_transfer import' in line:
        # Check if this is a duplicate or malformed
        if i > 0 and 'run_yahoo_s5_transfer' in lines[i-1]:
            i += 1
            continue
        # Check if it's at the right place (top-level)
        if not line.startswith('from '):
            i += 1
            continue
    
    fixed.append(line)
    i += 1

# Check if we have the yahoo import at top level
has_yahoo_top = any(l.strip() == 'from tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer' for l in fixed[:80])
if not has_yahoo_top:
    # Add after the smap import
    for i, line in enumerate(fixed):
        if 'from tessera.experiments.run_smap_transfer import' in line:
            fixed.insert(i+1, 'from tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer\n')
            break

# Check if json is imported at top
has_json = any(l.strip() == 'import json' for l in fixed[:20])
if not has_json:
    for i, line in enumerate(fixed):
        if line.startswith('import ') or line.startswith('from '):
            fixed.insert(i, 'import json\n')
            break

with open('src/tessera/cli.py', 'w') as f:
    f.writelines(fixed)

print("Fixed imports")

# Verify syntax
import subprocess
result = subprocess.run(['python', '-c', 'import ast; ast.parse(open("src/tessera/cli.py").read()); print("Syntax OK")'], 
                       capture_output=True, text=True, cwd='.')
print(result.stdout or result.stderr)
