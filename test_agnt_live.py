
import urllib.request, json, base64, tarfile, io
from pathlib import Path

AGNT = "http://localhost:3333/api"

# 1. Check AGNT health
try:
    r = urllib.request.urlopen(f"{AGNT}/plugins/installed", timeout=5)
    data = json.loads(r.read())
    print(f"AGNT: OK, {len(data.get('plugins', []))} plugins")
except Exception as e:
    print(f"AGNT error: {e}")
    exit(1)

# 2. Check if Tessera is already registered
plugins = data.get("plugins", [])
tessera = [p for p in plugins if p["name"] == "tessera-neural-sidecar"]
if tessera:
    print(f"Tessera: ALREADY REGISTERED")
    print(f"  Status: {tessera[0].get('status')}")
    print(f"  Tools: {len(tessera[0].get('tools', []))}")
else:
    print("Tessera: NOT registered, registering now...")
    
    # Build package
    plugin_dir = Path("agnt-plugin")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for fname in ["manifest.json", "package.json", "index.js", "README.md"]:
            fpath = plugin_dir / fname
            if fpath.exists():
                data_bytes = fpath.read_bytes()
                info = tarfile.TarInfo(name=fname)
                info.size = len(data_bytes)
                tar.addfile(info, io.BytesIO(data_bytes))
    
    pkg_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    
    # Register
    body = json.dumps({
        "name": "tessera-neural-sidecar",
        "fileData": pkg_b64,
        "fileName": "tessera.agnt"
    }).encode("utf-8")
    
    req = urllib.request.Request(
        f"{AGNT}/plugins/install-file",
        data=body,
        headers={"Content-Type": "application/json"}
    )
    try:
        r = urllib.request.urlopen(req, timeout=30)
        result = json.loads(r.read())
        print(f"Registration: {result}")
    except Exception as e:
        print(f"Registration error: {e}")

# 3. Get all tools
try:
    r = urllib.request.urlopen(f"{AGNT}/plugins/tools", timeout=5)
    tools = json.loads(r.read())
    tool_names = [t["type"] for t in tools.get("tools", [])]
    print(f"\nAll AGNT tools: {len(tool_names)}")
    tessera_tools = [t for t in tool_names if "tessera" in t]
    print(f"Tessera tools: {tessera_tools}")
except Exception as e:
    print(f"Tools error: {e}")
