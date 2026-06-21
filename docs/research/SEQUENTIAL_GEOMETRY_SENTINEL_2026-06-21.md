# EVO-040 Sequential Geometry Sentinel

## Cross-domain search

EVO-040 searched four neighboring fields for mechanisms relevant to Tessera's
next limitation:

- streaming subspace tracking treats a principal direction as state that can
  be updated and monitored online;
- statistical process control uses CUSUM to detect persistent small shifts
  that may not cross a single-observation limit;
- conformal test martingales accumulate sequential evidence against
  exchangeability and distinguish validity from detection efficiency;
- recurrent inference preserves hidden state between steps instead of
  repeatedly reconstructing all prior computation.

Primary references:

- Wang, Eldar, and Lu, *Subspace Estimation from Incomplete Observations*:
  https://arxiv.org/abs/1805.06834
- NIST, *CUSUM Control Charts*:
  https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm
- Vovk et al., *Retrain or not retrain: Conformal test martingales for
  change-point detection*:
  https://proceedings.mlr.press/v152/vovk21b.html
- PyTorch TorchRL GRU documentation, single-step and multi-step recurrent
  execution:
  https://docs.pytorch.org/rl/stable/reference/generated/torchrl.modules.GRUModule.html

Tessera does not claim a conformal false-alarm guarantee in EVO-040. The
reference chronology is not asserted to be exchangeable, and the implemented
sentinel is a bounded CUSUM-like engineering gate rather than a conformal
martingale.

## Problem

EVO-039 audits batches of completed sessions. Its static geometry is effective
for support changes, rotations, translations, and scale changes, but a
persistent weak departure can remain below each individual geometric limit.

The calibrated duration filament has unit principal direction `v`. In its
two-dimensional standardized support, the orthogonal direction is:

```text
n = (-v_2, v_1)
```

For each completed session `z_t`, the residual is:

```text
r_t = |z_t dot n|
```

Robust calibration supplies residual center `m` and scale `s`. Nonconformity
and bounded sequential evidence are:

```text
q_t = max(0, (r_t - m) / s)
b_t = min(3, q_t)
S_t = max(0, S_(t-1) + b_t - 0.75)
```

The sentinel latches when:

```text
S_t > 5
```

The evidence clip prevents one extreme observation from buying unlimited
authority. The reference allowance makes evidence decay when the stream
returns to the calibrated filament.

## Results

| Trial | Maximum evidence | Alarm |
|---|---:|---:|
| Untouched 60-session chronology | 2.25 | no |
| One extreme orthogonal impulse | 4.50 | no |
| Persistent 0.2-unit orthogonal shift | 5.389 | yes |

The persistent change began at monitoring index `20`; the alarm latched at
index `27`, a delay of seven completed sessions.

Once latched, the sentinel:

- emits `abstain`;
- suppresses memory candidacy;
- remains latched until an explicit validated reset.

## Emerging architecture

Tessera now has two complementary temporal surfaces:

```text
window geometry  -> large structural changes
sequential evidence -> weak persistent changes
```

This creates a deeper rule:

```text
Magnitude earns attention.
Persistence earns significance.
Neither earns host authority.
```

EVO-040 also introduces the first conservative state reuse: identical
admitted-checkpoint queries reuse an exact packet keyed by normalized matrix
shape and bytes. Any event change invalidates the key. Incremental recurrent
state across changed prefixes remains a future target and still requires
stepwise parity proof.

## Claim boundary

EVO-040 proves controlled separation of an impulse from one persistent
synthetic departure on the reference chronology. It does not establish
independent-host false-alarm rates, conformal validity, general concept-drift
detection, failure prediction, consciousness, or autonomous authority.
