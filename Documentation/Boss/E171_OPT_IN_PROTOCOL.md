# E171 owner-scoped protocol: gap-closer persistence tuning

## Owner decision
Owner decides whether gap-closer eligibility/persistence should be profile-tunable, which observed state can extend eligibility, and the maximum duration/range.

## Default and invariants
Keep current behavior and defaults. Any added tuning remains disabled by default, bounded, and must not bypass target validity, move-model eligibility, cooldown, attack windows, or arena leash limits.

## Paired evidence and rollback
Lead compares default behavior with each approved opt-in profile at below/equal/above persistence boundaries, including target loss, generation reset, and refusal controls. Roll back by disabling the profile option and restoring prior settings. Protocol only; no implementation authorized.
