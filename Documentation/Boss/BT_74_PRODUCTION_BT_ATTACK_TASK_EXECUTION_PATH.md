# BT-74: Map Production BehaviorTree Attack-Task Execution Path

- **Date:** 2026-11-17
- **Task ID:** BT-74 (board `BT-74`)
- **Implementer:** Antigravity
- **Lead / Reviewer:** Codex
- **Reference Context:** BT-13, BT-57, BT-66, BT-70, `L_SevarogArena` C-1619 Production Route

---

## 1. Executive Summary

This read-only audit traces the selected production Sevarog route from encounter and card selection through runtime execution components, contrasting the project-owned C++ framework architecture against the legacy vendor BehaviorTree attack path.

### Key Architecture Finding
The production framework duel (`DA_Sevarog_Framework_Encounter` + `DA_Boss_Sevarog_FrameworkProfile_Production`) **does NOT use a BehaviorTree for attack-task execution**.
- **Production Framework Route**: Attack selection and execution are 100% C++ project-owned via `ARPGFrameworkBossCharacter::Tick()`, `FRPGBossMoveSelector::Select()`, and `URPGFrameworkMoveExecutor::StartCard()`. It does not execute `UBTTaskNode` or `UBehaviorTreeComponent`.
- **Legacy Vendor Pack Route**: Relies on `BT_ExampleBoss.uasset` and Blueprint attack task `T_TryActivateAbilitiesByTags.uasset` (inheriting from `BTT_StateMachineTaskBase` -> `UBTTask_BlueprintBase`).
- **Suppression Mechanism**: In `URPGPlayerMovesSubsystem::ReplacePlacedArenaBosses()`, placed vendor pack actors (`BP_ExampleGreatSwordBoss`) are intercepted before actor `BeginPlay`, subjected to `StopLogic()`, and destroyed (`PackBoss->Destroy()`).

---

## 2. Selected Production Sevarog Route Execution Trace

### 2.1 Route Entry & Asset Binding
1. **Encounter Definition**:
   - Reflected Path: `/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter.DA_Sevarog_Framework_Encounter`
   - Properties:
     * `bUseFrameworkBoss = true`
     * `FrameworkBossProfile = /Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Production.DA_Boss_Sevarog_FrameworkProfile_Production`
2. **Actor Lifecycle & Replacement**:
   - In `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:115-180`:
     * Listens to `FWorldDelegates::OnWorldInitializedActors`.
     * Identifies placed pack boss `Actor` via `IsPackBoss(Actor)` (`BP_ExampleGreatSwordBoss`).
     * Calls `SuppressArenaBoss(PackBoss)`:
       ```cpp
       if (AAIController* AI = Cast<AAIController>(PackBoss->GetController())) {
           AI->StopMovement();
           if (UBrainComponent* Brain = AI->GetBrainComponent()) {
               Brain->StopLogic(TEXT("ArenaRoute.Suppressed"));
           }
       }
       PackBoss->Destroy();
       ```
     * Spawns deferred framework character: `ARPGFrameworkBossCharacter`.
     * Configures mesh from production profile: `MeshComponent->SetSkeletalMesh(ProfileMesh)`.
     * Initializes encounter binding: `InitializeSelectedEncounter(*Binding, PlayerPawn, Error)`.

### 2.2 Framework Card Selection & Move Execution (No BehaviorTree)
1. **Decision Gate (`ARPGFrameworkBossCharacter::Tick()`)**:
   - Location: `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:724-822`.
   - When in neutral state (`Executor->IsIdle()`), native `Tick` constructs `FRPGBossDecisionSnapshot S`.
   - Calls project C++ selector:
     ```cpp
     bool bAsked = Selector.Select(Executor->Model(), S, Decision, Pattern);
     ```
   - Selector evaluates the 7 production cards (`S1` through `S8`, excluding non-production cards).
2. **Move Execution (`URPGFrameworkMoveExecutor::StartCard()`)**:
   - Location: `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:822`.
   - Dispatches chosen card directly to `URPGFrameworkMoveExecutor`:
     ```cpp
     Executor->StartCard(Dependencies->Candidates[Decision.ChosenIndex].Card, StartSnapshot, Error);
     ```
   - `URPGFrameworkMoveExecutor` (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp`) runs the motion model, montage playback, hit windows, and collision queries on the game thread.
   - **Conclusion**: The production framework boss has zero dependency on `UBehaviorTreeComponent` or `UBTTaskNode`.

---

## 3. Vendor Pack BehaviorTree Attack Path (`BT_ExampleBoss`)

The placed pack boss (`BP_ExampleGreatSwordBoss_C_3`), if allowed to run, executes the vendor AI stack:

### 3.1 BehaviorTree Hierarchy
- **BehaviorTree Asset**:
  `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss.uasset`
- **Root / Selectors**:
  Evaluates combat state, distance, and combat abilities.
- **Attack Task Nodes**:
  1. `T_TryActivateAbilitiesByTags` (`/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_TryActivateAbilitiesByTags.uasset`)
  2. `T_TryActivateSeparateAbilitiesByTags` (`/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_TryActivateSeparateAbilitiesByTags.uasset`)

### 3.2 Task Class Inheritance & Lifecycle Analysis

Both attack tasks share identical architectural inheritance and lifecycle characteristics:

- **Class Inheritance Hierarchy**:
  - `T_TryActivateAbilitiesByTags` (Blueprint Class) / `T_TryActivateSeparateAbilitiesByTags` (Blueprint Class)
    └── `BTT_StateMachineTaskBase` (Blueprint Class in `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/`)
        └── `UBTTask_BlueprintBase` (Engine C++ class in `/Script/AIModule`)
            └── `UBTTaskNode` (Engine C++ class in `/Script/AIModule`)
                └── `UBTNode` -> `UObject`

- **Parent Class (`BTT_StateMachineTaskBase.uasset`) Audit**:
  - Binary inspection of `BTT_StateMachineTaskBase.uasset` confirms that `ParentClass` / `NativeParentClass` is `BTTask_BlueprintBase` directly (no intermediate classes).
  - Raw byte-string scanning found no literal tick-name text in the parent package; this is negative string evidence, not a parsed Unreal reflection result.
  - Raw byte-string scanning found no literal `ReceiveTick` or `ReceiveTickAI` text in `BTT_StateMachineTaskBase`; this does not establish its generated-class event flags.
  - It implements task state tracking (`IsTaskExecuting`, `AbortBehaviorTask`, `OnAbortCurrentBehaviorTask`), wrapping `FinishExecute` and `FinishAbort`. Its tick-graph/event status remains unverified by package-aware reflection.

- **Task Method Overrides & Execution Lifecycle**:
  Static binary asset inspection across child tasks and intermediate parent confirms:
  1. **`ExecuteTask` (`ReceiveExecuteAI` / `ReceiveExecute`)**:
     * Engine calls `UBTTask_BlueprintBase::ExecuteTask(OwnerComp, NodeMemory)`.
     * Both `T_TryActivateAbilitiesByTags` and `T_TryActivateSeparateAbilitiesByTags` export `ReceiveExecuteAI` and `ReceiveExecute`.
     * The task attempts to activate Gameplay Abilities matching specified gameplay tags on the vendor ASC (`UAbilitySystemComponent`).
  2. **`TickTask` (`ReceiveTickAI` / `ReceiveTick`) Hierarchy Traversal**:
     * In `UBTTask_BlueprintBase.cpp:44-46`, the engine determines whether to tick via:
       ```cpp
       ReceiveTickImplementations = FBTNodeBPImplementationHelper::CheckEventImplementationVersion(
           TEXT("ReceiveTick"), TEXT("ReceiveTickAI"), *this, *StopAtClass);
       bNotifyTick = ReceiveTickImplementations != FBTNodeBPImplementationHelper::NoImplementation;
       ```
     * `CheckEventImplementationVersion` scans up the class hierarchy starting at the child task and stopping at `UBTTask_BlueprintBase`.
     * Raw string scans of the leaf and parent packages found no literal tick-event names; absence from these scans does not establish generated-class event flags.
     * The engine traverses the class hierarchy up to `UBTTask_BlueprintBase`; the resulting implementation state is unknown without package-aware reflection.
     * Since the engine check traverses the class hierarchy and package-aware reflection was not run, the resulting `ReceiveTickImplementations` and `bNotifyTick` values are **unknown** from this audit.
  3. **`AbortTask` (`ReceiveAbortAI` / `ReceiveAbort`)**:
     * When combat is interrupted or the tree resets, engine calls `UBTTask_BlueprintBase::AbortTask()`.
     * Both child tasks export `ReceiveAbortAI` and `ReceiveAbort` handlers, which call into `BTT_StateMachineTaskBase::AbortBehaviorTask` and `FinishAbort`.

- **Limits of Offline Binary Inspection**:
  Raw string analysis is negative string evidence only. It does not prove the absence of `ReceiveTick` / `ReceiveTickAI` implementations or determine `bNotifyTick`; package-aware Unreal reflection or runtime observation is required. Internal Blueprint graph wiring and compiled bytecode also remain uninspected.

---

## 4. Synthesis & Observability Gap

1. **Production Route vs Vendor BT**:
   - The selected production Sevarog route never executes `BT_ExampleBoss`, `T_TryActivateAbilitiesByTags`, or `T_TryActivateSeparateAbilitiesByTags`.
   - The acceptance criterion `raw_behavior_tree_tick_count` was originally conceived as proof that the *suppressed* pack boss did not execute any attacks.
2. **Pre-BeginPlay Suppression vs Historical Tick Count (BT-66 Caveat)**:
   - In the production route, the pack boss is intercepted and destroyed before actor `BeginPlay` (`began_play=0`, `montage_active=0`).
   - **Critical Caveat from BT-66**: Pre-`BeginPlay` suppression proves the placed vendor pack actor was intercepted, had logic stopped, and was destroyed before standard gameplay began; it establishes absence from the live combat census.
   - However, **pre-BeginPlay suppression is NOT a historical tick counter**. Pre-`BeginPlay` AI controller and brain component initialization ordering was not instrumented in the runtime run; reporting `raw_behavior_tree_tick_count = 0` based on actor suppression confuses structural suppression evidence with an actively monitored BehaviorTree tick stream where 0 ticks occurred over time.
3. **Why Raw BT Ticks Cannot Be Sampled in C++**:
   - Because both attack tasks are vendor Blueprints inheriting from `UBTTask_BlueprintBase`, engine `ExecuteTask` and `TickTask` are dispatch virtuals within `AIModule`, but no external engine delegate or hook exists (as proven in BT-66).
   - Whether either attack task implements a tick event in its generated class was not established by this audit.
   - Consequently, any direct instrumentation hook must either be placed on the engine/task level (prohibited by vendor asset immutability) or replaced by an explicit lifecycle suppression criterion (`[X-2558]`).

---

## 5. Verification & Operating Discipline
- Read-only source and asset mapping per [X-2576].
- 0 builds, 0 Unreal Editor launches, 0 PIE runs executed, 0 tests run.
- 0 assets or configuration files modified; 0 git commits/pushes.
