# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260617_015939`

## Claim ceiling

`diagnostic_baseline_limited`

## Core metrics

```json
{
  "mean_J_RD": 806.3054568323728,
  "mean_delta_phi": 0.16089655550425513,
  "warn_rate": 0.17543859649122806,
  "block_rate": 0.21052631578947367,
  "memory_candidate_rate": 0.21052631578947367,
  "replay_pass_rate": 0.017543859649122806,
  "false_memory_rate": 0.0,
  "auc": 0.4486486486486487,
  "f1_warn": 0.6,
  "precision_warn": 0.9,
  "recall_warn": 0.45,
  "false_memory_candidate_rate": 0.55,
  "memory_selectivity": 0.02702702702702703,
  "block_false_positive": 0.08108108108108109,
  "missed_warning": 0.55,
  "governance_harm": 0.19337837837837837,
  "mean_prediction_loss": 407.61472441020766,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4"
}
```

## Baselines

```json
[
  {
    "model": "persistence",
    "mean_prediction_loss": 230.47926330566406,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 524.2716064453125,
    "mean_reconstruction_loss": 1.6286272330745533e-10
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 524.4909057617188,
    "mean_reconstruction_loss": 16.014015197753906
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 141.8318634033203,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
