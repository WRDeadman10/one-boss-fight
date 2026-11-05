# E185 owner-scoped protocol: yaw probe tuning

## Owner decision
Owner decides whether the current development-only yaw probe needs configurable center/amplitude/period and whether it remains test-only.

## Default and invariants
Keep the hook off by default and absent from shipping builds. Any tuning stays a test instrument, is bounded to the documented signed-yaw domain unless a wrap test explicitly approves otherwise, and cannot affect normal actor yaw when disabled.

## Paired evidence and rollback
Lead compares hook-off control and fixed-seed hook samples over a complete period, including extrema and signed-angle edges; confirm disabled parity, deterministic sample sequence in the tested build, and no shipping exposure. Roll back by setting the probe to off/removing the opt-in config. Protocol only; no implementation authorized.
