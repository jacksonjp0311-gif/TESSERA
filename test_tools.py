import urllib.request, json, time

AGNT = "http://localhost:3333/api"

# Trigger reload
print("Reloading plugins...")
try:
    req = urllib.request.Request(f"{AGNT}/plugins/reload", method="POST")
    r = urllib.request.urlopen(req, timeout=10)
    print("Reload:", json.loads(r.read()))
except Exception as e:
    print("Reload error:", e)

time.sleep(2)

# Check tools again
r = urllib.request.urlopen(f"{AGNT}/plugins/tools", timeout=5)
tools = json.loads(r.read())
tessera_tools = [t for t in tools.get("tools", []) if "tessera" in t.get("type", "")]
print(f"\nTessera tools: {len(tessera_tools)}")
for t in tessera_tools:
    print(f"  {t['type']}")

# Call tessera-health
if tessera_tools:
    print("\nCalling tessera-health...")
    body = json.dumps({"type": "tessera-health", "input": {}}).encode("utf-8")
    req = urllib.request.Request(
        f"{AGNT}/plugins/tools",
        data=body,
        headers={"Content-Type": "application/json"}
    )
    try:
        r = urllib.request.urlopen(req, timeout=10)
        result = json.loads(r.read())
        print(f"Result: {json.dumps(result, indent=2)[:500]}")
    except Exception as e:
        print(f"Call error: {e}")
        if hasattr(e, 'read'):
            print(f"Body: {e.read().decode()[:300]}")
