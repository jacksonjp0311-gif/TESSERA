"""
EVO-051: Real NAB Evaluation + Test Suite Optimization
======================================================
Priority 1: Run NAB transfer with REAL data from Kaggle
Priority 4: Optimize test suite into fast/slow tiers
"""
from __future__ import annotations

import json
import sys
import os
import time
import subprocess
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

base = str(Path(__file__).resolve().parent.parent)

# ============================================================
# Priority 1: Real NAB Evaluation
# ============================================================
print("=" * 60)
print("Priority 1: Real NAB Evaluation")
print("=" * 60)

# Check real NAB data exists
nab_dir = Path(base) / "datasets" / "nab"
machine_temp_file = nab_dir / "realAWSCloudwatch" / "machine_temperature_system_failure.csv"
labels_file = nab_dir / "combined_windows.json"

print(f"Machine temp file: {machine_temp_file.exists()} ({machine_temp_file.stat().st_size if machine_temp_file.exists() else 0} bytes)")
print(f"Labels file: {labels_file.exists()} ({labels_file.stat().st_size if labels_file.exists() else 0} bytes)")

# Read the labels
if labels_file.exists():
    with open(labels_file) as f:
        labels = json.load(f)
    print(f"Labels: {len(labels)} entries")
    for key in list(labels.keys())[:5]:
        print(f"  {key}: {labels[key][:3]}...")

# Read first few lines of machine temp data
if machine_temp_file.exists():
    with open(machine_temp_file) as f:
        for i, line in enumerate(f):
            if i < 5:
                print(f"  {line.strip()}")
            else:
                break
    # Count total lines
    with open(machine_temp_file) as f:
        total = sum(1 for _ in f)
    print(f"  ... {total} total lines")

# Run the NAB transfer evaluation
print("\nRunning NAB transfer evaluation with real data...")
try:
    result = subprocess.run(
        [sys.executable, "-m", "tessera", "transfer-nab", "--root", ".", "--epochs", "4", "--seed", "42"],
        capture_output=True, text=True, timeout=120, cwd=base
    )
    print("STDOUT:", result.stdout[-2000:])
    if result.stderr:
        print("STDERR:", result.stderr[-500:])
    print("Return code:", result.returncode)
except subprocess.TimeoutExpired:
    print("TIMEOUT — NAB evaluation took too long")
except Exception as e:
    print(f"Error: {e}")

# ============================================================
# Priority 4: Test Suite Optimization
# ============================================================
print("\n" + "=" * 60)
print("Priority 4: Test Suite Optimization")
print("=" * 60)

test_dir = Path(base) / "tests"
test_files = sorted([f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")])

fast_tests = []
slow_tests = []

slow_keywords = ['transfer', 'benchmark', 'repair', 'synthetic', 'trajectory', 'checkpoint', 'neural_checkpoint', 'production', 'release', 'security', 'failure_recovery', 'host_integration', 'manifold', 'prefix_state', 'restart_state']

for f in test_files:
    filepath = test_dir / f
    content = filepath.read_text()
    test_count = content.count('def test_')
    
    is_slow = any(kw in f for kw in slow_keywords)
    
    if is_slow:
        slow_tests.append((f, test_count, filepath.stat().st_size))
    else:
        fast_tests.append((f, test_count, filepath.stat().st_size))

fast_total = sum(t[1] for t in fast_tests)
slow_total = sum(t[1] for t in slow_tests)

print(f"\nFast tests ({len(fast_tests)} files, {fast_total} tests):")
for f, c, s in fast_tests:
    print(f"  {f}: {c} tests, {s} bytes")

print(f"\nSlow tests ({len(slow_tests)} files, {slow_total} tests):")
for f, c, s in slow_tests:
    print(f"  {f}: {c} tests, {s} bytes")

print(f"\nTotal: {fast_total + slow_total} tests in {len(test_files)} files")
print(f"Fast tier: {fast_total} tests (should run in <30s)")
print(f"Slow tier: {slow_total} tests (may take 1-3 min)")

# Create pytest markers for fast/slow tiers
print("\nCreating pytest configuration for fast/slow tiers...")

# Create a conftest.py with custom markers
conftest_content = '''
"""
Pytest configuration for fast/slow test tiers.

Usage:
  pytest -m fast          # Run only fast tests (<30s)
  pytest -m slow          # Run only slow tests (1-3 min)
  pytest -m "not slow"   # Skip slow tests
  pytest                  # Run all tests
"""
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "fast: fast tests that complete in <30s")
    config.addinivalue_line("markers", "slow: slow tests that train models or run evaluations (1-3 min)")
    config.addinivalue_line("markers", "integration: integration tests requiring external services")

def pytest_collection_modifyitems(config, items):
    for item in items:
        # Mark slow tests
        if any(kw in item.nodeid for kw in [
            "transfer_nab", "transfer_smap", "transfer_ucr", "benchmark",
            "repair_ablation", "trajectory", "checkpoint", "neural_checkpoint",
            "production", "release", "security", "failure_recovery",
            "host_integration", "manifold", "prefix_state", "restart_state",
            "synthetic"
        ]):
            item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.fast)
'''

conftest_path = test_dir / "conftest.py"
with open(conftest_path, 'w') as f:
    f.write(conftest_content)
print(f"Created {conftest_path}")

# Create a fast test runner script
fast_test_script = '''"""Run only fast tests (no model training)"""
import subprocess
import sys
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-m", "fast", "-v", "--tb=line", "-q"],
    cwd=r"C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera"
)
sys.exit(result.returncode)
'''
with open(Path(base) / "run_fast_tests.py", 'w') as f:
    f.write(fast_test_script)
print("Created run_fast_tests.py")

# Run fast tests to verify they work
print("\nRunning fast tests...")
try:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-m", "fast", "--tb=line", "-q"],
        capture_output=True, text=True, timeout=120, cwd=base
    )
    print(result.stdout[-1000:])
    if result.stderr:
        print("STDERR:", result.stderr[-300:])
    print("Return code:", result.returncode)
except subprocess.TimeoutExpired:
    print("TIMEOUT")
except Exception as e:
    print(f"Error: {e}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
print("EVO-051 Summary")
print("=" * 60)
print(f"Priority 1 (Real NAB Data): {'Downloaded' if machine_temp_file.exists() else 'NOT FOUND'}")
print(f"Priority 4 (Test Optimization): {fast_total} fast + {slow_total} slow = {fast_total + slow_total} total")
print(f"  Fast tier marker: @pytest.mark.fast")
print(f"  Slow tier marker: @pytest.mark.slow")
print(f"  Run fast: pytest -m fast")
print(f"  Run slow: pytest -m slow")
