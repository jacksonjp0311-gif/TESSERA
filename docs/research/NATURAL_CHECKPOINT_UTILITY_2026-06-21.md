# Natural Checkpoint Utility — EVO-030

## Question

Does the admitted checkpoint architecture improve prediction of real,
chronologically ordered Agent CLI validation sessions beyond simple memory
controls?

## Cohort

The immutable stream contains 120 clean natural sessions:

- 40 EVO-021 validation sessions
- 40 EVO-024 aggregate-context sessions
- 40 EVO-025 mechanism-context sessions

The first 100 sessions were available to checkpoint train, validation, and
replay. The final 20 remained untouched until the admission decision was
fixed.

Each session was represented by privacy-safe means, standard deviations, and
terminal values. Five session dimensions varied in the checkpoint period.

## Preregistered Gate

Promotion required:

- mean replay loss no worse than persistence by more than 2%
- at least 60% row-level replay wins
- replay admission before final-test inspection
- final-test loss no worse than every matched control

Controls were persistence, validation-selected EWMA, rolling mean, and nearest
transition retrieval.

## Result

The checkpoint improved mean replay loss but won only `52.63%` of replay rows,
below the `60%` consistency gate. Admission was rejected before final-test
inspection.

On the untouched final 20 sessions:

- checkpoint loss: `0.03189`
- persistence: `0.05102`
- rolling mean: `0.03058`
- validation-selected EWMA: `0.02569`
- nearest-transition retrieval: `1.81688`

The checkpoint was `24.15%` worse than the best control, EWMA with alpha
`0.05`.

## Decision

Reject natural checkpoint admission and preserve the validated fast path.

The important architectural result is that prediction ownership remains with
the stable expert. The neural field may continue to provide bounded awareness,
compression, and candidate residuals, but it has not earned natural prediction
authority.

## Next Gate

Test a bounded neural residual that can only adjust the validation-selected
stable expert within a preregistered influence budget. Promotion requires
replicated replay improvement without degrading final-test loss, warning
specificity, latency, or rollback.

## Claim Boundary

Clean-session prediction does not establish failure sensitivity, task success,
production readiness, consciousness, or autonomous authority.
