# E175 owner-scoped protocol: combo graph editor validation

## Owner decision
Owner decides whether graph validation should run in the editor, when it runs (edit/save/cook), and how warnings/errors are surfaced to content authors.

## Default and invariants
Keep runtime behavior and current graph validity rules unchanged. Any editor validation is advisory or blocking only as explicitly approved; it must not silently rewrite assets, nodes, or edges and must preserve runtime validation as the safety boundary.

## Paired evidence and rollback
Lead compares validation-disabled baseline and opt-in editor validation on valid, malformed, cyclic, over-depth, and unreachable-node fixtures; verify diagnostics identify asset/node/edge and no asset mutation occurs. Roll back by disabling the editor validation hook. Protocol only; no implementation authorized.
