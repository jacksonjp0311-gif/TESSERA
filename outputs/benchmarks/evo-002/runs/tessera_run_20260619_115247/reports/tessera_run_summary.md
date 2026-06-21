# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_115247`

## Claim ceiling

`diagnostic`

## Core metrics

```json
{
  "mean_J_RD": 343.65227736095767,
  "mean_delta_phi": 0.17775197605324256,
  "warn_rate": 0.15584415584415584,
  "block_rate": 0.19480519480519481,
  "memory_candidate_rate": 0.16883116883116883,
  "replay_pass_rate": 0.0,
  "false_memory_rate": 0.0,
  "auc": 0.4414814814814814,
  "f1_warn": 0.5641025641025641,
  "precision_warn": 0.9166666666666666,
  "recall_warn": 0.4074074074074074,
  "false_memory_candidate_rate": 0.48148148148148145,
  "memory_selectivity": 0.0,
  "block_false_positive": 0.08,
  "missed_warning": 0.5925925925925926,
  "governance_harm": 0.20577777777777775,
  "mean_prediction_loss": 78.78544238712881,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.0,
  "best_baseline_prediction_loss": 78.78077697753906,
  "baseline_gap": -0.004665409589748037
}
```

## Baselines

```json
[
  {
    "model": "persistence",
    "mean_prediction_loss": 112.1211166381836,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 334.8507385253906,
    "mean_reconstruction_loss": 1.7584930039893365e-11
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 272.5636901855469,
    "mean_reconstruction_loss": 61.166378021240234
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 78.78077697753906,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "dense_autoencoder",
    "mean_prediction_loss": 260.0291442871094,
    "mean_reconstruction_loss": 257.6998596191406,
    "parameter_count": 494
  },
  {
    "model": "reservoir_esn",
    "mean_prediction_loss": 390.24041733619316,
    "mean_reconstruction_loss": 0.0,
    "parameter_count": 1408
  },
  {
    "model": "matrix_profile_neighbor",
    "mean_prediction_loss": 272.59661865234375,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
