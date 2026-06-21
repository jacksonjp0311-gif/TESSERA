# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260619_115255`

## Claim ceiling

`diagnostic`

## Core metrics

```json
{
  "mean_J_RD": 365.73567961444496,
  "mean_delta_phi": 0.13726772009334587,
  "warn_rate": 0.16883116883116883,
  "block_rate": 0.22077922077922077,
  "memory_candidate_rate": 0.16883116883116883,
  "replay_pass_rate": 0.0,
  "false_memory_rate": 0.0,
  "auc": 0.4096296296296296,
  "f1_warn": 0.55,
  "precision_warn": 0.8461538461538461,
  "recall_warn": 0.4074074074074074,
  "false_memory_candidate_rate": 0.48148148148148145,
  "memory_selectivity": 0.0,
  "block_false_positive": 0.08,
  "missed_warning": 0.5925925925925926,
  "governance_harm": 0.20577777777777775,
  "mean_prediction_loss": 78.37565490293812,
  "code_dim": 8,
  "field_dim": 16,
  "topology": "q4",
  "replay_false_memory_rate": 0.0,
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
