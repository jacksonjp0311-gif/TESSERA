# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_115253`

## Claim ceiling

`diagnostic`

## Core metrics

```json
{
  "mean_J_RD": 506.51595071692185,
  "mean_delta_phi": 0.1590614505716926,
  "warn_rate": 0.16883116883116883,
  "block_rate": 0.19480519480519481,
  "memory_candidate_rate": 0.6103896103896104,
  "replay_pass_rate": 0.0,
  "false_memory_rate": 0.0,
  "auc": 0.4444444444444444,
  "f1_warn": 0.6,
  "precision_warn": 0.9230769230769231,
  "recall_warn": 0.4444444444444444,
  "false_memory_candidate_rate": 0.5185185185185185,
  "memory_selectivity": 0.66,
  "block_false_positive": 0.04,
  "missed_warning": 0.5555555555555556,
  "governance_harm": 0.18066666666666664,
  "mean_prediction_loss": 115.09393644313533,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.0,
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
