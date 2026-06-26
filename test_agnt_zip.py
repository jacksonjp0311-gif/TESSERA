
import urllib.request, json, base64, zipfile, io
from pathlib import Path

AGNT = "http://localhost:3333/api"

# Build ZIP package (Windows-compatible)
plugin_dir = Path("agnt-plugin")
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
    for fname in ["manifest.json", "package.json", "index.js", "README.md"]:
        fpath = plugin_dir / fname
        if fpath.exists():
            zf.write(fpath, fname)

pkg_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

# Register with AGNT
body = json.dumps({
    "name": "tessera-neural-sidecar",
    "fileData": pkg_b64,
    "fileName": "tessera.zip"
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
