# BT-78: Consolidated BehaviorTree Task-Tick Instrumentation Feasibility Recommendation

- **Date:** 2026-11-17
- **Task ID:** BT-78 (board `BT-78`)
- **Implementer:** Antigravity
- **Lead / Reviewer:** Codex
- **Reference Context:** BT-13, BT-66, BT-74, BT-75, BT-76, BT-77, `L_SevarogArena` C-1619 Production Route

---

## 1. Executive Summary

This report consolidates the findings of the five-task BehaviorTree raw task-tick feasibility investigation (`BT-74` through `BT-78`), conducted per Technical Lead directive `[X-2576]`.

The objective was to determine whether a project-owned runtime observer can directly count BehaviorTree attack-task `TickTask` invocations for the placed vendor pack boss (`BP_ExampleGreatSwordBoss_C_3`) in `L_SevarogArena` without violating vendor asset immutability, and to present a minimal, actionable implementation recommendation to advance `BT-62`.

### Core Investigation Findings

1. **Production Duel Route is 100% C++ Framework Owned (BT-74)**:
   - In `DA_Sevarog_Framework_Encounter`, boss decision-making and attack execution run entirely through `ARPGFrameworkBossCharacter::Tick()`, `FRPGBossMoveSelector::Select()`, and `URPGFrameworkMoveExecutor::StartCard()`.
   - The production route does **not** instantiate or execute `UBehaviorTreeComponent`, `BT_ExampleBoss.uasset`, or any BehaviorTree task nodes.
2. **Vendor Task Tick Status is Unverified by Runtime (BT-74 / BT-75)**:
   - Offline byte-string scans did not find literal ReceiveTick names in task/parent packages. This is not package-aware Unreal reflection and does not verify inherited generated-class event flags.
   - A raw byte scan found no ASCII/UTF-16 tick substring in the inspected parent file; this is limited serialized-string evidence, not runtime telemetry or parsed reflection.
   - Engine class UBTTask_BlueprintBase.cpp:44-46 uses a hierarchy-aware event check, but the binary string scan alone does not prove the generated class result is NoImplementation.
   - In `BTTaskNode.cpp:241-260`, `UBTTaskNode::WrappedTickTask` gates `TickTask()` behind `if (bNotifyTick)`.
   - **Conclusion**: Do not claim TickTask callbacks are impossible or that a runtime count is zero from the current scan. Keep task-tick evidence uninstrumented until package-aware/reflection verification or a real observer exists.
3. **No Non-Invasive Engine Hook Exists in UE 5.5.4 (BT-75)**:
   - `UBehaviorTreeComponent::ExecuteTask` and `OnTaskFinished` are **non-virtual** member functions.
   - `FBehaviorTreeDelegates` provides zero task-level multicast delegates.
   - Project C++ cannot intercept task execution without reparenting vendor Blueprint assets under `Content/AdvancedARPGCombat/`, which violates the vendor asset immutability constraint (`AGENTS.md`).
4. **Current Route Telemetry Gaps & Tamper Risks (BT-76)**:
   - In the inspected driver, `parse_route_markers()` does not capture `bt_attack_ticks`, so the current route receipt cannot produce an instrumented raw count; this describes the audited version, not all future versions.
   - If an unverified `bt_attack_ticks: 0` were injected, the driver would evaluate `True` without checking sensor presence.
   - Defined a robust `raw_behavior_tree_telemetry` schema binding run tokens, BT assets, sampling windows, and sensor states.
5. **Acceptance and Overhead Guardrails (BT-77)**:
   - Formulated 6 fail-closed acceptance rules separating static proof from runtime evidence and requiring `null` telemetry counts when uninstrumented.
   - No overhead was measured. Existing suppression adds no recurring monitor in this proposal; startup cost and overall performance impact remain unprofiled.

---

## 2. Technical Evaluation of Implementation Options

| Architecture Option | Feasibility | Compliance with Rules | Frame Budget Impact | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Option A: Reparent Vendor Assets to Custom C++ Tasks** | Not evaluated | Would modify vendor assets, contrary to current project rule. | Unmeasured | Not proposed |
| **Option B: Engine / Source Assembly Hooking** | Infeasible | **VIOLATION**: Prohibited engine code modification; breaks packaging. | High risk | **REJECTED** |
| **Option C: Active Tree Polling during Combat** | Not applicable to the destroyed actor as currently routed | Requires a separate design | Unmeasured | Not recommended without a concrete need. |
| **Option D: Formal Adoption of Pre-BeginPlay Suppression Criterion** | Technically available as an alternate evidence model | Requires explicit Owner approval (X-2558) | Unmeasured | PROPOSED, NOT APPROVED |

---

## 3. Minimal Recommended Implementation Path

The recommended path is **Option D**, which formally aligns the route acceptance contract with physical engine reality:

1. **Replace Raw-Tick Metric with Lifecycle Suppression Proof**:
   - Retire the unmeasurable and engine-inapplicable `raw_behavior_tree_tick_count` criterion.
   - Replace it with the verified pre-`BeginPlay` suppression criterion: `pack_boss_suppressed_pre_begin_play`.
2. **Implement Structured Telemetry Schema (from BT-76)**:
   - Update `pie_sevarog_arena_route_acceptance.py` to emit the `raw_behavior_tree_telemetry` block.
   - Record:
     * Keep raw task telemetry `is_instrumented: false` and `telemetry_counts: null` unless a genuine raw task-tick observer is implemented.
     * Record suppression lifecycle observations in a separate lifecycle evidence block; do not label this as a task-tick sensor.
     * `status: "SUPPRESSED_PRE_BEGIN_PLAY"`
     * `began_play: 0`
     * `montage_active: 0`
     * `live_pack_actor_count: 0`
3. **Runner Verification & Cryptographic Binding**:
   - Update `run_sevarog_arena_route_acceptance.ps1` to parse the telemetry block, enforce the anti-spoofing rule (`is_instrumented == false` $\implies$ `counts == null`), and verify the log digest.

---

## 4. Exact Unresolved Owner Decision(s)

Implementation of Option D requires the following explicit Owner decision:

- **Owner Decision `[X-2558]`**:
  * **Question**: Does the Owner approve replacing the legacy `raw_behavior_tree_tick_count` acceptance criterion with the verified pre-`BeginPlay` suppression lifecycle criterion (`pack_boss_suppressed=true`, `began_play=0`, `montage_active=0`, `live_pack_actor_count=0`)?
  * **Rationale**: BT-74 and BT-75 establish the production route mapping and suppression path, but raw asset string scans do not determine generated-class `bNotifyTick`; runtime raw task ticks remain uninstrumented. Owner approval would adopt lifecycle suppression evidence as a separate acceptance criterion.
  * **Impact**: Approving `[X-2558]` unblocks `BT-62` (Smoke gate) and enables Full-mode acceptance upon successful boss defeat.

---

## 5. Scoped Follow-On Implementation Proposal

Upon Owner approval of `[X-2558]`, the following scoped implementation task is proposed:

### Proposed Task: `BT-79: Route Driver and Runner Telemetry Schema Integration`
- **Assignee**: Antigravity (Implementer)
- **Reviewer**: Codex (Tech Lead)
- **Scope**:
  1. `Scripts/Editor/pie_sevarog_arena_route_acceptance.py`:
     - Implement `raw_behavior_tree_telemetry` block generation.
     - Update `criteria` dictionary to evaluate `pack_boss_suppressed_pre_begin_play: true`.
     - Remove `"RAW_BEHAVIOR_TREE_TICK_COUNTER_NOT_INSTRUMENTED"` blocker when pre-`BeginPlay` suppression is verified.
  2. `Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`:
     - Update evidence parser to validate `raw_behavior_tree_telemetry`.
     - Remove legacy `raw_behavior_tree_tick_count` boolean check.
     - Enforce anti-spoofing and run token validation rules.
  3. `Scripts/Tools/test_c1619_sevarog_arena_route_contract.py` & `test_c1619_route_build_runner_contract.py`:
     - Update contract tests to validate new telemetry schema and criteria keys.
- **Constraints**:
  - Strictly gated on Owner approval of `[X-2558]`.
  - Zero asset writes outside locked runner; zero git commits/pushes.

---

## 6. Verification & Operating Discipline
- Source and architectural synthesis per BT-78.
- 0 builds, 0 Unreal Editor launches, 0 PIE runs executed, 0 tests run.
- 0 assets or configuration files modified; 0 git commits/pushes.
