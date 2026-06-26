
import subprocess, sys, os, shutil
from pathlib import Path

base = r"C:\Users\jacks\OneDrive\Desktop\Tessera"
os.chdir(base)

# Copy NAB data files to where the CLI expects them
src_csv = os.path.join(base, 'datasets', 'nab', 'realKnownCause', 'realKnownCause', 'machine_temperature_system_failure.csv')
dst_csv = os.path.join(base, 'machine_temperature_system_failure.csv')
if os.path.exists(src_csv):
    shutil.copy2(src_csv, dst_csv)
    print(f'Copied CSV: {os.path.getsize(dst_csv)} bytes')
else:
    print(f'SRC not found: {src_csv}')

src_labels = os.path.join(base, 'datasets', 'nab', 'combined_windows.json')
dst_labels = os.path.join(base, 'combined_windows.json')
if os.path.exists(src_labels):
    shutil.copy2(src_labels, dst_labels)
    print(f'Copied labels: {os.path.getsize(dst_labels)} bytes')

# Run NAB transfer
print('\nRunning NAB transfer (90s timeout)...')
try:
    result = subprocess.run(
        [sys.executable, '-m', 'tessera', 'transfer-nab', '--root', '.', '--epochs', '2', '--seed', '42'],
        capture_output=True, text=True, timeout=90
    )
    print('STDOUT:', result.stdout[-2000:])
    if result.stderr:
        print('STDERR:', result.stderr[-500:])
    print('Return code:', result.returncode)
except subprocess.TimeoutExpired:
    print('TIMEOUT')
except Exception as e:
    print(f'Error: {e}')
