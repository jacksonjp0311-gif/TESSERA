# Tessera Nexus Registry

## Specification

Canonical machine-readable repository surface and mini-README profile registry.

## Hooks

- Inbound: RHP latest pointer and repository context
- Outbound: geometry graph, README obligations, validation gates

## Artifacts

- `surface_registry.json`
- `mini_readme_profiles.json`

## Invariants

- Every registered surface has a route, README, profile, validation, and claim boundary.
- The lightest sufficient README profile is used.
- Navigation remains distinct from validation.

## Claim Boundary

The Nexus improves orientation and change-impact analysis only.
