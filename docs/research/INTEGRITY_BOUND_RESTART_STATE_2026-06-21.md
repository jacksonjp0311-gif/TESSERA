# EVO-042 Integrity-Bound Restart State

EVO-041 proved that an unchanged recurrent prefix can be extended exactly.
EVO-042 carries that witness across a worker restart.

The portable capsule binds under one canonical SHA-256 envelope:

- checkpoint payload hash;
- feature contract;
- uncertainty router;
- normalized historical prefix;
- recurrent field, level, previous code, and last observation;
- historical metric rows;
- last inference packet;
- normalized-prefix cache key.

A new worker verifies the envelope and every semantic binding before loading
state. Tampering, checkpoint mismatch, contract mismatch, router mismatch, or
prefix mismatch prevents continuation.

## Result

| Metric | Result |
|---|---:|
| Restored prefix rows | 110 |
| Packet parity | 100% |
| Metric-row parity | 100% |
| Restored continuation | 1.13 ms |
| Full replay | 56.12 ms |
| Restart speedup | 49.47x |
| Tampered capsule | rejected |
| Wrong checkpoint | rejected |
| Changed historical prefix | full replay |

## Emerging rule

```text
State without lineage is a hint.
State with verified lineage is a witness.
Neither state grants authority.
```

The capsule provides integrity, not secrecy or privileged-attacker
authenticity. A future deployment may add host-keyed authentication and
atomic durable storage, but those are not claimed here.

## Claim boundary

Local SHA-256 integrity and restart parity do not establish confidentiality,
authenticity against a privileged attacker, cross-platform floating-point
identity, independent production safety, consciousness, or autonomous
authority.
