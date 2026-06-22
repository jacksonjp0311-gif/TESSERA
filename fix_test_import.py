"""Fix the missing HTTPServer import in test_evo048.py"""
with open('tests/test_evo048.py', 'r') as f:
    content = f.read()

# Add the missing import
content = content.replace(
    'from tessera.agnt_bridge import (',
    'from http.server import HTTPServer\nfrom tessera.agnt_bridge import ('
)

with open('tests/test_evo048.py', 'w') as f:
    f.write(content)

print('Fixed import in test_evo048.py')
