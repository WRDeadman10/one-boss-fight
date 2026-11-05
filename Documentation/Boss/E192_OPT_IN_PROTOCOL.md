# E192 owner-scoped protocol: selector score saturation

## Owner decision
Owner decides whether explicit saturation is desired for scores near representational limits and whether it is diagnostic-only or part of scoring semantics.

## Default and invariants
Keep current scoring and input bounds unchanged. Any future saturation must be opt-in until approved, preserve candidate eligibility and tie-tier definitions, and specify how saturation affects ordering without silently changing selection.

## Paired evidence and rollback
Lead compares current finite-score behavior and proposed saturation at maximum legal multipliers, subnormal products, ties, and invalid inputs; record score/order changes and prove disabled parity. Roll back by disabling saturation and restoring original scorer. Protocol only; no implementation authorized.
