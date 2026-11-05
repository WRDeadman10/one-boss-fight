# E193 owner-scoped protocol: bleed counter telemetry

## Owner decision
Owner decides whether bleed buildup/proc counts need observable telemetry and its audience, lifetime, and retention.

## Default and invariants
No telemetry API is added. If approved, telemetry is observational and must not change buildup, threshold escalation, once-per-frame proc, damage, or reset behavior.

## Paired evidence and rollback
Lead compares telemetry-off/on for below/equal/above thresholds, repeated same-frame hits, saturation, death/transition ignore paths, and generation reset. Verify identical state and damage; bound log/API volume. Roll back by disabling telemetry. Protocol only; no implementation authorized.
