# V-A067: Content Folder Structure Review (`/Game/OneBossFight`)

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-A067`, `V_A037`, `V_A039`, `V_A066`
**Sources:** Content/OneBossFight/, Scripts/Tools/test_content_script_safety.py

---

## 1. Executive Summary

This architectural review audits the layout, taxonomy, and distribution of assets under the primary project namespace `/Game/OneBossFight` (743 total `.uasset` files). 

While the project strictly respects the top-level `/Game/OneBossFight` root boundary (with 0 broken redirectors and 0 dangling cross-package references), multiple redundant and legacy test subdirectories exist that bloat the content tree, create developer ambiguity, and increase risk of staging dead assets in Shipping builds.

---

## 2. Directory Census & Structural Analysis

| Subdirectory | File Count | Primary Contents | Structural Role | Audit Assessment & Findings |
|---|:---:|---|---|---|
| `/Game/OneBossFight/Boss` | 4 | Legacy Sevarog montages (`AM_Sevarog_Death`, `AM_Sevarog_PhaseRoar`, etc.) | Legacy Prototypes | **Redundant:** Superseded by `/Game/OneBossFight/Boss01`. |
| `/Game/OneBossFight/Boss01` | 75 | Authoritative combat animations (`AM_Boss01_A1..A6`, `AN_*`, blendspaces) | Core Production | **Authoritative:** Cleanly organized under `Animations/`. Fully wired into `DirectoriesToAlwaysCook`. |
| `/Game/OneBossFight/Characters` | 12 | Base character blueprints, skeletons, physics assets | Shared Skeletons | **Authoritative:** Hosts `SK_CombatMannequin` and master anim blueprints. |
| `/Game/OneBossFight/Environment` | 82 | Arena meshes, materials, textures, braziers, dusk sky sphere | Arena Dressing | **Authoritative:** 100% Nanite enabled; clean modular structure. |
| `/Game/OneBossFight/Effects` | 8 | Flipbook textures and particle billboard materials (`MI_Boss01_FB_*`) | Legacy 2D VFX | **Taxonomy Split:** Separate from `/VFX`. |
| `/Game/OneBossFight/VFX` | 2 | Tier 1 Niagara Systems (`NS_Boss_ShockwaveRing`, `NS_Combat_ParrySpark`) | Core 3D VFX | **Taxonomy Split:** Modern Niagara emitters separated from Flipbook effects. |
| `/Game/OneBossFight/FrameworkProof` | 193 | Historical milestone DataAssets (`DA_Sevarog_AggroSwitch_R13`, `DA_Sevarog_*`) | Verification Proofs | **Developer Bloat:** 193 proof assets from early milestone tests; unreferenced by the live encounter. |
| `/Game/OneBossFight/Scratch` | 2 | Temporary Route A behavior tree and data asset | Scratch Leftovers | **Shipping Risk:** Untracked/experimental scratch assets in the content root. |
| `/Game/OneBossFight/ReviewFixtures` | 1 | Uncooked weapon item test fixture | Test Fixtures | **Test Only:** Used exclusively for ABI tests. |
| `/Game/OneBossFight/Audio` | 18 | Combat SFX, parry cues, dusk wind ambiance, sound cues | Audio Stems | **Clean:** Proper sound cue wrapping. |
| `/Game/OneBossFight/Input` | 14 | Enhanced Input actions (`IA_*`) and mapping contexts (`IMC_*`) | Controls | **Clean:** Fully bound to C++ delegates. |
| `/Game/OneBossFight/Levels` | 3 | Master arena map `L_SevarogArena`, lighting scenarios | Level Geometry | **Authoritative:** Single duel arena. |
| `/Game/OneBossFight/UI` | 26 | Boss health bar, HUD, combat prompts, victory banner | User Interface | **Clean:** Proper Slate / UMG asset split. |

---

## 3. Structural Recommendations (Consolidation Plan)

### 3.1 Unify Boss Animation Namespaces
- **Current Issue:** Having both `/Game/OneBossFight/Boss/` (4 files) and `/Game/OneBossFight/Boss01/` (75 files) causes developer confusion regarding which montages are authoritative.
- **Proposal:** Deprecate `/Game/OneBossFight/Boss/`. Relocate or retire the 4 stand-in montages and standardize on `/Game/OneBossFight/Boss01/`.

### 3.2 Consolidate Visual Effects
- **Current Issue:** 2D sprite flipbooks live in `/Effects/Flipbook`, while 3D Niagara systems live in `/VFX/`.
- **Proposal:** Consolidate under a unified `/Game/OneBossFight/VFX/` root with structured subfolders:
  - `/Game/OneBossFight/VFX/Niagara/` (`NS_*`)
  - `/Game/OneBossFight/VFX/Flipbooks/` (`FB_*`, `MI_FB_*`)
  - `/Game/OneBossFight/VFX/Materials/` (`M_VFX_*`)

### 3.3 Isolate Non-Shipping Proofs and Scratch Assets
- **Current Issue:** `/FrameworkProof/` contains 193 legacy proof DataAssets, and `/Scratch/` contains experimental behavior trees directly in the cookable Content path.
- **Proposal:** Move non-production test assets to `/Game/OneBossFight/QA/` or exclude them via `DefaultEditor.ini` (`DirectoriesToNeverCook`). This ensures zero dead proof assets leak into the Shipping IoStore container (`.ucas`).
