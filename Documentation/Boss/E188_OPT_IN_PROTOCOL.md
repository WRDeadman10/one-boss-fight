# E188 owner-scoped protocol: grounded-height tolerance

## Owner decision
Owner decides whether grab release/grounding needs a tolerance or fallback beyond the current supplied floor-Z calculation, including acceptable skin and missing-floor behavior.

## Default and invariants
Keep `GroundedZ` unchanged. Any optional tolerance remains disabled by default; valid floor placement must not put the capsule below the floor, and invalid input handling must remain explicit.

## Paired evidence and rollback
Lead compares current floor placement against approved tolerance on flat, sloped, missing/invalid floor, capsule-size, and near-overflow cases. Verify no penetration and no displacement when disabled. Roll back by disabling tolerance and restoring previous parameters. Protocol only; no implementation authorized.
