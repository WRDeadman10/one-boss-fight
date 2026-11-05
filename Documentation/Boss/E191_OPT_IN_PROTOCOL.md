# E191 owner-scoped protocol: cooldown clock diagnostic

## Owner decision
Owner decides whether selector cooldown timestamps and stale-clock refusals need diagnostics, and which timestamp/route fields may be logged.

## Default and invariants
No diagnostic is added. If approved, instrumentation is development-only by default and cannot change clock source, stale-decision refusal, cooldown equality, selection, or reset behavior.

## Paired evidence and rollback
Lead compares instrumented and control routes around below/equal/above cooldown, clock regression, and generation reset; confirm identical decisions/refusals and bounded output. Roll back by disabling/removing instrumentation. Protocol only; no implementation authorized.
