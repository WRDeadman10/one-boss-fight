# E197 owner-scoped protocol: window cleanup visualization

## Owner decision
Owner decides whether active hit-window lifetime/cleanup needs a developer visualization and what detail level is useful.

## Default and invariants
No visualization is added. Any approved display is observational, disabled by default, and cannot open/close windows, change contact resolution, or affect executor tick timing.

## Paired evidence and rollback
Lead compares visualization-off/on during normal completion, abort, watchdog, death, and restart; confirm exact same window/contact/cleanup outcomes and bounded render cost. Roll back by disabling the display. Protocol only; no implementation authorized.
