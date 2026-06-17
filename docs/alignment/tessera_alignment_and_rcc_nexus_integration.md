# Tessera Alignment and RCC Nexus Integration

## Core extraction

Tessera becomes repository-ready only when the runtime, theory, evidence, navigation, validation, and claim ceilings are all visible to both humans and agents.

```text
runtime -> evidence -> certificate -> RCC route -> validation -> claim ceiling
```

## Alignment law

```text
No origin alignment, no durable mutation.
No certificate, no memory promotion.
No manifest, no transfer claim.
No validation, no push.
```

## RCC-N role

RCC-N does not validate the model. RCC-N orients humans and agents so validation can be executed correctly.

```text
RCC tells the agent what the repository means.
RCC-N tells the agent where it is.
Validation tells the agent whether reality agreed.
```

## Tessera-specific route

```text
README -> AGENTS -> docs/context -> rcc/nexus -> docs/theory -> docs/alignment -> src/tessera -> tests -> outputs/evidence
```

## Pre-push gate

Before GitHub push:

```bash
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python -m unittest discover -s tests
python -m tessera run --out outputs
```

Push remains blocked until James explicitly says to push.
