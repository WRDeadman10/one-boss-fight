# E178 owner-scoped protocol: encounter restart diagnostics

## Owner decision
Owner decides whether restart reasons and reset summaries should be emitted, which fields may be logged, and retention/privacy expectations.

## Default and invariants
No diagnostic behavior is added. Any opt-in diagnostic must be observational and must not permit restart, alter generation IDs, clear/add state differently, or weaken terminal-state guards.

## Paired evidence and rollback
Lead compares diagnostics-off control with diagnostic-enabled repeated restart/failure cases, checking identical state transitions, generation increment, stale-event refusal, bounded output, and no sensitive data. Roll back by disabling the diagnostic gate. Protocol only; no implementation authorized.
