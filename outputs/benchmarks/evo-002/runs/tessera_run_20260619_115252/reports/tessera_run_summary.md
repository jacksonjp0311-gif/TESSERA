# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_115252`

## Claim ceiling

`diagnostic`

## Core metrics

```json
{
  "mean_J_RD": 440.28478596897713,
  "mean_delta_phi": 0.1358254642842652,
  "warn_rate": 0.15584415584415584,
  "block_rate": 0.16883116883116883,
  "memory_candidate_rate": 0.18181818181818182,
  "replay_pass_rate": 0.0,
  "false_memory_rate": 0.0,
  "auc": 0.4407407407407407,
  "f1_warn": 0.5641025641025641,
  "precision_warn": 0.9166666666666666,
  "recall_warn": 0.4074074074074074,
  "false_memory_candidate_rate": 0.5185185185185185,
  "memory_selectivity": 0.0,
  "block_false_positive": 0.02,
  "missed_warning": 0.5925925925925926,
  "governance_harm": 0.18477777777777776,
  "mean_prediction_loss": 95.22867042716447,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.0,
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
