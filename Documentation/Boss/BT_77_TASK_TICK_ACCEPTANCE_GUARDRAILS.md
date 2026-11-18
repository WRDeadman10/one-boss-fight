# BT-77: Acceptance and Overhead Guardrails for BehaviorTree Task-Tick Proof

- **Date:** 2026-11-17
- **Task ID:** BT-77 (board `BT-77`)
- **Implementer:** Antigravity
- **Lead / Reviewer:** Codex
- **Reference Context:** BT-13, BT-66, BT-74, BT-75, BT-76, `L_SevarogArena` C-1619 Production Route

---

## 1. Executive Summary

This report proposes acceptance guardrails for future evidence. It does not establish that zero task ticks or executions occurred, and does not claim that proposed monitoring is implemented. These proposals separate verification boundaries from overhead considerations for the `L_SevarogArena` route; they are not adopted acceptance criteria.

---

## 2. Core Guardrail Principles

### 2.1 Principle 1: Strict Source vs. Runtime Separation

A static structural proof and a runtime empirical proof represent distinct epistemic categories. Conflating them introduces verification failure:

| Category | Evidentiary Basis | Permissible Claims | Impermissible Claims |
| :--- | :--- | :--- | :--- |
| **Static / Source Proof** | C++ source, raw binary strings, header declarations | • Production route uses the framework C++ path.<br>• Raw task-package string scans did not find tick-event names; generated-class `bNotifyTick` remains unknown.<br>• `ReplacePlacedArenaBosses` contains pre-`BeginPlay` suppression logic. | • "0 ticks occurred during the fight" (cannot be claimed from source).<br>• "Runtime execution was verified zero." |
| **Runtime / Empirical Proof** | In-engine logs, reflected census, telemetry receipts | • Placed pack boss lifecycle observations at their recorded points.<br>• A census establishes counts only at its observation times; current Smoke evidence does not establish continuous sampling. | • "BehaviorTree ran and executed 0 ticks" without a task monitor.<br>• Claiming continuous task sampling when no monitor was attached. |

**Acceptance Rule 1 (Source/Runtime Non-Conflation)**:
Any receipt or documentation claiming that zero BehaviorTree attack-task ticks occurred must explicitly state whether the claim derives from **pre-BeginPlay actor suppression** or from an **active runtime monitor**. Static source proofs must never be recorded as runtime telemetry counts.

---

## 3. Coverage Window & Lifecycle Guardrails

### 3.1 Observation Window Boundaries

```
[Level Loading]
       │
       ▼
 ┌─────────────┐
 │  T_0: Init  │ ◄── Proposed monitor start and census baseline (not implemented)
 └──────┬──────┘
        │      ◄── Suppression executed: Brain->StopLogic(), PackBoss->Destroy()
        ▼
 ┌─────────────┐
 │ T_1: Begin  │ ◄── Recorded lifecycle observations may show began_play=0 and montage_active=0
 └──────┬──────┘
        │
        ▼      ◄── Active Combat: continuous census is proposed; current evidence does not establish it
 ┌─────────────┐
 │ T_2: Defeat │ ◄── BossDefeated: Boss health reaches 0, death sequence begins
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ T_3: Cleanup│ ◄── Proposed monitor teardown and receipt emission
 └─────────────┘
```

**Acceptance Rule 2 (Continuous Coverage Window)**:
- **T_0 (Earliest Bound)**: Monitoring must commence at `FWorldDelegates::OnWorldInitializedActors` prior to any actor's `BeginPlay`.
- **T_3 (Latest Bound)**: Monitoring must persist until `UEditorEngine::EndPlayMap` or level unbinding.
- **Fail-Closed Condition**: If sampling begins after `BeginPlay` has fired on any arena actor, or terminates before combat resolution, the run MUST fail closed with `COVERAGE_WINDOW_INCOMPLETE`.

### 3.2 Proposed Lifecycle Teardown Checks

The following are proposed checks for a future implementation; this report does not establish these properties at runtime:

1. **Movement Termination**: `AAIController::StopMovement()` invoked immediately.
2. **Brain Logic Cessation**: `UBrainComponent::StopLogic(TEXT("ArenaRoute.Suppressed"))` called to abort active evaluation trees.
3. **Actor Destruction**: `AActor::Destroy()` invoked on `BP_ExampleGreatSwordBoss`.
4. **Census Confirmation**: On the frame immediately following destruction and on all subsequent frames, `live_pack_actor_count` must evaluate to exactly `0`.
5. **Garbage Collection Immunity**: Placed actor destruction must not leave lingering references in subsystems or player target slots.

**Acceptance Rule 3 (Lifecycle Invariant Enforcement)**:
If at any point between T_0 and T_3:
- `PackBoss->HasActorBegunPlay()` evaluates to `true`, OR
- `PackBoss->GetMesh()->GetAnimInstance()->Montage_IsActive()` > 0, OR
- `live_pack_actor_count` > 0 after T_1,
the test MUST immediately abort and record `SUPPRESSION_LIFECYCLE_BREACH`.

---

## 4. Receipt Cryptographic Integrity & Anti-Spoofing Rules

As identified in BT-76, unanchored booleans and uninstrumented numeric zeros present severe tampering and false-positive risks.

### 4.1 Anti-Spoofing Semantic Contract

```json
{
  "sensor_binding": {
    "is_instrumented": false,
    "telemetry_counts": null
  }
}
```

**Acceptance Rule 4 (Uninstrumented Data Invariant)**:
- If `is_instrumented == false`: `telemetry_counts` MUST be `null`.
- If `telemetry_counts` contains integer values (`{"task_ticks": 0}`) while `is_instrumented == false`, the runner MUST fail closed with `SPOOFED_TELEMETRY_REJECTED`.
- A missing sensor cannot establish an empirical zero.

### 4.2 Cryptographic Anchoring Guardrails

**Acceptance Rule 5 (Receipt-Artifact Cryptographic Binding)**:
1. **Run Token Binding**: The receipt JSON must contain a `run_token` that matches the directory name and status file token.
2. **Log Digest**: The runner must compute and verify the SHA-256 digest of `editor.log` against the receipt before declaring acceptance.
3. **Temporal Bounding**:
   $$\text{Epoch}_{\text{receipt}} > \text{Epoch}_{\text{PIE\_Start}} \quad \text{and} \quad \text{ReceiptWriteTimeUtc} \le \text{RunnerDeadline}$$
   Any receipt written post-deadline or bearing a timestamp prior to session start is rejected unconditionally.

---

## 5. Performance and Overhead Guardrails

### 5.1 Project Frame Budget Constraints
- **Target Platform**: RTX 2060 Super @ 1080p.
- **Frametime Target**: 60 FPS sustained; p99 frame time $\le 16.67\text{ ms}$ (`AGENTS.md`).
- **Game Thread Overhead Budget**: No numeric allowance is approved or measured; profile future telemetry against the project frame-time target.

### 5.2 Overhead Comparison: Invasive Monitoring vs. Lifecycle Suppression

| Telemetry Architecture | Mechanism | CPU Overhead per Frame | Cache / GC Impact | Frame Budget Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Invasive Task Hooking** (Hypothetical) | Engine delegate broadcast or per-frame reflection query across all `UBTTaskNode` instances | Unmeasured | Not evaluated | Overhead and frame-budget impact unmeasured |
| **Full Actor Polling** (Hypothetical) | `GameplayStatics::GetAllActorsOfClass(world, Pawn)` every tick | Unmeasured | Not evaluated | Overhead and frame-budget impact unmeasured |
| **Lifecycle Suppression Hook** (Existing Route Logic) | One-time route suppression; no recurring monitor proposed | Unmeasured | No per-frame observer proposed | Startup cost and total frame impact have not been profiled. |

**Acceptance Rule 6 (Overhead Budget Guardrail)**:
No numeric per-monitor overhead allowance is approved or measured. Any future recurring telemetry must be profiled against the project 60 FPS / p99 <= 16.67 ms target before acceptance.

---

## 6. Synthesis: Definitive Acceptance Gate Matrix

| Acceptance Criterion | Verification Mode | Guardrail Rule | Required Output / Evidence |
| :--- | :--- | :--- | :--- |
| **Pack Boss Suppression** | Runtime (PIE / Package) | Rule 2 & Rule 3 | `suppression.began_play == 0`, `suppression.montage_active == 0` |
| **Combat Census Isolation** | Runtime (PIE / Package) | Rule 3 & Rule 6 | `live_framework_actor_count == 1`, `live_pack_actor_count == 0` |
| **BehaviorTree / Task-Tick Status** | Runtime / Source | Rule 1 & Rule 4 | Report observations separately; generated-class `bNotifyTick` and raw task ticks remain unknown |
| **Receipt Authenticity** | Post-Execution Runner | Rule 5 | Cryptographic digest match, run token match, deadline compliance |
| **Frametime Compliance** | Performance Profile | Rule 6 | Profile against project p99 target; no measurement or per-monitor budget is claimed here |

---

## 7. Verification & Operating Discipline
- Read-only architectural and performance analysis per BT-77.
- 0 builds, 0 Unreal Editor launches, 0 PIE runs executed, 0 tests run.
- 0 assets or configuration files modified; 0 git commits/pushes.
