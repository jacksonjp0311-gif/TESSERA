# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_121549`

## Claim ceiling

`diagnostic`

## Core metrics

```json
{
  "mean_J_RD": 440.28478596897713,
  "mean_anomaly_score": 9.849635748954674,
  "mean_delta_phi": 0.1358254642842652,
  "warn_rate": 0.7272727272727273,
  "block_rate": 0.5454545454545454,
  "memory_candidate_rate": 0.2727272727272727,
  "replay_pass_rate": 0.8,
  "false_memory_rate": 0.07407407407407407,
  "auc": 0.7962962962962963,
  "f1_warn": 0.6024096385542169,
  "precision_warn": 0.44642857142857145,
  "recall_warn": 0.9259259259259259,
  "false_memory_candidate_rate": 0.07407407407407407,
  "memory_selectivity": 0.30592592592592593,
  "block_false_positive": 0.4,
  "missed_warning": 0.07407407407407407,
  "governance_harm": 0.18814814814814815,
  "mean_prediction_loss": 95.22867042716447,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.06666666666666667,
  "anomaly_ablation": {
    "prediction_loss": 0.7651851851851851,
    "reconstruction_loss": 0.5,
    "delta_phi": 0.6651851851851851,
    "code_drift": 0.7807407407407406,
    "rate": 0.42,
    "combined_multiscale": 0.7962962962962963
  },
  "best_baseline_prediction_loss": 95.227783203125,
  "baseline_gap": -0.0008872240394737219
}
```

## Baselines

```json
[
  {
    "model": "persistence",
    "mean_prediction_loss": 143.75164794921875,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 356.39459228515625,
    "mean_reconstruction_loss": 3.395804817896142e-11
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 365.5517578125,
    "mean_reconstruction_loss": 133.28521728515625
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 95.227783203125,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "dense_autoencoder",
    "mean_prediction_loss": 340.6875305175781,
    "mean_reconstruction_loss": 339.1275939941406,
    "parameter_count": 494
  },
  {
    "model": "reservoir_esn",
    "mean_prediction_loss": 312.25307806973,
    "mean_reconstruction_loss": 0.0,
    "parameter_count": 1408
  },
  {
    "model": "matrix_profile_neighbor",
    "mean_prediction_loss": 342.743896484375,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
