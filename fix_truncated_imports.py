"""Fix the truncated import lines in cli.py"""
with open('src/tessera/cli.py', 'r') as f:
    content = f.read()

# Fix truncated imports
content = content.replace(
    'from tessera.experiments.run_smap_transfer import run\n',
    'from tessera.experiments.run_smap_transfer import run_smap_transfer\n'
)
content = content.replace(
    'from tessera.experiments.run_ucr_transfer import run\n',
    'from tessera.experiments.run_ucr_transfer import run_ucr_transfer\n'
)

# Also fix any json import issues - ensure json is at top level
lines = content.split('\n')
has_json = any(l.strip() == 'import json' for l in lines[:15])
if not has_json:
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            lines.insert(i, 'import json')
            break
    content = '\n'.join(lines)

with open('src/tessera/cli.py', 'w') as f:
    f.write(content)

# Verify syntax
import subprocess
r = subprocess.run(['python', '-c', 'import ast; ast.parse(open("src/tessera/cli.py").read()); print("OK")'],
                   capture_output=True, text=True, cwd='.')
print(r.stdout.strip() or r.stderr.strip())
