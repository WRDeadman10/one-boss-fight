# E169 owner-scoped protocol: reactive dodge attempt budget

## Owner decision
Owner decides whether reactive dodge attempts need a per-encounter cap and the cap/reset semantics.

## Default and invariants
Keep the budget feature disabled by default. If enabled, cap only reactive dodge attempts; preserve the existing probability calculation, dodge invulnerability, attack eligibility, and safety rules. Refused attempts must not consume budget unless owner explicitly approves that policy.

## Paired evidence and rollback
Lead compares default-off control with enabled profiles against fixed attack sequences, proving cap boundary, no attempt consumption on refused calls, reset at generation change, and no effect on non-reactive dodges. Roll back by disabling the gate. Protocol only; no implementation authorized.
