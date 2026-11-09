# AX-C31–C35 — runtime coverage and stale-status reconciliation

Date: 2026-11-09. Read-only source/evidence reconciliation. No Unreal, build, PIE, or asset access in this batch.

| Task | Finding | Evidence / acceptance |
|---|---|---|
| AX-C31 / KI-179 | The registered `ExecutorWatchdogRule` test checks only the pure timeout formula and invalid-input behavior. It does not execute `URPGFrameworkMoveExecutor::TickComponent` or observe `WatchdogFired`; the harness comment explicitly says it has not advanced the watchdog tick. | `RPGFrameworkRuntimeTests.cpp:480-491`; `RPGBossExecutorHarnessTests.cpp:144-145`; `RPGFrameworkMoveExecutor.cpp:177-193`. Coverage matrix's `BOSS-EXE-007` “Covered” classification needs a narrow reading as the pure rule, not the runtime watchdog lifecycle. Design a fixture that visibly ticks world/component time before claiming integration coverage. |
| AX-C32 / KI-181 | Existing tests pin the sole eligible underflowed card and the mixed positive/zero score tie-band case, but not a multi-card case where all eligible products underflow to zero and seeded selection applies. | `RPGBossMoveSelectorTests.cpp:265-279,353-364`; `RPGBossMoveSelector.cpp:66-80`. Candidate regression: two eligible zero-score cards with TieBand enabled; assert documented seeded/deterministic selection and eligibility. Keep implementation unchanged until intended behavior is decided. |
| AX-C33 / KI-182 | The x3 death/reset pair is authored and locally validated, but the latest source trail still says Lead-run pending. | `Documentation/Boss/QUEUE_S.md` S27 and `S27_S29_RESPAWN_AND_TICK_ORDER_AUDIT.md` state four contexts × three cycles per route, 12 respawns/arm and 75 checks expected, with no runtime pass claimed. Keep the single-cycle C-868 result separate. |
| AX-C34 / KI-183 | Numerous native startup tests directly call the stored-definition setter and exercise transient selected-route compilation; this does not establish a Blueprint node caller or Shipping package invocation. | `RPGEncounterSelectionSubsystem.h:30`; `RPGBossStartupActivationTests.cpp:379,426,494,523,532,572,588,694,749,782,809,877,913,954,984,1032,1084,1116,1170,1196,1294,1323,1354,1389,1485`; C-876 H1 result is zero Content Blueprint callers. Existing source decision and release/package gate remain separate. |
| AX-C35 / KI-188 | The issue row still said OPEN although its recurrence cause and archive visibility were already fixed and accepted. | C-913 directed root anchoring; A-533 records accepted `.gitignore` `/Archive/` and commit `ea328b9`, 53 archived files tracked (54 changed including `.gitignore`), link check 0, line-count guards pass. The 40 unrecovered documents remain permanent historical loss; close only the active root-cause/process-control issue. |

## Validation and limits

Five scoped source/evidence checks were completed with cited test names, task counts, and receipt IDs. No runtime or package claim is added. KI-179 integration, KI-181 all-zero tie semantics, KI-182's Lead x3 run, and KI-183's real caller/package proof remain open. KI-188's active ignore/visibility cause is fixed; the lost-content impact remains recorded.

