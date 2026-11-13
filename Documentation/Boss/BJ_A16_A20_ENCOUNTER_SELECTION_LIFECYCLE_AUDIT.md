# BJ-A16..BJ-A20: Encounter Selection, Generations & Restart Lifecycle Audit

**Authority:** [`QUEUE_BJ_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BJ_AG.md) Batch 4 (`BJ-A16..BJ-A20`)  
**Scope:** Strictly read-only C++/test-source audit (`0` config/default/build/engine/commit operations).

---

## 1. `BJ-A16`: Selection Input & Fallback/Default Precedence (`RPGEncounterSelectionSubsystem.cpp`, `RPGPlayerMovesSubsystem.cpp`)

Exact precedence verified in [`RPGEncounterSelectionSubsystem.cpp:56-254`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.cpp#L56-L254) and [`RPGPlayerMovesSubsystem.cpp:120-165, 1152-1184`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L1152-L1184):

1. Explicit `SetSelectedDefinition(Definition)` (`RPGEncounterSelectionSubsystem.cpp:133`).
2. Benchmark CLI `-RPGBenchmark -H019EncounterDefinition=<path>` (non-Shipping only, `:67-76`).
3. Development CVar `rpg.EncounterDefinition` (`GEncounterDefinitionPath`, non-Shipping only, `:21-26, 135-137`).
4. Config default `ApplyDefaultDataSelection()` (`RPGPlayerMovesSubsystem.cpp:1152-1184`): runs only if `!Selection->HasSelectionRequest()`, `bDefaultToDataStartup == true`, `DefaultEncounterDefinition` non-empty, `RemovePIEPrefix(MapName) == DefaultEncounterMap`, and NOT overridden by `-RPGLegacyStartup` or `RPG_LEGACY_STARTUP=1` (`!UE_BUILD_SHIPPING`). Failed `TryLoad()` preserves legacy startup cleanly (`:1177-1181`).
5. Legacy route fallback (`LastEncounterRoute = bUseLegacyStartup ? "legacy" : "disabled"`, `:145`).

Framework boss definitions additionally require `rpg.FrameworkEncounterSelection != 0` via `RPGEncounterSelectionRules::AllowsFrameworkDefinition` (`RPGEncounterSelectionSubsystem.cpp:192`).

---

## 2. `BJ-A17..BJ-A18`: Generation Advancement, Stale Callbacks & Restart Cleanup

- **`RPGEncounterGenerationRules::CanAdvance` (`RPGEncounterGenerationRules.h:13-27`):** Rejects `0` and `MAX_uint64` (`GenerationExhausted`), requires `BroadcastGeneration > CurrentGeneration` (`GenerationNotIncreasing`).
- **`URPGBossEncounter::ResetEncounter` (`RPGBossEncounter.cpp:328-439`):** Refuses if `Death->IsDeathActive()` (`++DeathResetRefusals`), `ResetCount == MAX_int32`, or `!CanAdvance`; closes trace & remains first, increments counters, notifies `IFrames->OnEncounterReset()`, resets stagger/phases/AI/attributes/posture/bleed, and broadcasts `(ParticipantGeneration, ResetCount)` last (`:438`).
- **`OnEncounterResetBroadcast` & `FailSelectedRebind` (`RPGPlayerMovesSubsystem.cpp:481-669`):**
  - Same generation (`== LastAcceptedParticipantGeneration`) is a clean `DuplicateNoOp` (`:567-573`).
  - Unbinds `ResetBroadcastSource` at `:612` *before* validating replacement binding; arms `RebindTimeoutHandle` (`5.0s`) + `RebindPollHandle` (`0.05s`) when `AuthoritativePlayerCount == 0` (`:588-604`).
  - `FailSelectedRebind` clears both timers (`:523-524`), releases `ActiveDataActivation`, destroys `ActiveTransientBinding` only when `bReleaseClean` (`:540-544`), disables pack bosses, clears pending fields, and enters `HardError`.
- **Observations (`Low`):**
  1. `RPGPlayerMovesSubsystem.cpp:251, 665`: `BindResetBroadcast` skips `ARPGFrameworkBossCharacter` (`IsPackBoss(*It)` only), consistent with framework restart ownership (`InitializeSelectedEncounter` + framework lifecycle).
  2. `RPGPlayerMovesSubsystem.cpp:590-595`: A second reset `G+1` arriving while already `PendingPlayerPossession` updates `PendingRebindGeneration = G+1` without restarting the original `5.0s` timeout timer.

---

## 3. `BJ-A19..BJ-A20`: Activation & Restart Test Mapping (`0` Pure-Rule Defects)

- **Covered Thoroughly:** `RPGBossStartupActivationTests.cpp` (`30+` tests: manifest change, census fail, generation advance/duplicate/stale/overflow/exhaustion, polling, timeout, subsystem shutdown, default data startup, framework opt-in), `RPGEncounterGenerationRulesTests.cpp` (`256`-step property), `RPGBossEncounterLoopTests.cpp`, `RPGBossEncounterRestartMatrixTests.cpp`.
- **Minor Gap:** Nested `G -> G+1` generation bump arriving *inside* `PendingPlayerPossession` before timeout (`RPGPlayerMovesSubsystem.cpp:590`) is documented for Lead world-test coverage if ever encountered (`0` code/config edits).
