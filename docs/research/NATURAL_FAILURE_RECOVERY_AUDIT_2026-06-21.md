# EVO-036 Natural Failure and Recovery Audit

## Preregistered question

Would the frozen EVO-032 latent-drift threshold abstain before an untouched
natural operator-loop failure and return to trust on the subsequent successful
recovery session?

The evaluation was frozen in
`EVO036_FAILURE_RECOVERY_PREREGISTRATION.json` before scoring. The failure
event itself was excluded from the 25-event precursor.

## Result

No.

| Observation | Latent drift | Threshold | Route |
|---|---:|---:|---|
| Failure precursor | 0.01241 | 0.03938 | trusted |
| Clean recovery prefix | 0.40924 | 0.03938 | abstain |

The neural route therefore achieved 0% failure abstention and 0% recovery
release on the single observed pair. Natural failure/recovery promotion is
rejected, both because behavior was inverted and because support is one
incident against the preregistered minimum of five.

## Architectural response

The neural threshold was not changed. EVO-036 added a deterministic,
host-owned incident governor:

```text
observed failure -> latch abstain -> suppress memory
clean terminal recovery -> release latch -> return to neural route
```

The latch passed failure containment, memory suppression, and clean recovery
release checks. It provides containment after an observed incident; it does
not predict incidents.

## Local security gate

The release-source scan covered 147 files and found:

- zero tracked secret patterns;
- zero builtin `eval`/`exec` or `shell=True` calls;
- zero plugin network imports;
- six denied mutation/authority permissions;
- checkpoint loading with `weights_only=True`;
- spawned subprocess isolation, hard timeout, and circuit breaker controls.

This remains a local static check, not an independent security review.

## Decision

Promote deterministic incident containment. Reject neural failure-prediction
and natural recovery claims. Collect four additional independent incidents
without relaxing the frozen gate.
