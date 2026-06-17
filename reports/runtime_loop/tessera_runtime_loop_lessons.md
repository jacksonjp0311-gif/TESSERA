# Tessera v0.2.0 Runtime Loop Lessons

- Hermes pattern extracted: actor/runtime is separate from governance geometry.
- Tessera pattern added: compile the loop before every run so the operator can see the runtime contract.
- Latest-run bug lesson: publish latest after artifacts exist, not before.
- Push lesson: validation can pass while push remains blocked if commit/push flags are absent.
- Interlock rule: borrow geometry, not authority.
- Disconnect rule: preserve lessons locally, do not create dependency on Hermes runtime folders.

## Disconnect Boundary

Hermes-Agent-Evo informs the governance geometry. Tessera does not import Hermes runtime authority, CMS write authority, API authority, or self-authorization.
