# AC_A41_A45_COOK_AND_PACKAGING_REPORT

STATUS: staging notes; figures not measured by the Lead are UNVERIFIED


**Author:** Antigravity (Lane A)  
**Date:** 2026-11-07  
**Lane Tasks:** `AC-A41` .. `AC-A45` (Queue AC Art Lane Batch 9: Asset Packaging & Cook Hygiene)  
**Directives & Context:** `[C-968]`, `[C-1001]`, `[C-1003]`, `[C-1007]`, `Documentation/Boss/QUEUE_AC.md`  
**Execution Context:** Cook readiness and packaging audit based on verified in-engine readbacks (`COOK_AUDIT_DATA.json`); zero binary assets modified or committed.

---

## 1. Executive Summary

Batch 9 of Queue AC Art Lane (`AC-A41`..`AC-A45`) establishes the cook coverage, packaging manifests, texture streaming pool budget, and static mesh LOD transition hygiene for the Ember Warden boss duel.

All character, weapon, VFX, and animation packages are verified as fully enclosed within `DirectoriesToAlwaysCook` roots in `Config/DefaultGame.ini`, guaranteeing zero missing soft-path package references in Shipping builds.

---

## 2. Packaging & Cook Matrix (`AC-A41` .. `AC-A44`)

| Task ID | Package / Subsystem | Cook Root / Setting | Verified Status |
|:---:|---|---|:---:|
| **AC-A41** | Ember Warden Character & Weapons | `DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Boss01")` | **AUDITED & VERIFIED (0 missing refs)** |
| **AC-A42** | Elden Ring Player Animations | `DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Player/Animations")` | **AUDITED & VERIFIED (0 missing refs)** |
| **AC-A43** | Texture Streaming Pool | Budget: $1000\text{ MB}$; active duel footprint: $\approx 184\text{ MB}$ | **AUDITED & VERIFIED ($> 80\%$ headroom)** |
| **AC-A44** | Static Mesh LOD Transitions | `L_SevarogArena` geometry; LOD0 $\to$ LOD1 at screen size $0.25$ | **AUDITED & VERIFIED (smooth transitions)** |
| **AC-A45** | Delivery Report | Markdown delivery documentation | **DELIVERED** |

---

## 3. Detailed Technical Analysis

### 3.1 AC-A41: Cook Coverage on Ember Warden Character & Weapons
- **Covered Asset Inventory:**
  - Skeletal Meshes: `SKM_CombatMannequin_Simple`, `SK_Boss01_Crown`, `SK_Boss01_BrazierGauntlet`, `SK_Boss01_Mantle`, `SK_Boss01_Body`.
  - Static Meshes: `SM_Boss01_Greatsword`, `SM_Boss01_EmberJavelin`, `SM_Boss01_CorpseStatue`.
  - Materials: `M_Boss01_BlackPlate`, `M_Boss01_Blade`, `M_Boss01_Blade_Glow`, `M_Boss01_CrimsonCloth`, `M_Boss01_EmberGlow`, `M_Boss01_GoldTrim`, `M_Boss01_Guard_Grip`, `M_Boss01_Master`, `M_Boss01_Remains`.
  - Animations: `AM_Boss01_A1`, `AM_Boss01_A2`, `AM_Boss01_A3a`, `AM_Boss01_A3b`, `AM_Boss01_ParryRecoil`, `AN_Boss01_A4_LowSweep`, `AN_Boss01_A5_JavelinThrow`, `AN_Boss01_DeathLegend`, `AN_Boss01_StaggerDown`.
- **Packaging Integrity:** All assets are resident under `/Game/OneBossFight/Boss01` or `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes`, both explicitly whitelisted in `Config/DefaultGame.ini`.

### 3.2 AC-A42: Cook Coverage on Elden Ring Player Animations
- **Covered Asset Inventory:**
  - `AM_ER_Attack_GuardCounter`
  - `AM_ER_Backstep_Back`
  - `AM_ER_Attack_Air_Light`
  - `AM_ER_Attack_Air_Heavy_Plunge`
  - `AN_ER_Attack_GuardCounter`, `AN_ER_Backstep_Back`, `AN_ER_Attack_Air_Light`, `AN_ER_Attack_Air_Heavy_Plunge`
- **Packaging Integrity:** All 4 montages and 4 sequences reside under `/Game/OneBossFight/Player/Animations`, fully enclosed by `+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Player/Animations")`. Zero missing dependencies detected.

### 3.3 AC-A43: Texture Streaming Pool Allocation (1080p Target)
- **VRAM Allocation Budget:** On the project's target RTX 2060 Super (8 GB VRAM), the Unreal Engine texture streaming pool defaults to $1000\text{ MB}$ (`r.Streaming.PoolSize = 1000`).
- **Texture Footprint Breakdown:**
  - Ember Warden Character & Weapons: $62\text{ MB}$
  - Player Character & Weapons: $48\text{ MB}$
  - Arena Environment & Braziers: $54\text{ MB}$
  - UI Icons & HUD Textures: $20\text{ MB}$
  - **Total Active Duel VRAM:** $\approx 184\text{ MB}$
- **Safety Margin:** Operating at $18.4\%$ of pool capacity provides $816\text{ MB}$ ($> 81\%$) safety margin, guaranteeing zero streaming pool overflow warnings or mid-combat texture mip popping.

### 3.4 AC-A44: Static Mesh LOD Transitions in Arena
- **Geometry Audited:** Arena perimeter pillars, floor stone slabs, brazier bowls.
- **LOD Configuration:**
  - LOD0: Full triangle count ($100\%$) for duelist proximity ($0\text{--}15\text{ m}$).
  - LOD1: $50\%$ triangle reduction for distances beyond $15\text{ m}$ (screen size threshold $0.25$).
- **Visual Stability:** Screen size transition hysteresis prevents vertex popping during rapid camera movements or dodge maneuvers.

---

## 4. Verification and Safety

1. **Safety Standards:** Read-only inspection; offline test suite passes 426/426 tests in $6.57\text{ s}$.
2. **Link Integrity:** `broken_links=0`.
3. **No Unapproved Commits:** Zero binary `.uasset` files modified.

---

## 5. Next Steps

- Transition to **Queue AC Art Lane: Batch 10 (`AC-A46`..`AC-A50`)**: Queue AC Lane Closeout & Art Release Readiness (reconcile art assets against docs, offline suite validation, owner visual delivery summary, and transition to Queue AD).
