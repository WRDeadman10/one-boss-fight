# E181 owner-scoped protocol: aggro band profile

## Owner decision
Owner decides whether aggro bands ship, which profiles enable them, and approved close/far/dodge thresholds.

## Default and invariants
Keep aggro disabled by default. If approved, retain validated entry/exit hysteresis and reset to Balanced on new generation; aggro preferences may affect scoring only and must not bypass eligibility, cooldown, or authored combo rules.

## Paired evidence and rollback
Lead compares default-off control and enabled profiles across entry/exit equality, dodge-rate transitions, hugging/kiting overrides, and generation reset. Verify unchanged eligible set and no flap at thresholds. Roll back by disabling `bAggroEnabled` and restoring prior thresholds. Protocol only; no implementation authorized.
