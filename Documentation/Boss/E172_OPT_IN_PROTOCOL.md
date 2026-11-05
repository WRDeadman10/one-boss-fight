# E172 owner-scoped protocol: cue jitter profile

## Owner decision
Owner decides whether cue timing jitter is a shipped feature, its per-move/profile authoring surface, distribution expectation, and acceptable bounds.

## Default and invariants
Keep existing cue behavior unchanged and jitter disabled unless explicitly approved. If enabled, preserve authored minimum/maximum, commit/active-window validity, deterministic seed/index inputs, and avoid changing damage or hit-window timing.

## Paired evidence and rollback
Lead compares default-off control and enabled fixed-seed runs for bounds, repeatability, monotonic valid timing, and player reaction window. If a distribution guarantee is wanted, define and test it separately; bounded deterministic offsets alone do not prove uniformity. Roll back by disabling the profile and restoring prior values. Protocol only; no implementation authorized.
