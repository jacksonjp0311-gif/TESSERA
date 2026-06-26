import urllib.request, json, base64
from pathlib import Path

AGNT = "http://localhost:3333/api"
pkg_b64 = base64.b64encode(Path("tessera.agnt").read_bytes()).decode("utf-8")

req = urllib.request.Request(
    f"{AGNT}/plugins/install-file",
    data=json.dumps({"name": "tessera-neural-sidecar", "fileData": pkg_b64, "fileName": "tessera.agnt"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
try:
    r = urllib.request.urlopen(req, timeout=30)
    print("Result:", json.loads(r.read()))
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print("Body:", e.read().decode()[:500])
