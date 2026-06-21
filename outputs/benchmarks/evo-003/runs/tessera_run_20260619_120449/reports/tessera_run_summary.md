# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_120449`

## Claim ceiling

`synthetic_phase_1_run_supported`

## Core metrics

```json
{
  "mean_J_RD": 343.65227736095767,
  "mean_anomaly_score": 9.74761906282284,
  "mean_delta_phi": 0.17775197605324256,
  "warn_rate": 0.6493506493506493,
  "block_rate": 0.5454545454545454,
  "memory_candidate_rate": 0.35064935064935066,
  "replay_pass_rate": 0.6461538461538462,
  "false_memory_rate": 0.0,
  "auc": 0.8088888888888889,
  "f1_warn": 0.6493506493506493,
  "precision_warn": 0.5,
  "recall_warn": 0.9259259259259259,
  "false_memory_candidate_rate": 0.07407407407407407,
  "memory_selectivity": 0.5,
  "block_false_positive": 0.38,
  "missed_warning": 0.07407407407407407,
  "governance_harm": 0.1552222222222222,
  "mean_prediction_loss": 78.78544238712881,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.0,
  "anomaly_ablation": {
    "prediction_loss": 0.7703703703703705,
    "reconstruction_loss": 0.5,
    "delta_phi": 0.6644444444444445,
    "code_drift": 0.7874074074074074,
    "rate": 0.7814814814814814,
    "combined_multiscale": 0.8088888888888889
  },
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
