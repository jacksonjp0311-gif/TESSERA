# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_121547`

## Claim ceiling

`diagnostic`

## Core metrics

```json
{
  "mean_J_RD": 388.7290605677795,
  "mean_anomaly_score": 9.878371540916255,
  "mean_delta_phi": 0.16771021036600525,
  "warn_rate": 0.7142857142857143,
  "block_rate": 0.4805194805194805,
  "memory_candidate_rate": 0.2857142857142857,
  "replay_pass_rate": 0.86,
  "false_memory_rate": 0.07407407407407407,
  "auc": 0.8022222222222222,
  "f1_warn": 0.6097560975609756,
  "precision_warn": 0.45454545454545453,
  "recall_warn": 0.9259259259259259,
  "false_memory_candidate_rate": 0.07407407407407407,
  "memory_selectivity": 0.32592592592592595,
  "block_false_positive": 0.32,
  "missed_warning": 0.07407407407407407,
  "governance_harm": 0.16014814814814812,
  "mean_prediction_loss": 100.06898159514387,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.06666666666666667,
  "anomaly_ablation": {
    "prediction_loss": 0.7496296296296296,
    "reconstruction_loss": 0.48148148148148145,
    "delta_phi": 0.7518518518518519,
    "code_drift": 0.712962962962963,
    "rate": 0.9259259259259259,
    "combined_multiscale": 0.8022222222222222
  },
  "best_baseline_prediction_loss": 100.06897735595703,
  "baseline_gap": -4.239186836230147e-06
}
```

## Baselines

```json
[
  {
    "model": "persistence",
    "mean_prediction_loss": 179.35760498046875,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 315.8506164550781,
    "mean_reconstruction_loss": 1.250125437196603e-11
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 327.3168640136719,
    "mean_reconstruction_loss": 43.072593688964844
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 100.06897735595703,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "dense_autoencoder",
    "mean_prediction_loss": 278.90435791015625,
    "mean_reconstruction_loss": 275.320556640625,
    "parameter_count": 494
  },
  {
    "model": "reservoir_esn",
    "mean_prediction_loss": 395.3641594490207,
    "mean_reconstruction_loss": 0.0,
    "parameter_count": 1408
  },
  {
    "model": "matrix_profile_neighbor",
    "mean_prediction_loss": 287.7799072265625,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
