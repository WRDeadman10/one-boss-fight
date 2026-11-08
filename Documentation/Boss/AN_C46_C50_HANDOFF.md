# Queue AN-C46–C50 — closeout and evidence index

**Date:** 2026-11-08. Offline queue work only; no commits, builds, Editor, PIE, package, media rerender, or owner decisions by Codex. Lead's C-1067 BUILD-263 run artifacts appeared after the offline handoff and are reflected below.

## Queue census

`QUEUE_AN.md` contains exactly 50 task rows, AN-C01 through AN-C50, with 50 unique IDs, ten consecutive groups of five, and nonempty file/acceptance fields. The table has no standalone `Owner` column. The top-level protocol and each acceptance specify the relevant Codex offline work versus Lead runtime/build or owner/Antigravity review gates; this is not a machine-verifiable owner-field audit.

## Changed artifacts by batch

- **C36–C40:** `AN_C36_C40_VIDEO_REVIEW_HANDOFF.md`; refreshed `FIGHT_VIDEO_REVIEW.md` and `OWNER_REVIEW_PACK.md`. No edits to the Antigravity visual verdict, owner review ticks, footage, or renderer.
- **C41–C45:** fixed `Scripts/Tools/check_ki_references.py` to return failure for missing references; added `Scripts/Tools/test_check_ki_references.py`. Added `AN_C41_C45_REGRESSION_AUDIT.md` and refreshed project/task/queue status. Global BUILD table checker still detects historical cross-section ID collisions; no historical IDs were renumbered.
- **First-dodge priority (C-1065/C-1066/C-1067):** source candidate, tests and KI-199 updates are recorded in `AN_C1065_FIRST_DODGE_RETRY_HOTFIX.md`, `RPGDodgeActivationRules.h`, `RPGDodgeTiming.cpp/.h`, `RPGAutomationTests.cpp`, `test_dodge_first_activation_retry_contract.py`, `KNOWN_ISSUES.md`, and `TEST_PLAN.md`. Lead BUILD-263 compiled and passed 486/486; retained first-standing showcase shows V2 root motion after `activated=1` and buffer consumption. This validates the recovery for that case, not the underlying root cause or both-route/moving acceptance.
- **Mailbox receipts:** X-1487 reports C-1065 candidate; X-1488 reports C36–C40; X-1489 reports C41–C45. Latest Claude feedback available at the end of this cycle remains C-1066; no BUILD-263 result or rejection is recorded.

## Offline checks

- Scoped unittest modules: `test_check_ki_references`, `test_first_dodge_after_draw_contract`, `test_dodge_first_activation_retry_contract`, `test_make_fight_video`: **15/15 passed**.
- `py_compile` for the changed/checker/render contract scripts: passed.
- `check_ki_references.py`: 33 Source references, 199 documented IDs, zero missing.
- `check_test_plan_ids.py`: reports BUILD-003–006 reused across historical sections and ordering drift (47 rows, 43 unique); Queue AN contributed no BUILD table rows.
- `check_doc_links.py`: zero broken links. `git diff --check`: only existing LF/CRLF conversion notices.

## Open gates for Lead / owner

| Gate | Current state | Required evidence/action |
|---|---|---|
| First post-draw dodge, KI-199 | BUILD-263 compiled; suite 486/486; retained one-route first-standing showcase passed via retry with V2 motion and buffer consumption. Cause not established. | Run fresh standing/moving first presses on both routes and repeat controls; verify montage, displacement, no duplicate; inspect fallback and buffer logs and isolate the InputBuffer/Enhanced Input/context cause. |
| Default-wired moving dodge, KI-196 | Runtime-assigned observations do not close no-assignment behavior. | Lead both-route no-assignment probe with real press-time input/speed and exact standing/moving montage. |
| Camera composition | A/B/C selection pending owner. | Owner choice; dynamic camera probe and wall/floor safety evidence before any camera Source change. |
| Tier 2 visibility/package, KI-191/KI-193 | Lifecycle and PIE signals are separate from full-fight aura visibility and packaged runtime. | Owner disposition of C-1062 proposal; Lead first-use and package evidence; keep Antigravity's not-visible finding distinct. |
| Full-fight visual review | BUILD-259 report exists; owner boxes remain unchecked. | Owner review of exact retained capture; future recapture should preserve source frames/log/ASS/concat/output together. |

No owner gate was marked complete by this offline handoff.
