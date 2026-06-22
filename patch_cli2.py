"""Fix the yahoo_s5 import in cli.py"""
with open('src/tessera/cli.py', 'r') as f:
    content = f.read()

# Fix: add json import and fix the yahoo import
if 'import json' not in content.split('\n')[:15]:
    content = 'import json\n' + content
    print("Added json import")

# The function uses json.dump but json isn't imported in the function scope
# Also need to ensure run_yahoo_s5_transfer is importable
if 'from tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer' not in content:
    content = content.replace(
        'from tessera.experiments.run_smap_transfer import',
        'from tessera.experiments.run_smap_transfer import\nfrom tessera.experiments.run_yahoo_s5_transfer import run_yahoo_s5_transfer'
    )
    print("Added yahoo import")

with open('src/tessera/cli.py', 'w') as f:
    f.write(content)

print("Fixed imports")
