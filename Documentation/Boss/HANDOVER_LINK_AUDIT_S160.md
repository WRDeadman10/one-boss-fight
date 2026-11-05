# Handover link and command audit (S160)

Audited the active Queue B continuation handover, `Documentation/Boss/QUEUE_200_B_HANDOVER.md`, against the current repository paths and script interfaces. The older `Docs/BossCombatReview/Execution/CODEX_HANDOFF.md` and dated resume prompts are historical role-transfer records, not current instructions; their historical rules must not override `AGENTS.md`, the current Project State, or new mailbox orders.

## Path corrections

The handover named three witness companion files without their actual subdirectories and used two incomplete issue-document paths. Updated the handover to point to:

- `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json` and `.../Ledger/WITNESS_STATUS_F3_F11.md`.
- `Docs/BossCombatReview/Execution/Antigravity/Reviews/NOT_YET_CENSUS.md` and `.../Reviews/PARTIAL_UPGRADE_PLAN.md`.
- `Documentation/KNOWN_ISSUES.md` and `Documentation/Boss/OPEN_ISSUES_DIGEST.md`.
- `Documentation/TEST_PLAN.md` for the BUILD-174 reference.

Each target exists. Ledger v3.36 still reports 75 WITNESSED, 7 PARTIAL, and 0 NOT YET out of 82, matching the historical snapshot's census.

## Command interface check

The documented `Rebuild.ps1 -Tests` flag is declared in `Scripts/Rebuild.ps1:2-4`. `RunDrivers.ps1 -Only`, `-Full`, and `-SkipWarmup` are declared in `Scripts/RunDrivers.ps1:3-7`; `<driver_names>` is a placeholder for the script's comma-separated registered names, not a literal argument. The three offline tool invocations were checked using `--help`:

- `check_validator_tokens.py --root .` supports `--root`.
- `check_test_plan_ids.py --root .` supports `--root`.
- `check_doc_links.py .` accepts a positional root.

All three help commands exited successfully. No build, suite, editor, or PIE run was performed.
