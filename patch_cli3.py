"""Fix the broken import in cli.py"""
with open('src/tessera/cli.py', 'r') as f:
    content = f.read()

# Remove the broken import line inside the function
content = content.replace(
    '    from tessera.experiments.run_smap_transfer import run\nfrom tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer',
    '    from tessera.experiments.run_smap_transfer import run'
)

# Also remove any other misplaced yahoo import
content = content.replace(
    'from tessera.experiments.run_smap_transfer import\nfrom tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer',
    'from tessera.experiments.run_smap_transfer import'
)

# Add the yahoo import at the top-level (after the other experiment imports)
# Find the top-level import block
if 'from tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer' not in content:
    # Add after the existing top-level experiment imports
    content = content.replace(
        'from tessera.experiments.run_ucr_transfer import',
        'from tessera.experiments.run_ucr_transfer import\nfrom tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer'
    )
    print("Added top-level yahoo import")

# Also ensure json is imported at top level
lines = content.split('\n')
has_json_import = any(l.strip() == 'import json' for l in lines[:20])
if not has_json_import:
    # Find the first import line
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            lines.insert(i, 'import json')
            break
    content = '\n'.join(lines)
    print("Added json import")

with open('src/tessera/cli.py', 'w') as f:
    f.write(content)

print("Fixed cli.py imports")

# Verify syntax
import subprocess
result = subprocess.run(['python', '-c', 'import ast; ast.parse(open("src/tessera/cli.py").read()); print("Syntax OK")'], 
                       capture_output=True, text=True, cwd='.')
print(result.stdout or result.stderr)
