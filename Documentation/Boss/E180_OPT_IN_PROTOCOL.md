# E180 owner-scoped protocol: stagger resistance profile

## Owner decision
Owner decides whether stagger resistance is shipped, which incoming events it affects, and approved values/stacking/reset rules.

## Default and invariants
Keep existing stagger behavior unchanged and resistance disabled by default. If approved, apply only to the specified stagger input; do not change health damage, parry/dodge precedence, attack windows, or terminal-state behavior.

## Paired evidence and rollback
Lead compares default-off and enabled profiles at below/equal/above resistance boundaries, including parry, dodge, repeated hits, recovery, and encounter reset. Verify unchanged damage and no resistance carryover unless explicitly specified. Roll back by disabling the profile gate. Protocol only; no implementation authorized.
