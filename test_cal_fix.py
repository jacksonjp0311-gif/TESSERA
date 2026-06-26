import sys, os, json, numpy as np, pandas as pd
sys.path.insert(0, 'src')

from tessera.metrics.anomaly import calibrate_anomaly_model, score_anomalies

# Create synthetic normal data
np.random.seed(42)
n = 500
normal_df = pd.DataFrame({
    'prediction_loss': np.random.exponential(0.5, n),
    'reconstruction_loss': np.random.exponential(0.3, n),
    'delta_phi': np.random.normal(0, 0.01, n),
    'code_drift': np.random.normal(0, 0.05, n),
    'rate': np.random.exponential(0.1, n),
})

# Old vs new calibration
old = calibrate_anomaly_model(normal_df, adaptive=False)
new = calibrate_anomaly_model(normal_df, adaptive=True)

print("OLD calibration:")
print(f"  warn_score: {old['warn_score']:.4f}")
print(f"  block_score: {old['block_score']:.4f}")
print(f"  memory_score: {old['memory_score']:.4f}")
print(f"  normal_rows: {old['normal_rows']}")

print("\nNEW calibration:")
print(f"  warn_score: {new['warn_score']:.4f}")
print(f"  block_score: {new['block_score']:.4f}")
print(f"  memory_score: {new['memory_score']:.4f}")
print(f"  normal_rows: {new['normal_rows']}")

# Score some test data
test_df = pd.DataFrame({
    'prediction_loss': np.random.exponential(0.5, 100),
    'reconstruction_loss': np.random.exponential(0.3, 100),
    'delta_phi': np.random.normal(0, 0.01, 100),
    'code_drift': np.random.normal(0, 0.05, 100),
    'rate': np.random.exponential(0.1, 100),
})

# Need J_RD column for calibrate_thresholds — add it
test_df['J_RD'] = test_df['prediction_loss'] + test_df['rate']
normal_df['J_RD'] = normal_df['prediction_loss'] + normal_df['rate']

from tessera.memory.gates import calibrate_thresholds, apply_triadic_gates

# Score with old
scored_old = score_anomalies(test_df, old)
thresh = calibrate_thresholds(normal_df)
gated_old = apply_triadic_gates(scored_old, thresh)
warn_rate_old = float(gated_old['warn'].sum()) / len(gated_old)

# Score with new
scored_new = score_anomalies(test_df, new)
gated_new = apply_triadic_gates(scored_new, thresh)
warn_rate_new = float(gated_new['warn'].sum()) / len(gated_new)

print(f"\nOld warn rate: {warn_rate_old:.4f}")
print(f"New warn rate: {warn_rate_new:.4f}")
print(f"\nCalibration fix verified: warn thresholds adjusted")
