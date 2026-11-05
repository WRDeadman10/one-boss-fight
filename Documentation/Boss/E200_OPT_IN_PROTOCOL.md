# E200 owner-scoped protocol: offline audit report index

## Owner decision
Owner decides whether to maintain a generated index of offline audit reports, its source of truth, update cadence, and stale-report policy.

## Default and invariants
No index is generated. If approved, it remains offline/read-only, links reports without implying acceptance, distinguishes static audit from runtime evidence, and does not edit or reclassify source reports automatically.

## Paired evidence and rollback
Lead compares generated entries against the report directory, Queue/task IDs, and disposition sources; verify missing/duplicate/stale detection and stable output. Roll back by removing the generated index/tool and restoring the prior manual index. Protocol only; no implementation authorized.
