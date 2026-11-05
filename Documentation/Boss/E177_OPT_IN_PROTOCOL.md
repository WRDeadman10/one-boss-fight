# E177 owner-scoped protocol: executor window telemetry

## Owner decision
Owner decides which window lifecycle events and counters are useful, retention/log format, and whether telemetry is development-only or shipped.

## Default and invariants
No telemetry contract is added here. If approved, diagnostics remain observational, bounded, and must not change contact resolution, damage, hit counts, or executor timing. Do not promise current counters as stable public API without separate approval.

## Paired evidence and rollback
Lead compares telemetry-off and telemetry-on runs for identical authored contacts, accepted/refused windows, cleanup on completion/abort/death, and measured overhead/log volume. Roll back by disabling the telemetry gate. Protocol only; no implementation authorized.
