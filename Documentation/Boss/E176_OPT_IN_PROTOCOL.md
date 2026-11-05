# E176 owner-scoped protocol: combo reachability visualization

## Owner decision
Owner decides whether to expose a graph reachability visualization to designers and where it appears (editor details, asset report, or offline tool).

## Default and invariants
No editor visualization is added by this protocol. Any approved view is read-only, derived from the current graph, and must not repair/reorder nodes or alter runtime validation or combo behavior.

## Paired evidence and rollback
Lead checks valid, unreachable-node, malformed-edge, cyclic, and over-depth fixtures; compare displayed reachability with runtime `LongestPath`/`Validate` results and verify opening/saving does not modify source assets. Roll back by disabling/removing the view. Protocol only; no implementation authorized.
