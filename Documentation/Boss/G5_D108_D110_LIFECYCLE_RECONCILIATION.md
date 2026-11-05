# Queue G — D108 / D110 lifecycle evidence reconciliation

**Task:** G041. Static reconciliation of the existing D108 open-window cleanup and D110 completion/restart audits with current C++ automation and retained Lead evidence. No source/test edits or runs.

## D108: open-window cleanup

- `RPGBossMoveModelTests.cpp` now has direct `OpenWindowCount()==0` assertions for normal finish (`OpenWindowFinishCleanup`), abort (`OpenWindowAbortCleanup`), backward-clock refusal (`BackwardClockWindowCleanup`), and generation reset (`GenerationAndDoubleStart`). These directly close the model-level count gap called out in `EXECUTOR_OPEN_WINDOW_CLEANUP_AUDIT_D108.md`.
- `RPGBossExecutorHarnessTests.cpp` exercises executor abort/rearm/stale-token and repeated-abort cleanup, but its transient fixture documents that `TickComponent` watchdog observation was not reached. It does not prove montage-driven normal completion or actor-level window cleanup.
- `RPGBossFrameworkBossCharacter.cpp` routes `Die`, `Fail`, and `EndPlay` through `Executor->Abort`; that is current source behavior, not a new runtime claim.
- BUILD-65 and BUILD-66 in `Documentation/TEST_PLAN.md` record live BossDefeated and restart-to-generation-2 flows. BUILD-66 records the second encounter ending `CompletedWithDamage`. Those are retained Lead reports; no raw logs were independently re-opened in this reconciliation.

## D110: terminal outcomes and restart

- `RPGBossEncounterRestartMatrixTests.cpp` currently directly tests repeated failure idempotence and refusal to restart an uninitialized failed boss. It does not test successful completion/death restart on the actor.
- `RPGFrameworkBossCharacter::CanRestart` and `RestartEncounter` remain the source authority for initialized + not-failed + dead/succeeded + strictly newer generation; restart re-arms the executor before resetting generation and combat state.
- BUILD-66/67 supply retained PIE evidence for death, generation-2 restart and a second completion. BUILD-65 covers death terminal output. The records do not cover the failure terminal path in live PIE or establish player respawn behavior.

## Remaining precise gaps

1. The D108 pure model now asserts window-count cleanup across normal finish/abort/reset/refusal; there is still no observed real-montage executor completion assertion tying authored window closure to playback.
2. D110 actor automation still lacks a fully initialized success/death restart pair and the matching failure refusal on the same supported actor setup. The one current restart matrix test covers only uninitialized failure.
3. Runtime claims above are limited to the retained TEST_PLAN reports; this task did not reopen their raw bundles or rerun Editor/PIE.

**Disposition:** G041 complete; G042 can only add supported native actor setup without synthetic pack-health workarounds or production-only hooks. If that setup cannot initialize the boss through public production APIs, mark G042 blocked and continue to unblocked tasks as required by C-797.

## G043 cleanup assertions

Existing executing source assertions already cover reachable owned-window cleanup: `OpenWindowFinishCleanup` asserts active window then zero at normal model finish; `OpenWindowAbortCleanup` asserts active then zero on abort; `BackwardClockWindowCleanup` asserts active then zero on clock refusal; `GenerationAndDoubleStart` asserts zero after generation reset. These are stronger than a new idle-only assertion and meet G043 for model-owned windows. `RPGBossExecutorHarnessTests.cpp` covers abort/rearm/card identity/idempotence but has no real montage terminal tick; no assertion is added that would overstate that boundary. Components attached by `ActivateWorld` have separate preparation/registration cleanup coverage and are not part of D108/D110's executor lifecycle scope.
