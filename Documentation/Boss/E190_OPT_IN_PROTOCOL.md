# E190 owner-scoped protocol: snapshot freshness trace

## Owner decision
Owner decides whether route snapshot identity/age should be logged or exposed for diagnostics and which fields are acceptable.

## Default and invariants
No trace/API is added. Any approved trace is observational, development-only by default, and must not retain actor pointers or alter stale-decision refusal, generation checks, or the fresh snapshot contract.

## Paired evidence and rollback
Lead compares trace-off and on across normal, immediate combo, delayed wake, generation reset, and regressed-clock cases; verify identical choices/refusals, bounded logs, and no sensitive identifiers. Roll back by disabling/removing the trace. Protocol only; no implementation authorized.
