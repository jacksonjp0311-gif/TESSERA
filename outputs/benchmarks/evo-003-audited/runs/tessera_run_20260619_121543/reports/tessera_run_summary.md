# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_121543`

## Claim ceiling

`synthetic_phase_1_run_supported`

## Core metrics

```json
{
  "mean_J_RD": 343.65227736095767,
  "mean_anomaly_score": 9.74761906282284,
  "mean_delta_phi": 0.17775197605324256,
  "warn_rate": 0.7662337662337663,
  "block_rate": 0.5454545454545454,
  "memory_candidate_rate": 0.23376623376623376,
  "replay_pass_rate": 0.74,
  "false_memory_rate": 0.037037037037037035,
  "auc": 0.8088888888888889,
  "f1_warn": 0.6046511627906976,
  "precision_warn": 0.4406779661016949,
  "recall_warn": 0.9629629629629629,
  "false_memory_candidate_rate": 0.037037037037037035,
  "memory_selectivity": 0.302962962962963,
  "block_false_positive": 0.38,
  "missed_warning": 0.037037037037037035,
  "governance_harm": 0.15707407407407403,
  "mean_prediction_loss": 78.78544238712881,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.06666666666666667,
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
