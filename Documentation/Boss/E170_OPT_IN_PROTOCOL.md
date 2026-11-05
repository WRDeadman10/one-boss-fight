# E170 owner-scoped protocol: retreat vertical gate

## Owner decision
Owner decides whether retreat eligibility should include vertical separation, the height threshold, and whether equality is accepted.

## Default and invariants
Keep the current retreat helper and behavior unchanged; vertical gating remains absent/off unless approved. If added, it may only narrow retreat eligibility and must not change the existing strict close-range or inclusive threat comparisons.

## Paired evidence and rollback
Lead compares default-off control and enabled threshold cases for same-floor, just-below, equality, and just-above height, alongside existing range/threat boundary controls. Verify no change when disabled and no unrelated move-selection changes. Roll back by disabling the vertical gate. Protocol only; no implementation authorized.
