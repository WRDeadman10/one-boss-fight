# QUEUE_BJ_AG Batch 9 Audit (`BJ-A41..BJ-A45`): UI/HUD Idempotence, Parity Guards, Shipping Headers & Test Assertion Quality

**Scope:** Read-only offline C++/Python/test-source audit (`QUEUE_BJ_AG` Batch 9, `0` Unreal Editor / build / runtime / asset / commit operations). Conditional code notes follow Lead review guidance (`[X-1917]`) and are not claimed as confirmed runtime defects.

---

## Summary Table

| Task | Audited Files | Verdict |
|---|---|---|
| `BJ-A41` | [`RPGBossHud.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBossHud.cpp#L101-L545), [`RPGFlaskHud.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGFlaskHud.cpp#L58-L208), [`RPGBossDeath.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.cpp#L31-L160) | Verified with 1 Low conditional note |
| `BJ-A42` | [`RPGBossSelectorStartParityTests.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossSelectorStartParityTests.cpp#L32-L114) | Verified exact parity coverage |
| `BJ-A43` | [`check_shipping_guards.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/check_shipping_guards.py#L1-L165), [`RPGBossDeath.h`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.h#L139-L153), [`RPGCombatDebug.h`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatDebug.h#L80-L100), `Source/OneBossFight/**/*.h` preprocessor scan | `declarations=42 shipping_uses=0`; UHT-safe header pattern verified |
| `BJ-A44` | All `Source/OneBossFight/Tests/*.cpp` scanned for tautologies (`TestTrue(..., true)` / `TestFalse(..., false)`) and zero-`Test*()` files | 1 Low tautology note; 1 Info alternate-macro note |
| `BJ-A45` | `QUEUE_BJ_AG` Batch 9 synthesis & zero-edit disposition | 0 runtime defects; test/UI notes recorded |

---

## `BJ-A41` — UI, HUD & Terminal Idempotence

### Verified Behavior
- **`URPGBossHud` Generation & Terminal Fence (`RPGBossHud.cpp:356-545`)**:
  - `HandleNativeTerminal` (`:394-405`) validates `IsValid(Boss) && Boss == GetOwner()` and delegates to `RPGBossTerminalRules::ShouldAccept(NativeHealth->NativeEncounterGeneration(), Generation, Completed, bHaveHealth, Health)` before latching `NativeTerminalGeneration`.
  - Generation change (`Generation != LastGeneration`, `:428-451`) clears the banner, disables retry, re-enables pawn input if `bPlayerLocked` was set (`:441-449`), and resets `bSeenAlive` cleanly while preserving `NativeTerminalGeneration` only if it already matches the new `Generation` (`:431-433`).
  - Victory admission (`:466-496`) guards `State != EState::Victory` and `VictoryFiredGeneration != Generation` so `VictoryCount`, `DisableInput` (`bPlayerLocked`), `EnableRetry`, and `OnVictory.Broadcast(Generation)` fire at most once per encounter generation.
  - `EndPlay` (`:356-380`) removes `NativeTerminalHandle` and calls `Widget->Detach()` when `State == EState::Victory && EndPlayReason == EEndPlayReason::Destroyed` (`:369-372`), allowing the victory banner fade to finish in `URPGBossHudWidget::NativeTick` (`:193-197`) before self-removing (`RemoveFromParent()`).
- **`URPGFlaskHud` (`RPGFlaskHud.cpp:58-208`)**:
  - Creates viewport widget only on local player controllers (`:147`), collapses widget cleanly if art assets fail (`:89-93`), removes widget in `EndPlay` (`:115-119`), and reads pack `BP_EquipmentComponent_C` slots via prefix-safe reflection (`:178-208`).
- **`URPGBossDeath::EndPlay` (`RPGBossDeath.cpp:117-130`)**:
  - Spawns remains only once when `!bEnding && State == EState::Dead && EndPlayReason == EEndPlayReason::Destroyed` and `!World->bIsTearingDown && bRemainsTransformKnown`, then sets `bEnding = true`.

### Conditional Edge Case / Follow-Up Risk
1. **Low — Detached victory widget persistence while `bRetryEnabled == true` (`RPGBossHud.cpp:158-214, 369-372`)**:
   `NativeTick` removes a detached widget when `bDetached && Alpha <= 0.f && !bRetryEnabled` (`:193`). When victory enables retry, `!bRetryEnabled` intentionally stays `false` until the player presses retry (which calls `OpenLevel` at `:210` and resets `bRetryEnabled = false`). Conditional on any non-level-reload flow where a boss is destroyed after victory while the same world stays loaded: the detached retry widget remains in the viewport until a level transition.

---

## `BJ-A42` — Selector/Start Parity & Legacy/Framework Guards

- **`RPGBossSelectorStartParityTests.cpp:32-114`**:
  - Exercises `FRPGBossMoveSelector::Select` vs `FRPGBossMoveModel::IsEligible` / `Model.Start` on the exact same `FRPGBossDecisionSnapshot`:
    - Exact cone boundary (`60.` deg on `FrontConeDegrees = 120.f`, `:50-63`) accepted by both.
    - Just-outside cone (`60.0001` deg, `:65-79`) refused by both with identical refusal token (`Decision.Traces[0].Refusal == Error`).
    - Empty candidate initialization (`Selector.NoCandidates`, `:87-88`) and seeded `TieBand` repeatability (`:97-113`).

---

## `BJ-A43` — Shipping Guards & Header Macro Scan

- **Observed Command Result (`check_shipping_guards.py --source C:\UnrealProject\OneBossFight\Source`)**:
  - Reported `[SHIPPING_GUARDS] declarations=42 shipping_uses=0` across all `42` non-Shipping `CVar*` declarations (`Arena/RPGPerfSwitches.cpp`, `Boss/RPGFrameworkBossCharacter.cpp`, `Boss/RPGFrameworkBossController.cpp`, `Boss/RPGFrameworkMoveExecutor.cpp`, `Player/RPGBossDormantWake.cpp`, `Player/RPGBossRemains.cpp`, `Player/RPGCameraProbe.cpp`, `Player/RPGCameraRig.cpp`, `Player/RPGCombatCatalog.cpp`, `Player/RPGCombatDebug.cpp`, `Player/RPGEncounterSelectionSubsystem.cpp`, `Player/RPGPlayerMovesSubsystem.cpp`, `Player/RPGPlayerParry.cpp`).
- **Header UHT Safety Scan (`Source/OneBossFight/**/*.h`)**:
  - `RPGBossDeath.h:139-153`, `RPGCombatDebug.h:87-100`, `RPGBossHealPunish.h:86`, `RPGCombatCatalog.h:130`, `RPGHitIntake.h:135`, and `RPGSwingTracker.h:123` keep `UFUNCTION()` declarations unguarded so Unreal Header Tool generates identical Shipping/Development reflection signatures, placing `#if !UE_BUILD_SHIPPING` inside inline/definition bodies (`RPGCombatDebug.h:87` documents this invariant explicitly).
  - Editor-only metadata/debug properties (`RPGFrameworkBossCharacter.h`, `RPGFrameworkProofFixture.h`, `RPGDamageResolver.h`, `RPGDodgeTiming.h`, `RPGIFrameMonitor.h`) use `#if WITH_EDITORONLY_DATA`.
  - **Audit Limit:** `check_shipping_guards.py` validates `CVar*` identifiers only; compiled Shipping UHT reflection and `CheckShippingBinary` checks remain Lead-owned.

---

## `BJ-A44` & `BJ-A45` — Test-Quality & Assertion-Strength Scan

- Scanned all `Source/OneBossFight/Tests/*.cpp` files:
  1. **Low — Literal `true` smoke assertions (`Tests/RPGSourceTestGapTests.cpp:143-156`)**:
     `FRPGBossInterruptNoComponentsTest` calls `RPGBossInterrupt::CancelOffence` on an empty `AActor` and `nullptr`, then asserts `TestTrue(..., true)` at `:152` and `:154`. This verifies non-crash execution only rather than asserting zero added components/tags or state invariants.
  2. **Informational — Custom error-accumulator macro pattern (`Tests/RPGPlayerMovesAttachWitnessTests.cpp:400-456`)**:
     Regexes looking strictly for `TestTrue`/`TestEqual` match `0` lines because the file records failures via `Test.AddError(...)` and returns `!Test.HasAnyErrors()` (`:439`), and intentionally logs rather than asserts `HasBegunPlay` in a bare test world (`:10-13`).

- **Batch 9 Disposition:** `0` runtime/compiler defects; `1` Low UI lifecycle note (`bRetryEnabled` after detached boss destruction without reload), `1` Low test-quality note (`RPGSourceTestGapTests.cpp:152,154`), plus explicit scope limit of `check_shipping_guards.py` vs Lead Shipping UHT proof.
