# AY-C01–C05 native preflight

**Status:** preflight only; Batch 1 regression work is not complete. Claude accepted the scope in C-1163. No production source change is retained.

## Findings

| Task | Read-only finding | Result |
|---|---|---|
| AY-C01 / KI-175 | `URPGPlayerMovesSubsystem::AttachPlayerComponents` adds one `URPGPlayerParry` to each player pawn if absent (`RPGPlayerMovesSubsystem.cpp:887–911`). The component keeps `RPGParry::FState` and its `BeginPlay`/`EndPlay` do not reset that timing state (`RPGPlayerParry.h:83`, `RPGPlayerParry.cpp:30–34,236–241`). Project C++ contains no player respawn/repossess lifecycle that proves the same pawn/component is reused. | No lifecycle red or reset change. Needs a Lead/owner reproduction of same-pawn reuse.
| AY-C02 / KI-176 | If current stamina is readable and maximum stamina is not, `FinishStaminaCost` adds half the paid cost without a cap (`RPGPlayerParry.cpp:219–224`). Existing `ParryRefund` only covers a readable maximum (`RPGParryCostRules.h:23–27`). | Source risk confirmed, but the fallback has no injectable attribute fixture here; no production change without an actual-path red.
| AY-C03 / KI-177 | The pending recovery is applied after a move finishes (`RPGFrameworkBossCharacter.cpp:596–604`); a stance break aborts and rearms the current move while preserving the pending values (`:723–727`; existing lifecycle harness). C-707's next-card timing proof used a non-posture-breaking parry and did not define what an aborted, posture-breaking move should consume. | No expected result inferred; keep the candidate open pending an explicit recovery boundary.
| AY-C04 / KI-154 | Javelin ends as `Parried`; LowSweep increments its parry counter and marks the contact consumed; Shockwave increments its parry counter once. These routes use the shared resolver and its `NotifyParried` dedupe path. Existing adapter tests cover configuration, not live collision/outcome branches. | Static source shows no defect; runtime contact regression remains unproven. Keep C-1152 dedupe behavior in any later fixture.
| AY-C05 / KI-179 | Existing watchdog rule tests cover timeout arithmetic, while the transient lifecycle harness explicitly avoids ticking the watchdog. An experimental component test reached `Framework.Playback.NoSlotContribution` before the watchdog interval, so that failure is a fixture artifact. The experiment was reverted. | No runtime watchdog conclusion and no production change. A fixture with verified animation slot contribution/tick is still needed.

## Verification and limits

- With the temporary watchdog experiment, the editor build succeeded but the full suite was 492/494; one failure was the experimental watchdog fixture and one was the unrelated `OneBossFight.Binding.AuthoredDraft.SavedProductionPreflight` assertion at `RPGBossAuthoredDraftPreflightTests.cpp:111`.
- After restoring the original harness source, the editor build succeeded and the full suite was 493/494. The only failure remained `SavedProductionPreflight` at line 111: the test expected the explicit `DD27jManifestHash` to be 64 hexadecimal digits. The run is not a green suite and is not a Lead acceptance build.
- `Docs/BossCombatReview/Execution/Codex/C1165_AY_BATCH1/` retains the restored-source build/suite log, the suite with the failed experiment, the targeted fixture failure, and the exact temporary test snapshot. Engine usage followed C-1155: Codex-owned lock, no active UnrealEditor before launch, `-nosound`, and `-NoRelaunch`; the lock is released after recording this report.

## Next step

Keep Batch 1 open. Do not add guards from these findings. Continue only where a deterministic, production-relevant regression can be built; keep KI-175/177 bounded by the unresolved lifecycle/behavior contract and KI-179 by the missing slot-contribution fixture. The Mid01 range-band follow-up remains deferred until after AY Batch 1 per C-1164.
