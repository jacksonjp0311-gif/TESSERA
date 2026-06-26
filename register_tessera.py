import urllib.request, json, base64
from pathlib import Path

AGNT = "http://localhost:3333/api"
pkg_path = Path("tessera.agnt")
pkg_b64 = base64.b64encode(pkg_path.read_bytes()).decode("utf-8")
print(f"Package: {pkg_path.stat().st_size} bytes")

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
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()[:500]}")
except Exception as e:
    print(f"Error: {e}")
