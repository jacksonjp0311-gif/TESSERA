"""Run EVO-048 bridge tests"""
import subprocess, sys, os
base = r"C:\Users\jacks\OneDrive\Desktop\Tessera"
os.chdir(base)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_evo048.py::TestBridgeEndpoints", "-v", "--tb=short"],
    capture_output=True, text=True, timeout=120
)
sys.stdout.write(result.stdout[-2000:])
sys.stdout.flush()
if result.stderr:
    sys.stderr.write("STDERR:" + result.stderr[-500:])
    sys.stderr.flush()
sys.stdout.write("\nExit: " + str(result.returncode) + "\n")
sys.stdout.flush()
