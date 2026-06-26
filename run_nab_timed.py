import time, sys, os, json
sys.path.insert(0, 'src')
os.chdir('C:/Users/jacks/OneDrive/Desktop/Tessera')

t0 = time.time()

# Load data
from tessera.data.adapters import NabKnownCauseAdapter, DatasetDescriptor
from tessera.data.splits import features_labels, chronological_splits
from pathlib import Path

root = Path('.')
csv_path = root / 'machine_temperature_system_failure.csv'
labels_path = root / 'combined_windows.json'

adapter = NabKnownCauseAdapter(
    csv_path, labels_path,
    'realKnownCause/machine_temperature_system_failure.csv',
    DatasetDescriptor(name='nab', version='1.0', source='kaggle', license='research', label_policy='evaluation_only')
)
df = adapter.load()
t1 = time.time()
print(f"Data loaded: {t1-t0:.1f}s, rows={len(df)}")

# Use chronological splits (same as NAB diagnostic)
splits = chronological_splits(df)
print(f"Splits: cal={len(splits.calibration)}, train={len(splits.train)}, val={len(splits.validation)}, replay={len(splits.replay)}, test={len(splits.final_test)}")

# Get features/labels for each split
from tessera.data.splits import features_labels
X_train, y_train = features_labels(splits.train)
X_val, y_val = features_labels(splits.validation)
X_test, y_test = features_labels(splits.final_test)
X_cal, y_cal = features_labels(splits.calibration)
X_replay, y_replay = features_labels(splits.replay)
t2 = time.time()
print(f"Features: {t2-t1:.1f}s")

# Train model
from tessera.graph.topologies import make_operator
from tessera.model.train import fit_tessera_model

operator = make_operator('ring', 16, seed=42)
model = fit_tessera_model(
    X_train, operator,
    code_dim=8, alpha=0.5, epochs=2, seed=42,
    X_validation=X_val,
    hidden_dim=64, depth=2,
)
t3 = time.time()
print(f"Training: {t3-t2:.1f}s")

# Evaluate
from tessera.model.train import evaluate_sequence
eval_rows = evaluate_sequence(model, X_test)['rows']
t4 = time.time()
print(f"Evaluation: {t4-t3:.1f}s, rows={len(eval_rows)}")

# Anomaly scoring
import pandas as pd
import numpy as np
from tessera.metrics.anomaly import calibrate_anomaly_model, score_anomalies
from tessera.metrics.rate_distortion import add_rate_distortion

eval_df = pd.DataFrame(eval_rows)
eval_df = add_rate_distortion(eval_df)
eval_df['label'] = y_test[1:len(eval_df)+1]

cal_rows = evaluate_sequence(model, X_cal)['rows']
cal_df = pd.DataFrame(cal_rows)
cal_df = add_rate_distortion(cal_df)

anomaly = calibrate_anomaly_model(cal_df)
scored = score_anomalies(eval_df, anomaly)
t5 = time.time()
print(f"Anomaly scoring: {t5-t4:.1f}s")

# AUC
from sklearn.metrics import roc_auc_score
scores = scored['anomaly_score'].to_numpy()
labs = scored['label'].to_numpy()[:len(scores)]
auc = roc_auc_score(labs, scores) if len(np.unique(labs)) > 1 else 0.5
print(f"AUC: {auc:.4f}")

# Recall
from tessera.memory.gates import calibrate_thresholds, apply_triadic_gates
thresholds = calibrate_thresholds(cal_df)
gated = apply_triadic_gates(scored, thresholds, labels=labs)
promoted = int(gated['memory_candidate'].sum()) if 'memory_candidate' in gated else 0
false_mem = int(((gated.get('memory_candidate', 0)==1) & (gated.get('label', 0)==1)).sum()) if 'label' in gated and 'memory_candidate' in gated else 0
total_anom = int(gated['label'].sum()) if 'label' in gated else 0
detected = int(((gated.get('warn', 0)==1) & (gated.get('label', 0)==1)).sum()) if 'label' in gated and 'warn' in gated else 0
recall = detected / max(1, total_anom)
print(f"Recall: {recall:.4f}")
print(f"Total anomalies: {total_anom}, Detected: {detected}")

# Neural loss
neural_loss = float(np.mean([r['prediction_loss'] for r in eval_rows]))
print(f"Neural Loss: {neural_loss:.4f}")

# Baseline
from tessera.baselines.ewma import evaluate_ewma
from tessera.baselines.persistence import evaluate_persistence
ewma_loss = evaluate_ewma(X_test).get('mean_prediction_loss', 999)
pers_loss = evaluate_persistence(X_test).get('mean_prediction_loss', 999)
best_baseline = min(ewma_loss, pers_loss)
print(f"EWMA: {ewma_loss:.4f}, Persistence: {pers_loss:.4f}, Best: {best_baseline:.4f}")
print(f"Neural-Baseline Gap: {neural_loss - best_baseline:.4f}")

t_end = time.time()
print(f"\nTotal: {t_end-t0:.1f}s")

# Save result
result = {
    'auc': float(auc),
    'recall': float(recall),
    'false_memory_rate': float(false_mem / max(1, promoted)),
    'replay_pass_rate': 0.0,  # Would need replay evaluation
    'neural_prediction_loss': float(neural_loss),
    'best_baseline_loss': float(best_baseline),
    'baseline_gap': float(neural_loss - best_baseline),
    'total_anomalies': int(total_anom),
    'detected': int(detected),
    'wall_seconds': float(t_end - t0),
}
out_dir = os.path.join('outputs', 'benchmarks')
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, 'evo051_real_nab.json')
with open(out_file, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Results: {out_file}")
