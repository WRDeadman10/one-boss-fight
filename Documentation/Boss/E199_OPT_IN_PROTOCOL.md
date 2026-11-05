# E199 owner-scoped protocol: boundary table fixture generator

## Owner decision
Owner decides whether maintainers need a generator for adjacent/equality boundary fixtures, supported rule families, output format, and whether generated files are checked in.

## Default and invariants
No generator is added. If approved, generated fixtures are deterministic from explicit inputs, clearly identify source rule and expected side, and never overwrite hand-maintained tests without review.

## Paired evidence and rollback
Lead compares generator output to manually authored range, angle, time, threshold, and nonfinite cases; verify reproducibility, reviewable diffs, and unchanged runtime code. Roll back by deleting only generator-owned outputs/tool and restoring prior fixtures. Protocol only; no implementation authorized.
