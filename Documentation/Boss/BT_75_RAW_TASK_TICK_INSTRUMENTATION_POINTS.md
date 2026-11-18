# BT-75: Identification of Raw Task-Tick Instrumentation Points in UE 5.5.4

- **Date:** 2026-11-17
- **Task ID:** BT-75 (board `BT-75`)
- **Implementer:** Antigravity
- **Lead / Reviewer:** Codex
- **Reference Context:** BT-13, BT-57, BT-66, BT-74, `L_SevarogArena` C-1619 Production Route

---

## 1. Executive Summary

This read-only feasibility audit examines potential engine, plugin, and project hooks in Unreal Engine 5.5.4 for observing and counting BehaviorTree task execution and ticks. It evaluates whether a project-owned hook can instrument raw attack-task `TickTask` invocations for the placed vendor pack boss (`BP_ExampleGreatSwordBoss_C_3`) without violating vendor asset immutability or inferring runtime behavior.

### Primary Architectural Findings

1. **Engine Tick Gate (Generated-Class State Unknown)**:
   - Engine inspection of `UBTTask_BlueprintBase.cpp:44-46` reveals:
     ```cpp
     ReceiveTickImplementations = FBTNodeBPImplementationHelper::CheckEventImplementationVersion(
         TEXT("ReceiveTick"), TEXT("ReceiveTickAI"), *this, *StopAtClass);
     bNotifyTick = ReceiveTickImplementations != FBTNodeBPImplementationHelper::NoImplementation;
     ```
   - In `BTTaskNode.cpp:241-260`, `UBTTaskNode::WrappedTickTask` executes `TickTask()` **only if `bNotifyTick == true`**.
   - **Hierarchy-Aware Scan Audit**:
     * `CheckEventImplementationVersion` evaluates the class hierarchy starting at the leaf task and terminating at `StopAtClass` (`UBTTask_BlueprintBase`).
     * Child tasks: package string scans found execute/abort names; absence of tick names in these scans does not establish generated-class event flags.
     * Intermediate parent: `BTT_StateMachineTaskBase.uasset` directly inherits from `BTTask_BlueprintBase`. Raw string scanning is not package-aware reflection.
     * Terminal class: `UBTTask_BlueprintBase` (`StopAtClass`).
     * Result: The generated-class hierarchy check result and resulting `bNotifyTick` values are **unknown** because package-aware reflection was not run.
   - **Conclusion**: This audit cannot determine whether either attack task receives `TickTask` callbacks. Runtime task-tick count remains uninstrumented and unknown.

2. **Categorical Distinction of Execution Concepts**:
   - **Tree Tick (`UBehaviorTreeComponent::TickComponent`)**: Evaluates blackboard keys, executes active services, and traverses decorators.
   - **Task Execution (`UBTTaskNode::ExecuteTask` / `ReceiveExecuteAI`)**: Invoked exactly once when entering an attack task node. Both vendor tasks implement this.
   - **Task Tick (`UBTTaskNode::TickTask` / `ReceiveTickAI`)**: Frame-by-frame callback when enabled by the generated task class; whether these vendor tasks enable it is unknown from string scans.
   - **BT Service Tick (`UBTService::TickNode` / `ReceiveTickAI`)**: Periodic background logic attached to composite nodes.
   - **Gameplay Card Callbacks**: Project-owned C++ framework methods (`URPGFrameworkMoveExecutor::StartCard()`, `AdvancePlayback()`), completely decoupled from `AIModule`.

3. **No Non-Invasive Project-Owned Hook Exists in UE 5.5.4**:
   - `UBehaviorTreeComponent::ExecuteTask` and `OnTaskFinished` are **non-virtual** member functions (`BehaviorTreeComponent.h:176, 437`).
   - `FBehaviorTreeDelegates` provides only `OnTreeStarted`, `OnDebugSelected`, and `OnDebugLocked` (`BehaviorTreeDelegates.h:35-41`), with zero node-level or task-level multicast delegates.
   - Intercepting `ExecuteTask` at the task node level requires subclassing the task node in C++, which cannot be bound to vendor Blueprints without reparenting vendor assets under `Content/AdvancedARPGCombat/` (prohibited by `AGENTS.md`).

---

## 2. Distinction of Execution and Tick Concepts

To ensure precise telemetry and avoid conflating different engine subsystems, the table below delineates the five operational concepts:

| Execution Concept | Engine Class / Method | Invocation Frequency | Vendor Attack Task Status |
| :--- | :--- | :--- | :--- |
| **Tree Tick** | `UBehaviorTreeComponent::TickComponent` | Every frame while `BrainComponent` logic is running | Runs if `BrainComponent` active; stopped by `StopLogic()` |
| **Task Execution** | `UBTTaskNode::ExecuteTask` -> `ReceiveExecuteAI` | Once per task activation entry | Implemented in vendor Blueprints; runs once per ability trigger |
| **Task Tick** | `UBTTaskNode::TickTask` -> `ReceiveTickAI` | Every frame while task is `InProgress` **AND** `bNotifyTick == true` | **Unknown**: generated-class `bNotifyTick` was not verified |
| **BT Service Tick** | `UBTService::TickNode` -> `ReceiveTickAI` | Periodic interval (`Interval` ± `RandomDeviation`) | Independent of attack tasks; used for perception / range evaluation |
| **Gameplay Card Callback** | `URPGFrameworkMoveExecutor::StartCard` / `AdvancePlayback` | Frame-by-frame on game thread within project C++ framework | **Production Duel Route**: 100% project-owned; 0 BehaviorTree involvement |

---

## 3. Exhaustive Audit of Potential Instrumentation Hook Points

### 3.1 Hook Point A: Subclassing `UBehaviorTreeComponent`
- **Location**: `Engine/Source/Runtime/AIModule/Classes/BehaviorTree/BehaviorTreeComponent.h`
- **Audit Findings**:
  * Line 176: `AIMODULE_API void OnTaskFinished(const UBTTaskNode* TaskNode, EBTNodeResult::Type TaskResult);` -> **NON-VIRTUAL**.
  * Line 437: `AIMODULE_API void ExecuteTask(UBTTaskNode* TaskNode);` -> **NON-VIRTUAL**.
  * Line 202: `AIMODULE_API virtual void TickComponent(...) override;` -> **VIRTUAL**, but overrides component-level ticking, providing no callback or parameter identifying which task node (if any) is executing.
  * `InstanceStack` and `ActiveNode` are internal state evaluated during search, not accessible via safe public multicast delegates.
- **Verdict**: **INFEASIBLE**. Subclassing `UBehaviorTreeComponent` cannot intercept individual task executions or ticks.

### 3.2 Hook Point B: Engine BehaviorTree Delegates
- **Location**: `Engine/Source/Runtime/AIModule/Public/BehaviorTreeDelegates.h`
- **Audit Findings**:
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
- **Verdict**: **INFEASIBLE**. The engine exposes no delegates for task execution, task ticking, task abortion, or task completion.

### 3.3 Hook Point C: Subclassing `UBTTaskNode` / `UBTTask_BlueprintBase`
- **Location**: `Engine/Source/Runtime/AIModule/Classes/BehaviorTree/BTTaskNode.h`
- **Audit Findings**:
  * `UBTTaskNode::ExecuteTask` and `TickTask` are virtual:
    ```cpp
    virtual EBTNodeResult::Type ExecuteTask(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory);
    virtual void TickTask(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory, float DeltaSeconds);
    ```
  * However, vendor assets `T_TryActivateAbilitiesByTags` and `T_TryActivateSeparateAbilitiesByTags` already inherit from `BTT_StateMachineTaskBase` -> `UBTTask_BlueprintBase`.
  * Injecting a custom C++ class into this hierarchy requires reparenting `BTT_StateMachineTaskBase.uasset` or editing `BT_ExampleBoss.uasset`. Both actions violate the vendor asset immutability constraint.
- **Verdict**: **INFEASIBLE without modifying vendor assets**.

### 3.4 Hook Point D: Global Engine / World Delegates
- **Location**: `Engine/Source/Runtime/Engine/Classes/Engine/World.h` (`FWorldDelegates`)
- **Audit Findings**:
  * `FWorldDelegates::OnWorldTickStart`, `OnWorldPostActorTick`.
  * These delegates observe world-level or actor-level ticks. They have no visibility into the internal call stack or node execution of `AIModule` components.
- **Verdict**: **INFEASIBLE**. World delegates operate at macro actor granularity.

### 3.5 Hook Point E: Project-Owned Suppression Lifecycle Hook (Narrowest Hook)
- **Location**: `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:115-180`
- **Audit Findings**:
  * Subscribed to `FWorldDelegates::OnWorldInitializedActors`.
  * Intercepts `BP_ExampleGreatSwordBoss` before actor `BeginPlay`:
    ```cpp
    if (AAIController* AI = Cast<AAIController>(PackBoss->GetController()))
    {
        AI->StopMovement();
        if (UBrainComponent* Brain = AI->GetBrainComponent())
        {
            Brain->StopLogic(TEXT("ArenaRoute.Suppressed"));
        }
    }
    PackBoss->Destroy();
    ```
  * This hook is **100% project-owned**, requires zero engine modifications, and requires zero vendor asset edits.
  * **Capability**: Proves conclusively that the vendor pack boss had its brain logic stopped and was destroyed prior to `BeginPlay`.
  * **Limitation (BT-66 Caveat)**: It is a **lifecycle suppression proof**, not a continuous runtime monitor of BehaviorTree task execution over time.

---

## 4. Summary of UE 5.5.4 API & Ownership Limitations

1. **Non-Virtual Component APIs**:
   `UBehaviorTreeComponent::ExecuteTask` and `OnTaskFinished` are non-virtual, preventing component-level interception of task lifecycles in C++.
2. **Missing Multicast Delegates**:
   `AIModule` does not provide public event delegates for task execution or ticking.
3. **Engine `bNotifyTick` Gating**:
   In `UBTTask_BlueprintBase`, `TickTask` is gated behind `bNotifyTick`. The vendor generated-class values were not established by raw string scanning, so whether their tasks tick remains unknown.
4. **Vendor Asset Immutability Boundary**:
   Modifying vendor Blueprints to insert instrumentation or reparent classes is strictly prohibited by project rules.
5. **Suppressed Actor Monitoring Boundary**:
   Pre-`BeginPlay` suppression supports a lifecycle claim about the placed actor. It does not establish a historical raw task-tick count or the generated task class's `bNotifyTick` value.

---

## 5. Recommendation

- **Technical Recommendation**:
  Do **not** implement engine or assembly hooks under this audit. The production route uses the C++ framework and the placed vendor actor is suppressed pre-`BeginPlay`; however, task `bNotifyTick` and raw historical counts remain unknown.
- **Route Proof Alignment**:
  Acceptance proof should formally transition from the unmeasurable `raw_behavior_tree_tick_count` to verified **pre-BeginPlay suppression evidence** (`pack_boss_suppressed=true`, `pack_boss_began_play=false`, `pack_boss_destroyed=true`), as recommended in BT-66 and pending Owner decision `[X-2558]`.

---

## 6. Verification & Operating Discipline
- Read-only source audit of UE 5.5.4 engine headers and project C++ source.
- 0 builds, 0 Unreal Editor launches, 0 PIE runs executed, 0 tests run.
- 0 assets or configuration files modified; 0 git commits/pushes.
