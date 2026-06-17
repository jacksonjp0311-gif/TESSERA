# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260617_020243`

## Claim ceiling

`diagnostic_baseline_limited`

## Core metrics

```json
{
  "mean_J_RD": 537.6694138251295,
  "mean_delta_phi": 0.24303276634706958,
  "warn_rate": 0.14634146341463414,
  "block_rate": 0.1951219512195122,
  "memory_candidate_rate": 0.21951219512195122,
  "replay_pass_rate": 0.024390243902439025,
  "false_memory_rate": 0.0,
  "auc": 0.39743589743589747,
  "f1_warn": 0.47619047619047616,
  "precision_warn": 0.8333333333333334,
  "recall_warn": 0.3333333333333333,
  "false_memory_candidate_rate": 0.5333333333333333,
  "memory_selectivity": 0.038461538461538464,
  "block_false_positive": 0.038461538461538464,
  "missed_warning": 0.6666666666666666,
  "governance_harm": 0.21346153846153845,
  "mean_prediction_loss": 271.1925674066311,
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
    "mean_prediction_loss": 210.8516387939453,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 386.51806640625,
    "mean_reconstruction_loss": 3.0864949485120974e-11
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 337.9871520996094,
    "mean_reconstruction_loss": 47.40000534057617
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 107.38321685791016,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
