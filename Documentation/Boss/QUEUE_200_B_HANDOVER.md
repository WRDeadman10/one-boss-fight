# QUEUE_200_B handover

Snapshot: 2026-11-03, after X-537. QUEUE_200_B R1–R195 is recorded; R196–R200 is this closing block. QUEUE_200 (A) is complete at BUILD-164. Claude owns builds, suite execution, Unreal and live PIE; the owner commits.

## Fresh-session read order

1. `AGENTS.md` and `Documentation/PROJECT_STATE.md` (current state, commands, team protocol).
2. `Documentation/TASKS.md`, then the last ~100 lines of `Documentation/TEAM_MAILBOX.md` and the newest mailsocket messages. Claim only the current Lead order; use one X- receipt per five tasks.
3. `Docs/BossCombatReview/Execution/Codex/QUEUE_200_B.md`, `Documentation/TEST_PLAN.md`, and relevant `Documentation/Boss/` audit/how-to pages.
4. For framework proof status, use `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json` as the count authority (v3.36: 75 WITNESSED, 7 PARTIAL, 0 NOT YET of 82); read `Docs/BossCombatReview/Execution/Antigravity/Ledger/WITNESS_STATUS_F3_F11.md`, `Docs/BossCombatReview/Execution/Antigravity/Reviews/NOT_YET_CENSUS.md`, and `Docs/BossCombatReview/Execution/Antigravity/Reviews/PARTIAL_UPGRADE_PLAN.md` for row detail. Do not infer live proof from code or a passing suite.

## Current implementation and proof state

The whole suite last passed 327/327 at BUILD-174 (`Documentation/TEST_PLAN.md`; evidence `Docs/BossCombatReview/Execution/Claude/B_CODEX_R141_180`). Later Codex work has not been built or run. The profile gate inventory is `Documentation/Boss/PROFILE_OPT_IN_AUDIT_R156_160.md`; it covers each positive gate and paired setting, validation, reset, telemetry, and docs. Row-level unit/live status belongs to the witness ledger.

Recent opt-in proof lane:

| Feature | State at handover |
|---|---|
| WarpEaseInOut | Coded and built; live-proven (BUILD-165). |
| GuardChipFraction | Coded and built; live-proven (BUILD-166). |
| ParryRecoveryScale | Coded and built; grade scaling and next-card gate live-proven (BUILD-167/173). |
| Telegraph fair scale | Coded and built; live scaling and restore live-proven (BUILD-172). |
| Cone hysteresis / selector-start slack | Coded and built; eight-attack live run passes (BUILD-173); Codex regression source was included in BUILD-174. |
| NeutralStrafeSeconds | Coded and built; normal neutral strafe is live-proven (BUILD-149). Stuck detection/recovery is unit proven but live not proven: C-712's R3c run emitted no `strafe_stuck`. |
| Aggro switch, fatigue, yaw probe, and remaining profile opt-ins | Authored/offline proof preparation and source/test coverage are indexed in the audit, profile how-to, and expected sheets. No live proof is claimed here; check the exact requirement row before making a status claim. Fatigue's current shift schedule only establishes a candidate first whiff. |

Accepted caveats: non-shipping `ProofGStart`/`ProofIF*` timers may survive an interrupted restart (KI-157); executor hit/damage counters are lifetime totals across `Rearm`; result graders do not validate per-generation counter scope. The test-hook limit and W3 live-proof limit are in `Documentation/KNOWN_ISSUES.md` and `Documentation/Boss/OPEN_ISSUES_DIGEST.md`.

## Commands and evidence

- Build and suite (Lead/editor owner): `powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1 -Tests`.
- PIE regression drivers (Lead, editor open): `powershell -ExecutionPolicy Bypass -File Scripts\RunDrivers.ps1 -Only <driver_names>`. Use `-Full` only for the long drivers; restart the editor after a timed-out driver.
- Token/document tools: `py Scripts/Tools/check_validator_tokens.py --root .`, `py Scripts/Tools/check_test_plan_ids.py --root .`, and `py Scripts/Tools/check_doc_links.py .` (check each script's `--help`/usage before relying on a command).
- Keep raw logs and result metadata with evidence; distinguish a build, unit suite, validator pass, and live PIE witness. Do not delete existing proof assets or commit/push.

## Queue status

Historical snapshot after X-537: R199 generated the ranked Queue C proposal (`Documentation/Boss/QUEUE_200_C_PROPOSAL.md`). The prior R200 broad final pass is superseded by the single current Queue C S200 final consistency pass after the additional Queue C work; do not run two separate final passes. Lead review may add hotfixes; address them before closing.

## Queue C updates after the historical snapshot

- **C-715 live proof review (2026-11-03):** parry stamina and overlay passed with evidence in `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA`; the opening cost remains spent on a whiff, and a Perfect parry refunds half the cost. Insufficient-stamina refusal was not exercised. Fatigue passed to three consecutive whiffs, then reset on contact; the 0.5 floor remains unit-tested only, and later target shifts caused `NoCandidate`. Exact observed results and the six-card target-shift schedule are in `Docs/BossCombatReview/Execution/Codex/Proofs/FATIGUE_EXPECTED.md`. The stuck-recovery branch remains unit-proven but not live-proven (W3/KI-149). `rpg.ParryStaminaCost` is already listed in `Documentation/Boss/TEST_HOOKS.md`.
- The current open-issue digest records these proof limits. C-715's aggregate statement that all ten opt-in feature checks are live-proven except W3 is retained as Claude's report; consult each feature's named evidence before treating it as a witness.
- **C-716 validator follow-up (X-557):** coverage includes missing-required-field mutation across the current 133 retained valid token samples, six hand-authored source-format samples for the schemas identified as sample-less in C-716, and validation of all 161 literal `UE_LOG` format variants against the updated schemas (zero mismatches). The validator module passed 33/33; no Unreal or full project suite was run. No new build result is implied.

## Queue C continuation (2026-11-03 addendum)

The snapshot above is historical. C-713 accepted R181–R198 and directed Codex to post Queue C and start immediately. X-539 delivered the 200-task proposal. Later Queue C receipts supersede the old S1–S15 position. Claude owns review/build/test/live proof; BUILD-182 is the latest recorded full suite at 332/332, but it predates S189 and later uncommitted Source edits, so it does not verify the current checkout.
