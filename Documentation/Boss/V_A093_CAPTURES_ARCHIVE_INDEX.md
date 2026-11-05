# V-A093: Visual Captures & Evidence Archive Index

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Canonical index of tracked visual captures, combat animation contact sheets, architecture diagrams, and review renders across the repository.
**Sources:** Unreal_Boss_Combat_Engineering_Kit/diagrams/, Docs/BossCombatReview/Execution/Claude/D3/evidence/

---

## 1. Executive Summary

This index catalogs all tracked visual assets and evidence frames utilized for combat analysis, animation timing verification, and architectural review. In accordance with project hygiene directives ([`Documentation/Boss/V_A073_COMMIT_HYGIENE_CHECK.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A073_COMMIT_HYGIENE_CHECK.md)), all heavy video footage (`*.webm`, `*.mp4`) and transient scratch directories (`scratch/sheet_frames`) remain strictly excluded from git tracking.

---

## 2. Tracked Capture & Diagram Collections

### 2.1 Architecture & Combat Flow Diagrams (`Unreal_Boss_Combat_Engineering_Kit/diagrams/`)
Primary engineering diagrams illustrating the Soulslike combat architecture (11 tracked PNGs):
* [`01_system_architecture.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/01_system_architecture.png): Subsystem boundaries and execution order.
* [`02_decision_tree.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/02_decision_tree.png): Boss combat decision and scoring evaluation.
* [`03_attack_graph.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/03_attack_graph.png): Combo graph transitions and branching weights.
* [`04_combat_state_machine.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/04_combat_state_machine.png): High-level boss combat states (Dormant -> Engage -> PhaseTransition -> Lethal).
* [`05_attack_timing.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/05_attack_timing.png): Anticipation, active damage trace, and recovery windows.
* [`06_hit_geometry.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/06_hit_geometry.png): Weapon collision boxes and sweep capsules.
* [`07_tracking_and_commit.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/07_tracking_and_commit.png): Yaw turn-rate clamping and tracking commit thresholds.
* [`08_pressure_rhythm.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/08_pressure_rhythm.png): Stamina pacing and attack frequency scaling.
* [`09_arena_and_spacing.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/09_arena_and_spacing.png): Arena ring radii, leash boundary, and brazier positions.
* [`10_damage_pipeline.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/10_damage_pipeline.png): Hit registration, poise depletion, parry evaluation, and bleed.
* [`11_utility_scoring.png`](file:///c:/UnrealProject/OneBossFight/Unreal_Boss_Combat_Engineering_Kit/diagrams/11_utility_scoring.png): Dynamic move-selection score calculation.

### 2.2 Combat Verification Evidence (`Docs/BossCombatReview/Execution/Claude/D3/evidence/`)
36 high-resolution extracted video frames documenting the canonical D3 anticipation and telegraph windows against reference footage (e.g. `frame_0012.png` .. `frame_0432.png`), cited in [`Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json).

### 2.3 Character & Boss Presentation Renders (`Import/Characters/Builds/`, `Import/Boss01/`)
* **Character Skin Previews (27 files):** Orthographic and perspective alignment renders for candidate player skins (`SKM_GirlWarrior`, `SKM_IndianGoddess`, `SKM_IndianYoddha`, `SKM_MedievalWarrior`, `SKM_Samurai`, `SKM_Viking`).
* **Boss01 Animation Contact Sheets (21 files):** Visual frame sequences in `Import/Boss01/Animations/` documenting attack poses for `AM_Boss01_A1` through `AM_Boss01_A5`.
* **Arena & Prop Previews (22 files):** Photographic references and render sheets in `Shiva_Statue_Project/` documenting arena centerpieces.

---

## 3. Exclusion Enforcement Policy

1. **Zero Media in Git:** All video files (`Morgott_*.webm`, playtest screen recordings) remain strictly untracked and excluded in `.gitignore` ([`V_A044:15`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A044_GITIGNORE_REVIEW.md#L15)).
2. **Scratch Isolation:** Ephemeral contact sheets generated during offline analysis (`scratch/sheet_frames/`) are barred from staging.
