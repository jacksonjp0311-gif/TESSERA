# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260616_230100`

## Claim ceiling

`diagnostic_baseline_limited`

## Core metrics

```json
{
  "mean_J_RD": 1112.3328952240831,
  "mean_delta_phi": 0.24561966098845006,
  "warn_rate": 0.2,
  "block_rate": 0.15,
  "memory_candidate_rate": 0.45,
  "replay_pass_rate": 0.25,
  "false_memory_rate": 0.0,
  "auc": 0.3736263736263736,
  "f1_warn": 0.36363636363636365,
  "precision_warn": 0.5,
  "recall_warn": 0.2857142857142857,
  "false_memory_candidate_rate": 0.5714285714285714,
  "memory_selectivity": 0.38461538461538464,
  "block_false_positive": 0.07692307692307693,
  "missed_warning": 0.7142857142857143,
  "governance_harm": 0.24120879120879118,
  "mean_prediction_loss": 552.010912322998,
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
    "mean_prediction_loss": 184.9776611328125,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 463.82379150390625,
    "mean_reconstruction_loss": 8.77243763741653e-11
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 477.85516357421875,
    "mean_reconstruction_loss": 66.24418640136719
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 169.2637481689453,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
