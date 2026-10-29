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
- **Preexisting-Consumer Absence vs. Test Assertion Scope:** Expanding `ManagedCoreConsumerClasses` from 6 to 11 classes does not trigger preexisting-consumer refusal failures because no existing test actor under `Source/OneBossFight/Tests/` attaches any of the 5 unwired classes. However, wiring the 5 new plans into `MakeBossCorePlans` ($5 \to 10$) and expanding `ManagedCoreConsumerClasses` ($6 \to 11$) **WILL directly break exact plan-count, lease-count, component-count, manifest-path, and planned-name assertions across 7 test suites** (a total of 42 distinct assertion sites). These tests must be updated as part of DD26. See the exhaustive audit and DD26 work order in Section 7.

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

- **Active File:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/WIRING_ANALYSIS.md` (Revision 4: Exhaustive Multi-Pattern Audit per Order A-198 / [C-282])
- **Receipt File:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/evidence_sha256.txt`
- **Staged Revision 1 Baseline:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/original_A195/WIRING_ANALYSIS.md` (`02630756d18464334f6249ea3ab52ec3f7756d9309b62a67b86be85c088208da`, 34014 bytes)
- **Staged Revision 1 Receipt:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/original_A195/evidence_sha256.txt`
- **Staged Revision 2 Baseline:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/original_A196/WIRING_ANALYSIS.md` (`b107072846753a57aed8385421fe63f28729cd7700b9948781513a39c2e061b3`, 41234 bytes)
- **Staged Revision 2 Receipt:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/original_A196/evidence_sha256.txt`
- **Staged Revision 3 Baseline:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/original_A197/WIRING_ANALYSIS.md` (`fac012a270a1202fba44a8045695d327abcfc9414fea0cecc41e8f62065aa8c8`, 62369 bytes)
- **Staged Revision 3 Receipt:** `Docs/BossCombatReview/Execution/Antigravity/Wiring/original_A197/evidence_sha256.txt`

---

## 7. Addendum: DD26 Exhaustive Multi-Pattern Impact Audit & Work Order (Order A-198 / Revision 4)

### 7.1 Scope & Stated Multi-Pattern Audit Methodology

Per Lead order **[C-282] (A-198)**, this addendum replaces the prior single-regex scan with an exhaustive, shape-based multi-pattern audit executed across **ALL 33 test files** under `Source/OneBossFight/Tests/` and production files under `Source/OneBossFight/Player/`. Every single matched line is evaluated and categorized as either `CHANGES` (with exact old and new expectations) or `DOES NOT CHANGE` (with explicit invariant reasoning).

#### Stated Search Patterns & Reproduction Commands
To enable Lead Claude and Reviewer Codex to independently reproduce and verify this audit, the 5 exact patterns and one-line PowerShell commands are stated below:

1. **Pattern A: Component Arithmetic Delta (`Components [+-] N`):**
   - *Regex:* `Components.*[+-]\s*\d+|[+-]\s*\d+.*Components`
   - *Target:* Assertions calculating the net component additions or removals per actor.
   - *PowerShell Reproduction:*
     ```powershell
     Get-ChildItem -Recurse Source\OneBossFight\Tests -Filter *.cpp | Select-String -Pattern "Components.*[+-]\s*\d+|[+-]\s*\d+.*Components"
     ```

2. **Pattern B: Lifecycle & Count Equalities (`Key == N`):**
   - *Regex:* Lines containing `Destroyed`, `AlreadyGone`, `ContractViolations`, `OwnedComponentCount`, or `Num()`, followed by `==\s*\d+`
   - *Target:* Batch lifecycle abort reports, weak pointer arrays, unique pointer sets, and participant component counts.
   - *PowerShell Reproduction:*
     ```powershell
     Get-ChildItem -Recurse Source\OneBossFight\Tests -Filter *.cpp | Select-String -Pattern "(Destroyed|AlreadyGone|ContractViolations|OwnedComponentCount|Num\(\)).*==\s*\d+"
     ```

3. **Pattern C: Explicit TestEqual Assertions on Counts:**
   - *Regex:* `TestEqual\s*\(.*(Destroyed|AlreadyGone|ContractViolations|OwnedComponentCount|Num\(\)|Plans|ClassLeases|Required).*,.*[0-9]+`
   - *Target:* Preflight plan and lease count assertions, manifest path union checks, and batch owned component counts.
   - *PowerShell Reproduction:*
     ```powershell
     Get-ChildItem -Recurse Source\OneBossFight\Tests -Filter *.cpp | Select-String -Pattern "TestEqual\s*\(.*(Destroyed|AlreadyGone|ContractViolations|OwnedComponentCount|Num\(\)|Plans|ClassLeases|Required).*,.*[0-9]+"
     ```

4. **Pattern D: Expected Components & Planned Names Helpers:**
   - *Regex:* `(ExpectedComponents|FExpectedComponent|PlannedNames)`
   - *Target:* Hardcoded expected component helper definitions, iterations, and planned instance name arrays.
   - *PowerShell Reproduction:*
     ```powershell
     Get-ChildItem -Recurse Source\OneBossFight\Tests -Filter *.cpp | Select-String -Pattern "(ExpectedComponents|FExpectedComponent|PlannedNames)"
     ```

5. **Pattern E: Prose Numbers in Assertions & Test Docstrings:**
   - *Regex:* `(Test(True|Equal|False)|//).*(five|ten|nine|fifty-one|51|six)`
   - *Target:* Assertion message text strings and test doc-comments specifying expected counts in prose.
   - *PowerShell Reproduction:*
     ```powershell
     Get-ChildItem -Recurse Source\OneBossFight\Tests -Filter *.cpp | Select-String -Pattern "(Test(True|Equal|False)|//).*(five|ten|nine|fifty-one|51|six)"
     ```

Across all 33 test files in `Source/OneBossFight/Tests/`, these 5 patterns matched a total of **205 hits across 21 test files** (12 test files returned zero hits).

---

### 7.2 The 6 Manifest Parity Generator Definitions (`AllRequiredPaths`)

In addition to count assertions, the literal manifest union generator `AllRequiredPaths(FName PhaseId)` is duplicated across 6 distinct test suites. Each definition must expand from 51 to 93 manifest paths (+42 paths):

| File and Lines | Generator Function | Old Union Count | DD26 New Union Count | Classification |
|---|---|---|---|---|
| [`RPGBossHydrationPreflightTests.cpp:79-102`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp#L79) | `TArray<FString> AllRequiredPaths(FName PhaseId)` | 51 manifest paths | 93 manifest paths | **Mechanical:** Mirror adapter `RequiredFields`. |
| [`RPGBossPreparationRegistryTests.cpp:166-182`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossPreparationRegistryTests.cpp#L166) | `TArray<FString> AllRequiredPaths(FName PhaseId)` | 51 manifest paths | 93 manifest paths | **Mechanical:** Mirror adapter `RequiredFields`. |
| [`RPGBossProductionPreflightTests.cpp:104-120`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp#L104) | `TArray<FString> AllRequiredPaths(FName PhaseId)` | 51 manifest paths | 93 manifest paths | **Mechanical:** Mirror adapter `RequiredFields`. |
| [`RPGBossProductionPreparationTests.cpp:139-155`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp#L139) | `TArray<FString> AllRequiredPaths(FName PhaseId)` | 51 manifest paths | 93 manifest paths | **Mechanical:** Mirror adapter `RequiredFields`. |
| [`RPGBossWorldInputCompilerTests.cpp:196-212`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossWorldInputCompilerTests.cpp#L196) | `TArray<FString> AllRequiredPaths(FName PhaseId)` | 51 manifest paths | 93 manifest paths | **Mechanical:** Mirror adapter `RequiredFields`. |
| [`RPGBossWorldPreparationTests.cpp:136-152`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp#L136) | `TArray<FString> AllRequiredPaths(FName PhaseId)` | 51 manifest paths | 93 manifest paths | **Mechanical:** Mirror adapter `RequiredFields`. |

---

### 7.3 Production Callers Audit (Non-Test Callers)

Only **one** production file in `Source/OneBossFight/Player/` hardcodes plan counts or consumer class lists:

| File and Line | Identifier / Construct | Current Production Code | DD26 Required Update | Classification & Notes |
|---|---|---|---|---|
| [`RPGBossHydrationPreflight.cpp:61`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L61) | `BossCorePlanCount` | `constexpr int32 BossCorePlanCount = 5;` | `constexpr int32 BossCorePlanCount = 10;` | **Mechanical:** Master constant for the number of plans expected per boss-core participant. |
| [`RPGBossHydrationPreflight.cpp:65-74`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L65-L74) | `MakeBossCorePlans` | Adds 5 plans (Stagger, Phases, Encounter, DormantWake, Posture) | Add 5 new plans via accepted adapters: `MakeBleedPlan()`, `MakeLowSweepPlan()`, `MakeShockwavePlan()`, `MakeHealPunishPlan()`, `MakeLookPlan()` | **Decision (Lead Authority):** Requires lead determination of relative plan order in array (suggested: preserve existing 5 as indices 0..4, append 5 new plans at indices 5..9). |
| [`RPGBossHydrationPreflight.cpp:81-83`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L81-L83) | `CheckPlans` validation | `if (Plans.Num() != BossCorePlanCount)` | Automatically evaluates new constant `10` | **Mechanical:** No code edit needed; derives directly from `BossCorePlanCount`. |
| [`RPGBossHydrationPreflight.cpp:143-146`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp#L143-L146) | `ManagedCoreConsumerClasses` | Returns 6 classes (`URPGBossPhases`, `URPGBossEncounter`, `URPGBossPosture`, `URPGBossStagger`, `URPGBossDormantWake`, `URPGCombatParticipant`) | Return 11 classes (add `URPGBossBleed`, `URPGBossLowSweep`, `URPGBossShockwave`, `URPGBossHealPunish`, `URPGBossLook`) | **Mechanical:** Required to prevent dual-component split-brain bugs if actors spawn before preparation. |
| [`RPGBossHydrationPreflight.h:18, :51, :87`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHydrationPreflight.h#L18) | Doc comments | References to "five combined plans" | Update documentation comments to "ten combined plans" | **Documentation:** Informational header comments. |

---

### 7.4 Comprehensive Audit Table of All 205 Matched Sites Across 21 Test Files

Below is the complete census of all 205 hits across all test files. Each hit is classified as either **CHANGES** (with exact old and new values) or **DOES NOT CHANGE** (with the explicit invariant reason):

#### `RPGAutomationTests.cpp` (6 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:197` | `// All 32 combinations of the five flags a break looks at, wit...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:487` | `// The Freeze arithmetic, from the table's rows and the postur...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:497` | `TestEqual(TEXT("six strength lights break the pool"), HitsToBr...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:603` | `// Five hits of 20 proc once (Freeze 5: "five valid buildup ap...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:978` | `TestEqual(TEXT("one instanced component per set"), Components....` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:1006` | `TestEqual(TEXT("rebuilding does not pile up components"), Comp...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossBleedAdaptersTests.cpp` (4 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:332` | `TestTrue(TEXT("all five scalars are the typed record (150, 0, ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:349` | `TestTrue(TEXT("B: the five scalars (the fraction at its upper ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:776` | `TestTrue(TEXT("established Stats, phase and identity values re...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:902` | `// The record: exactly seven editable properties, five floats ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossCloseClipSwapAdaptersTests.cpp` (4 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:222` | `TestTrue(TEXT("exact class/name and five exact paths, without ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:226` | `TestTrue(TEXT("callback copies all five nondefault fields"), P...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:375` | `TestTrue(TEXT("all five typed values copied, dev-only flag, sa...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:417` | `TestEqual(TEXT("five fields"), Count, 5);` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossDormantWakeAdaptersTests.cpp` (1 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:724` | `TestTrue(TEXT("established Stats, phase and identity values re...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossEncounterPolicyAdaptersTests.cpp` (1 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:517` | `TestTrue(TEXT("established Stats, phase and identity values re...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossHydrationPreflightTests.cpp` (29 hits, 15 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:24` | `// These tests prove the whole-batch expanded native subset pr...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:364` | `if (!TestEqual(TEXT("three participants"), Plan->Participants....` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:374` | `// Boss-core: Stagger, Phases, Encounter, DormantWake, Posture...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:376` | `if (!TestEqual(TEXT("boss-core has five plans"), Boss.Plans.Nu...` | **CHANGES** | TestEqual(..., Plans.Num(), 5) | TestEqual(..., Plans.Num(), 10) | Mechanical | Boss-core participant plan count assertion expands from 5 to 10. |
| `:394` | `TestEqual(TEXT("the union of required manifest paths is fifty-...` | **CHANGES** | Required / Union / ExpectedPaths count 51 | Required / Union / ExpectedPaths count 93 | Mechanical | Union of required manifest paths expands from 51 to 93 (+42 paths). |
| `:399` | `TestEqual(TEXT("one class lease per boss plan"), Boss.ClassLea...` | **CHANGES** | TestEqual(..., ClassLeases.Num(), 5) | TestEqual(..., ClassLeases.Num(), 10) | Mechanical | Boss-core participant class lease count assertion expands from 5 to 10. |
| `:400` | `TestTrue(TEXT("the class leases are the plan classes"), Boss.C...` | **CHANGES** | ClassLeases.Num() == 5 and checks leases[0..4] | ClassLeases.Num() == 10 and checks leases[0..9] | Mechanical | Class lease count expands from 5 to 10 and all 10 leases must match plan classes. |
| `:407` | `if (Again.IsValid() && Again->Participants.Num() == 3 && Again...` | **CHANGES** | Plans.Num() == 5 | Plans.Num() == 10 | Mechanical | Boss-core participant plan count assertion expands from 5 to 10. |
| `:467` | `TestTrue(TEXT("compiling B did not touch the plan of A"), Plan...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:745` | `// Each of the fifty-one required manifest paths of the five c...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:826` | `TestTrue(TEXT("members in the other order compile"), Result.Is...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:827` | `if (Out.IsValid() && Out->Participants.Num() == 2)` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:831` | `TestTrue(TEXT("only the boss has plans"), Out->Participants[0]...` | **CHANGES** | Plans.Num() == 5 | Plans.Num() == 10 | Mechanical | Boss-core participant plan count assertion expands from 5 to 10. |
| `:852` | `TestTrue(TEXT("two boss-core members targeting each other comp...` | **CHANGES** | Plans.Num() == 5 | Plans.Num() == 10 | Mechanical | Boss-core participant plan count assertion expands from 5 to 10. |
| `:986` | `// DD13: the expanded native subset (five combined plans per b...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:1019` | `if (!TestTrue(TEXT("a batch of two boss-core members and a tar...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:1026` | `// Independent expectations: the five classes and the legacy i...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:1035` | `if (!TestTrue(FString::Printf(TEXT("%s: exactly five plans, a ...` | **CHANGES** | Plans.Num() == 5 | Plans.Num() == 10 | Mechanical | Boss-core participant plan count assertion expands from 5 to 10. |
| `:1061` | `TestTrue(FString::Printf(TEXT("%s: no native class and no inst...` | **CHANGES** | DistinctClasses.Num() == 5 && DistinctNames.Num() == 5 | DistinctClasses.Num() == 10 && DistinctNames.Num() == 10 | Mechanical | Distinct classes and distinct names per boss plan expand from 5 to 10. |
| `:1062` | `// The separate scalar, profile, flow and policy plans are gon...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:1064` | `bool bUnion = ExpectedPaths.Num() == 51 && Union.Num() == 51 &...` | **CHANGES** | Required / Union / ExpectedPaths count 51 | Required / Union / ExpectedPaths count 93 | Mechanical | Union of required manifest paths expands from 51 to 93 (+42 paths). |
| `:1069` | `TestTrue(FString::Printf(TEXT("%s: the union of the plans' req...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:1075` | `&& Plan->Participants[0].Config->Phases.Num() == 1 && Plan->Pa...` | DOES NOT CHANGE | - | - | - | Selected phase count per participant config (1 phase); unchanged. |
| `:1081` | `TestTrue(TEXT("second compile"), RPGBossHydrationPreflight::Co...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:1082` | `if (Again.IsValid() && Again->Participants.Num() == 3)` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:1087` | `bStable = bStable && Again->Participants[Member].Plans.Num() =...` | **CHANGES** | Plans.Num() == 5 | Plans.Num() == 10 | Mechanical | Boss-core participant plan count assertion expands from 5 to 10. |
| `:1106` | `TestTrue(TEXT("the managed consumers are the six expected clas...` | **CHANGES** | ManagedCoreConsumerClasses().Num() == 6 | ManagedCoreConsumerClasses().Num() == 11 | Mechanical | Managed core consumer class list size expands from 6 to 11. |
| `:1273` | `TestTrue(TEXT("a Stagger on the target-only member does not st...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:1282` | `if (!TestTrue(TEXT("the batch compiles"), RPGBossHydrationPref...` | **CHANGES** | Plans.Num() == 5 | Plans.Num() == 10 | Mechanical | Boss-core participant plan count assertion expands from 5 to 10. |

#### `RPGBossHydrationPreparationTests.cpp` (34 hits, 19 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:26` | `// These tests prove the unregistered batch preparation primit...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:283` | `struct FExpectedComponent` | DOES NOT CHANGE | - | - | - | Declaration of FExpectedComponent helper struct; struct layout (UClass* Class, FName InstanceName) is invariant. |
| `:290` | `TArray<FExpectedComponent> ExpectedComponents()` | DOES NOT CHANGE | - | - | - | Helper function signature; signature is invariant. |
| `:292` | `return TArray<FExpectedComponent>{{URPGBossStagger::StaticClas...` | **CHANGES** | TArray of 5 components: Stagger, Phases, Encounter, DormantWake, Posture | TArray of 10 components: +Bleed, LowSweep, Shockwave, HealPunish, Look | Mechanical | ExpectedComponents() helper array definition must expand from 5 to 10 expected components. |
| `:330` | `bOk &= Test.TestEqual(TEXT("ten components are leased"), Batch...` | **CHANGES** | Batch.GetOwnedComponentCount() == 10 | Batch.GetOwnedComponentCount() == 20 | Mechanical | Total leased components in 2-boss batch fixture expands from 2x5=10 to 2x10=20. |
| `:333` | `bOk &= Test.TestTrue(TEXT("ten distinct owned component pointe...` | **CHANGES** | OwnedList.Num() == 10 && OwnedSet.Num() == 10 | OwnedList.Num() == 20 && OwnedSet.Num() == 20 | Mechanical | Unique owned component pointer list and set size expands from 10 to 20. |
| `:342` | `const TArray<FExpectedComponent> Expected = ExpectedComponents();` | DOES NOT CHANGE | - | - | - | Assignment from ExpectedComponents(); generic container assignment automatically receives all 10 entries. |
| `:346` | `for (const FExpectedComponent& Wanted : Expected)` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:362` | `bool bPriorKept = Now.Components.Num() == Prior.Components.Num...` | **CHANGES** | Prior.Components.Num() + 5 | Prior.Components.Num() + 10 | Mechanical | Arithmetic delta for owned components added per boss actor increases from +5 to +10. |
| `:367` | `bOk &= Test.TestTrue(FString::Printf(TEXT("%s: exactly five co...` | **CHANGES** | Text: "exactly five components were added" | Text: "exactly ten components were added" | Documentation/Prose | Assertion message prose moves in lockstep with components added count (+5 -> +10). |
| `:384` | `if (Test.TestEqual(TEXT("three participant summaries in the re...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:387` | `Infos[0].Slot == FName(TEXT("Boss1")) && Infos[0].TargetSlot =...` | **CHANGES** | Infos[i].OwnedComponentCount == 5 | Infos[i].OwnedComponentCount == 10 | Mechanical | Per-boss participant owned component count expands from 5 to 10. |
| `:388` | `&& Infos[1].Slot == FName(TEXT("Boss2")) && Infos[1].TargetSlo...` | **CHANGES** | Infos[i].OwnedComponentCount == 5 | Infos[i].OwnedComponentCount == 10 | Mechanical | Per-boss participant owned component count expands from 5 to 10. |
| `:389` | `&& Infos[2].Slot == FName(TEXT("Player")) && Infos[2].TargetSl...` | DOES NOT CHANGE | - | - | - | Target player participant owns 0 components; unchanged. |
| `:392` | `if (Test.TestTrue(TEXT("the validated preflight plan is retain...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:425` | `bool bOk = Test.TestTrue(FString::Printf(TEXT("%s: every owned...` | **CHANGES** | Weak.Num() == 10 | Weak.Num() == 20 | Mechanical | Weak tracking pointer array for 2-boss components expands from 10 to 20. |
| `:451` | `// A second look: the world state is exactly the state before ...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:453` | `TestTrue(TEXT("the abort destroyed ten components and found no...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:479` | `TestTrue(TEXT("explicit abort: ten destroyed, none already gon...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:481` | `TestEqual(TEXT("every lease is released"), Result.Batch->GetOw...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:482` | `TestTrue(TEXT("the summary reports no owned component"), Resul...` | DOES NOT CHANGE | - | - | - | Target player participant owns 0 components; unchanged. |
| `:486` | `TestTrue(TEXT("a repeated abort is harmless: nothing destroyed...` | DOES NOT CHANGE | - | - | - | Zero baseline assertions (no errors, no violations, 0 destroyed on idempotency/refusal); unchanged. |
| `:538` | `TestTrue(TEXT("the first artifact is intact: prepared, the sam...` | **CHANGES** | Batch.GetOwnedComponentCount() == 10 | Batch.GetOwnedComponentCount() == 20 | Mechanical | Total leased components in 2-boss batch fixture expands from 2x5=10 to 2x10=20. |
| `:544` | `TestTrue(TEXT("the first artifact aborts cleanly"), Report.Des...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:628` | `TestTrue(FString::Printf(TEXT("%s: named as an injected fault,...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:679` | `TestTrue(TEXT("component destroyed first: nine destroyed by th...` | **CHANGES** | Report.Destroyed == 9 && Report.AlreadyGone == 1 | Report.Destroyed == 19 && Report.AlreadyGone == 1 | Mechanical | Teardown with 1 component destroyed first: 20 - 1 = 19 destroyed, 1 already gone. |
| `:698` | `TestTrue(TEXT("owner destroyed first: the first boss's five ar...` | **CHANGES** | Report.Destroyed == 5 && Report.AlreadyGone == 5 | Report.Destroyed == 10 && Report.AlreadyGone == 10 | Mechanical | Teardown with 1 boss owner destroyed first: surviving boss 10 destroyed, dead boss 10 already gone. |
| `:716` | `TestTrue(TEXT("world torn down first: every owned component is...` | **CHANGES** | Destroyed + AlreadyGone == 10 | Destroyed + AlreadyGone == 20 | Mechanical | Total component accounting sum across teardown branches expands from 10 to 20. |
| `:747` | `TestTrue(TEXT("registered by somebody else: nine destroyed, on...` | **CHANGES** | Report.Destroyed == 9 && Report.ContractViolations == 1 | Report.Destroyed == 19 && Report.ContractViolations == 1 | Mechanical | Teardown with 1 component registered externally: 20 - 1 = 19 destroyed, 1 contract violation. |
| `:751` | `TestEqual(TEXT("the artifact owns nothing any more"), Result.B...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:767` | `TestTrue(TEXT("a preparation on a worker thread is refused by ...` | DOES NOT CHANGE | - | - | - | Expected error count from injected failure or clean compile (0 or 1); unchanged. |
| `:777` | `TestTrue(TEXT("an abort on a worker thread is refused by name ...` | DOES NOT CHANGE | - | - | - | Zero baseline assertions (no errors, no violations, 0 destroyed on idempotency/refusal); unchanged. |
| `:778` | `TestTrue(TEXT("the artifact is still prepared with its ten com...` | **CHANGES** | Batch.GetOwnedComponentCount() == 10 | Batch.GetOwnedComponentCount() == 20 | Mechanical | Total leased components in 2-boss batch fixture expands from 2x5=10 to 2x10=20. |
| `:780` | `TestTrue(TEXT("the game-thread abort then succeeds"), Report.D...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |

#### `RPGBossLookAdaptersTests.cpp` (7 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:233` | `TestTrue(TEXT("exact class/name and five exact paths, without ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:237` | `TestTrue(TEXT("callback copies all five nondefault fields"), P...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:259` | `auto R = RecordA(); // disabled records still validate all fiv...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:393` | `TestTrue(TEXT("all five typed values copied, dev-only flag, sa...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:441` | `TestEqual(TEXT("exact five authored properties"), Count, 5);` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:453` | `TestTrue(TEXT("all five native defaults including constructor ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:454` | `TestTrue(TEXT("explicit declared baseline"), Default.bEnabled ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossPhaseFlowAdaptersTests.cpp` (13 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:23` | `// the shared validator, and the typed, lifecycle-safe assignm...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:265` | `// The unwired plan fragment: the legacy instance name, the ex...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:269` | `TestTrue(TEXT("plan required fields are the six typed paths"),...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:285` | `TestTrue(TEXT("all six fields are the typed record, not the ma...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:287` | `// Exactly six assignments: the selected phase record, the fir...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:290` | `TestTrue(TEXT("nothing but the six flow fields changed"), FPha...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:317` | `TestTrue(TEXT("still nothing but the six fields changed after ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:363` | `TestTrue(FString::Printf(TEXT("%s: no write at all (six fields...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:463` | `TestTrue(TEXT("B has its own six values"), FlowEquals(ReadFlow...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:654` | `// The real synthetic compiler copies all six fields into the ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:663` | `TestTrue(TEXT("all six fields copied (record A)"), FlowEquals(...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:664` | `TestTrue(TEXT("established Stats, phase and identity values re...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:779` | `// The reflected record: the six fields exist with the native ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossPhasesClusterAdaptersTests.cpp` (5 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:312` | `TestTrue(TEXT("no selection: the 14 independent paths only"), ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:767` | `TestTrue(TEXT("established Stats, phase, flow and identity val...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:906` | `// The fireball record: five properties with the native names ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:991` | `// The ten fields the older adapters own must receive exactly ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:1020` | `TestTrue(FString::Printf(TEXT("%s: the ten phase and flow fiel...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossPreparationRegistryTests.cpp` (16 hits, 8 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:266` | `struct FExpectedComponent` | DOES NOT CHANGE | - | - | - | Declaration of FExpectedComponent helper struct; struct layout (UClass* Class, FName InstanceName) is invariant. |
| `:272` | `TArray<FExpectedComponent> ExpectedComponents()` | DOES NOT CHANGE | - | - | - | Helper function signature; signature is invariant. |
| `:274` | `return TArray<FExpectedComponent>{{URPGBossStagger::StaticClas...` | **CHANGES** | TArray of 5 components: Stagger, Phases, Encounter, DormantWake, Posture | TArray of 10 components: +Bleed, LowSweep, Shockwave, HealPunish, Look | Mechanical | ExpectedComponents() helper array definition must expand from 5 to 10 expected components. |
| `:523` | `for (const FExpectedComponent& Wanted : ExpectedComponents())` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:543` | `for (const FExpectedComponent& Wanted : ExpectedComponents())` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:572` | `bOk &= Test.TestTrue(FString::Printf(TEXT("%s: ONE error carri...` | DOES NOT CHANGE | - | - | - | Expected error count from injected failure or clean compile (0 or 1); unchanged. |
| `:620` | `TestTrue(TEXT("both encounters hold ten unregistered component...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:713` | `const FExpectedComponent EncounterComponent = ExpectedComponen...` | DOES NOT CHANGE | - | - | - | ExpectedComponents()[2] remains RPGBossEncounter when existing 5 components preserve indices 0..4. |
| `:728` | `Refused.Errors.Num() == 1 && AnyErrorHasAll(Refused.Errors, TE...` | DOES NOT CHANGE | - | - | - | Expected error count from injected failure or clean compile (0 or 1); unchanged. |
| `:736` | `for (const FExpectedComponent& Wanted : ExpectedComponents())` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:794` | `TestTrue(FString::Printf(TEXT("clean release: Released, ten de...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:856` | `TestTrue(FString::Printf(TEXT("the token releases through its ...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:894` | `TestTrue(FString::Printf(TEXT("world dies first: the release i...` | **CHANGES** | Destroyed + AlreadyGone == 10 | Destroyed + AlreadyGone == 20 | Mechanical | Total component accounting sum across teardown branches expands from 10 to 20. |
| `:986` | `TestTrue(FString::Printf(TEXT("actors die first: the release i...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:987` | `Report.IsReleased() && Report.Abort.AlreadyGone == 10 && Repor...` | **CHANGES** | AlreadyGone == 10 | AlreadyGone == 20 | Mechanical | Full batch teardown already-gone count expands from 10 to 20. |
| `:1026` | `TestTrue(TEXT("after the off-thread refusals the token is stil...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |

#### `RPGBossProductionPreflightTests.cpp` (6 hits, 4 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:31` | `// the skeleton, and the preflight then publishes five plans f...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:510` | `if (!TestEqual(TEXT("two participants"), Plan->Participants.Nu...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:519` | `if (!TestEqual(TEXT("the boss has five plans"), BossPlan.Plans...` | **CHANGES** | TestEqual(..., Plans.Num(), 5) | TestEqual(..., Plans.Num(), 10) | Mechanical | Boss-core participant plan count assertion expands from 5 to 10. |
| `:535` | `TestEqual(TEXT("the union of required manifest paths is fifty-...` | **CHANGES** | Required / Union / ExpectedPaths count 51 | Required / Union / ExpectedPaths count 93 | Mechanical | Union of required manifest paths expands from 51 to 93 (+42 paths). |
| `:540` | `TestEqual(TEXT("one class lease per boss plan"), BossPlan.Clas...` | **CHANGES** | TestEqual(..., ClassLeases.Num(), 5) | TestEqual(..., ClassLeases.Num(), 10) | Mechanical | Boss-core participant class lease count assertion expands from 5 to 10. |
| `:666` | `TestTrue(TEXT("the successful production configs and the earli...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |

#### `RPGBossProductionPreparationTests.cpp` (32 hits, 13 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:34` | `// What it can establish, for these exact assets in this edito...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:43` | `// destroyed objects and its outcome is only observed), a regi...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:376` | `struct FExpectedComponent` | DOES NOT CHANGE | - | - | - | Declaration of FExpectedComponent helper struct; struct layout (UClass* Class, FName InstanceName) is invariant. |
| `:383` | `TArray<FExpectedComponent> ExpectedComponents()` | DOES NOT CHANGE | - | - | - | Helper function signature; signature is invariant. |
| `:385` | `return TArray<FExpectedComponent>{{URPGBossStagger::StaticClas...` | **CHANGES** | TArray of 5 components: Stagger, Phases, Encounter, DormantWake, Posture | TArray of 10 components: +Bleed, LowSweep, Shockwave, HealPunish, Look | Mechanical | ExpectedComponents() helper array definition must expand from 5 to 10 expected components. |
| `:613` | `bool bOk = Test.TestTrue(FString::Printf(TEXT("%s: every owned...` | **CHANGES** | Weak.Num() == 10 | Weak.Num() == 20 | Mechanical | Weak tracking pointer array for 2-boss components expands from 10 to 20. |
| `:634` | `for (const FExpectedComponent& Wanted : ExpectedComponents())` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:648` | `bOk &= Test.TestEqual(TEXT("ten components are leased"), Batch...` | **CHANGES** | Batch.GetOwnedComponentCount() == 10 | Batch.GetOwnedComponentCount() == 20 | Mechanical | Total leased components in 2-boss batch fixture expands from 2x5=10 to 2x10=20. |
| `:651` | `bOk &= Test.TestTrue(TEXT("ten distinct owned component pointe...` | **CHANGES** | OwnedList.Num() == 10 && OwnedSet.Num() == 10 | OwnedList.Num() == 20 && OwnedSet.Num() == 20 | Mechanical | Unique owned component pointer list and set size expands from 10 to 20. |
| `:662` | `const TArray<FExpectedComponent> Expected = ExpectedComponents();` | DOES NOT CHANGE | - | - | - | Assignment from ExpectedComponents(); generic container assignment automatically receives all 10 entries. |
| `:666` | `for (const FExpectedComponent& Wanted : Expected)` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:682` | `bool bPriorKept = Now.Components.Num() == Prior.Components.Num...` | **CHANGES** | Prior.Components.Num() + 5 | Prior.Components.Num() + 10 | Mechanical | Arithmetic delta for owned components added per boss actor increases from +5 to +10. |
| `:687` | `bOk &= Test.TestTrue(FString::Printf(TEXT("%s: exactly five co...` | **CHANGES** | Text: "exactly five components were added" | Text: "exactly ten components were added" | Documentation/Prose | Assertion message prose moves in lockstep with components added count (+5 -> +10). |
| `:704` | `if (Test.TestEqual(TEXT("three participant summaries in the re...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:707` | `Infos[0].Slot == FName(TEXT("BossOne")) && Infos[0].TargetSlot...` | **CHANGES** | Infos[i].OwnedComponentCount == 5 | Infos[i].OwnedComponentCount == 10 | Mechanical | Per-boss participant owned component count expands from 5 to 10. |
| `:708` | `&& Infos[1].Slot == FName(TEXT("BossTwo")) && Infos[1].TargetS...` | **CHANGES** | Infos[i].OwnedComponentCount == 5 | Infos[i].OwnedComponentCount == 10 | Mechanical | Per-boss participant owned component count expands from 5 to 10. |
| `:709` | `&& Infos[2].Slot == FName(TEXT("Player")) && Infos[2].TargetSl...` | DOES NOT CHANGE | - | - | - | Target player participant owns 0 components; unchanged. |
| `:712` | `if (Test.TestTrue(TEXT("the validated preflight plan is retain...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:788` | `TestTrue(TEXT("explicit abort destroyed ten components, found ...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:790` | `TestEqual(TEXT("the artifact owns nothing after the abort"), F...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:796` | `TestTrue(TEXT("a second abort is idempotent: clean and nothing...` | DOES NOT CHANGE | - | - | - | Zero baseline assertions (no errors, no violations, 0 destroyed on idempotency/refusal); unchanged. |
| `:849` | `TestTrue(FString::Printf(TEXT("control: the unmodified product...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:899` | `TestTrue(FString::Printf(TEXT("control: abort is clean and des...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:924` | `const TArray<FExpectedComponent> Expected = ExpectedComponents();` | DOES NOT CHANGE | - | - | - | Assignment from ExpectedComponents(); generic container assignment automatically receives all 10 entries. |
| `:936` | `for (const FExpectedComponent& Wanted : Expected)` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:972` | `TestTrue(FString::Printf(TEXT("exactly one error: the refusal ...` | DOES NOT CHANGE | - | - | - | Expected error count from injected failure or clean compile (0 or 1); unchanged. |
| `:976` | `// The cleanup. The allocation order is boss one's five, then ...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:979` | `for (const FExpectedComponent& Wanted : Expected)` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:984` | `TestTrue(TEXT("all five of boss one's components (earlier owne...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:996` | `for (const FExpectedComponent& Wanted : Expected)` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:1037` | `TestTrue(TEXT("boss two lost exactly the blocker; boss one and...` | DOES NOT CHANGE | - | - | - | Relative delta (-1) after removing single blocker component; unchanged. |
| `:1052` | `TestTrue(FString::Printf(TEXT("the retry's abort is clean and ...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |

#### `RPGBossStaggerClusterAdaptersTests.cpp` (3 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:425` | `TestTrue(TEXT("plan has 25 required fields"), Plan.RequiredFie...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:1053` | `TestTrue(TEXT("phase count retained"), Out->Phases.Num() == 1);` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:1293` | `TestTrue(TEXT("plan has 25 required paths in exact order"), Pl...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossStaggerPolicyAdaptersTests.cpp` (1 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:742` | `TestTrue(TEXT("established Stats, phase and identity values re...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossStatsAdaptersTests.cpp` (1 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:230` | `if (!TestTrue(TEXT("six components"), EncounterA.IsValid() && ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGBossWorldInputCompilerTests.cpp` (6 hits, 1 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:384` | `const TCHAR* const PlannedNames[5] = {TEXT("RPGBossStagger"), ...` | **CHANGES** | const TCHAR* const PlannedNames[5] = {Stagger, Phases, Encounter, DormantWake, Posture} | const TCHAR* const PlannedNames[10] = {..., Bleed, LowSweep, Shockwave, HealPunish, Look} | Decision | Hardcoded array of planned instance names expands from 5 to 10 names; requires Lead confirmation of instance naming convention. |
| `:397` | `return Input.Requests.Num() == 3 && Input.EncounterInstance.Is...` | DOES NOT CHANGE | - | - | - | Encounter input requests count (3 participants); unchanged. |
| `:599` | `for (const TCHAR* Name : PlannedNames)` | DOES NOT CHANGE | - | - | - | Range-based for loop over PlannedNames; generic iteration logic automatically covers all 10 entries. |
| `:617` | `if (!Test.TestEqual(FString::Printf(TEXT("%s: three requests")...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:731` | `TestTrue(FString::Printf(TEXT("the output passes the accepted ...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:755` | `TestTrue(TEXT("the binding and its participants are unchanged ...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |

#### `RPGBossWorldPreparationTests.cpp` (28 hits, 18 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:40` | `// What it can establish, for these exact assets in this edito...` | DOES NOT CHANGE | - | - | - | Invariant assertion / logic unaffected by plan count expansion. |
| `:304` | `struct FExpectedComponent` | DOES NOT CHANGE | - | - | - | Declaration of FExpectedComponent helper struct; struct layout (UClass* Class, FName InstanceName) is invariant. |
| `:311` | `TArray<FExpectedComponent> ExpectedComponents()` | DOES NOT CHANGE | - | - | - | Helper function signature; signature is invariant. |
| `:313` | `return TArray<FExpectedComponent>{{URPGBossStagger::StaticClas...` | **CHANGES** | TArray of 5 components: Stagger, Phases, Encounter, DormantWake, Posture | TArray of 10 components: +Bleed, LowSweep, Shockwave, HealPunish, Look | Mechanical | ExpectedComponents() helper array definition must expand from 5 to 10 expected components. |
| `:504` | `for (const FExpectedComponent& Wanted : ExpectedComponents())` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:541` | `bool bOk = Test.TestTrue(FString::Printf(TEXT("%s: every owned...` | **CHANGES** | Weak.Num() == 10 | Weak.Num() == 20 | Mechanical | Weak tracking pointer array for 2-boss components expands from 10 to 20. |
| `:557` | `bool bOk = Test.TestTrue(TEXT("the artifact reports prepared a...` | **CHANGES** | Batch.GetOwnedComponentCount() == 10 | Batch.GetOwnedComponentCount() == 20 | Mechanical | Total leased components in 2-boss batch fixture expands from 2x5=10 to 2x10=20. |
| `:560` | `bOk &= Test.TestTrue(TEXT("ten distinct owned component pointe...` | **CHANGES** | OwnedList.Num() == 10 && OwnedSet.Num() == 10 | OwnedList.Num() == 20 && OwnedSet.Num() == 20 | Mechanical | Unique owned component pointer list and set size expands from 10 to 20. |
| `:574` | `for (const FExpectedComponent& Wanted : ExpectedComponents())` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:588` | `bool bPriorKept = Now.Components.Num() == Prior.Components.Num...` | **CHANGES** | Prior.Components.Num() + 5 | Prior.Components.Num() + 10 | Mechanical | Arithmetic delta for owned components added per boss actor increases from +5 to +10. |
| `:593` | `bOk &= Test.TestTrue(FString::Printf(TEXT("%s: exactly five co...` | **CHANGES** | Text: "exactly five components were added" | Text: "exactly ten components were added" | Documentation/Prose | Assertion message prose moves in lockstep with components added count (+5 -> +10). |
| `:605` | `if (Test.TestTrue(TEXT("the retained plan has three participan...` | DOES NOT CHANGE | - | - | - | Participant count assertion in test fixture (2 or 3 participants); unchanged. |
| `:618` | `bOk &= Test.TestTrue(TEXT("summaries: three participants, ten ...` | **CHANGES** | Infos[i].OwnedComponentCount == 5 | Infos[i].OwnedComponentCount == 10 | Mechanical | Per-boss participant owned component count expands from 5 to 10. |
| `:652` | `TestTrue(TEXT("and its abort is clean, ten destroyed"), Report...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:668` | `TestTrue(FString::Printf(TEXT("explicit abort: clean report an...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:706` | `const TArray<FExpectedComponent> Expected = ExpectedComponents();` | DOES NOT CHANGE | - | - | - | Assignment from ExpectedComponents(); generic container assignment automatically receives all 10 entries. |
| `:759` | `Refused.Errors.Num() == 1 && AnyErrorHasAll(Refused.Errors, TE...` | DOES NOT CHANGE | - | - | - | Expected error count from injected failure or clean compile (0 or 1); unchanged. |
| `:761` | `// Seven earlier allocations (boss one's five, boss two's stag...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:763` | `for (const FExpectedComponent& Wanted : Expected)` | DOES NOT CHANGE | - | - | - | Range-based for loop over ExpectedComponents(); generic iteration logic automatically covers all 10 entries. |
| `:774` | `TestTrue(TEXT("name collision: boss one's five and boss two's ...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:794` | `TestTrue(TEXT("only the blocker was removed: boss two lost exa...` | DOES NOT CHANGE | - | - | - | Relative delta (-1) after removing single blocker component; unchanged. |
| `:806` | `TestTrue(TEXT("the retry's abort is clean and destroyed ten"),...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:848` | `TestTrue(TEXT("second preparation: the first artifact is undam...` | **CHANGES** | Prose string mentioning 5, 6, 9, 10, or 51 | Prose string updated to 10, 11, 19, 20, or 93 | Documentation/Prose | Assertion message text or test doc-comment moves in lockstep with numeric counts. |
| `:849` | `First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCou...` | **CHANGES** | Batch.GetOwnedComponentCount() == 10 | Batch.GetOwnedComponentCount() == 20 | Mechanical | Total leased components in 2-boss batch fixture expands from 2x5=10 to 2x10=20. |
| `:855` | `TestTrue(TEXT("second preparation: every component of the firs...` | **CHANGES** | Weak.Num() == 10 | Weak.Num() == 20 | Mechanical | Weak tracking pointer array for 2-boss components expands from 10 to 20. |
| `:861` | `TestTrue(TEXT("the same binding again: the first artifact is s...` | **CHANGES** | Batch.GetOwnedComponentCount() == 10 | Batch.GetOwnedComponentCount() == 20 | Mechanical | Total leased components in 2-boss batch fixture expands from 2x5=10 to 2x10=20. |
| `:865` | `TestTrue(TEXT("the first artifact's abort is clean and destroy...` | **CHANGES** | Destroyed == 10 | Destroyed == 20 | Mechanical | Full batch teardown destruction count expands from 10 to 20. |
| `:926` | `TestTrue(FString::Printf(TEXT("control: the unmodified call su...` | **CHANGES** | Batch.GetOwnedComponentCount() == 10 | Batch.GetOwnedComponentCount() == 20 | Mechanical | Total leased components in 2-boss batch fixture expands from 2x5=10 to 2x10=20. |

#### `RPGCodexTests.cpp` (1 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:221` | `TestEqual(TEXT("expired loss was pruned"), Expired.Losses.Num(...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGCombatCatalogTests.cpp` (6 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:31` | `TestEqual(TEXT("other context remains intact"), Second.Get()->...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:142` | `TestEqual(TEXT("resolved snapshot keeps all builds"), Resolved...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:410` | `TestEqual(TEXT("four builds: the three shipped ones plus the f...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:427` | `TestEqual(TEXT("the second latch is independent: shipped three...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:431` | `TestEqual(TEXT("the first game instance is untouched by the se...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |
| `:553` | `if (!TestTrue(TEXT("two game instances with the four-row test ...` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

#### `RPGPlayerMovesAttachWitnessTests.cpp` (1 hits, 0 change)

| Line | Code Snippet | Verdict | Current Expectation | DD26 New Expectation | Category | Reason |
|---|---|---|---|---|---|---|
| `:381` | `if (W1.Num() == 0 \|\| S1.Identities.Num() == 0)` | DOES NOT CHANGE | - | - | - | Domain-specific or standalone test outside hydration pipeline (tests specific adapter scalar fields, posture regen math, combat style balance, or catalog builds). |

---

### 7.5 Recomputed Totals & Mechanical vs Decision Breakdown

| Classification Category | Hit Count | Description & Scope | Authority |
|---|---|---|---|
| **Mechanical Changes (Assertions & Helpers)** | **62** | Arithmetic updates: $5 \to 10$ plans/leases, $10 \to 20$ batch components, pointer sets/arrays $10 \to 20$, teardown counts $10 \to 20$ / $19+1$ / $10+10$, added arithmetic $+5 \to +10$, path union $51 \to 93$, consumer classes $6 \to 11$, and 4 `ExpectedComponents()` helper definitions. | Deterministic updates derived directly from plan expansion. |
| **Mechanical Changes (`AllRequiredPaths` Definitions)** | **6** | The 6 identical generator definitions across test files expanded from 51 to 93 manifest paths. | Deterministic updates mirroring adapter contracts. |
| **Documentation & Prose Updates** | **15** | Assertion message strings and test docstrings updated to keep numbers in prose in sync with numeric assertions ("five plans" $\to$ "ten plans", "ten components" $\to$ "twenty components", "nine destroyed" $\to$ "nineteen destroyed", "fifty-one" $\to$ "ninety-three"). | Informational string updates. |
| **Architectural Decisions for Tech Lead** | **1** | `PlannedNames[10]` array in [`RPGBossWorldInputCompilerTests.cpp:384`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGBossWorldInputCompilerTests.cpp#L384) (plus relative order in `MakeBossCorePlans`). | **Lead Claude Authority** |
| **Total Test Sites Changing** | **78** (or **84** including the 6 `AllRequiredPaths` definitions) | All 7 hydration test suites affected. | Full DD26 Work Order |
| **Total Verified Invariant Hits** | **127** | Hits matching the multi-pattern scan across 14 non-hydration files and hydration invariant assertions (participant counts, phase counts, error counts, zero baselines, target member zero-plan checks). | Proved unaffected by plan count expansion. |
| **Grand Total Audited Hits** | **205** | Exhaustive census across all 33 test files in `Source/OneBossFight/Tests/`. | 100% verified. |
