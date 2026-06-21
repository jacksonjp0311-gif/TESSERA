# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260621_065621`

## Claim ceiling

`synthetic_phase_1_run_supported`

## Core metrics

```json
{
  "mean_J_RD": 746.9958673969377,
  "mean_anomaly_score": 9.731525201696652,
  "mean_delta_phi": 0.18758574221283197,
  "warn_rate": 0.8,
  "block_rate": 0.4,
  "memory_candidate_rate": 0.2,
  "replay_pass_rate": 0.8461538461538461,
  "false_memory_rate": 0.0,
  "auc": 1.0,
  "f1_warn": 0.6086956521739131,
  "precision_warn": 0.4375,
  "recall_warn": 1.0,
  "false_memory_candidate_rate": 0.0,
  "memory_selectivity": 0.3076923076923077,
  "block_false_positive": 0.07692307692307693,
  "missed_warning": 0.0,
  "governance_harm": 0.026923076923076925,
  "mean_prediction_loss": 169.26374990940093,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.25,
  "anomaly_ablation": {
    "prediction_loss": 1.0,
    "reconstruction_loss": 0.5,
    "delta_phi": 0.49450549450549447,
    "code_drift": 0.7802197802197802,
    "rate": 0.5164835164835164,
    "combined_multiscale": 1.0
  },
  "best_baseline_prediction_loss": 169.2637481689453,
  "baseline_gap": -1.7404556160727225e-06
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
  },
  {
    "model": "dense_autoencoder",
    "mean_prediction_loss": 536.3521728515625,
    "mean_reconstruction_loss": 548.8662719726562,
    "parameter_count": 494
  },
  {
    "model": "reservoir_esn",
    "mean_prediction_loss": 542.31591540162,
    "mean_reconstruction_loss": 0.0,
    "parameter_count": 1408
  },
  {
    "model": "matrix_profile_neighbor",
    "mean_prediction_loss": 526.0848388671875,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
