# Queue C five-task review receipt template (S191)

Use this format when submitting a five-task batch for Lead review. Under the active C-737 instruction, still post one X- receipt per completed task; this batch summary supplements those receipts and must not imply acceptance before Claude's verdict.

```text
QUEUE C REVIEW — S<first>–S<last> — submitted <date/time>

CLAUDE VERDICT: pending | ACCEPTED | HOTFIX | PARTIAL | REJECTED

| Task | Result | Changed artifacts | Acceptance evidence | Open limit |
|---|---|---|---|---|
| S<id> | complete / partial / blocked | <paths> | <commands/results or source citations> | <none or exact limit> |
| S<id> | ... | ... | ... | ... |
| S<id> | ... | ... | ... | ... |
| S<id> | ... | ... | ... | ... |
| S<id> | ... | ... | ... | ... |

BUILD / SUITE: <build id, count, exit status, evidence paths; or “not run and why”>
EDITOR / PIE / PACKAGE: <run id and evidence; or “not run and why”>
HOTFIXES: <rejected/partial task -> exact correction and re-review evidence, or “none”>
NEXT: <next task/batch; list any Lead-owned verification separately>
```

## Rules

- Keep each row bounded to what was changed and observed. Link raw logs, snapshots, and hash manifests; a source-only finding must say source-only.
- Record the Lead verdict per task. A posted X message, passing test, build, or complete batch table is not an acceptance receipt.
- If a row is rejected or partial, keep its follow-up scoped to that row, fix it before mixing in later work, and resubmit the correction evidence. Do not count the hotfix as accepted until reviewed.
- Distinguish `not run`, `blocked`, and `failed`; preserve the actual count and exit status. Never substitute a historical suite baseline for a run against changed source.
- End with the next bounded batch and any required Lead build/Editor work. Do not ask the owner to make a decision unless the batch reaches an actual owner-choice boundary.
