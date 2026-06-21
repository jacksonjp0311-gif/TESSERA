# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_120457`

## Claim ceiling

`synthetic_phase_1_run_supported`

## Core metrics

```json
{
  "mean_J_RD": 365.73567961444496,
  "mean_anomaly_score": 9.431731607185,
  "mean_delta_phi": 0.13726772009334587,
  "warn_rate": 0.6363636363636364,
  "block_rate": 0.5584415584415584,
  "memory_candidate_rate": 0.36363636363636365,
  "replay_pass_rate": 0.6615384615384615,
  "false_memory_rate": 0.0,
  "auc": 0.8422222222222222,
  "f1_warn": 0.6578947368421053,
  "precision_warn": 0.5102040816326531,
  "recall_warn": 0.9259259259259259,
  "false_memory_candidate_rate": 0.07407407407407407,
  "memory_selectivity": 0.52,
  "block_false_positive": 0.38,
  "missed_warning": 0.07407407407407407,
  "governance_harm": 0.1552222222222222,
  "mean_prediction_loss": 78.37565490293812,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.0,
  "anomaly_ablation": {
    "prediction_loss": 0.8014814814814815,
    "reconstruction_loss": 0.5,
    "delta_phi": 0.7251851851851852,
    "code_drift": 0.7644444444444444,
    "rate": 0.8533333333333333,
    "combined_multiscale": 0.8422222222222222
  },
  "best_baseline_prediction_loss": 78.37889099121094,
  "baseline_gap": 0.003236088272814186
}
```

## Baselines

```json
[
  {
    "model": "persistence",
    "mean_prediction_loss": 102.77293395996094,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 309.5216064453125,
    "mean_reconstruction_loss": 4.2617798179378497e-11
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 312.63470458984375,
    "mean_reconstruction_loss": 12.605525970458984
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 78.37889099121094,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "dense_autoencoder",
    "mean_prediction_loss": 281.03387451171875,
    "mean_reconstruction_loss": 280.0171813964844,
    "parameter_count": 494
  },
  {
    "model": "reservoir_esn",
    "mean_prediction_loss": 291.98420706890676,
    "mean_reconstruction_loss": 0.0,
    "parameter_count": 1408
  },
  {
    "model": "matrix_profile_neighbor",
    "mean_prediction_loss": 288.9347839355469,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
