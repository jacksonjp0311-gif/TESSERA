# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_115250`

## Claim ceiling

`diagnostic`

## Core metrics

```json
{
  "mean_J_RD": 388.7290605677795,
  "mean_delta_phi": 0.16771021036600525,
  "warn_rate": 0.16883116883116883,
  "block_rate": 0.19480519480519481,
  "memory_candidate_rate": 0.18181818181818182,
  "replay_pass_rate": 0.0,
  "false_memory_rate": 0.0,
  "auc": 0.4422222222222222,
  "f1_warn": 0.6,
  "precision_warn": 0.9230769230769231,
  "recall_warn": 0.4444444444444444,
  "false_memory_candidate_rate": 0.5185185185185185,
  "memory_selectivity": 0.0,
  "block_false_positive": 0.06,
  "missed_warning": 0.5555555555555556,
  "governance_harm": 0.18766666666666665,
  "mean_prediction_loss": 100.06898159514387,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.0,
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
