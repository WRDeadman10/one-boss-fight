# E189 owner-scoped protocol: combo fallback telemetry

## Owner decision
Owner decides whether combo continuation refusal and ordinary fallback need diagnostics, including event names, fields, retention, and development/shipping scope.

## Default and invariants
No telemetry contract is added. Any approved logging remains observational and must not change the combo refusal token, consume gates differently, alter selector memory, or change the fresh snapshot used for ordinary fallback.

## Paired evidence and rollback
Lead compares telemetry-off and on for each refusal class with valid ordinary fallback and no-eligible-card controls; verify identical choice, start snapshot, gate consumption, bounded output, and no sensitive data. Roll back by disabling the diagnostic gate. Protocol only; no implementation authorized.
