import time, sys
sys.path.insert(0, 'src')

t0 = time.time()
from tessera.data.adapters import NabKnownCauseAdapter, DatasetDescriptor
from pathlib import Path

# Use forward slashes to avoid escape issues
root = Path('C:/Users/jacks/OneDrive/Desktop/Tessera')
print('Root:', root)
print('Root exists:', root.exists())

csv_path = root / 'machine_temperature_system_failure.csv'
labels_path = root / 'combined_windows.json'
print('CSV exists:', csv_path.exists())
print('Labels exists:', labels_path.exists())

if csv_path.exists():
    print('CSV size:', csv_path.stat().st_size, 'bytes')

# Try loading
try:
    adapter = NabKnownCauseAdapter(
        csv_path, labels_path,
        'realKnownCause/machine_temperature_system_failure.csv',
        DatasetDescriptor(name='nab', version='1.0', source='kaggle', license='research', label_policy='evaluation_only')
    )
    df = adapter.load()
    t1 = time.time()
    print(f'Data loaded in {t1-t0:.1f}s, rows={len(df)}')
    print('Columns:', list(df.columns))
    print(df.head(2))
except Exception as e:
    t1 = time.time()
    print(f'Load failed after {t1-t0:.1f}s: {e}')
