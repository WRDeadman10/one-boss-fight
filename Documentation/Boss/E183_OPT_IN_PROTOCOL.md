# E183 owner-scoped protocol: leash visualization

## Owner decision
Owner decides whether arena leash state should have a designer/debug visualization and whether it is development-only.

## Default and invariants
No visualization or actor behavior change is authorized. If approved, rendering is observational, disabled by default, and must not modify arena center/radius, target state, movement, or leash recovery.

## Paired evidence and rollback
Lead compares visualization-off and on in the proof arena at inside/equal/outside radii and recovery transitions; confirm no gameplay state changes and bounded rendering cost. Roll back by disabling the visualization. Protocol only; no implementation authorized.
