# E174 owner-scoped protocol: selector tie policy

## Owner decision
Owner decides whether nonzero tie-band selection is enabled in shipped profiles and whether reproducibility is required only within a build or across platforms/versions.

## Default and invariants
Keep tie band zero unless explicitly approved. If enabled, preserve eligibility and top-tier bounds, allow only eligible candidates, and do not claim cross-platform/version sequence stability without a separately approved PRNG contract.

## Paired evidence and rollback
Lead compares zero-band control and approved nonzero band with fixed candidate order, seeds, and start counts; verify membership, tie boundary, start-count reset, and determinism scope. Roll back to zero tie band and prior seed. Protocol only; no implementation authorized.
