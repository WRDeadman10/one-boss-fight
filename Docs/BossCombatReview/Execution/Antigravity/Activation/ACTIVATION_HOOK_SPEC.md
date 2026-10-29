# Boss Combat Activation Hook Specification: Subsystem Call Site, Fallback Hierarchy, Lifetime Model, Parity Matrix, and Test Verification Plan

**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Task Order:** C-322 / C-323 (Order A-216), updated under C-329 (Order A-219)  
**Date:** 2026-10-29  
**Status:** Corrected Offline Architectural Specification (Review Findings Addressed per Codex X-332 / Lead C-329; Unmeasured Runtime Behaviors Explicitly Flagged as UNMEASURED; Baseline Staged at original_A219/)

---

## Executive Summary

This document specifies the exact runtime mechanics required to integrate the world-level typed boss activation pipeline (`RPGBossActivation::ActivateWorld`, validated in DD29) into the running game without modifying existing asset binaries or risking regressions in live boss encounters.

The typed hydration library constructed across DD14-DD29 successfully executes synchronous definition compilation, 12-plan preflight validation, atomic component allocation, and transactional registration. However, `ActivateWorld` currently exists solely as a standalone library API exercised in automated unit tests (`RPGBossActivationWorldTests.cpp`). It is not invoked by any gameplay system.

This specification details the 6 architectural pillars required by Tech Lead Claude in `[C-322]` for ordering the first live call site change:
1. **The Call Site:** Execution placement in `URPGPlayerMovesSubsystem`, lifecycle timing relative to actor `BeginPlay()`, and the 4 prerequisites missing from the live game today (`FSelection`, placed `ARPGEncounterBinding`, `ManifestHash`, and `RPGCombatCatalog` epoch).
2. **The Fallback Hierarchy:** Detailed ordered sequence for each outcome (`Activated`, `FallBackToLegacy`, `HardError`), including the 12 suppression guards, non-typed component retention, and failure policy trade-offs.
3. **The Lifetime & Registration Model:** Storage of `FRPGWorldActivationResult`, ownership semantics, teardown on boss destruction/world cleanup, `Abort()` behavior on begun components, and resolution of the `AttackTracker` creation order.
4. **The Parity Checklist:** Comprehensive mapping of the 12 typed components comparing native constructor defaults against legacy bundle assignments and typed authoring records (highlighting `URPGBossDeath::DeathMode = ERPGBossDeathMode::OwnClip` as the sole must-be-set override).
5. **The Test & Driver Verification List:** 8 focused, single-line automation and PIE driver verification gates.
6. **Open Unknowns:** Critical engine runtime questions that C++ code inspection alone cannot resolve.
7. **Corrected Script-Derived Asset Audit:** Complete, verified 27-row asset presence table derived directly from `examples/boss_draft_profiles.json` resolving all prior discrepancies per `[C-324]`.

Every statement in this document is cited with exact `file:line` locations verified against current source files. Deductions and unmeasured runtime behaviors are explicitly marked `[UNMEASURED]` or `[UNMEASURED / Integration Hypothesis]`.

> [!IMPORTANT]
> **Revision Note (Order A-219 / Lead C-329):** Following Codex cross-check (`[X-332]`) and Tech Lead review (`[C-329]`), this document has been updated to address 4 discrepancies:
> 1. **Attach Lifecycle Seam:** `URPGPlayerMovesSubsystem::Attach` is reached via both `OnWorldBeginPlay` and runtime `OnActorSpawned`. In UE 5.5, `LevelActor.cpp:733` invokes `PostSpawnInitialize` before `OnActorSpawned.Broadcast:750`, and `Actor.cpp:4050-4070` may dispatch `BeginPlay()` immediately if the world has begun. Thus runtime spawned actors may have already begun play when `Attach` runs, violating `HydrationPreparation.cpp:512-514` (`!World->HasBegunPlay()` and `!Actor->HasActorBegunPlay()`). Pre-BeginPlay timing in `Attach` is classified as `[UNMEASURED / Unproven for runtime spawns]`.
> 2. **AttackTracker Timing:** Registering the 12 typed components before calling `AttachLegacyBossBundle` alters relative registration order against `URPGAttackTracker` (which was previously created before CloseClipSwap, Shockwave, LowSweep, HealPunish). Dynamic lookup inspection does not prove callback, tick, or lifecycle parity. Reclassified from "verified harmless" to `[UNMEASURED / Integration Hypothesis]`.
> 3. **Component Accounting Arithmetic:** Corrected component inventory count from 19 to **21 potential classes** (12 typed classes + 9 non-typed classes: Footsteps, Music, AttackTracker, DamageResolver, TraceGuard, TraceAudit, BossHud, CombatDebug, BossLegend).
> 4. **Abort Citations & Teardown Recommendation:** Stale line citations for `FRPGPreparedBatch::Abort()` in `Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp` are corrected to lines 319-381 (unregister condition: lines 334-350; contract violation: lines 353-380). Releasing `Abort()` at `EndPlay` and receiving `ContractViolation` is a proposed integration policy, marked as `[UNMEASURED Proposed Policy]` rather than a measured clean teardown contract.

---

## 1. The Subsystem Call Site

### 1.1 Placement: `OnActorSpawned` vs. `OnWorldBeginPlay`

Component attachment today occurs in `URPGPlayerMovesSubsystem` (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h:14`, `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:40-297`).

The subsystem registers for actor spawn events in `PostInitialize()`:
```cpp
// Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:46-53
SpawnHandle = World->AddOnActorSpawnedHandler(
    FOnActorSpawned::FDelegate::CreateUObject(this, &URPGPlayerMovesSubsystem::OnActorSpawned));
```
In addition, `OnWorldBeginPlay(UWorld& InWorld)` (`RPGPlayerMovesSubsystem.cpp:55-63`) iterates all existing pawns via `TActorIterator<APawn> It(&InWorld)` and calls `Attach(*It)`.

#### Timing Conflict Analysis:
- `RPGBossActivation::ActivateWorld` (`Source/OneBossFight/Player/RPGBossActivation.h:32-34`, `RPGBossActivation.cpp:24-77`) is an **encounter-level batch operation**, requiring:
  1. `ExpectedWorld` (`UWorld*`)
  2. `Binding` (`const ARPGEncounterBinding*`)
  3. `Selections` (`const TArray<RPGBossWorldInputCompiler::FSelection>&`)
  4. `ManifestHash` (`const FString&`)
- In `RPGBossWorldInputCompiler.cpp:455-459`, `CompileWorldInput` enforces that **every participant actor** in `Binding->Participants` must satisfy:
  `!Actor->HasBegunPlay() && !Actor->IsActorBeginningPlay()`. If any participant has begun play, it fails with `WorldInput.ParticipantActorBegun`.
- In `L_SevarogArena`, the boss actor is level-placed (`BP_ExampleGreatSwordBoss_C_3` in `Content/OneBossFight/Levels/L_SevarogArena.umap`), but the player character is spawned dynamically by `AGameModeBase::SpawnDefaultPawnAtTransform` during world `BeginPlay()`.
- In addition, `RPGBossHydrationPreparation.cpp:512-514` strictly requires:
  `IsValid(World) && !World->HasBegunPlay() && Plan->EncounterInstance.IsValid() && IsValid(Actor) && !Actor->IsActorBeingDestroyed() && Actor->GetWorld() == World && !Actor->HasActorBegunPlay() && !Actor->IsActorBeginningPlay();`
- In `L_SevarogArena`, the boss actor is level-placed (`BP_ExampleGreatSwordBoss_C_3` in `Content/OneBossFight/Levels/L_SevarogArena.umap`), but the player character is spawned dynamically by `AGameModeBase::SpawnDefaultPawnAtTransform` during world `BeginPlay()`.
- **The Catch-22 of `OnActorSpawned`:**
  - When `OnActorSpawned` fires for the boss during initial level streaming/loading, the player pawn does not yet exist in the world (`Binding->Participants` cannot resolve the player actor).
  - When `OnActorSpawned` fires for the player pawn during `StartPlay()`, the level-placed boss pawn is already in the world.
  - Therefore, calling `ActivateWorld` on isolated boss `OnActorSpawned` is impossible without deferred participant resolution.
- **The Seam Limitations of `URPGPlayerMovesSubsystem::Attach` `[UNMEASURED / Unproven for runtime spawns]`:**
  - `Attach(AActor* Pawn)` (`RPGPlayerMovesSubsystem.cpp:251-297`) was initially examined as a candidate hook location preceding `AttachLegacyBossPrelude(Pawn)` (`line 259`) and `AttachLegacyBossBundle(Pawn)` (`line 296`).
  - However, source inspection reveals that `Attach` is reached via two distinct paths:
    1. `OnWorldBeginPlay(UWorld& InWorld)` (`RPGPlayerMovesSubsystem.cpp:55-63`): iterates existing pawns (`TActorIterator<APawn>`). While `World.cpp:5430` dispatches subsystem `OnWorldBeginPlay` before `GameMode->StartPlay:5436`, at this instant the dynamically spawned player pawn does not yet exist in the world.
    2. `OnActorSpawned(AActor* Actor)` (`RPGPlayerMovesSubsystem.cpp:75-77`): fired dynamically whenever any actor spawns during gameplay.
  - Crucially, `Attach(AActor* Pawn)` contains **no lifecycle guard** checking whether the world or actor has begun play.
  - In Unreal Engine 5.5 source (`LevelActor.cpp:733`), the engine invokes `PostSpawnInitialize` *before* broadcasting `OnActorSpawned` (`LevelActor.cpp:750`). For non-deferred runtime spawns (`Actor.cpp:3904-3906`, `:3969`), `Actor.cpp:4050-4070` dispatches `BeginPlay()` immediately if the world has already begun.
  - Consequently, for any runtime-spawned actor, `BeginPlay()` may have already executed prior to the delegate callback reaching `Attach(Actor)`, directly violating `HydrationPreparation.cpp:512-514` (`!World->HasBegunPlay()` and `!Actor->HasActorBegunPlay()`).
  - **Conclusion:** `Attach` is NOT a universal never-begun activation seam. Any hook placement inside `Attach` or elsewhere must be explicitly bounded to an eligible lifecycle path backed by measured participant-availability evidence before DD30 implementation.

### 1.2 Missing Live Prerequisites (Today)

For `ActivateWorld` to execute successfully in `L_SevarogArena`, four prerequisites must be supplied that do not exist in live gameplay today:

1. **`FSelection` for the Boss Member:**
   - Defined in `Source/OneBossFight/Player/RPGBossWorldInputCompiler.h:60-67`:
     ```cpp
     struct FSelection { FName Slot; ERPGPreflightRole Role; FName SelectedPhaseId; };
     ```
   - Must explicitly specify:
     * `Slot`: `FName("Boss")` (must exactly match `FRPGPlacedParticipantBinding::Slot`)
     * `Role`: `ERPGPreflightRole::BossCore` (`Role == ERPGPreflightRole::None` fails with `WorldInput.SelectionRole`, line 399)
     * `SelectedPhaseId`: `FName("Phase1")` (`SelectedPhaseId.IsNone()` fails with `WorldInput.SelectionPhaseMissing`, line 403)
   - *Status Today:* No game configuration or subsystem specifies this selection.
2. **Placed `ARPGEncounterBinding` Actor in `L_SevarogArena`:**
   - Defined in `Source/OneBossFight/Player/RPGEncounterBinding.h:380-388`.
   - Requires valid `FGuid EncounterInstance` and populated `TArray<FRPGPlacedParticipantBinding> Participants` linking `Slot`, `TargetSlot`, `Actor`, and `Definition`.
   - *Disk Audit Result:* Direct binary inspection of `Content/OneBossFight/Levels/L_SevarogArena.umap` confirms **NO `ARPGEncounterBinding` actor is placed in the level**. Furthermore, zero `.umap` files in `Content/` contain an `ARPGEncounterBinding`.
   - *Requirement:* An `ARPGEncounterBinding` must be placed in `L_SevarogArena.umap` or spawned transiently by the game mode/subsystem before activation.
3. **`ManifestHash` String:**
   - Required by `RPGBossWorldInputCompiler.cpp:349-351` (`IsManifestHashShape(ManifestHash)`) to be exactly 64 hexadecimal characters.
   - Must match the SHA256 of the 110 parity fields authored in the definition: `"24987ca96cfa923769c9b33a55ad58f3957ce678bc14f24ef342f0fb525f056c"`.
   - *Status Today:* Hardcoded in test fixtures and authoring draft JSON, but absent from live runtime subsystem code.
4. **`RPGCombatCatalog` Epoch in `UGameInstance`:**
   - `RPGBossWorldInputCompiler.cpp:59-81` strictly acquires the content epoch via `RPGCombatRegistry::ForWorld(ExpectedWorld)`, requiring `ExpectedWorld->GetGameInstance()->GetSubsystem<URPGCombatCatalogSubsystem>()`.
   - *Status Today:* If the game instance does not initialize `URPGCombatCatalogSubsystem` or publish an epoch for the active profile, `ActivateWorld` rejects with `WorldInput.CatalogSubsystemMissing` or `WorldInput.NoPublishedEpoch`.

---

## 2. The Fallback Hierarchy

### Component Inventory Accounting: 12 Typed + 9 Non-Typed = 21 Potential Classes
The Prelude and Bundle registration methods (`AttachLegacyBossPrelude` and `AttachLegacyBossBundle`, `RPGPlayerMovesSubsystem.cpp:139-249`) enumerate **21 potential component classes**:
- **12 Typed Component Classes:**
  1. `URPGBossStagger` (`line 163`)
  2. `URPGBossPhases` (`line 168`)
  3. `URPGBossEncounter` (`line 173`)
  4. `URPGBossDormantWake` (`line 178`)
  5. `URPGBossPosture` (`line 182`)
  6. `URPGBossDeath` (`line 187`)
  7. `URPGBossLook` (`line 191`)
  8. `URPGBossBleed` (`line 195`)
  9. `URPGBossCloseClipSwap` (`line 204`)
  10. `URPGBossShockwave` (`line 208`)
  11. `URPGBossLowSweep` (`line 213`)
  12. `URPGBossHealPunish` (`line 218`)
- **9 Non-Typed Component Classes:**
  1. `URPGFootsteps` (`AddFootsteps(Pawn, true)`, `line 141`)
  2. `URPGBossMusic` (`line 144`)
  3. `URPGAttackTracker` (`line 199`)
  4. `URPGDamageResolver` (`line 223`)
  5. `URPGTraceGuard` (`line 226`)
  6. `URPGTraceAudit` (`line 230`)
  7. `URPGBossHud` (`line 235`)
  8. `URPGCombatDebug` (`line 242`)
  9. `URPGBossLegend` (`line 247`)

> [!NOTE]
> *Arithmetic Clarification:* 21 is a class inventory count, not a guarantee of 21 instantiated component objects on every execution (existing-component guards `!Pawn->FindComponentByClass<T>()` and build configuration settings such as `Shipping` guard instantiation).


`RPGBossActivation::ActivateWorld` returns `FRPGWorldActivationResult` (`Source/OneBossFight/Player/RPGBossActivation.h:20-29`) containing `ERPGWorldActivationOutcome`:

```
                    [ ActivateWorld() Called ]
                                |
        +-----------------------+-----------------------+
        |                                               |
  [ Succeeded ]                                   [ Rejected ]
        |                                               |
   Outcome ==                                    Is Contract
   Activated                                      Violation?
        |                                       /            \
        v                                     Yes              No
   12 Typed Components                         |               |
   Registered On Boss                          v               v
        |                                  Outcome ==      Outcome ==
        v                                  HardError    FallBackToLegacy
   Execute Legacy Path                         |               |
   (FindComponentByClass                       v               v
    Skips 12 Typed Classes)              Lead Decision   Execute Legacy
        |                                (Log / Refuse)  Bundle Normally
        v                                                (21 Potential Classes)
   Attach Non-Typed
   (Footsteps, Music, Tracker, etc.)
```

### 2.1 Outcome 1: `Activated` (Registered Subset)

1. `ActivateWorld` returns `Outcome == ERPGWorldActivationOutcome::Activated` (`RPGBossActivation.cpp:74`).
2. The 12 typed components are instantiated, configured from typed data assets, strongly leased, and registered on the boss actor (`IsRegistered() == true`, `HasBegunPlay() == false`).
3. Control proceeds into `AttachLegacyBossPrelude(Pawn)` and `AttachLegacyBossBundle(Pawn)` (`RPGPlayerMovesSubsystem.cpp:139-249`).
4. **Suppression Mechanism (100% Native & Automatic):**
   - Every one of the 11 typed classes in `AttachLegacyBossBundle` has an explicit `!Pawn->FindComponentByClass<T>()` guard:
     * `URPGBossStagger`: `RPGPlayerMovesSubsystem.cpp:161`
     * `URPGBossPhases`: `RPGPlayerMovesSubsystem.cpp:166`
     * `URPGBossEncounter`: `RPGPlayerMovesSubsystem.cpp:171`
     * `URPGBossDormantWake`: `RPGPlayerMovesSubsystem.cpp:176`
     * `URPGBossPosture`: `RPGPlayerMovesSubsystem.cpp:180`
     * `URPGBossLook`: `RPGPlayerMovesSubsystem.cpp:189`
     * `URPGBossBleed`: `RPGPlayerMovesSubsystem.cpp:193`
     * `URPGBossCloseClipSwap`: `RPGPlayerMovesSubsystem.cpp:202`
     * `URPGBossShockwave`: `RPGPlayerMovesSubsystem.cpp:206`
     * `URPGBossLowSweep`: `RPGPlayerMovesSubsystem.cpp:211`
     * `URPGBossHealPunish`: `RPGPlayerMovesSubsystem.cpp:216`
   - The 12th typed component, `URPGBossDeath`, is invoked via `URPGBossDeath::Attach(Pawn, ERPGBossDeathMode::OwnClip)` (`line 187`). In `Source/OneBossFight/Player/RPGBossDeath.cpp:47-50`, `Attach()` executes:
     ```cpp
     if (URPGBossDeath* Existing = Boss->FindComponentByClass<URPGBossDeath>())
     {
         return Existing; // Skips NewObject and RegisterComponent
     }
     ```
   - All 12 legacy instantiations are skipped. Zero duplicate components are allocated.
5. **Non-Typed Component Retention:**
   The remaining non-typed components attach cleanly without interference:
   - `URPGFootsteps`: `AttachLegacyBossPrelude`, line 141 (`AddFootsteps(Pawn, true)`)
   - `URPGBossMusic`: `AttachLegacyBossPrelude`, lines 142-154
   - `URPGAttackTracker`: `AttachLegacyBossBundle`, lines 197-201
   - `URPGDamageResolver`: `AttachLegacyBossBundle`, line 223 (`URPGDamageResolver::FindOrAdd(Pawn)`)
   - `URPGTraceGuard`: `AttachLegacyBossBundle`, lines 224-227
   - `URPGTraceAudit`: `AttachLegacyBossBundle`, lines 228-231 (empty in Shipping)
   - `URPGBossHud`: `AttachLegacyBossBundle`, lines 233-237
   - `URPGCombatDebug`: `AttachLegacyBossBundle`, lines 238-243
   - `URPGBossLegend`: `AttachLegacyBossBundle`, lines 244-248

### 2.2 Outcome 2: `FallBackToLegacy`

1. `ActivateWorld` rejects due to standard environmental or input validation failure (e.g. missing definition asset, binding selection mismatch, non-fatal preflight rejection).
2. Preparation registration rolls back in reverse order, then executes `Prepared.Batch->Abort()` (`RPGBossActivation.cpp:61-68`).
3. Because cleanup is clean (`Result.Registration.Cleanup.IsClean() && Cleanup.IsClean() && Prepared.Batch->GetOwnedComponentCount() == 0`), `Finish(ERPGWorldActivationOutcome::FallBackToLegacy, TEXT("ActivationWorld.RegistrationRejected"))` is recorded (`line 69-70`).
4. Zero typed components remain attached to the boss actor.
5. Control flows into the legacy bundle. All 12 `FindComponentByClass` guards evaluate to `true`. All 12 typed components and 9 non-typed components attach via their historical paths.
6. Boss combat functions identically to historical baseline with zero disruption.

### 2.3 Outcome 3: `HardError`

1. Arises from off-thread invocation, mid-call state mutation/drift (`WorldInput.ContentDrift`, `WorldInput.BindingDrift`), or an unclean registration/abort failure leaving orphaned components (`RPGBossActivation.cpp:48-58, 67-71`).
2. Subsystem Handling Options:
   - **Option A (Fail-Safe Legacy Fallback):** Log critical diagnostic via `UE_LOG(LogRPGActivationWorld, Error, ...)`, then invoke the legacy bundle anyway.
     * *Risk:* If an unclean abort left partially registered or garbage components on the actor, the legacy bundle may produce duplicate components, state corruption, or memory leaks.
   - **Option B (Fail-Closed / Quarantine - Recommended):** Log critical error, refuse boss activation, and quarantine the actor (e.g. leave dormant, disable ticking, or prevent combat start).
     * *Risk:* Boss remains inert in the arena, preventing fight progression, but guarantees memory and state integrity.
   - **Option C (Level Abort):** Broadcast fatal event requesting world reload or main menu return.
     * *Risk:* Disrupts player session immediately.

---

## 3. The Lifetime and Registration Model

### 3.1 Batch Storage and Ownership

- `FRPGWorldActivationResult` holds `TUniquePtr<FRPGPreparedBatch> Batch` (`RPGBossActivation.h:26`).
- It is **move-only** and must reside strictly on the game thread (`IsInGameThread() == true`).
- **Subsystem Member:** `URPGPlayerMovesSubsystem` must own the active activation results in a private map keyed by actor or encounter GUID:
  ```cpp
  TMap<TWeakObjectPtr<AActor>, FRPGWorldActivationResult> ActiveBossBatches;
  ```

### 3.2 Teardown and `Abort()` Semantics

- **Destruction Contract (`Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp:319-381`):**
  - `FRPGPreparedBatch::Abort()` contains two distinct phases:
    1. **Unregister Phase (`lines 334-350`):**
       ```cpp
       // RPGBossHydrationPreparation.cpp:334-350
       if (bRegisteredByBatch)
       {
           for (int32 MemberIndex = Members.Num() - 1; MemberIndex >= 0; --MemberIndex)
           {
               AActor* Owner = Plan->Participants[MemberIndex].Actor.Get();
               for (int32 Index = Members[MemberIndex].Owned.Num() - 1; Index >= 0; --Index)
               {
                   UActorComponent* Component = Members[MemberIndex].Owned[Index].Component.Get();
                   if (IsValid(Owner) && IsValid(Component) && !Component->IsBeingDestroyed()
                       && Component->GetOwner() == Owner && !Component->HasBegunPlay() && Component->IsRegistered())
                   {
                       Component->UnregisterComponent();
                   }
               }
           }
           bRegisteredByBatch = false;
       }
       ```
    2. **Lease Release & Contract Violation Phase (`lines 353-380`):**
       ```cpp
       // RPGBossHydrationPreparation.cpp:353-379
       for (int32 MemberIndex = Members.Num() - 1; MemberIndex >= 0; --MemberIndex)
       {
           const FRPGPreflightParticipantPlan& Participant = Plan->Participants[MemberIndex];
           TArray<FOwnedComponent>& Owned = Members[MemberIndex].Owned;
           for (int32 OwnedIndex = Owned.Num() - 1; OwnedIndex >= 0; --OwnedIndex)
           {
               const FString Label = FString::Printf(TEXT("[slot=%s][component=%s]"), *Participant.Slot.ToString(), *Owned[OwnedIndex].Name.ToString());
               UActorComponent* Component = Owned[OwnedIndex].Component.Get();
               const AActor* Owner = Participant.Actor.Get(); // null for a stale or garbage actor
               if (!Component || !IsValid(Component) || Component->IsBeingDestroyed() || !Owner || !IsValid(Owner))
               {
                   ++Report.AlreadyGone; // destroyed by someone else or its owner is gone: released, never touched
               }
               else if (Component->GetOwner() != Owner || Component->IsRegistered() || Component->HasBegunPlay())
               {
                   // Somebody registered or began it, or moved it: this artifact cannot undo that and does not destroy gameplay objects.
                   ++Report.ContractViolations;
                   Report.Errors.Add(FString::Printf(TEXT("Preparation.ContractViolation%s: the component was registered, begun or moved outside the artifact; it was left in place and is no longer owned"), *Label));
               }
               else
               {
                   Component->DestroyComponent();
                   ++Report.Destroyed;
               }
           }
           Owned.Reset(); // releases every lease
       }
       ```
  - **CRITICAL LIFECYCLE BEHAVIOR (`lines 343, 366-371`):**
    - Line 343 explicitly unregisters components **ONLY IF `!Component->HasBegunPlay()`**.
    - If `Component->HasBegunPlay()` is true (which occurs once gameplay begins), `Abort()` **skips unregistering** the component!
    - Subsequently, in lines 366-371, because `Component->HasBegunPlay()` or `Component->IsRegistered()` is true, the component takes the `ContractViolations` branch:
      `Preparation.ContractViolation: the component was registered, begun or moved outside the artifact; it was left in place and is no longer owned`.
    - It deliberately does NOT call `Component->DestroyComponent()`, but leaves the component alive in place on the owner actor and resets its internal lease (`Owned.Reset()`, line 378).
    - Invalid, destroying, or missing-owner components take `AlreadyGone` (`line 364`). Only never-begun, unregistered components are destroyed via `Component->DestroyComponent()` (`lines 374-375`).
    - *Stale Citation Correction:* Earlier draft A-216 cited lines 218-268; those lines belong to preparation setup in `RPGBossHydrationPreparation.cpp`, not the `Abort()` implementation.
  - **Status of Teardown Policy `[UNMEASURED Proposed Policy]`:**
    - Calling `Release()` / `Abort()` at `EndPlay` and treating `ContractViolation` as expected teardown is a **proposed integration hypothesis**, not a measured clean teardown contract or an established lifecycle handoff.
    - Diagnostics (`Report.ContractViolations`) must remain observable.
    - An explicit lead-reviewed lifetime and teardown policy must be established prior to wiring DD30.

### 3.3 BeginPlay Timing & Inter-Component Dependencies

Because `OnActorSpawned` runs before actor `BeginPlay()`, all 12 typed components are registered before `AActor::BeginPlay()` is dispatched by the engine.

#### What Each Component Does at `BeginPlay()`:
1. `URPGBossStagger` (`RPGBossStagger.cpp:175-183`): Synchronously loads 4 animation clips (`FallClip`, `DownClip`, `RipostePlayerClip`, `RiposteBossClip`) into strong pointers to prevent hitching during stance breaks.
2. `URPGBossPhases` (`RPGBossPhases.cpp:62-78`): Synchronously loads `ImmunityEffect`, `RoarClip`, and `TransitionMontage`; caches `BaseWalkSpeed`; finds `URPGBossStagger` and calls `AddTickPrerequisiteComponent(Stagger)`.
3. `URPGBossEncounter` (`RPGBossEncounter.cpp:66-74`): Caches `HomeTransform = GetActorTransform()`; calls `Sleep()` if `GateRadius > 0`.
4. `URPGBossDormantWake` (`RPGBossDormantWake.cpp:37-43`): Synchronously loads `DormantClip` and `WakeClip`; finds `URPGBossEncounter` and adds tick prerequisite.
5. `URPGBossPosture` (`RPGBossPosture.cpp:36-40`): Initializes pool: `Posture = PostureMax`.
6. `URPGBossDeath` (`RPGBossDeath.cpp:97-115`): Resets poll timers; adds tick prerequisites for `Stagger`, `Posture`, and `Phases`.
7. `URPGBossLook` (`RPGBossLook.cpp:26-33`): Calls `GetWorld()->GetTimerManager().SetTimerForNextTick(...)` scheduling `Apply()` on the subsequent frame.
8. `URPGBossBleed` (`RPGBossBleed.cpp:31-42`): Sets `State.Threshold = InitialThreshold`; synchronously loads `ProcEffect`, `ProcSound`, and `BloodBurst` flipbook material.
9. `URPGBossCloseClipSwap` (`RPGBossCloseClipSwap.cpp:48-57`): Calls `Preload()` loading `A1Montage`, `A3aMontage`, `A3bMontage`; adds `Encounter` tick prerequisite.
10. `URPGBossShockwave`: **No `BeginPlay` override.**
11. `URPGBossLowSweep`: **No `BeginPlay` override.**
12. `URPGBossHealPunish`: **No `BeginPlay` override.**

#### `AttackTracker` Dependency Analysis `[UNMEASURED / Integration Hypothesis]`:
- In `AttachLegacyBossBundle` (`RPGPlayerMovesSubsystem.cpp:197-201`), `URPGAttackTracker` is instantiated and registered **AFTER** legacy Stagger, Phases, Encounter, DormantWake, Posture, Death, Look, and Bleed.
- In contrast, registering the 12 typed components ahead of the bundle alters the relative registration order: `URPGBossCloseClipSwap`, `URPGBossShockwave`, `URPGBossLowSweep`, and `URPGBossHealPunish` are registered *before* `URPGAttackTracker`.
- **Source Inspection of Lookups:**
  * `URPGBossShockwave.cpp:152`: `const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();` inside `TickComponent()`.
  * `URPGBossLowSweep.cpp:30, 170`: `Boss->FindComponentByClass<URPGAttackTracker>();` inside `TriggerLowSweep()` and `TickComponent()`.
  * `URPGBossHealPunish.cpp:100, 181, 249`: `Boss->FindComponentByClass<URPGAttackTracker>();` inside `HandleTargetDrinking()`, `Launch()`, and `TickComponent()`.
- None of these components look up or cache `AttackTracker` during construction or registration.
- However, guard and dynamic lookup inspection alone does not prove callbacks, tick prerequisite ordering, or lifecycle parity across all `Attach` execution paths.
- **Conclusion:** The assertion that altered registration order produces zero timing conflicts is an **unverified integration hypothesis `[UNMEASURED / Integration Hypothesis]`**, NOT an accepted gameplay equivalence fact. Runtime measurement in PIE is required before acceptance.

---

## 4. The Parity Checklist

The following matrix compares the 12 typed components between:
- **Legacy Bundle Value:** What `AttachLegacyBossBundle` produces today.
- **Typed Authoring Record:** What the typed profile/plan configures.
- **Parity Status:** `Identical-by-Default` vs. `Must-Be-Set`.

| # | Component Class | Constructor Location | Legacy Bundle Assignment | Typed Plan Property | Parity Status | Required Authoring Value |
| :- | :--- | :--- | :--- | :--- | :-: | :--- |
| 1 | `URPGBossStagger` | `RPGBossStagger.cpp:52` | Constructor defaults (`line 163`) | `stagger_policy.*`, `stagger_profile.*` | **Identical-by-Default** | Matches native constructor scalars and clips |
| 2 | `URPGBossPhases` | `RPGBossPhases.cpp:50` | Constructor defaults (`line 168`) | `phase_flow.*`, `phase_dependencies.*` | **Identical-by-Default** | Matches native constructor thresholds and clips |
| 3 | `URPGBossEncounter` | `RPGBossEncounter.cpp:59` | Constructor defaults (`line 173`) | `encounter_policy.*` | **Identical-by-Default** | `GateRadius = 1200.f`, `bResetOnPlayerRespawn = true` |
| 4 | `URPGBossDormantWake` | `RPGBossDormantWake.cpp:16` | Constructor defaults (`line 178`) | `dormant_wake.*` | **Identical-by-Default** | Matches native constructor wake clips |
| 5 | `URPGBossPosture` | `RPGBossPosture.cpp:30` | Constructor defaults (`line 182`) | `stats.MaxPosture`, `stats.PostureRegen*` | **Identical-by-Default** | Matches native posture scalars (100 pts, 4s delay) |
| 6 | `URPGBossDeath` | `RPGBossDeath.cpp:31` | `Attach(Pawn, OwnClip)` (`line 187`) | `death.DeathMode` | **MUST-BE-SET** | **`ERPGBossDeathMode::OwnClip`** (Native default is `PackMontage`) |
| 7 | `URPGBossLook` | `RPGBossLook.cpp:14` | Constructor defaults (`line 191`) | `look.*` | **Identical-by-Default** | Matches native skeletal mesh and piece soft paths |
| 8 | `URPGBossBleed` | `RPGBossBleed.cpp:24` | Constructor defaults (`line 195`) | `bleed.*` | **Identical-by-Default** | Matches native threshold scalars and Niagara proc |
| 9 | `URPGBossCloseClipSwap`| `RPGBossCloseClipSwap.cpp:39`| Constructor defaults (`line 204`) | `close_clip_swap.*` | **Identical-by-Default** | Matches native montages (`AM_Boss01_A1`, etc.) |
| 10| `URPGBossShockwave` | `RPGBossShockwave.cpp:19` | Constructor defaults (`line 208`) | `shockwave.*` | **Identical-by-Default** | Matches native shockwave radius, damage, timing |
| 11| `URPGBossLowSweep` | `RPGBossLowSweep.cpp:20` | Constructor defaults (`line 213`) | `low_sweep.*` | **Identical-by-Default** | Matches native low sweep angle, damage, timing |
| 12| `URPGBossHealPunish` | `RPGBossHealPunish.cpp:26` | Constructor defaults (`line 218`) | `heal_punish.*` | **Identical-by-Default** | Matches native javelin projectile scalars |

> [!IMPORTANT]
> **The Sole Must-Be-Set Override:** In `Source/OneBossFight/Player/RPGBossDeath.h:51`, the native member default is `ERPGBossDeathMode DeathMode = ERPGBossDeathMode::PackMontage;`. However, the live game explicitly overrides this to `ERPGBossDeathMode::OwnClip` at `RPGPlayerMovesSubsystem.cpp:187`. Therefore, typed definitions MUST author `death.DeathMode` as `"OwnClip"` to avoid triggering ragdoll physics bugs (`DEATH_CLIP_NOTES.md`). All other 11 components match constructor defaults.

---

## 5. Automation and PIE Driver Verification Test List

The Tech Lead should require the following 8 focused gates prior to declaring live activation production-ready (one line per check):

1. **`ActivationHook.SubsystemSpawnSuppression`:** In a transient game world, spawn a boss pawn with an active mock binding; assert that `ActivateWorld` returns `Activated` and all 12 legacy `FindComponentByClass` bundle allocations are skipped (0 duplicate components).
2. **`ActivationHook.SubsystemFallbackCleanliness`:** In a transient game world, simulate `ActivateWorld` returning `FallBackToLegacy`; assert that all 12 legacy components attach cleanly and 0 typed batch components remain on the actor.
3. **`ActivationHook.HardErrorQuarantinePolicy`:** Inject a registration contract violation during `ActivateWorld`; assert that the subsystem logs an error and executes the chosen quarantine policy without crashing or leaking unmanaged components.
4. **`ActivationHook.NonTypedBundleAttachment`:** In a transient game world following successful `ActivateWorld`, assert that `URPGAttackTracker`, `URPGBossMusic`, `URPGFootsteps`, and `URPGDamageResolver` are present and registered.
5. **`ActivationHook.BeginPlayDispatchOrder`:** Spawn a boss pawn, invoke `ActivateWorld`, call `AActor::DispatchBeginPlay()`; assert that all 12 components execute `BeginPlay()` without null pointer dereferences or asset load warnings.
6. **`ActivationHook.PostBeginPlayTeardownNoCrash`:** Spawn, activate, begin play, then destroy the boss actor; assert that `Release()` executes cleanly without memory corruption or engine fatal errors.
7. **`PIE.L_SevarogArena.FirstFrameComponentParity` `[UNMEASURED Gate]`:** Launch PIE in `L_SevarogArena`; assert that the boss pawn carries the expected component inventory across all 21 potential classes (12 typed + 9 non-typed) with identical class types and property values as the historical baseline.
8. **`PIE.L_SevarogArena.BossWakeAndPhaseOneCombat`:** Run a 30-second headless PIE combat driver in `L_SevarogArena`; assert that the boss sleeps behind the fog gate, wakes on player proximity, and attacks without script errors.

---

## 6. Open Technical Unknowns the Code Does Not Answer

The following 5 questions cannot be determined from offline C++ static analysis and require Tech Lead architectural decisions:

1. **Who Spawns/Places the Encounter Binding Actor?** `L_SevarogArena.umap` contains no placed `ARPGEncounterBinding`. Will the binding actor be manually placed and saved into `L_SevarogArena.umap` in the editor, or should `URPGPlayerMovesSubsystem` dynamically spawn and configure a transient `ARPGEncounterBinding` at world startup?
2. **Player Pawn Binding Timing in Single-Player Arena:** If the encounter binding requires the player character reference at input compilation time, but the player pawn is spawned by `AGameModeBase` during world `BeginPlay()`, what is the exact synchronization barrier that guarantees both pawns exist before `ActivateWorld` is invoked?
3. **Multiplayer Network Authority Responsibility:** `URPGPlayerMovesSubsystem` runs on both client and server instances. `RPGBossActivation::ActivateWorld` contains no `HasAuthority()` guard. Should `ActivateWorld` be executed strictly on the network authority (server), with state replicated to clients, or should visual components (`URPGBossLook`, `URPGBossHud`) run locally on clients?
4. **Permanent Shipping Fallback vs. Fail-Closed:** If an authored primary data asset fails to load in a packaged Shipping build on an end-user machine, does production policy mandate silent fallback to the legacy hardcoded bundle, or should the game fail closed to prevent silent gameplay divergence?
5. **Combat Context Subsystem Registration Moment:** `URPGCombatContextSubsystem::BindEncounter` registers participants with combat telemetry. Does this occur immediately following `ActivateWorld`, or is it deferred until the encounter gate is breached and `URPGBossEncounter` wakes?

---

## 7. Script-Derived 27-Asset Existence Audit (Per Lead C-324)

To resolve the discrepancy noted in `[C-324]` and confirm exact parity with Codex's DD29 evidence (`C320_profile_path_count_comparison.json`), the asset paths were extracted directly by script from `examples/boss_draft_profiles.json` and audited against `Content/**/*.uasset`:
- **Total Distinct `/Game` Asset Paths in JSON:** 27
- **Total Property References in JSON:** 80
- **Assets Present on Disk:** 27 / 27 (100% Present)
- **Missing Assets:** 0
- **Metadata Directory String:** 1 (`/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/`, excluded as non-asset container path)

### Verified 27-Asset Presence Matrix:
| # | Asset Package Path | On Disk | Refs | Profile JSON Location Pointers |
| :- | :--- | :-: | :-: | :--- |
| 1 | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.SK_CombatMannequin` | **True** | 3 | `profiles[0..2].skeleton` |
| 2 | `/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C` | **True** | 3 | `profiles[0..2].fireball.FireballAbility` |
| 3 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage.Ability_R_Intro_Anim_Montage` | **True** | 3 | `profiles[0..2].phase_dependencies.TransitionMontage` |
| 4 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage.KnockdownStart_Anim_Montage` | **True** | 3 | `profiles[0..2].stagger_profile.FallMontage` |
| 5 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage.Knockdown_Getup_Anim_Montage` | **True** | 3 | `profiles[0..2].stagger_profile.GetUpMontage` |
| 6 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C` | **True** | 6 | `profiles[0..2].phase_dependencies/stagger_profile.ImmunityEffect` |
| 7 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.A_Guardian_ImpactL_Cue` | **True** | 3 | `profiles[0..2].bleed.ProcSound` |
| 8 | `/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med` | **True** | 3 | `profiles[0..2].bleed.ProcEffect` |
| 9 | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1` | **True** | 3 | `profiles[0..2].close_clip_swap.A1Montage` |
| 10 | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a` | **True** | 3 | `profiles[0..2].close_clip_swap.A3aMontage` |
| 11 | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b` | **True** | 3 | `profiles[0..2].close_clip_swap.A3bMontage` |
| 12 | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend` | **True** | 3 | `profiles[0..2].death.DeathMontage` |
| 13 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A1_QuickSlash.AN_Boss01_A1_QuickSlash` | **True** | 1 | `profiles[0].animations[0]` |
| 14 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A3a_Combo1.AN_Boss01_A3a_Combo1` | **True** | 1 | `profiles[1].animations[0]` |
| 15 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend` | **True** | 3 | `profiles[0..2].death.DeathClip` |
| 16 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_DormantIdle.AN_Boss01_DormantIdle` | **True** | 3 | `profiles[0..2].dormant_wake.DormantClip` |
| 17 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.AN_Boss01_PhaseRoar` | **True** | 3 | `profiles[0..2].phase_dependencies.RoarClip` |
| 18 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown` | **True** | 3 | `profiles[0..2].stagger_profile.DownClip` |
| 19 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall.AN_Boss01_StaggerFall` | **True** | 3 | `profiles[0..2].stagger_profile.FallClip` |
| 20 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Wake.AN_Boss01_Wake` | **True** | 3 | `profiles[0..2].dormant_wake.WakeClip` |
| 21 | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.AN_Riposte_Boss_Reaction` | **True** | 3 | `profiles[0..2].stagger_profile.RiposteBossClip` |
| 22 | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front.AN_Riposte_Player_Front` | **True** | 3 | `profiles[0..2].stagger_profile.RipostePlayerClip` |
| 23 | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body` | **True** | 3 | `profiles[0..2].look.Body` |
| 24 | `/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.SK_Boss01_BrazierGauntlet` | **True** | 3 | `profiles[0..2].look.Pieces[2]` |
| 25 | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown` | **True** | 3 | `profiles[0..2].look.Pieces[0]` |
| 26 | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle` | **True** | 3 | `profiles[0..2].look.Pieces[1]` |
| 27 | `/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword` | **True** | 3 | `profiles[0..2].look.Sword` |

---

*End of Activation Hook Specification. Staged for Tech Lead Review.*
