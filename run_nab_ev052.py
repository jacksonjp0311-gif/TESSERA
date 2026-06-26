import sys, os, json, time, numpy as np, pandas as pd
sys.path.insert(0, 'src')
os.chdir('C:/Users/jacks/OneDrive/Desktop/Tessera')

# Load data
from tessera.data.adapters import NabKnownCauseAdapter, DatasetDescriptor
from tessera.data.splits import features_labels, chronological_splits
from pathlib import Path

root = Path('.')
csv_path = root / 'machine_temperature_system_failure.csv'
labels_path = root / 'combined_windows.json'
adapter = NabKnownCauseAdapter(csv_path, labels_path, 'realKnownCause/machine_temperature_system_failure.csv', DatasetDescriptor(name='nab', version='1.0', source='kaggle', license='research', label_policy='evaluation_only'))
df = adapter.load()
splits = chronological_splits(df)
X_train, y_train = features_labels(splits.train)
X_val, y_val = features_labels(splits.validation)
X_test, y_test = features_labels(splits.final_test)
X_cal, y_cal = features_labels(splits.calibration)

print(f"Data: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}, cal={len(X_cal)}")

# Train model
from tessera.graph.topologies import make_operator
from tessera.model.train import fit_tessera_model, evaluate_sequence
from tessera.metrics.rate_distortion import add_rate_distortion
from tessera.metrics.anomaly import calibrate_anomaly_model, score_anomalies, anomaly_ablation
from tessera.memory.gates import calibrate_thresholds, apply_triadic_gates
from sklearn.metrics import roc_auc_score

operator = make_operator('ring', 16, seed=42)
model = fit_tessera_model(X_train, operator, code_dim=8, alpha=0.5, epochs=2, seed=42, X_validation=X_val, hidden_dim=64, depth=2)
print(f"Training done")

# Evaluate
eval_rows = evaluate_sequence(model, X_test)['rows']
eval_df = pd.DataFrame(eval_rows)
eval_df = add_rate_distortion(eval_df)
eval_df['label'] = y_test[1:len(eval_df)+1]

cal_rows = evaluate_sequence(model, X_cal)['rows']
cal_df = pd.DataFrame(cal_rows)
cal_df = add_rate_distortion(cal_df)

labs = eval_df['label'].to_numpy()
total_anom = int(labs.sum())
print(f"Test: {len(eval_df)} rows, {total_anom} anomalies")

# OLD calibration (strict, quantile-based)
anomaly_old = calibrate_anomaly_model(cal_df, adaptive=False)
scored_old = score_anomalies(eval_df, anomaly_old)
auc_old = roc_auc_score(labs, scored_old['anomaly_score'].to_numpy()[:len(labs)])
thresh_old = calibrate_thresholds(cal_df)
gated_old = apply_triadic_gates(scored_old, thresh_old, labels=labs)
detected_old = int(((gated_old.get('warn',0)==1) & (gated_old.get('label',0)==1)).sum())
recall_old = detected_old / max(1, total_anom)

# NEW calibration (adaptive, per-component multimax)
anomaly_new = calibrate_anomaly_model(cal_df, adaptive=True)
scored_new = score_anomalies(eval_df, anomaly_new)
auc_new = roc_auc_score(labs, scored_new['anomaly_score'].to_numpy()[:len(labs)])
thresh_new = calibrate_thresholds(cal_df)
gated_new = apply_triadic_gates(scored_new, thresh_new, labels=labs)
detected_new = int(((gated_new.get('warn',0)==1) & (gated_new.get('label',0)==1)).sum())
recall_new = detected_new / max(1, total_anom)

print(f"\n=== RESULTS ===")
print(f"OLD: AUC={auc_old:.4f}, Recall={recall_old:.4f} ({detected_old}/{total_anom}), warn_thresh={anomaly_old['warn_score']:.4f}")
print(f"NEW: AUC={auc_new:.4f}, Recall={recall_new:.4f} ({detected_new}/{total_anom}), warn_thresh={anomaly_new['warn_score']:.4f}")

# Ablation
ablation = anomaly_ablation(scored_new)
print(f"\nAblation: {json.dumps(ablation, indent=2)}")
