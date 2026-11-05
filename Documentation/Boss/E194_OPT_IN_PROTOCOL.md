# E194 owner-scoped protocol: damage-scaler diagnostics

## Owner decision
Owner decides whether reciprocal damage-scaler matching/refusal needs diagnostics, which fields are exposed, and whether reporting is development-only.

## Default and invariants
No diagnostic output is added. Approved instrumentation must not change reciprocal matching, stale loss retention, finite-input refusal, or one-time consumption of a matched loss.

## Paired evidence and rollback
Lead compares diagnostic-off/on with matched, unmatched, nonfinite, stale, and repeated samples; verify same damage and pending-loss state plus bounded output. Roll back by disabling/removing diagnostics. Protocol only; no implementation authorized.
