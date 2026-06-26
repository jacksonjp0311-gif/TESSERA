
import time, json, sys
sys.path.insert(0, 'src')

start = time.time()
print("Starting NAB diagnostic...")

from tessera.experiments.run_nab_transfer import run_nab_diagnostic

result = run_nab_diagnostic(
    root='.',
    field_dim=16,
    code_dim=8,
    alpha=0.5,
    epochs=2,
    seed=42,
    hidden_dim=64,
    depth=2,
)

elapsed = time.time() - start
print(f"Completed in {elapsed:.1f}s")

# Write result
import os
out_dir = os.path.join('outputs', 'transfers', 'nab')
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, 'machine_temperature_result.json')
with open(out_file, 'w') as f:
    json.dump(result, f, indent=2, default=str)
print(f"Written to {out_file}")

# Print key metrics
metrics = result.get('metrics', {})
print(f"\nKey Metrics:")
print(f"  AUC: {metrics.get('auc', result.get('auc', 'N/A'))}")
print(f"  Recall: {metrics.get('recall', result.get('recall', 'N/A'))}")
print(f"  FMR: {metrics.get('false_memory_rate', result.get('false_memory_rate', 'N/A'))}")
print(f"  Replay: {metrics.get('replay_pass_rate', result.get('replay_pass_rate', 'N/A'))}")
print(f"  Neural Loss: {metrics.get('neural_prediction_loss', result.get('neural_prediction_loss', 'N/A'))}")
print(f"  Baseline: {metrics.get('best_baseline_loss', result.get('best_baseline_loss', 'N/A'))}")
print(f"  Expert: {metrics.get('selected_expert', result.get('selected_expert', 'N/A'))}")
