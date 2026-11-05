# BossCombatReview evidence and work

This tree organizes boss architecture reviews, work orders, implementation batches, and their evidence. It is an evidence/work archive, not the active product task tracker. Current product state and status live in `Documentation/PROJECT_STATE.md`, `Documentation/TASKS.md`, `Documentation/TEST_PLAN.md`, and `Documentation/KNOWN_ISSUES.md`.

## Structure

- `ExistingBossAudit/` — source/reference audit of the existing boss, its behavior, critical gaps and prioritized recommendations. Start at `BOSS_AUDIT_SUMMARY.md`.
- `Reference/` — design and technical reference material used to compare expected versus current boss behavior.
- `Execution/Antigravity/` — art/content work orders, inspections and review artifacts.
- `Execution/Claude/` — lead-owned integration, build, test and PIE evidence, grouped by work/review ID.
- `Execution/Codex/` — Codex work queues, analyses, offline reports and handoffs.

## Evidence handling

Keep evidence with the corresponding work ID. Preserve raw logs and first-failure logs; do not rewrite evidence to make a report green. Hash files are relative to their manifest folder and can be checked with `Scripts/Tools/check_evidence_sha256.py`. A source or test change is not an engine result; state whether the evidence is static, built, automation-tested, or live PIE. The append-only team mailbox is `Documentation/TEAM_MAILBOX.md`, outside this archive.
