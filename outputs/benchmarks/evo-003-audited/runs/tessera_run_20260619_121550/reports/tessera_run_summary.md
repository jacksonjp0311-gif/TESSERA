# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_121550`

## Claim ceiling

`diagnostic`

## Core metrics

```json
{
  "mean_J_RD": 506.51595071692185,
  "mean_anomaly_score": 9.890999539189549,
  "mean_delta_phi": 0.1590614505716926,
  "warn_rate": 0.8051948051948052,
  "block_rate": 0.6233766233766234,
  "memory_candidate_rate": 0.19480519480519481,
  "replay_pass_rate": 0.52,
  "false_memory_rate": 0.0,
  "auc": 0.7844444444444445,
  "f1_warn": 0.6067415730337079,
  "precision_warn": 0.43548387096774194,
  "recall_warn": 1.0,
  "false_memory_candidate_rate": 0.0,
  "memory_selectivity": 0.3,
  "block_false_positive": 0.48,
  "missed_warning": 0.0,
  "governance_harm": 0.16799999999999998,
  "mean_prediction_loss": 115.09393644313533,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.0,
  "anomaly_ablation": {
    "prediction_loss": 0.7318518518518519,
    "reconstruction_loss": 0.5,
    "delta_phi": 0.6888888888888889,
    "code_drift": 0.782962962962963,
    "rate": 0.8348148148148148,
    "combined_multiscale": 0.7844444444444445
  },
  "best_baseline_prediction_loss": 115.08956146240234,
  "baseline_gap": -0.004374980732990252
}
```

## Baselines

```json
[
  {
    "model": "persistence",
    "mean_prediction_loss": 174.1857452392578,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 194.69227600097656,
    "mean_reconstruction_loss": 2.8320762401889965e-11
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 218.23277282714844,
    "mean_reconstruction_loss": 49.804847717285156
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 115.08956146240234,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "dense_autoencoder",
    "mean_prediction_loss": 390.21771240234375,
    "mean_reconstruction_loss": 386.67840576171875,
    "parameter_count": 494
  },
  {
    "model": "reservoir_esn",
    "mean_prediction_loss": 377.78059691577863,
    "mean_reconstruction_loss": 0.0,
    "parameter_count": 1408
  },
  {
    "model": "matrix_profile_neighbor",
    "mean_prediction_loss": 387.4097900390625,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
