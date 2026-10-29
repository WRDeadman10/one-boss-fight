# Architecture & Pipeline Analysis: Boss Component Hydration & Wiring
**Document:** `WIRING_ANALYSIS.md`  
**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Order Reference:** Tech Lead Claude `[C-278]` (Task `A-195`)  
**Scope:** Offline Read-Only Analysis of Boss Component Hydration, Preparation, and Registry Wiring  
**Hygiene:** Pure C++ / Unreal Engine 5.5.4 offline source audit; 100% CRLF line endings; zero engine processes; zero git operations  

---

## Executive Summary

Currently in `OneBossFight`, five native boss components are **wired** into the hydration and preparation pipeline:
1. `URPGBossStagger`
2. `URPGBossPhases`
3. `URPGBossEncounter`
4. `URPGBossDormantWake`
5. `URPGBossPosture`

Five additional typed plans exist, have verified adapter implementations, and are compiled into `FRPGParticipantConfig`, but are currently **unwired** from hydration preflight and world preparation:
1. `URPGBossBleed` (DD19)
2. `URPGBossLowSweep` (DD20)
3. `URPGBossShockwave` (DD21)
4. `URPGBossHealPunish` (DD22)
5. `URPGBossLook` (DD23)

This document provides a comprehensive, line-cited analysis of:
- Exactly how the five wired components are integrated today across definition compilation, hydration preflight, world preparation, and per-world reservation.
- Exactly what code changes and test assertions would be required to wire each of the five unwired plans.
- Concrete architectural, lifecycle, and initialization hazards provable directly from the C++ codebase.
- An explicit catalog of unknown questions that the codebase leaves unresolved (clearly distinguishing demonstrable code facts from inferences).

---

## 1. How the Five Wired Components Are Inserted Today

### 1.1 The Wired Component Manifest and Plan Order

In `Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp`, the static constant and factory define the plan list:
- `constexpr int32 BossCorePlanCount = 5;` ([`RPGBossHydrationPreflight.cpp:61`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L61))
- Factory function `MakeBossCorePlans(FName SelectedPhaseId)` ([`RPGBossHydrationPreflight.cpp:65-74`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L65-L74)) constructs the plans in deterministic relative plan order:

```cpp
// RPGBossHydrationPreflight.cpp:65-74
TArray<FRPGComponentPlan> MakeBossCorePlans(FName SelectedPhaseId)
{
    TArray<FRPGComponentPlan> Plans;
    Plans.Add(RPGBossStaggerClusterAdapters::MakeStaggerClusterPlan());         // #1: Stagger
    Plans.Add(RPGBossPhasesClusterAdapters::MakePhasesClusterPlan(SelectedPhaseId)); // #2: Phases
    Plans.Add(RPGBossEncounterClusterAdapters::MakeEncounterClusterPlan());     // #3: Encounter
    Plans.Add(RPGBossDormantWakeAdapters::MakeDormantWakePlan());               // #4: DormantWake
    Plans.Add(RPGBossStatsAdapters::MakePosturePlan());                         // #5: Posture
    return Plans;
}
```

The five component plans and their exact specifications:
1. **Stagger:**
   - Class: `URPGBossStagger::StaticClass()` ([`RPGBossStaggerClusterAdapters.cpp:193`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStaggerClusterAdapters.cpp#L193))
   - Instance Name: `TEXT("RPGBossStagger")` (`:194`)
   - Required Fields: **25 fields** (`:195-221`) composed of 14 `StaggerPolicy.*` fields and 11 `StaggerProfile.*` fields.
   - Configure Callback: Lambda invoking `ConfigureStaggerCluster` (`:222-225`).
2. **Phases:**
   - Class: `URPGBossPhases::StaticClass()` ([`RPGBossPhasesClusterAdapters.cpp:239`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhasesClusterAdapters.cpp#L239))
   - Instance Name: `TEXT("RPGBossPhases")` (`:240`)
   - Required Fields: **18 fields** (`:241-250`) composed of 4 selected phase fields (`Phases[SelectedId].*`), 6 `PhaseFlow.*` fields, 5 `Fireball.*` fields, and 3 `PhaseDependencies.*` fields.
   - Configure Callback: Lambda capturing `SelectedPhaseId` by value invoking `ConfigurePhasesCluster` (`:252-255`).
3. **Encounter:**
   - Class: `URPGBossEncounter::StaticClass()` ([`RPGBossEncounterClusterAdapters.cpp:81`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounterClusterAdapters.cpp#L81))
   - Instance Name: `TEXT("RPGBossEncounter")` (`:82`)
   - Required Fields: **3 fields** (`:83`) composed of `Stats.MaxHealth`, `EncounterPolicy.GateRadius`, and `EncounterPolicy.bResetOnPlayerRespawn`.
   - Configure Callback: Function pointer `&ConfigureEncounterCluster` (`:84`).
4. **DormantWake:**
   - Class: `URPGBossDormantWake::StaticClass()` ([`RPGBossDormantWakeAdapters.cpp:132`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDormantWakeAdapters.cpp#L132))
   - Instance Name: `TEXT("RPGBossDormantWake")` (`:133`)
   - Required Fields: **2 fields** (`:134`) composed of `DormantWake.DormantClip` and `DormantWake.WakeClip`.
   - Configure Callback: Function pointer `&ConfigureDormantWake` (`:135`).
5. **Posture:**
   - Class: `URPGBossPosture::StaticClass()` ([`RPGBossStatsAdapters.cpp:143`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStatsAdapters.cpp#L143))
   - Instance Name: `TEXT("RPGBossPosture")` (`:144`)
   - Required Fields: **3 fields** (`:145`) composed of `Stats.MaxPosture`, `Stats.PostureRegenDelay`, and `Stats.PostureRegenRate`.
   - Configure Callback: Function pointer `&ConfigurePosture` (`:146`).

### 1.2 The Required-Field Manifest (51 Unique Paths)

In `RPGBossHydrationPreflight.cpp:386-402`, the preflight engine verifies that every required path across all built plans is present in `Config->Fields`:
- The mathematical union of required fields:
  $$\text{Total} = 25 (\text{Stagger}) + 18 (\text{Phases}) + 3 (\text{Encounter}) + 2 (\text{DormantWake}) + 3 (\text{Posture}) = 51 \text{ paths}$$
- Each path is unique across the plans; no path is repeated across different plans except `FieldImmunityEffect` which is reconciled in the plan definitions.
- Preflight failure token: `Preflight.MissingRequiredField[slot=...]: required manifest path <Path> is not in the config` ([`RPGBossHydrationPreflight.cpp:399`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L399)).

### 1.3 Preflight Validation & Preexisting Consumer Guard

In `RPGBossHydrationPreflight.cpp`:
- `ManagedCoreConsumerClasses()` ([`RPGBossHydrationPreflight.cpp:143-146`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L143-L146)) declares the 6 classes that an actor must not already have:
  ```cpp
  TArray<UClass*> ManagedCoreConsumerClasses()
  {
      return {
          URPGBossPhases::StaticClass(),
          URPGBossEncounter::StaticClass(),
          URPGBossPosture::StaticClass(),
          URPGBossStagger::StaticClass(),
          URPGBossDormantWake::StaticClass(),
          URPGCombatParticipant::StaticClass()
      };
  }
  ```
- In `CompilePreflight` ([`RPGBossHydrationPreflight.cpp:289-297`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L289-L297)), if a member has `ERPGPreflightRole::BossCore` and already holds any of these components, preflight fails closed immediately:
  `Preflight.PreexistingConsumer[slot=...]: the actor already has a <ClassName>`
- Cluster validation calls in `CompilePreflight`:
  - `RPGBossStaggerClusterAdapters::ValidateStaggerCluster(*Config, Error)` (`:361-364`) -> `Preflight.StaggerRejected`
  - `RPGBossPhasesClusterAdapters::ValidatePhasesCluster(*Config, Request.SelectedPhaseId, Error)` (`:365-368`) -> `Preflight.PhaseRejected`
  - `RPGBossEncounterClusterAdapters::ValidateEncounterCluster(*Config, Error)` (`:371-374`) -> `Preflight.EncounterPolicyRejected` or `Preflight.StatsRejected`
  - `RPGBossDormantWakeAdapters::ValidateDormantWake(Config->DormantWake, Error)` (`:375-378`) -> `Preflight.DormantWakeRejected`

### 1.4 The Compiler (`CompileParticipantImpl`)

In `Source/OneBossFight/Player/RPGEncounterBinding.cpp:30-136`:
- `CompileParticipantImpl` receives `const URPGBossDefinition& D`, `Content`, and `Hash`.
- Validates identity, schema (`D.Schema == 1`), `DefinitionId`, and `PresentationId` (`:35-39`).
- Validates stats scalars (`:40-46`).
- Validates all component configs via their standalone adapter validators:
  - `ValidateEncounterPolicy` (`:48`)
  - `ValidateStaggerPolicy` (`:50`)
  - `ValidatePhaseFlow` (`:52`)
  - `ValidateFireball` (`:54`)
  - `ValidatePhaseDependencies` (`:56`)
  - `ValidateStaggerProfile` (`:58`)
  - `ValidateDormantWake` (`:60`)
  - `ValidateBleed` (`:62`) *(compiled into config, but unwired in preflight)*
  - `ValidateLowSweep` (`:64`) *(compiled into config, but unwired in preflight)*
  - `ValidateShockwave` (`:66`) *(compiled into config, but unwired in preflight)*
  - `ValidateHealPunish` (`:69`) *(compiled into config, but unwired in preflight)*
  - `ValidateLook` (`:74`) *(compiled into config, but unwired in preflight)*
- Populates `FRPGParticipantConfig` (`:105-121`), storing all validated structs into shared pointer `Out`.
- **Synthetic vs Production Dependency Branching:**
  - `Value->bSyntheticFixture = bSynthetic;` (`:122`)
  - If `!bSynthetic` (production path):
    - Synchronously loads `D.Skeleton.LoadSynchronous()` (`:125`).
    - Validates that `D.Animations` is non-empty (`:126`).
    - Synchronously loads every animation in `D.Animations` and verifies `Animation->GetSkeleton() == Value->Skeleton.Get()` (`:127-132`).
  - In `RPGBossHydrationPreflight.cpp:331-353`:
    - If `Config->bSyntheticFixture == true`: accepted ONLY `#if WITH_DEV_AUTOMATION_TESTS`; in shipping/cooked builds, fails with `Preflight.SyntheticUnavailable` (`:334-336`).
    - If `Config->bSyntheticFixture == false`: calls `CheckCompiledDependencies` (`:342-345`) and checks that `Cast<ACharacter>(Actor)->GetMesh()->GetSkeletalMeshAsset()` is compatible with `Config->Skeleton.Get()` via `CompiledSkeleton->IsCompatibleMesh(Mesh)` (`:346-352`).

### 1.5 World Preparation & Per-World Reservation

1. **`RPGBossWorldPreparation.cpp/.h`:**
   - Composes `CompileWorldInput` and `PrepareBatch` ([`RPGBossWorldPreparation.cpp:138-196`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossWorldPreparation.cpp#L138-L196)).
   - Enforces game-thread execution (`:142`).
   - `Capture`: captures live binding identities (`World`, `GameInstance`, `Encounter`, members) before Stage 1 (`:29-47`).
   - `Complete`: binds input content epoch and participant count (`:50-73`).
   - `Holds`: verifies zero drift after input compilation and after component preparation (`:76-118`).
   - In Stage 2 (`RPGBossHydrationPreparation::PrepareBatch`), for each plan in each boss-core member:
     - `Allocate`: `NewObject<UActorComponent>(Actor, ComponentPlan.Class, ComponentPlan.InstanceName)` ([`RPGBossHydrationPreparation.cpp:168`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp#L168)).
     - `Configure`: `ComponentPlan.Configure(*Component, *Participant.Config, ConfigureError)` (`:212`).
   - If drift occurs after preparation, calls `Prepared.Batch->Abort()` (`:178-189`) which destroys precisely the newly allocated components.
2. **`RPGBossPreparationRegistry.cpp/.h`:**
   - Explicit instance bound to a single `UWorld*` (`FRPGBossPreparationRegistry::FRPGBossPreparationRegistry(UWorld* InWorld)`, [`:288-300`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPreparationRegistry.cpp#L288-L300)).
   - `TryPrepareAndReserve` (`:415-566`):
     - Validates game thread (`:421-426`) and admission state (`:429-434`).
     - **Conflict Pre-Check:** checks whether `EncounterInstance` GUID or any participant actor is already reserved in this registry (`:468-489`) **BEFORE any component is allocated**.
     - Calls `RPGBossWorldPreparation::PrepareWorldBatch` (`:491`).
     - On success, publishes reservation record and returns move-only `FRPGPreparationLeaseToken` with unique serial (`:537-548`).
     - If post-preparation cleanup fails during admission, marks entry as `Quarantined` (`:503`, `:549`).

### 1.6 Exact Tests Asserting Plan and Field Counts

The following tests in `Source/OneBossFight/Tests/` contain hardcoded numeric assertions on plan and field counts:

1. **`RPGBossHydrationPreflightTests.cpp`:**
   - Literal array `AllRequiredPaths` (`:76-135`): lists exactly 51 path string literals.
   - `FRPGPreflightValidTest:376`: `TestEqual(TEXT("boss-core has five plans"), Boss.Plans.Num(), 5)`
   - `FRPGPreflightValidTest:394`: `TestEqual(TEXT("the union of required manifest paths is fifty-one"), Required.Num(), 51)`
   - `FRPGPreflightValidTest:399`: `TestEqual(TEXT("one class lease per boss plan"), Boss.ClassLeases.Num(), 5)`
   - `FRPGPreflightValidTest:400`: `TestTrue(TEXT("the class leases are the plan classes"), Boss.ClassLeases.Num() == 5 ...)`
   - `FRPGPreflightValidTest:402`: `TestTrue(TEXT("target-only members get no boss plan and no class lease"), Plan->Participants[0].Plans.IsEmpty() ...)`
   - `FRPGPreflightValidTest:407`: `TestTrue(..., Again->Participants[1].Plans.Num() == 5)`
   - `FRPGPreflightTargetsTest:831`: `TestTrue(TEXT("only the boss has plans"), Out->Participants[0].Plans.IsEmpty() && Out->Participants[1].Plans.Num() == 5)`
   - `FRPGPreflightTargetsTest:852`: `TestTrue(..., Out->Participants[0].Plans.Num() == 5 && Out->Participants[1].Plans.Num() == 5)`
   - `FRPGPreflightExpandedTest:1035`: `TestTrue(..., BossPlan.Plans.Num() == 5 && BossPlan.ClassLeases.Num() == 5)`
   - `FRPGPreflightExpandedTest:1064-1069`: `TestTrue(..., ExpectedPaths.Num() == 51 && Union.Num() == 51 && SumOfRequired == 51)`
   - `FRPGPreflightExpandedTest:1087`: `TestTrue(..., Again->Participants[Member].Plans.Num() == 5)`
   - `FRPGPreflightConsumersTest:1282`: `TestTrue(..., BossPlan.Plans.Num() == 5)`
2. **`RPGBossHydrationPreparationTests.cpp`:**
   - Line 330: `TestEqual(TEXT("ten components are leased"), Batch.GetOwnedComponentCount(), 10)` (in a 2-boss test fixture: 2 members * 5 plans = 10 components).
   - `FRPGPreparationAbortTest:481`: `TestEqual(TEXT("every lease is released"), Result.Batch->GetOwnedComponentCount(), 0)`
   - `FRPGPreparationExclusiveTest:538`: `TestTrue(..., First.Batch->GetOwnedComponentCount() == 10 ...)`
   - `FRPGPreparationLifetimeTest:751`: `TestEqual(TEXT("the artifact owns nothing any more"), Result.Batch->GetOwnedComponentCount(), 0)`
   - `FRPGPreparationLifetimeTest:778`: `TestTrue(..., Result.Batch->GetOwnedComponentCount() == 10)`
3. **`RPGBossWorldPreparationTests.cpp`:**
   - Line 557: `TestTrue(TEXT("the artifact reports prepared and leases ten components"), Batch.GetOwnedComponentCount() == 10)`
   - `FRPGWorldPreparationSecondTest:849, 861`: `TestTrue(..., First.Batch->GetOwnedComponentCount() == 10)`
   - `FRPGWorldPreparationRefusalsTest:926`: `TestTrue(..., Control.Batch->GetOwnedComponentCount() == 10)`
4. **Adapter Tests:**
   - `RPGBossEncounterClusterAdaptersTests.cpp:231-234`: asserts `Plan.RequiredFields == 3`.
   - `RPGBossDormantWakeAdaptersTests.cpp:296`: asserts `Plan.RequiredFields == 2`.
   - `RPGBossBleedAdaptersTests.cpp:314`: asserts `Plan.RequiredFields == 7`.
   - `RPGBossHealPunishAdaptersTests.cpp:248`: asserts `Plan.RequiredFields == 14`.

---

## 2. Wiring Analysis for Each Unwired Plan

Each of the five unwired plans already has a fully implemented `Make*Plan()` factory:

### 2.1 Specification of the Unwired Plans

| Component | Class | Instance Name | Factory Citation | Required Fields Count |
| :--- | :--- | :--- | :--- | :--- |
| **Bleed** | `URPGBossBleed` | `TEXT("RPGBossBleed")` | `RPGBossBleedAdapters.cpp:331` | **7 fields** (`InitialThreshold`, `ThresholdIncrease`, `ThresholdMax`, `HpFraction`, `EffectHeight`, `ProcEffect`, `ProcSound`) |
| **LowSweep** | `URPGBossLowSweep` | `TEXT("RPGBossLowSweep")` | `RPGBossLowSweepAdapters.cpp:241` | **8 fields** (`bEnabled`, `MoveId`, `Damage`, `Reach`, `InnerRadius`, `BladeHeight`, `SweepFromDegrees`, `SweepToDegrees`) |
| **Shockwave** | `URPGBossShockwave` | `TEXT("RPGBossShockwave")` | `RPGBossShockwaveAdapters.cpp:241` | **7 fields** (`bEnabled`, `MoveId`, `Damage`, `StartRadius`, `MaxRadius`, `Speed`, `Thickness`) |
| **HealPunish** | `URPGBossHealPunish` | `TEXT("RPGBossHealPunish")` | `RPGBossHealPunishAdapters.cpp:240` | **14 fields** (`bEnabled`, `MinRange`, `MaxRange`, `Cooldown`, `Damage`, `FlightTime`, `MinSpeed`, `MaxSpeed`, `JavelinRadius`, `JavelinMaxRange`, `SpawnSockets`, `AimHeight`, `bRespondToHeal`, `bCancelJavelinsOnInterrupt`) |
| **Look** | `URPGBossLook` | `TEXT("RPGBossLook")` | `RPGBossLookAdapters.cpp:244` | **5 fields** (`bEnabled`, `Body`, `Pieces`, `Sword`, `SwordSocket`) |

### 2.2 Exact Insertion Points Required

To wire all 5 components into hydration and preparation:
1. **`Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp`:**
   - `#include` adapter and component headers:
     - `RPGBossBleedAdapters.h`, `RPGBossBleed.h`
     - `RPGBossLowSweepAdapters.h`, `RPGBossLowSweep.h`
     - `RPGBossShockwaveAdapters.h`, `RPGBossShockwave.h`
     - `RPGBossHealPunishAdapters.h`, `RPGBossHealPunish.h`
     - `RPGBossLookAdapters.h`, `RPGBossLook.h`
   - `BossCorePlanCount`: increment from `5` to `10` (`RPGBossHydrationPreflight.cpp:61`).
   - `MakeBossCorePlans(FName SelectedPhaseId)` (`:65-74`): append:
     ```cpp
     Plans.Add(RPGBossBleedAdapters::MakeBleedPlan());
     Plans.Add(RPGBossLowSweepAdapters::MakeLowSweepPlan());
     Plans.Add(RPGBossShockwaveAdapters::MakeShockwavePlan());
     Plans.Add(RPGBossHealPunishAdapters::MakeHealPunishPlan());
     Plans.Add(RPGBossLookAdapters::MakeLookPlan());
     ```
   - `ManagedCoreConsumerClasses()` (`:143-146`): append the 5 component classes:
     ```cpp
     URPGBossBleed::StaticClass(),
     URPGBossLowSweep::StaticClass(),
     URPGBossShockwave::StaticClass(),
     URPGBossHealPunish::StaticClass(),
     URPGBossLook::StaticClass()
     ```
     *(Expands consumer array from 6 to 11 classes, ensuring `Preflight.PreexistingConsumer` guards all 10 boss-core components).*
   - `CompilePreflight` (`:356-378`): append cluster/domain validation calls:
     ```cpp
     if (!RPGBossBleedAdapters::ValidateBleed(Config->Bleed, Error))
     {
         FailMember(Result, TEXT("Preflight.BleedRejected"), Label, Error);
     }
     if (!RPGBossLowSweepAdapters::ValidateLowSweep(Config->LowSweep, Error))
     {
         FailMember(Result, TEXT("Preflight.LowSweepRejected"), Label, Error);
     }
     if (!RPGBossShockwaveAdapters::ValidateShockwave(Config->Shockwave, Error))
     {
         FailMember(Result, TEXT("Preflight.ShockwaveRejected"), Label, Error);
     }
     if (!RPGBossHealPunishAdapters::ValidateHealPunish(Config->HealPunish, Error))
     {
         FailMember(Result, TEXT("Preflight.HealPunishRejected"), Label, Error);
     }
     if (!RPGBossLookAdapters::ValidateLook(Config->Look, Error))
     {
         FailMember(Result, TEXT("Preflight.LookRejected"), Label, Error);
     }
     ```
2. **`Source/OneBossFight/Player/RPGBossHydrationPreflight.h`:**
   - Update documentation comments referencing "five combined native plans" (`:18`, `:51`, `:87`) to reflect the expanded plan set.

### 2.3 Impact on Existing Tests

#### What WOULD Change:
1. **Plan & Class Lease Counts:**
   - `Boss.Plans.Num()` and `Boss.ClassLeases.Num()` change from `5` to `10` in `FRPGPreflightValidTest` (:376, :399, :407), `FRPGPreflightTargetsTest` (:831, :852), `FRPGPreflightExpandedTest` (:1035, :1087), and `FRPGPreflightConsumersTest` (:1282).
2. **Required Manifest Path Counts:**
   - Required manifest paths expand from **51 to 92 paths** (51 existing + 7 Bleed + 8 LowSweep + 7 Shockwave + 14 HealPunish + 5 Look = 92).
   - In `RPGBossHydrationPreflightTests.cpp`:
     - Literal list `AllRequiredPaths` (:76) must add the 41 new field literals.
     - `Required.Num() == 51` (:394) becomes `92`.
     - `SumOfRequired == 51` (:1064) becomes `92`.
     - `ExpectedPaths.Num() == 51 && Union.Num() == 51` (:1064) becomes `92`.
3. **Owned Component Counts in Preparation & World Preparation Tests:**
   - In `RPGBossHydrationPreparationTests.cpp` and `RPGBossWorldPreparationTests.cpp`, the test fixture uses an encounter with 2 boss-core participants.
   - Currently: $2 \times 5 = 10$ owned components.
   - With 10 plans: $2 \times 10 = \mathbf{20}$ **owned components**.
   - Assertions in `Batch.GetOwnedComponentCount() == 10` (at `RPGBossHydrationPreparationTests:330, :538, :778` and `RPGBossWorldPreparationTests:557, :849, :861, :926`) change from `10` to `20`.
4. **Consumer Class Counts:**
   - Tests asserting `ManagedCoreConsumerClasses().Num() == 6` expand to `11`.
5. **Preflight Failure Tokens:**
   - Introduction of 5 new diagnostic tokens: `Preflight.BleedRejected`, `Preflight.LowSweepRejected`, `Preflight.ShockwaveRejected`, `Preflight.HealPunishRejected`, `Preflight.LookRejected`.

#### What would NOT Change:
1. **`CompileParticipantImpl` in `RPGEncounterBinding.cpp:30-136`:**
   - Already calls `ValidateBleed`, `ValidateLowSweep`, `ValidateShockwave`, `ValidateHealPunish`, `ValidateLook` (:62-77).
   - Already populates all 5 struct members on `FRPGParticipantConfig` (:116-120).
   - Needs **zero lines of code changes**.
2. **`RPGBossHydrationPreparation.cpp` Allocation & Configuration Engine:**
   - `Allocate` and `Configure` loops iterate generically over `Participant.Plans` (:155, :196).
   - Needs **zero lines of code changes**.
3. **`RPGBossWorldPreparation.cpp` & `RPGBossPreparationRegistry.cpp`:**
   - Facade and registry compose input compilation and batch preparation generically.
   - Conflict checking, token issuance, quarantine mechanics, and abort cleanup need **zero lines of code changes**.
4. **Target-Only Participants:**
   - Target-only participants continue receiving zero plans, zero class leases, and zero components.

---

## 3. Hazards Proven from Code

### 3.1 Ordering Dependencies Between Plans

1. **`RPGBossLook` Mesh Swap vs. Mesh/Socket Consumers:**
   - *Code Fact:* In `Source/OneBossFight/Player/RPGBossLook.cpp:26-32`, `BeginPlay()` schedules mesh application on the **next tick** via `GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateUObject(this, &URPGBossLook::Apply))`.
   - *Code Fact:* In `Source/OneBossFight/Player/RPGBossLook.cpp:52-88`, `Apply()` swaps the skeletal mesh (`Boss->GetMesh()->SetSkeletalMeshAsset(BodyMesh)`), attaches modular piece meshes (`Crown`, `Mantle`, `BrazierGauntlet`), and attaches `Sword` to `SwordSocket` (`HeavySwordSocket_R`).
   - *Hazard:* `RPGBossHealPunish::GetSpawnLocation` ([`RPGBossHealPunish.cpp:36-50`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp#L36-L50)) inspects `Mesh->DoesSocketExist(Socket)`. If `HealPunish` is initialized or triggered before tick 1, it queries the un-swapped mesh, potentially missing the socket and falling back to offset actor coordinates (:50).
   - *Hazard:* In `RPGBossDamage::FeetZ` ([`RPGBossLowSweep.cpp:43`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.cpp#L43) and [`RPGBossShockwave.cpp:39`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp#L39)), height calculations query the boss mesh capsule and transform. Swapping meshes at tick 1 rather than during hydration creates a 1-frame discrepancy in collision bounds and socket locations.
2. **`RPGBossDormantWake` vs. `RPGBossEncounter` Dependency:**
   - *Code Fact:* In `Source/OneBossFight/Player/RPGBossDormantWake.cpp:42-49`, `BeginPlay()` queries `Actor->FindComponentByClass<URPGBossEncounter>()`, sets `AddTickPrerequisiteComponent(Encounter)`, and inspects `Encounter->IsDormant()`.
   - *Hazard:* If `RPGBossEncounter` is not prepared or is configured after `DormantWake`, `DormantWake` fails to establish its tick prerequisite and skips `BeginDormant()`, allowing the boss to bypass its dormant idle state.
3. **`RPGBossLowSweep` & `RPGBossShockwave` Dependency on `URPGAttackTracker`:**
   - *Code Fact:* In `RPGBossLowSweep.cpp:30` and `RPGBossShockwave.cpp:34`, both components attempt to find `URPGAttackTracker` on their owner actor.
   - *Hazard:* `URPGAttackTracker` is **neither in the 5 wired plans nor in the 5 unwired plans**. It is a legacy component attached exclusively by `RPGPlayerMovesSubsystem.cpp:199`. In a pure hydrated environment where legacy attachments are suppressed, `StartForTest` and attack tracking would fail completely unless `URPGAttackTracker` is also wired or provided.
4. **`RPGBossBleed` vs. `RPGBossEncounter` / `RPGBossPhases` Interaction:**
   - *Code Fact:* `RPGBossBleed.cpp:5-7` includes `RPGBossEncounter.h`, `RPGBossPhases.h`, and `RPGBossStagger.h`. In `ApplyBleed` (:88-115), Bleed queries `URPGBossEncounter` to inflict health damage.
   - *Hazard:* If `Encounter` is destroyed or absent, Bleed procs cannot modify boss health.

### 3.2 Components That Exist on the Boss Actor Only for Some Definitions

1. **Authored Disabling (`bEnabled = false`):**
   - *Code Fact:* Four of the five unwired configs contain a `bEnabled` boolean flag: `LowSweep.bEnabled`, `Shockwave.bEnabled`, `HealPunish.bEnabled`, `Look.bEnabled`.
   - *Code Fact:* In `RPGBossLowSweepAdapters.cpp:241` and `RPGBossShockwaveAdapters.cpp:241`, `Plan.RequiredFields` explicitly requires `FieldEnabled`.
   - *Code Fact:* In `RPGBossLook.cpp:29`, if `bEnabled == false`, `Apply()` is never scheduled. In `RPGBossShockwave.cpp:32`, if `bEnabled == false`, `Launch()` exits immediately.
   - *Hazard:* If `MakeBossCorePlans` unconditionally builds plans for all 10 components, every boss actor will receive an allocated component instance for `LowSweep`, `Shockwave`, `HealPunish`, and `Look`, even if `bEnabled` is `false`. While the component remains inert, it consumes memory, UObject registrations, and tick evaluation unless conditionally omitted.
   - *Hazard:* If the preflight architecture requires a fixed `BossCorePlanCount`, it cannot support variable plan sets per definition without refactoring plan count checking.

### 3.3 Legacy Components Reading Constructor Defaults and Needing Suppression

1. **Where Legacy Attachments and Constructor Defaults Are Applied:**
   - *Code Citation:* `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:159-250` in `AttachLegacyBossBundle(AActor* Pawn)`.
   - When `IsPackBoss(Pawn)` evaluates true (`Pawn->GetClass()->GetName() == TEXT("BP_ExampleGreatSwordBoss_C")`), the subsystem creates and registers the following legacy components:
     - `URPGBossStagger` (`:161-164`)
     - `URPGBossPhases` (`:166-169`)
     - `URPGBossEncounter` (`:171-174`)
     - `URPGBossDormantWake` (`:176-178`)
     - `URPGBossPosture` (`:180-183`)
     - `URPGBossDeath` (`:185-187`)
     - `URPGBossLook` (`:189-191`)
     - `URPGBossBleed` (`:193-195`)
     - `URPGAttackTracker` (`:197-200`)
     - `URPGBossCloseClipSwap` (`:202-205`)
     - `URPGBossShockwave` (`:206-209`)
     - `URPGBossLowSweep` (`:211-214`)
     - `URPGBossHealPunish` (`:216-219`)
     - `URPGTraceGuard` (`:226`)
     - `URPGTraceAudit` (`:230`)
     - `URPGBossHud` (`:233`)
     - `URPGCombatDebug` (`:238`)
     - `URPGBossLegend` (`:244`)
2. **The Constructor Defaults That Apply If Not Prepared:**
   - `URPGBossBleed`: `InitialThreshold = 100.f`, `ProcEffect = NS_BulletHit_Med`, `ProcSound = A_Guardian_ImpactL_Cue` ([`RPGBossBleed.cpp:27-28`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossBleed.cpp#L27-L28)).
   - `URPGBossLowSweep`: `Damage = 20.f`, `SweepFromDegrees = 90.f` ([`RPGBossLowSweep.h:35, 52`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.h#L35)).
   - `URPGBossShockwave`: `Damage = 48.f`, `StartRadius = 200.f` ([`RPGBossShockwave.h:35, 40`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.h#L35)).
   - `URPGBossHealPunish`: `Damage = 12.f`, `MinRange = 400.f` ([`RPGBossHealPunish.h:35, 38`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.h#L35)).
   - `URPGBossLook`: `Body = SK_Boss01_Body`, `Pieces = Crown, Mantle, BrazierGauntlet`, `Sword = SM_Boss01_Greatsword` ([`RPGBossLook.cpp:17-23`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLook.cpp#L17-L23)).
3. **The Suppression Mechanism & Preexisting Consumer Conflict:**
   - *Code Fact:* In `RPGPlayerMovesSubsystem.cpp`, every attachment is guarded by `!Pawn->FindComponentByClass<T>()`.
   - If a component of that class already exists on `Pawn`, `AttachLegacyBossBundle` skips creating the legacy component.
   - *Hazard:* In `RPGBossHydrationPreflight.cpp:293-296`, preflight checks `Actor->FindComponentByClass(Managed[ClassIndex])`. If the actor already has the component before preflight, preflight fails with `Preflight.PreexistingConsumer`.
   - *Conclusion:* Preparation must occur strictly **BEFORE** `AttachLegacyBossBundle` runs (i.e. before `BeginPlay`). Once prepared, the components sit on the actor unregistered. When `AttachLegacyBossBundle` runs later at `BeginPlay`, its `!Pawn->FindComponentByClass<T>()` checks see the prepared components and correctly suppress the legacy constructor-default attachments.

### 3.4 CookCoverage and Epoch / Manifest Checks

1. **Manifest Integrity:**
   - In cooked builds (`#if !WITH_DEV_AUTOMATION_TESTS`), `bSyntheticFixture` is rejected with `Preflight.SyntheticUnavailable` ([`RPGBossHydrationPreflight.cpp:334-336`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L334-L336)).
   - Production assets must provide authentic `FRPGParityField` manifests in `URPGBossDefinition::Fields`.
   - If any of the 41 newly required unwired paths is missing from a cooked boss definition, `CompilePreflight` fails closed with `Preflight.MissingRequiredField`.
2. **Epoch Identity Check:**
   - In `RPGBossWorldPreparation.cpp:92-96`, the facade verifies that the epoch lease published by the world's game instance (`RPGCombatRegistry::ForWorld(World)`) is the exact same pointer as the compiled input's `ExpectedContent`.
   - In cooked packaging, if the game instance fails to publish the catalog epoch before world preparation runs, preparation fails with `WorldPrep.Drift`.

---

## 4. Unresolved Items the Code Does Not Answer

The following architectural and runtime questions are not answered by existing C++ source code:

1. **Encounter Coordinator & Invocation Site:**
   - *Code Fact:* `RPGBossWorldPreparation.h:20` explicitly states: *"Nothing in the project calls it: no spawn, startup or level hook, no UCLASS, no subsystem, no process-static world map."*
   - *Code Fact:* `RPGBossPreparationRegistry.h:18` states: *"there is no global registry, no subsystem, no process-static map and no automatic hook, and nothing here calls it."*
   - *Inference:* An authoritative gameplay coordinator (e.g. in `AOneBossFightGameModeBase`, an encounter subsystem, or level script) must be authored to instantiate the registry, call `PrepareWorldBatch`, and manage lease tokens. The exact lifecycle point where this coordinator will be invoked is currently unwritten.
2. **Component Registration Timing:**
   - *Code Fact:* `RPGBossHydrationPreparation` creates components with `NewObject` and configures them, but explicitly leaves them unregistered (`RegisterComponent()` is never called).
   - *Inference:* The architecture relies either on the actor's native deferred spawning completion (which automatically registers all owned components having `bAutoRegister = true`) or on an unwritten future `RegisterAll()` method. The exact trigger that transitions prepared components from unregistered to registered is not defined in code.
3. **AttackTracker Architecture:**
   - *Code Fact:* `RPGBossLowSweep` and `RPGBossShockwave` require `URPGAttackTracker` to resolve moves and execute attacks.
   - *Inference:* The codebase does not specify whether `URPGAttackTracker` will become a typed, authored component with its own plan and adapter (e.g. `FRPGAttackTrackerConfig`), or remain an un-profiled legacy component attached by `RPGPlayerMovesSubsystem`.
4. **Variable vs. Fixed Plan Sets for Boss Variants:**
   - *Code Fact:* Current preflight hardcodes `constexpr int32 BossCorePlanCount = 5;` and asserts that every `BossCore` participant receives all 5 plans.
   - *Inference:* If future boss definitions omit entire mechanics (e.g. a second boss that has no javelin throw or no low sweep), the current rigid plan count assertion would fail unless refactored to support conditional or definition-driven plan sets.
5. **CloseClipSwap (DD24) and Death (DD25) Integration Sequence:**
   - *Code Fact:* `URPGBossCloseClipSwap` is staged under `Codex/DD24/Staging` and `RPGBossDeath` is under review.
   - *Inference:* The code does not specify whether the 5 unwired components will be wired first in a batch of 10, or whether all 12 components (including DD24 CloseClipSwap and DD25 Death) will be wired together once their domains are accepted.

---

## 5. Verification Evidence & Hashes

### Active Directory File Inventory & Cryptographic Hashes

- `Docs/BossCombatReview/Execution/Antigravity/Wiring/WIRING_ANALYSIS.md`
- Receipt file: `Docs/BossCombatReview/Execution/Antigravity/Wiring/evidence_sha256.txt`

*(Hashes calculated upon file generation and recorded in receipt).*
