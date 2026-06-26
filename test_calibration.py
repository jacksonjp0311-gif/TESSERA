import sys, os, json, time, numpy as np, pandas as pd
sys.path.insert(0, 'src')
os.chdir('C:/Users/jacks/OneDrive/Desktop/Tessera')

from tessera.metrics.anomaly import calibrate_anomaly_model, score_anomalies, anomaly_ablation
from tessera.memory.gates import calibrate_thresholds, apply_triadic_gates
from sklearn.metrics import roc_auc_score

# Generate synthetic data with known anomalies
np.random.seed(42)
n_normal = 500
n_anomaly = 50

# Normal data
normal_data = {
    'prediction_loss': np.random.exponential(0.5, n_normal),
    'reconstruction_loss': np.random.exponential(0.3, n_normal),
    'delta_phi': np.random.normal(0, 0.01, n_normal),
    'code_drift': np.random.normal(0, 0.05, n_normal),
    'rate': np.random.exponential(0.1, n_normal),
}
normal_df = pd.DataFrame(normal_data)

# Test data (normal + anomalous)
test_data = {
    'prediction_loss': np.concatenate([np.random.exponential(0.5, n_normal), np.random.exponential(5.0, n_anomaly)]),
    'reconstruction_loss': np.concatenate([np.random.exponential(0.3, n_normal), np.random.exponential(3.0, n_anomaly)]),
    'delta_phi': np.concatenate([np.random.normal(0, 0.01, n_normal), np.random.normal(0, 0.5, n_anomaly)]),
    'code_drift': np.concatenate([np.random.normal(0, 0.05, n_normal), np.random.normal(0, 0.8, n_anomaly)]),
    'rate': np.concatenate([np.random.exponential(0.1, n_normal), np.random.exponential(2.0, n_anomaly)]),
}
test_df = pd.DataFrame(test_data)
test_df['label'] = np.concatenate([np.zeros(n_normal), np.ones(n_anomaly)])

labs = test_df['label'].to_numpy()
total_anom = int(labs.sum())
print(f"Test data: {len(test_df)} rows, {total_anom} anomalies")

# OLD calibration
anomaly_old = calibrate_anomaly_model(normal_df, adaptive=False)
scored_old = score_anomalies(test_df.drop(columns=['label']), anomaly_old)
scored_old['label'] = labs
auc_old = roc_auc_score(labs, scored_old['anomaly_score'].to_numpy())
thresh_old = calibrate_thresholds(normal_df)
gated_old = apply_triadic_gates(scored_old, thresh_old, labels=labs)
detected_old = int(((gated_old.get('warn',0)==1) & (gated_old.get('label',0)==1)).sum())
recall_old = detected_old / max(1, total_anom)

# NEW calibration (adaptive)
anomaly_new = calibrate_anomaly_model(normal_df, adaptive=True)
scored_new = score_anomalies(test_df.drop(columns=['label']), anomaly_new)
scored_new['label'] = labs
auc_new = roc_auc_score(labs, scored_new['anomaly_score'].to_numpy())
thresh_new = calibrate_thresholds(normal_df)
gated_new = apply_triadic_gates(scored_new, thresh_new, labels=labs)
detected_new = int(((gated_new.get('warn',0)==1) & (gated_new.get('label',0)==1)).sum())
recall_new = detected_new / max(1, total_anom)

print(f"\n=== CALIBRATION COMPARISON ===")
print(f"OLD (quantile-based):  AUC={auc_old:.4f}, Recall={recall_old:.4f} ({detected_old}/{total_anom})")
print(f"NEW (adaptive):       AUC={auc_new:.4f}, Recall={recall_new:.4f} ({detected_new}/{total_anom})")
print(f"\nOld warn_thresh: {anomaly_old['warn_score']:.4f}")
print(f"New warn_thresh: {anomaly_new['warn_score']:.4f}")

# Ablation
ablation = anomaly_ablation(scored_new)
print(f"\nAblation: {json.dumps({k: round(v,4) for k,v in ablation.items()}, indent=2)}")

# Save result
result = {
    'test': 'EVO-052_calibration_fix',
    'old_auc': float(auc_old), 'new_auc': float(auc_new),
    'old_recall': float(recall_old), 'new_recall': float(recall_new),
    'total_anomalies': total_anom,
    'old_detected': detected_old, 'new_detected': detected_new,
}
os.makedirs(os.path.join('outputs', 'benchmarks'), exist_ok=True)
with open(os.path.join('outputs', 'benchmarks', 'evo052_calibration.json'), 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nSaved to outputs/benchmarks/evo052_calibration.json")
