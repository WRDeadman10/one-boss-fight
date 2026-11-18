# BT-76: Audit of Route Receipt Binding for Raw BehaviorTree Tick Evidence

- **Date:** 2026-11-17
- **Task ID:** BT-76 (board `BT-76`)
- **Implementer:** Antigravity
- **Lead / Reviewer:** Codex
- **Reference Context:** BT-13, BT-66, BT-74, BT-75, `L_SevarogArena` C-1619 Production Route

---

## 1. Executive Summary

This read-only audit inspects the receipt generation and verification pipeline across the C-1619 PIE route driver (`Scripts/Editor/pie_sevarog_arena_route_acceptance.py`) and PowerShell runner (`Scripts/Editor/run_sevarog_arena_route_acceptance.ps1`). It examines how raw BehaviorTree task-tick evidence is currently captured, defines the minimal schema required to bind counts to production assets, world identity, and execution lifecycles, and highlights critical validation gaps.

### Key Audit Findings

1. **Current Telemetry is an Unbound Placeholder**:
   - In `pie_sevarog_arena_route_acceptance.py:141-165`, `bt_ticks` is parsed from `suppression.get("bt_attack_ticks")`.
   - In `parse_route_markers()` (lines 83-117), the regex parser **never populates `bt_attack_ticks`**.
   - As a result, `bt_ticks` is perpetually `None`, forcing `raw_behavior_tree_tick_count` to `"BLOCKED_NOT_INSTRUMENTED"` and blocking overall acceptance.
2. **Missing Sensor vs. Zero Count Vulnerability**:
   - The driver currently defines: `bt_ticks_verified_zero = (bt_ticks is not None and bt_ticks == 0)`.
   - If an unverified source injected `"bt_attack_ticks": 0` into the log stream, the driver would evaluate `raw_behavior_tree_tick_count: true` without verifying whether a monitoring hook ever existed, which actor was observed, or what BehaviorTree asset was sampled.
3. **Absence of Cryptographic and Lifecycle Binding**:
   - The acceptance receipt (`acceptance.json`) lacks run tokens, world instance GUIDs, engine commit/build hashes, BehaviorTree asset paths, and sampling time windows.

---

## 2. Current Receipt Pipeline Architecture

```
[UE Editor PIE Session]
        │
        ▼ (Log Stream Output)
[pie_sevarog_arena_route_acceptance.py]
  - parse_route_markers(): Scans log tail for regex tokens
  - write_receipt(): Evaluates criteria dictionary
  - Emits: acceptance.json
        │
        ▼ (Read & Validate)
[run_sevarog_arena_route_acceptance.ps1]
  - Validates: Test-Path, WriteTimeUtc <= deadline, ExitCode == 0
  - Evaluates: evidence.result == 'PASS' and evidence.accepted == true
  - Emits: Status receipt (STATUS_*.txt)
```

### Current Schema in `acceptance.json` (Observed from `Run_20261116_225156_a763f2ce`)

```json
{
  "task": "C-1619 route PIE acceptance",
  "mode": "Smoke",
  "result": "PASS",
  "accepted": false,
  "blockers": [
    "BOSS_DEATH_NOT_EXERCISED_SMOKE",
    "RAW_BEHAVIOR_TREE_TICK_COUNTER_NOT_INSTRUMENTED"
  ],
  "criteria": {
    "binding_framework_one_pack_zero": true,
    "boss_death_completed_encounter": "NOT_EXERCISED_SMOKE",
    "live_actor_census_framework_one_pack_zero": true,
    "no_pack_bosshud_widget": true,
    "no_pack_montage_at_suppression": true,
    "production_player_health_800_800": true,
    "production_tick_selected_card": true,
    "raw_behavior_tree_tick_count": "BLOCKED_NOT_INSTRUMENTED",
    "sevarog_health_1500": true,
    "smoke_starter_loadout_observed": true,
    "suppressed_pack_actor_observed": true
  },
  "definition": "/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter.DA_Sevarog_Framework_Encounter",
  "map": "/Game/OneBossFight/Maps/L_SevarogArena",
  "observations": {
    "suppression": {
      "actor": "BP_ExampleGreatSwordBoss_C_3",
      "began_play": 0,
      "montage_active": 0
    }
  },
  "raw_behavior_tree_tick_evidence": "No tick counter exists in the current runtime telemetry; montage/began_play observations are retained as a proxy only.",
  "runtime_acceptance_status": "SMOKE_PASS_LIFECYCLE_UNTESTED",
  "utc_epoch": 1794869552.7916038
}
```

---

## 3. Analysis of Current Validation Gaps

| Validation Gap | Description | Risk / Impact |
| :--- | :--- | :--- |
| **1. Conflation of Boolean Flag vs Raw Data** | `criteria.raw_behavior_tree_tick_count` stores `True` or `"BLOCKED_NOT_INSTRUMENTED"` rather than an integer count and telemetry structure. | Consumers cannot verify how many frames were observed or how zero was established. |
| **2. Missing BehaviorTree Asset Binding** | Neither `acceptance.json` nor the runner verifies the target BehaviorTree asset (`BT_ExampleBoss.uasset`) or task classes. | Verification is unanchored; could pass even if an unrelated tree ran. |
| **3. Missing Run Token & World Binding** | The receipt contains no `run_token`, `world_guid`, or `session_id`. It relies solely on directory location. | Replay/transplantation risk: receipts could be copied between run directories. |
| **4. Unverified Zero vs Missing Sensor** | If `suppression["bt_attack_ticks"]` is set to `0`, `raw_behavior_tree_tick_count` evaluates to `True` without verifying sensor presence. | False positive: a null/absent sensor can be spoofed by a literal zero. |
| **5. Unbounded Sampling Window** | No timestamps or frame counters indicate when monitoring began or ended relative to combat. | A check could report 0 ticks observed during a 0-millisecond observation window. |
| **6. Lack of Cryptographic Integrity** | The runner performs no checksum validation against `editor.log` or a signed manifest. | Post-run receipt mutation cannot be detected by PowerShell runner. |

---

## 4. Conceptual Future Schema (Not Current Runtime Evidence)

The current route has no raw task-tick sensor. This is a schema proposal only: lifecycle suppression is not a task-tick monitor. Current raw task counts remain null; lifecycle observations belong in a separate evidence block.

```json
"raw_behavior_tree_telemetry": {
  "schema_version": "1.0",
  "run_token": "Run_20261116_225156_a763f2ce",
  "world_name": "L_SevarogArena",
  "encounter_definition": "/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter.DA_Sevarog_Framework_Encounter",
  "target_tree_asset": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss.BT_ExampleBoss",
  "monitored_tasks": [
    "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_TryActivateAbilitiesByTags.T_TryActivateAbilitiesByTags_C",
    "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_TryActivateSeparateAbilitiesByTags.T_TryActivateSeparateAbilitiesByTags_C"
  ],
  "sensor_binding": {
    "sensor_type": "NONE",
    "observer_class": null,
    "is_instrumented": false,
    "status": "NOT_INSTRUMENTED"
  },
  "sampling_window": null,
  "telemetry_counts": null,
  "provenance_witness": {
    "placed_actor_name": "BP_ExampleGreatSwordBoss_C_3",
    "suppression_occurred": true,
    "began_play_observed": 0,
    "active_montage_count": 0,
    "destruction_confirmed": true
  }
}
```

### Essential Distinctions: Zero Ticks vs Missing Sensor

1. **`sensor_binding.is_instrumented == false`**:
   - `telemetry_counts` MUST be `null` (not `0`).
   - `criteria.raw_behavior_tree_tick_count` MUST evaluate to `"UNINSTRUMENTED"`.
   - The runner MUST fail closed if `telemetry_counts` contains numbers while `is_instrumented` is false.
2. **`sensor_binding.is_instrumented == true`**:
   - `telemetry_counts.task_tick_invocations` MUST be a non-negative integer.
   - If `task_tick_invocations == 0` AND `sampled_frames > 0` AND `monitored_tasks` matches the target set, the criterion passes as verified zero.
3. **Suppression Recognition (`status == "SUPPRESSED_PRE_BEGIN_PLAY"`)**:
   - Reflects the reality that the actor was destroyed pre-`BeginPlay`.
   - Distinct from an active tree running for 384 frames with 0 task activations.

---

## 5. Recommended Receipt Validation Guardrails

1. **Schema Validation**:
   - The PowerShell runner should validate that `raw_behavior_tree_telemetry` contains all mandatory keys and that `run_token` exactly matches the directory token.
2. **Integrity Hash**:
   - The Python driver should write `receipt_sha256` into the status block, or compute SHA256 over `editor.log` to bind the receipt to the exact execution artifact.
3. **Fail-Closed Type Safety**:
   - Reject any receipt where numeric fields (`telemetry_counts`) are populated while `is_instrumented` is false or null.

---

## 6. Verification & Operating Discipline
- Read-only source audit of driver scripts and runner receipts.
- 0 builds, 0 Unreal Editor launches, 0 PIE runs executed, 0 tests run.
- 0 assets or configuration files modified; 0 git commits/pushes.
