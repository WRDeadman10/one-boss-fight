# Architecture & Pipeline Analysis: Boss Component Hydration & Wiring (Revision 2)
**Document:** `WIRING_ANALYSIS.md`  
**Revision:** Revision 2 (A-196, incorporating Tech Lead Claude review `[C-279]`)  
**Baseline Preservation:** Original Revision 1 preserved byte-for-byte under `original_A195/` (hash `02630756d184...`, 34014 bytes) with self-receipt  
**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Order Reference:** Tech Lead Claude `[C-278]`, `[C-279]`  
**Scope:** Offline Read-Only Analysis of Boss Component Hydration, Preparation, and Registry Wiring  
**Hygiene:** Pure C++ / Unreal Engine 5.5.4 offline source audit; 100% pure CRLF; zero engine processes; zero git operations  

---

## Revision 2 Changelog (Corrections per C-279 Review)

The following specific corrections have been incorporated from Tech Lead Claude's review `[C-279]`:
1. **Unwired Plan Line Citations Corrected:**
   - Corrected citations from test file lines to implementation adapter `.cpp` lines:
     - `RPGBossBleedAdapters.cpp`: `MakeBleedPlan` is at `:194-202`, `Plan.RequiredFields` at `:199-200`. (Was cited as `:331`). File length: 203 lines.
     - `RPGBossLowSweepAdapters.cpp`: `MakeLowSweepPlan` is at `:132-141`, `Plan.RequiredFields` at `:137-139`. (Was cited as `:241`). File length: 142 lines.
     - `RPGBossShockwaveAdapters.cpp`: `MakeShockwavePlan` is at `:105-114`, `Plan.RequiredFields` at `:110-111`. (Was cited as `:241`). File length: 115 lines.
     - `RPGBossHealPunishAdapters.cpp`: `MakeHealPunishPlan` is at `:201-209`, `Plan.RequiredFields` at `:206-207`. (Was cited as `:240`). File length: 210 lines.
     - `RPGBossLookAdapters.cpp`: `MakeLookPlan` is at `:177-185`, `Plan.RequiredFields` at `:182`. (Was cited as `:244`). File length: 186 lines.
2. **Shockwave Field Count & Total Path Arithmetic Corrected:**
   - Corrected `RPGBossShockwave` required field count from 7 to **8 fields** (`FieldEnabled`, `FieldMoveId`, `FieldDamage`, `FieldStartRadius`, `FieldMaxRadius`, `FieldSpeed`, `FieldThickness`, `FieldJumpClearance` at `RPGBossShockwaveAdapters.cpp:110-111`).
   - Corrected added unwired paths from 41 to **42 paths** ($7 + 8 + 8 + 14 + 5 = 42$).
   - Corrected total required field manifest union expansion from 92 to **93 unique paths** ($51 + 42 = 93$).
3. **`AllRequiredPaths` Declaration Citation Corrected:**
   - Corrected `AllRequiredPaths` declaration citation to `Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp:79` (was cited as `:76`, which is the start of its documentation comment).
4. **Code Hazards: Proof vs. Inference Strictly Demarcated:**
   - Explicitly demarcated `RPGBossLook.cpp:31` next-tick timer scheduling as a demonstrable code fact, while classifying the consequence of socket lookups in `HealPunish` and bounds evaluations in `LowSweep`/`Shockwave` as an **inference regarding call timing**.
   - Provided complete enumeration of all 18 legacy components attached in `RPGPlayerMovesSubsystem.cpp:139-250` with exact line citations, detailing the 5 components that the unwired plans would replace.
5. **Test Arithmetic for 2-Boss Fixture Explicitly Derived:**
   - Explicitly documented the $2 \text{ boss actors} \times 5 \text{ plans} = 10 \text{ components}$ arithmetic in `RPGBossHydrationPreparationTests.cpp:330` and `RPGBossWorldPreparationTests.cpp:557`, showing how the new expectation of $2 \times 10 = 20 \text{ components}$ holds if and only if `BossCorePlanCount` remains the sole unconditional driver of allocation.
6. **Lead Decisive Analysis Added:**
   - (a) Documented legacy absence requirements at preparation time, what occurs if both legacy and prepared components exist, and the split-brain hazard if unwired classes are omitted from `ManagedCoreConsumerClasses`.
   - (b) Audited all existing tests across `Source/OneBossFight/Tests/`, verifying that **zero tests** attach unwired components to preflight test actors, confirming that expanding `ManagedCoreConsumerClasses` will not break existing test suites.

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
- Each path is unique across the plans; no path is repeated across different plans except `FieldImmunityEffect` which is shared between Stagger and Phases dependencies and reconciled via set union.
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
   - Literal array `AllRequiredPaths` ([`RPGBossHydrationPreflightTests.cpp:79-135`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp#L79-L135)): lists exactly 51 path string literals.
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

### 2.1 Specification of the Unwired Plans

Each of the five unwired plans already has a fully implemented `Make*Plan()` factory in its respective adapter `.cpp` file:

| Component | Class | Instance Name | Factory Citation | Required Fields Citation | Required Fields Count |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bleed** | `URPGBossBleed` | `TEXT("RPGBossBleed")` | [`RPGBossBleedAdapters.cpp:194`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossBleedAdapters.cpp#L194) | [`:199-200`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossBleedAdapters.cpp#L199-L200) | **7 fields** (`InitialThreshold`, `ThresholdIncrease`, `ThresholdMax`, `HpFraction`, `EffectHeight`, `ProcEffect`, `ProcSound`) |
| **LowSweep** | `URPGBossLowSweep` | `TEXT("RPGBossLowSweep")` | [`RPGBossLowSweepAdapters.cpp:132`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweepAdapters.cpp#L132) | [`:137-139`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweepAdapters.cpp#L137-L139) | **8 fields** (`bEnabled`, `MoveId`, `Damage`, `Reach`, `InnerRadius`, `BladeHeight`, `SweepFromDegrees`, `SweepToDegrees`) |
| **Shockwave** | `URPGBossShockwave` | `TEXT("RPGBossShockwave")` | [`RPGBossShockwaveAdapters.cpp:105`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwaveAdapters.cpp#L105) | [`:110-111`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwaveAdapters.cpp#L110-L111) | **8 fields** (`bEnabled`, `MoveId`, `Damage`, `StartRadius`, `MaxRadius`, `Speed`, `Thickness`, `JumpClearance`) |
| **HealPunish** | `URPGBossHealPunish` | `TEXT("RPGBossHealPunish")` | [`RPGBossHealPunishAdapters.cpp:201`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunishAdapters.cpp#L201) | [`:206-207`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunishAdapters.cpp#L206-L207) | **14 fields** (`bEnabled`, `MinRange`, `MaxRange`, `Cooldown`, `Damage`, `FlightTime`, `MinSpeed`, `MaxSpeed`, `JavelinRadius`, `JavelinMaxRange`, `SpawnSockets`, `AimHeight`, `bRespondToHeal`, `bCancelJavelinsOnInterrupt`) |
| **Look** | `URPGBossLook` | `TEXT("RPGBossLook")` | [`RPGBossLookAdapters.cpp:177`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLookAdapters.cpp#L177) | [`:182`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLookAdapters.cpp#L182) | **5 fields** (`bEnabled`, `Body`, `Pieces`, `Sword`, `SwordSocket`) |

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
   - Required manifest paths expand from **51 to 93 paths**:
     $$\text{Added Paths} = 7 (\text{Bleed}) + 8 (\text{LowSweep}) + 8 (\text{Shockwave}) + 14 (\text{HealPunish}) + 5 (\text{Look}) = 42 \text{ paths}$$
     $$\text{New Union} = 51 + 42 = \mathbf{93} \text{ paths}$$
   - In `RPGBossHydrationPreflightTests.cpp`:
     - Literal list `AllRequiredPaths` ([`RPGBossHydrationPreflightTests.cpp:79`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp#L79)) must add the 42 new field literals.
     - `Required.Num() == 51` (:394) becomes `93`.
     - `SumOfRequired == 51` (:1064) becomes `93`.
     - `ExpectedPaths.Num() == 51 && Union.Num() == 51` (:1064) becomes `93`.
3. **Owned Component Counts in Preparation & World Preparation Tests:**
   - In `RPGBossHydrationPreparationTests.cpp:324-334` (`ExpectPrepared`) and `RPGBossWorldPreparationTests.cpp:556-560`, the test fixture uses an encounter with 2 boss-core participants and 1 target-only participant.
   - Target-only members receive 0 components.
   - Each boss-core member receives `BossCorePlanCount` components.
   - Exact Arithmetic:
     $$\text{Current} = 2 \text{ boss-core actors} \times 5 \text{ plans} = 10 \text{ components}$$
     $$\text{New} = 2 \text{ boss-core actors} \times 10 \text{ plans} = \mathbf{20} \text{ components}$$
   - Assertions in `Batch.GetOwnedComponentCount() == 10` (at `RPGBossHydrationPreparationTests:330, :538, :778` and `RPGBossWorldPreparationTests:557, :849, :861, :926`) change from `10` to `20`, provided that `BossCorePlanCount` remains the sole unconditional driver of allocation.
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

## 3. Hazards Proven from Code & Call-Path Analysis

### 3.1 Ordering Dependencies Between Plans

1. **`RPGBossLook` Next-Tick Mesh Swap:**
   - **Code Fact (Demonstrated):** In `Source/OneBossFight/Player/RPGBossLook.cpp:26-32`, `BeginPlay()` schedules mesh application on the **next tick** via `GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateUObject(this, &URPGBossLook::Apply))`.
   - **Code Fact (Demonstrated):** In `Source/OneBossFight/Player/RPGBossLook.cpp:52-88`, `Apply()` swaps the skeletal mesh (`Boss->GetMesh()->SetSkeletalMeshAsset(BodyMesh)`), attaches modular piece meshes (`Crown`, `Mantle`, `BrazierGauntlet`), and attaches `Sword` to `SwordSocket` (`HeavySwordSocket_R`).
   - **Call Path Analysis & Timing Inference:**
     - `RPGBossHealPunish::GetSpawnLocation` ([`RPGBossHealPunish.cpp:36-50`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp#L36-L50)) inspects `Mesh->DoesSocketExist(Socket)`. This method is called inside `FireJavelin` (`RPGBossHealPunish.cpp:88`), which is triggered by player heal callbacks or tests.
     - `RPGBossLowSweep::Begin` ([`RPGBossLowSweep.cpp:35-50`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.cpp#L35-L50)) evaluates `RPGBossDamage::FeetZ(Boss)` (`:43`). It is triggered by `URPGAttackTracker` move callbacks or `StartForTest`.
     - `RPGBossShockwave::Launch` ([`RPGBossShockwave.cpp:31-45`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp#L31-L45)) evaluates capsule bounds and ground location (`:39`). It is triggered by `URPGAttackTracker` move callbacks or `LaunchForTest`.
     - *Inference (Call Timing):* If any attack, javelin fire, or test execution occurs on tick 0 before the timer manager executes tick 1, the mesh and socket lookups will evaluate against the unswapped pack mesh (`BP_ExampleGreatSwordBoss_C`) rather than the authored `Body` mesh. If attacks only occur after tick 1 has elapsed, the mesh will have already been swapped. Swapping the mesh on tick 1 rather than during hydration creates a temporal window where geometry queries depend on game frame timing.
2. **`RPGBossDormantWake` vs. `RPGBossEncounter` Dependency:**
   - **Code Fact (Demonstrated):** In `Source/OneBossFight/Player/RPGBossDormantWake.cpp:42-49`, `BeginPlay()` queries `Actor->FindComponentByClass<URPGBossEncounter>()`, sets `AddTickPrerequisiteComponent(Encounter)`, and inspects `Encounter->IsDormant()`.
   - **Hazard:** If `RPGBossEncounter` is not prepared or is configured after `DormantWake`, `DormantWake` fails to establish its tick prerequisite and skips `BeginDormant()`, allowing the boss to bypass its dormant idle state.
3. **`RPGBossLowSweep` & `RPGBossShockwave` Dependency on `URPGAttackTracker`:**
   - **Code Fact (Demonstrated):** In `RPGBossLowSweep.cpp:30` and `RPGBossShockwave.cpp:34`, both components attempt to find `URPGAttackTracker` on their owner actor.
   - **Hazard:** `URPGAttackTracker` is **neither in the 5 wired plans nor in the 5 unwired plans**. It is a legacy component attached exclusively by `RPGPlayerMovesSubsystem.cpp:199`. In a pure hydrated environment where legacy attachments are suppressed, `StartForTest` and attack tracking would fail completely unless `URPGAttackTracker` is also wired or provided.
4. **`RPGBossBleed` vs. `URPGBossEncounter` / `URPGBossPhases` Interaction:**
   - **Code Fact (Demonstrated):** `RPGBossBleed.cpp:5-7` includes `RPGBossEncounter.h`, `RPGBossPhases.h`, and `RPGBossStagger.h`. In `ApplyBleed` (:88-115), Bleed queries `URPGBossEncounter` to inflict health damage.
   - **Hazard:** If `Encounter` is destroyed or absent, Bleed procs cannot modify boss health.

### 3.2 Components That Exist on the Boss Actor Only for Some Definitions

1. **Authored Disabling (`bEnabled = false`):**
   - **Code Fact (Demonstrated):** Four of the five unwired configs contain a `bEnabled` boolean flag: `LowSweep.bEnabled`, `Shockwave.bEnabled`, `HealPunish.bEnabled`, `Look.bEnabled`.
   - **Code Fact (Demonstrated):** In `RPGBossLowSweepAdapters.cpp:137` and `RPGBossShockwaveAdapters.cpp:110`, `Plan.RequiredFields` explicitly requires `FieldEnabled`.
   - **Code Fact (Demonstrated):** In `RPGBossLook.cpp:29`, if `bEnabled == false`, `Apply()` is never scheduled. In `RPGBossShockwave.cpp:32`, if `bEnabled == false`, `Launch()` exits immediately.
   - **Hazard:** If `MakeBossCorePlans` unconditionally builds plans for all 10 components, every boss actor will receive an allocated component instance for `LowSweep`, `Shockwave`, `HealPunish`, and `Look`, even if `bEnabled` is `false`. While the component remains inert, it consumes memory, UObject registrations, and tick evaluation unless conditionally omitted.
   - **Hazard:** If the preflight architecture requires a fixed `BossCorePlanCount`, it cannot support variable plan sets per definition without refactoring plan count checking.

### 3.3 Legacy Components Reading Constructor Defaults and Needing Suppression

1. **Complete Enumeration of Attached Legacy Components:**
   - In `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:139-250`, when `IsPackBoss(Pawn)` evaluates true (`Pawn->GetClass()->GetName() == TEXT("BP_ExampleGreatSwordBoss_C")`), the subsystem creates and registers the following **18 legacy components**:
     1. `URPGBossMusic` (`:144`, in `AttachLegacyBossPrelude`)
     2. `URPGBossStagger` (`:163`) — *Replaced by wired plan #1*
     3. `URPGBossPhases` (`:168`) — *Replaced by wired plan #2*
     4. `URPGBossEncounter` (`:173`) — *Replaced by wired plan #3*
     5. `URPGBossDormantWake` (`:178`) — *Replaced by wired plan #4*
     6. `URPGBossPosture` (`:182`) — *Replaced by wired plan #5*
     7. `URPGBossDeath` (`:187`) — *Pending DD25*
     8. `URPGBossLook` (`:191`) — **Replaced by unwired plan #5**
     9. `URPGBossBleed` (`:195`) — **Replaced by unwired plan #1**
     10. `URPGAttackTracker` (`:199`) — *Un-modeled coordinator*
     11. `URPGBossCloseClipSwap` (`:204`) — *Pending DD24*
     12. `URPGBossShockwave` (`:208`) — **Replaced by unwired plan #3**
     13. `URPGBossLowSweep` (`:213`) — **Replaced by unwired plan #2**
     14. `URPGBossHealPunish` (`:218`) — **Replaced by unwired plan #4**
     15. `URPGTraceGuard` (`:226`) — *Trace collision guard*
     16. `URPGTraceAudit` (`:230`) — *Trace overlap observer*
     17. `URPGBossHud` (`:235`) — *HUD coordinator*
     18. `URPGCombatDebug` (`:241`) — *Debug overlay*
     19. `URPGBossLegend` (`:247`) — *Post-fight sequence coordinator*
2. **The Constructor Defaults That Apply If Not Prepared:**
   - `URPGBossBleed`: `InitialThreshold = 100.f`, `ProcEffect = NS_BulletHit_Med`, `ProcSound = A_Guardian_ImpactL_Cue` ([`RPGBossBleed.cpp:27-28`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossBleed.cpp#L27-L28)).
   - `URPGBossLowSweep`: `Damage = 20.f`, `SweepFromDegrees = 90.f` ([`RPGBossLowSweep.h:35, 52`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.h#L35)).
   - `URPGBossShockwave`: `Damage = 48.f`, `StartRadius = 200.f` ([`RPGBossShockwave.h:35, 40`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.h#L35)).
   - `URPGBossHealPunish`: `Damage = 12.f`, `MinRange = 400.f` ([`RPGBossHealPunish.h:35, 38`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.h#L35)).
   - `URPGBossLook`: `Body = SK_Boss01_Body`, `Pieces = Crown, Mantle, BrazierGauntlet`, `Sword = SM_Boss01_Greatsword` ([`RPGBossLook.cpp:17-23`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLook.cpp#L17-L23)).

---

## 4. Decisive Pipeline & Test Findings for the Lead

### 4.1 Absence of Legacy Components at Preparation Time & Dual-Component Outcome

1. **Preflight Failure on Preexisting Components:**
   - In `RPGBossHydrationPreflight.cpp:289-297`, preflight iterates `ManagedCoreConsumerClasses()`. If `Actor->FindComponentByClass(Class)` is found on a boss-core actor, preflight fails closed immediately:
     `Preflight.PreexistingConsumer[slot=...]: the actor already has a <ClassName>`
   - Result: If any legacy component in `ManagedCoreConsumerClasses` is attached *prior* to preflight, preflight produces **zero plans** and preparation is blocked entirely.
2. **Proper Lifecycle Sequencing (Preparation Before BeginPlay):**
   - In the intended architecture, preparation runs *before* `BeginPlay` (before `AttachLegacyBossBundle`).
   - When `AttachLegacyBossBundle` runs subsequently at `BeginPlay` (`RPGPlayerMovesSubsystem.cpp:159-250`), every attachment statement contains:
     `if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<T>())`
   - Because `FindComponentByClass<T>()` successfully finds the prepared component, `AttachLegacyBossBundle` **skips creating the legacy component**, safely suppressing constructor defaults.
3. **Split-Brain Hazard if Unwired Classes Are Omitted from `ManagedCoreConsumerClasses`:**
   - If the five unwired classes are added to `MakeBossCorePlans` but *omitted* from `ManagedCoreConsumerClasses`:
   - If an actor was spawned and already ran `AttachLegacyBossBundle`, preflight would *not* detect the existing legacy component.
   - `RPGBossHydrationPreparation::PrepareBatch` would then call `NewObject<T>(Actor, ComponentPlan.Class, ComponentPlan.InstanceName)` ([`RPGBossHydrationPreparation.cpp:168`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp#L168)).
   - **Outcome:** The actor would hold **two concurrent live component instances of the same class** (e.g. two `URPGBossBleed` instances)—one running legacy constructor defaults and one running prepared authored values. Therefore, expanding `ManagedCoreConsumerClasses` in lockstep with `MakeBossCorePlans` is strictly required to prevent dual-component split-brain bugs.

### 4.2 Impact on Existing Test Fixtures

An exhaustive audit of all test sources under `Source/OneBossFight/Tests/` establishes the following:
- **Zero Preflight/Preparation Tests Attach Unwired Components:**
  - Neither `RPGBossHydrationPreflightTests.cpp`, `RPGBossHydrationPreparationTests.cpp`, `RPGBossWorldPreparationTests.cpp`, nor `RPGBossPreparationRegistryTests.cpp` attach `URPGBossBleed`, `URPGBossLowSweep`, `URPGBossShockwave`, `URPGBossHealPunish`, or `URPGBossLook` to their test actors.
  - Test fixtures in these suites instantiate bare actors via `World->SpawnActor<AActor>()` or mock characters (`USkeletalMeshComponent`) with only the 5 currently wired classes.
  - `FRPGPreflightConsumersTest` ([`RPGBossHydrationPreflightTests.cpp:1246`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp#L1246)) tests preexisting consumer refusals using only `URPGBossStagger::StaticClass()` and `URPGBossDormantWake::StaticClass()`.
- **Conclusion:** Expanding `ManagedCoreConsumerClasses` from 6 to 11 classes will **NOT cause any existing preflight, preparation, or registry test fixture to fail**.

---

## 5. Unresolved Items the Code Does Not Answer

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

## 6. Verification Evidence & Receipts

- **Active File:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/WIRING_ANALYSIS.md`
- **Receipt File:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/evidence_sha256.txt`
- **Staged Baseline:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/original_A195/WIRING_ANALYSIS.md`
- **Baseline Receipt:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/original_A195/evidence_sha256.txt`
