# E196 owner-scoped protocol: terminal transition trace

## Owner decision
Owner decides whether terminal Completed/Dead/Failed transitions need diagnostics, which fields and event names are exposed, and retention/scope.

## Default and invariants
No trace is added. Any approved trace is observational, bounded, and cannot set terminal state, alter generation eligibility, suppress failure, or change cleanup.

## Paired evidence and rollback
Lead compares trace-off/on for each reachable terminal path and explicit unreachable cases; verify identical state/generation/counters, no duplicate transition, and bounded output. Roll back by disabling diagnostics. Protocol only; no implementation authorized.
