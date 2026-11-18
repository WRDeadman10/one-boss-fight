# BT-66: Reassessment of Direct Raw BehaviorTree Task-Tick Observability in UE 5.5.4

Date: 2026-11-17
Task: BT-66 (board `BT-66`)
Implementer: Antigravity
Reviewer / Lead: Codex
Context: Follow-up to BT-13 (`Documentation/Boss/BT_13_RAW_BT_TICK_EVIDENCE.md`), [X-2556], and BT-57 (`Documentation/Boss/BT_57_SEVAROG_PROFILE_AND_RAW_AI_TICK_AUDIT.md`).

---

## 1. Executive Summary

This report delivers a rigorous, evidence-backed assessment of whether a project-owned runtime observer can directly count BehaviorTree attack-task executions/ticks for the placed vendor pack boss (`BP_ExampleGreatSwordBoss_C_3`) in `L_SevarogArena` without modifying vendor pack assets or fabricating/sampling a zero counter.

### Primary Finding
**The audit found no public UE 5.5.4 task-level delegate or overridable component hook that directly observes the vendor attack task.** The task's own virtual callback could count its execution, but the vendor Blueprint must be changed to use a project-owned task class, or the engine/vendor boundary must be changed; both are outside current project rules.
1. **Engine Layer (UE 5.5.4 `AIModule`)**: No delegates or broadcasts exist for task node execution, ticking, or completion (`BehaviorTreeDelegates.h` defines only `OnTreeStarted` and debug tools; `UBehaviorTreeComponent::ExecuteTask` and `OnTaskFinished` are non-virtual).
2. **Vendor Asset Layer (`Content/AdvancedARPGCombat`)**: The attack tasks (`T_TryActivateAbilitiesByTags.uasset`) and their parent (`BTT_StateMachineTaskBase.uasset`) are vendor Blueprint assets inheriting from `UBTTask_BlueprintBase`. A project C++ class cannot intercept or wrap their `ExecuteTask`/`TickTask` methods without reparenting the vendor Blueprint assets or editing the vendor BehaviorTree (`BT_ExampleBoss.uasset`), both of which violate the strict project rule prohibiting vendor asset modification.
3. **Route Lifecycle Evidence**: In the C-1619 production route, the placed pack boss is intercepted and destroyed before actor `BeginPlay` (`began_play=0`, `montage_active=0`), after `StopLogic` is requested. This is strong suppression evidence. It does **not** directly establish the historical task execution/tick count; pre-BeginPlay controller/brain startup ordering was not instrumented in the runtime run.

An owner decision is needed to replace the raw-tick criterion with a suppression lifecycle criterion. Such a criterion can establish that the placed pack boss was suppressed before actor BeginPlay and absent from the live arena census; it must not be described as a measured raw task-tick count or proof that no task callback ran earlier.

---

## 2. Exhaustive Audit of UE 5.5.4 BehaviorTree APIs

Inspection of installed engine headers in `C:\Program Files\Epic Games\UE_5.5\Engine\Source\Runtime\AIModule`:

### A. Engine Delegates (`BehaviorTreeDelegates.h`)
- File: `Engine/Source/Runtime/AIModule/Public/BehaviorTreeDelegates.h`, lines 12–28.
- Declared delegates:
  ```cpp
  struct FBehaviorTreeDelegates
  {
      DECLARE_MULTICAST_DELEGATE_TwoParams(FOnTreeStarted, const UBehaviorTreeComponent&, const UBehaviorTree&);
      DECLARE_MULTICAST_DELEGATE_OneParam(FOnTreeDebugTool, const APawn*);

      static AIMODULE_API FOnTreeStarted OnTreeStarted;
      static AIMODULE_API FOnTreeDebugTool OnDebugSelected;
      static AIMODULE_API FOnTreeDebugTool OnDebugLocked;
  };
  ```
- **Finding**: Zero multicast delegates exist for node-level, task-level, or tick-level execution. `OnTreeStarted` fires only once when the tree instance is initialized, conveying no task execution telemetry.

### B. BehaviorTree Component (`BehaviorTreeComponent.h`)
- File: `Engine/Source/Runtime/AIModule/Classes/BehaviorTree/BehaviorTreeComponent.h`.
- Key Execution Methods:
  - Line 176: `AIMODULE_API void OnTaskFinished(const UBTTaskNode* TaskNode, EBTNodeResult::Type TaskResult);` -> **NON-VIRTUAL**.
  - Line 437: `AIMODULE_API void ExecuteTask(UBTTaskNode* TaskNode);` -> **NON-VIRTUAL**.
  - Line 227 / 583: `const UBTNode* GetActiveNode() const { return InstanceStack.Num() ? InstanceStack[ActiveInstanceIdx].ActiveNode : NULL; }` -> public accessor, but only reflects momentary active node during stack evaluation, not a tick counter or historical execution listener.
  - Zero dynamic multicast delegates or event dispatchers declared on `UBehaviorTreeComponent`.
- **Finding**: Subclassing `UBehaviorTreeComponent` cannot intercept task execution because `ExecuteTask` and `OnTaskFinished` are non-virtual member functions called directly by internal tree search and task execution routines.

### C. Brain Component (`BrainComponent.h`)
- File: `Engine/Source/Runtime/AIModule/Classes/BrainComponent.h`.
- Key Methods:
  - Lines 75–82: `FAIMessageObserverHandle Create(UBrainComponent*, FName MessageType, ...)` observes `FAIMessage` dispatches.
  - Line 115: `virtual void StopLogic(const FString& Reason) override;`.
- **Finding**: `FAIMessage` is used exclusively for latent task messaging (e.g. `AIMessage_MoveTaskCompleted`). Standard task execution and ticks (`ExecuteTask`, `TickTask`) do not broadcast `FAIMessage`.

### D. BehaviorTree Manager (`BehaviorTreeManager.h`)
- File: `Engine/Source/Runtime/AIModule/Classes/BehaviorTree/BehaviorTreeManager.h`.
- Tracks `LoadedTemplates` and `ActiveComponents`.
- **Finding**: Pure asset loader and template cache; contains zero execution callbacks or node instrumentation hooks.

### E. Task Node Base Classes (`BTTaskNode.h` and `BTTask_BlueprintBase.h`)
- `UBTTaskNode` (`BTTaskNode.h:40, 108, 118`):
  `virtual EBTNodeResult::Type ExecuteTask(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory);`
  `virtual void TickTask(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory, float DeltaSeconds);`
  `virtual void OnTaskFinished(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory, EBTNodeResult::Type TaskResult);`
- `UBTTask_BlueprintBase` (`BTTask_BlueprintBase.h:28, 152`):
  Overrides `ExecuteTask` and `TickTask` to dispatch into Blueprint bytecode (`ReceiveExecuteAI`, `ReceiveTickAI`).
- **Finding**: Virtual execution hooks exist **only** at the individual task node instance level. To intercept them in C++, the task class itself must be a project-owned C++ class.

---

## 3. Audit of Mounted Vendor Pack Assets

Inspection of vendor assets under `Content/AdvancedARPGCombat`:

1. **Vendor BehaviorTree**:
   - Path: `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss.uasset`.
   - References attack tasks: `T_TryActivateAbilitiesByTags.uasset` and `T_TryActivateSeparateAbilitiesByTags.uasset`.
2. **Vendor Attack Task**:
   - Path: `Content/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_TryActivateAbilitiesByTags.uasset`.
   - Type: Blueprint Class (`UBlueprintGeneratedClass`).
   - Parent Class: `BTT_StateMachineTaskBase` (`Content/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/BTT_StateMachineTaskBase.uasset`).
3. **Vendor Task Intermediate Parent**:
   - `BTT_StateMachineTaskBase.uasset` is a Blueprint class directly inheriting from C++ engine class `UBTTask_BlueprintBase`.
4. **Vendor AI Controller**:
   - Path: `Content/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BP_BaseAIController.uasset`.
   - Type: Blueprint Class inheriting from `AAIController`. Contains standard `BehaviorTreeComponent` subobject.
5. **Vendor Boss Character**:
   - Path: `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.uasset`.
   - Placed in `L_SevarogArena` as `BP_ExampleGreatSwordBoss_C_3`.

### The Vendor Immutability Boundary
Project rules (`RULE[c:\UnrealProject\OneBossFight\AGENTS.md]`) strictly forbid modifying vendor assets. Because `BT_ExampleBoss.uasset`, `T_TryActivateAbilitiesByTags.uasset`, and `BTT_StateMachineTaskBase.uasset` are binary `.uasset` files under `Content/AdvancedARPGCombat/`:
- They cannot be reparented to a project C++ class without modifying their binary asset files.
- The BehaviorTree cannot be rewired to point to custom project task nodes without modifying `BT_ExampleBoss.uasset`.

---

## 4. Evaluation of Technical Candidates

| Candidate | Mechanism | Feasibility | Reason for Infeasibility |
| :--- | :--- | :--- | :--- |
| **1. Global Engine Delegate** | Bind to `FBehaviorTreeDelegates` | **INFEASIBLE** | UE 5.5.4 has no task-level delegates in `FBehaviorTreeDelegates`. |
| **2. Component-Level Hook** | Override `ExecuteTask` in derived `UBehaviorTreeComponent` | **INFEASIBLE** | `ExecuteTask` and `OnTaskFinished` are strictly non-virtual in `UBehaviorTreeComponent`. |
| **3. C++ Task Class Wrapper** | Derive from `UBTTask_BlueprintBase` with tick counter | **INFEASIBLE** | Vendor Blueprint assets cannot inherit from a new C++ class without editing vendor `.uasset` files. |
| **4. BehaviorTree Rewiring** | Replace task nodes in `BT_ExampleBoss` with custom C++ task | **INFEASIBLE** | Requires editing vendor asset `BT_ExampleBoss.uasset`. |
| **5. Suppression-Time Sampling** | Query `GetActiveNode()` or `IsRunning()` during `SuppressArenaBoss` | **REJECTED (BT-13)** | Sampling momentary state at suppression is not a historical tick counter (per BT-13 lead review). |
| **6. Animation / Montage Check** | Check `USkeletalMeshComponent::IsAnyMontagePlaying()` | **VALIDATED** | Already instrumented (`montage_active=0`). Proves no attack animation started, but does not count BT task ticks. |

---

## 5. Root Structural Finding: The Zero-Execution Reality

In `URPGPlayerMovesSubsystem::SuppressArenaBoss` (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:815-841`):
```cpp
void URPGPlayerMovesSubsystem::SuppressArenaBoss(AActor* PackBoss)
{
    if (!IsValid(PackBoss)) { return; }
    ...
    if (AAIController* AI = Cast<AAIController>(Cast<APawn>(PackBoss) ? Cast<APawn>(PackBoss)->GetController() : nullptr))
    {
        AI->StopMovement();
        if (UBrainComponent* Brain = AI->GetBrainComponent())
        {
            Brain->StopLogic(TEXT("Sevarog framework arena route"));
        }
    }
    UE_LOG(LogTemp, Display, TEXT("[EncounterActivation] arena_pack_boss_suppressed actor=%s began_play=%d montage_active=%d"),
        *PackBoss->GetName(), PackBoss->HasActorBegunPlay() ? 1 : 0, bPackMontageActive ? 1 : 0);
    PackBoss->SetActorTickEnabled(false);
    PackBoss->SetActorEnableCollision(false);
    ...
    PackBoss->Destroy();
}
```

### What the Route Evidence Establishes
1. `PackBoss->HasActorBegunPlay()` evaluates to false at the suppression log (`began_play=0`).
2. The route requests `Brain->StopLogic`, disables actor/component ticking and collision, then destroys the actor.
3. The Smoke also reports a zero live pack-boss census and no pack-boss HUD. These are lifecycle/scene observations, not a task history.
4. The existing evidence does not observe when/if the controller started its BrainComponent or whether an attack task ran before suppression. Therefore it cannot claim a measured count of zero. A direct task callback counter remains unavailable through the examined public component/delegate APIs.

---

## 6. Recommendations & Owner Decisions

To unblock acceptance without compromising engineering truth or violating vendor immutability:

### Recommendation A: Alternate Lifecycle Criterion (Strongly Recommended)
Replace the uninstrumented `raw_behavior_tree_tick_count` criterion in `pie_sevarog_arena_route_acceptance.py` with the verified physical proof of suppression:
- **Criterion Name**: `pack_boss_suppression_verified` (or `pack_boss_suppressed_prior_to_beginplay`)
- **Required Conditions**:
  1. `suppressed_pack_actor_observed == true` (pack actor detected and intercepted).
  2. `began_play == 0` (strictly verified `HasActorBegunPlay() == false`).
  3. `montage_active == 0` (no attack montages active).
  4. `live_pack_actor_count == 0` (census confirms zero live pack actors in arena).
  5. `no_pack_bosshud_widget == true` (zero pack HUD widgets added to viewport).
- **Justification and limitation**: This provides deterministic evidence that the placed pack actor was suppressed before actor BeginPlay, then removed from the arena with no pack HUD. It supports the design goal of preventing a competing pack boss, but does not measure BehaviorTree task ticks or independently prove that no AI callback ran before suppression.

### Recommendation B: Invasive Vendor Modification (Rejected)
Reparent `BTT_StateMachineTaskBase.uasset` to a project C++ class `URPGInstrumentedBTTask` containing an execution counter.
- **Why Rejected**: Modifies vendor pack binaries, creates ongoing merge/update conflicts, and risks breaking vendor Blueprint serialization.

### Recommendation C: Maintain Blocked Status for Raw Ticks
If the owner/lead strictly requires an execution counter inside the task node itself, retain `raw_behavior_tree_tick_count: "BLOCKED_NOT_INSTRUMENTED"` and accept that BT-62 Smoke gate records `runtime_acceptance_status: "SMOKE_PASS_LIFECYCLE_UNTESTED"` while the production route is actively verified.

---

## 7. Operating Discipline Statement

- Audit type: Source and API inspection only. Codex lead review accepted the API feasibility findings with the qualification above; the report's earlier zero-tick inference is withdrawn.
- 0 tests, 0 builds, 0 Unreal Editor launches, 0 PIE runs executed.
- 0 assets, configurations, or C++ files modified.
- 0 git commits or pushes performed.
