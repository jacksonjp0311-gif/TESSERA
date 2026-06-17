# TESSERA Engine v0.1 Run Summary

run_id: `tessera_run_20260617_012047`

## Claim ceiling

`diagnostic_baseline_limited`

## Core metrics

```json
{
  "mean_J_RD": 528.4817369026282,
  "mean_delta_phi": 0.1409488161326318,
  "warn_rate": 0.09871244635193133,
  "block_rate": 0.17167381974248927,
  "memory_candidate_rate": 0.19742489270386265,
  "replay_pass_rate": 0.008583690987124463,
  "false_memory_rate": 0.0,
  "auc": 0.41358024691358025,
  "f1_warn": 0.4230769230769231,
  "precision_warn": 0.9565217391304348,
  "recall_warn": 0.2716049382716049,
  "false_memory_candidate_rate": 0.5432098765432098,
  "memory_selectivity": 0.013157894736842105,
  "block_false_positive": 0.02631578947368421,
  "missed_warning": 0.7283950617283951,
  "governance_harm": 0.227729044834308,
  "mean_prediction_loss": 277.01634170466735,
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
    "mean_prediction_loss": 121.3536148071289,
    "mean_reconstruction_loss": 0.0
  },
  {
    "model": "pca_codec",
    "mean_prediction_loss": 212.7289276123047,
    "mean_reconstruction_loss": 1.7501303141084779e-12
  },
  {
    "model": "random_projection",
    "mean_prediction_loss": 186.734130859375,
    "mean_reconstruction_loss": 6.216370582580566
  },
  {
    "model": "ewma",
    "mean_prediction_loss": 75.84559631347656,
    "mean_reconstruction_loss": 0.0
  }
]
```

## Non-claim lock

Synthetic success is not transfer. Low loss is not truth. Memory is certified compression.
