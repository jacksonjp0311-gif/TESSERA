import urllib.request, json

AGNT = "http://localhost:3333/api"

r = urllib.request.urlopen(f"{AGNT}/plugins/installed", timeout=5)
data = json.loads(r.read())

tessera = [p for p in data.get("plugins", []) if p["name"] == "tessera-neural-sidecar"]
if tessera:
    p = tessera[0]
    print("Tessera Neural Trust Layer")
    print(f"  Status: {p.get('status')}")
    print(f"  Version: {p.get('version')}")
    print(f"  Tools: {len(p.get('tools', []))}")
    for t in p.get('tools', []):
        print(f"    - {t.get('type')}: {t.get('title', '')}")
    print(f"  Valid: {p.get('isValid')}")
else:
    print("NOT found")

r2 = urllib.request.urlopen(f"{AGNT}/plugins/tools", timeout=5)
tools = json.loads(r2.read())
tessera_tools = [t for t in tools.get("tools", []) if "tessera" in t.get("type", "")]
print(f"\nTessera tools in AGNT: {len(tessera_tools)}")
for t in tessera_tools:
    print(f"  {t['type']}: {t.get('description', '')[:80]}")
