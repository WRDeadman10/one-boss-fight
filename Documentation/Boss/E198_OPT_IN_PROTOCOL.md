# E198 owner-scoped protocol: combo cycle policy

## Owner decision
Owner decides whether authored combo cycles should be rejected, truncated, or bounded at runtime, and whether unreachable nodes are an error or allowed content.

## Default and invariants
Preserve current DAG validation and depth limit. No cycle-enabled behavior is introduced. Any approved policy must remain bounded and must not change current valid graph execution or fallback behavior.

## Paired evidence and rollback
Lead compares current validator with the approved policy on valid DAG, self-loop, multi-node cycle, unreachable acyclic node, over-depth path, and malformed edge fixtures. Roll back by restoring current validation policy. Protocol only; no implementation authorized.
