# AG-9: Consolidated Content Production Backlog (Revision 02)

**Document ID:** `AG9_CONTENT_BACKLOG` (Rev 02)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Target Engine:** Unreal Engine 5.5.4 (`OneBossFight`, packaged 1080p / 60 FPS)  
**Parent Work Orders:** `ANTIGRAVITY_WORK_ORDER_02.md` (`AG-9`), `ANTIGRAVITY_WORK_ORDER_03.md` (`AG-13`)  
**Status:** DELIVERED & RECONCILED  
**Automated Coverage Check:** `Docs/BossCombatReview/Execution/Antigravity/check_ag9_coverage.py` (100% Coverage, 76/76 assets verified)  

---

## 1. Executive Summary & Reconciliation Notice

Per `ANTIGRAVITY_WORK_ORDER_03.md` (`AG-13`), this revised backlog reconciles all content specifications across:
- **AG-1:** Content requirements for the eight former-N/A rows (`HIT-012`, `DEF-005`, `ANM-003`, `ANM-006`, `SEL-004`, `SEL-008`, `AWR-008`, `QA-008`).
- **AG-2:** Second-boss canary content brief ("Cinder Knight Alistair"), halberd weapon mesh, and fourth player build ("Vanguard").
- **AG-3:** P1 telegraph readability curves, weapon glow emitters, and sprint attack runup audio/VFX.
- **AG-4:** Production shockwave cues (`RV-01` / `VIS-05` / `G01`), Niagara ring mesh, and ground decals.
- **AG-5:** Authored A2 trio (`AN_Boss01_A2_Raise`, `ApexHold`, `Slam`, `AM_Boss01_A2_OverheadSlam`).
- **AG-12:** Pack reuse candidate assets (`GA_AI_BlockGuard`, `GA_EnemyDodge`, `GA_EnemyGrabAttack`, etc.).

### Phase Alignment
All pseudo-phases (`P0` to `P3`) from Revision 01 have been eliminated. Every backlog item is now strictly assigned to an authoritative project program phase:
- **`DD-1`:** Data-Driven Architecture & Canary Verification (23 assets)
- **`P1`:** Visual Telegraphs & Readability (10 assets)
- **`P2`:** Attack Repertoire & Pacing (15 assets)
- **`P3`:** Fair Boss Defenses, Posture & Reactions (19 assets)
- **`P4`:** Adaptive Memory Tells & Spatial Feedback (3 assets)
- **`P7`:** Grab Fail-Safe & Edge Case Recovery (6 assets)
*(Total discrete backlog items: **76 assets**)*.

---

## 2. Program Phase Breakdown

### Phase DD-1: Canary Boss, Weapon & Build Verification (23 Assets)
*Goal: Prove data-driven registry extensibility, isolation, and multi-window/branching execution without touching Boss01.*

| Asset ID | Category | Asset Name | Engine Target Path | Replaced / Reused | Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B-01** | SkeletalMesh | `SKM_Canary_Alistair` | `/Game/OneBossFight/BossCanary/Body/SKM_Canary_Alistair` | Authored | Medium |
| **B-02** | StaticMesh | `SM_Canary_Halberd` | `/Game/OneBossFight/BossCanary/Weapons/SM_Canary_Halberd` | Authored | Small |
| **B-03** | Animation | `AN_Canary_Dormant` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_Dormant` | Authored | Small |
| **B-04** | Animation | `AN_Canary_Wake` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_Wake` | Authored | Medium |
| **B-05** | Animation | `AN_Canary_Stagger` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_Stagger` | Authored | Medium |
| **B-06** | Animation | `AN_Canary_Riposte_Victim` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_Riposte_Victim` | Authored | Medium |
| **B-07** | Animation | `AN_Canary_PhaseTransition` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_PhaseTransition` | Authored | Medium |
| **B-08** | Animation | `AN_Canary_Death` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_Death` | Authored | Medium |
| **B-09** | Animation | `AN_Canary_M1_DoubleCleave` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_M1_DoubleCleave` | Authored | Medium |
| **B-10** | Animation | `AN_Canary_M2_CrescentThrow`| `/Game/OneBossFight/BossCanary/Animations/AN_Canary_M2_CrescentThrow`| Authored | Medium |
| **B-11** | VFX | `NS_Canary_CrescentArc` | `/Game/OneBossFight/BossCanary/Effects/NS_Canary_CrescentArc` | Authored | Small |
| **B-12** | Animation | `AN_Canary_M3_FrostSlam` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_M3_FrostSlam` | Authored | Medium |
| **B-13** | VFX | `NS_Canary_FrostShockwave` | `/Game/OneBossFight/BossCanary/Effects/NS_Canary_FrostShockwave` | Authored | Medium |
| **B-14** | Animation | `AN_Canary_M4_Vault_Startup` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_M4_Vault_Startup` | Authored | Medium |
| **B-15** | Animation | `AN_Canary_M4_Vault_Success` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_M4_Vault_Success` | Authored | Medium |
| **B-16** | Animation | `AN_Canary_M4_Vault_Whiff` | `/Game/OneBossFight/BossCanary/Animations/AN_Canary_M4_Vault_Whiff` | Authored | Medium |
| **B-17** | StaticMesh | `SM_Player_SilversteelHalberd` | `/Game/OneBossFight/Characters/Builds/Weapons/SM_Player_SilversteelHalberd` | Authored | Small |
| **B-18** | UI | `T_Icon_SilversteelHalberd` | `/Game/OneBossFight/UI/Art/T_Icon_SilversteelHalberd` | Authored | Small |
| **B-19** | DataAsset | `DA_VanguardWeapon` | `/Game/OneBossFight/Data/DA_VanguardWeapon` | Authored | Small |
| **B-20** | Animation | `AN_Player_Halberd_Light01` | `/Game/OneBossFight/Characters/Builds/Animations/AN_Player_Halberd_Light01` | Authored | Medium |
| **B-21** | Animation | `AN_Player_Halberd_Light02` | `/Game/OneBossFight/Characters/Builds/Animations/AN_Player_Halberd_Light02` | Authored | Medium |
| **B-22** | Animation | `AN_Player_Halberd_HeavyCharged` | `/Game/OneBossFight/Characters/Builds/Animations/AN_Player_Halberd_HeavyCharged` | Authored | Medium |
| **B-23** | Animation | `AN_Player_Halberd_DodgeThrust` | `/Game/OneBossFight/Characters/Builds/Animations/AN_Player_Halberd_DodgeThrust` | Authored | Medium |

---

### Phase P1: Visual Telegraphs & Readability (10 Assets)
*Goal: Provide unambiguous human-readable telegraphs, shockwave visual parity, and sprint warnings.*

| Asset ID | Category | Asset Name | Engine Target Path | Replaced / Reused | Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B-24** | Curve | `Curve_TelegraphEase` | `/Game/OneBossFight/Boss01/Data/Curve_TelegraphEase` | Authored | Small |
| **B-25** | VFX | `NS_Boss01_ChargeUp` | `/Game/OneBossFight/Boss01/Effects/NS_Boss01_ChargeUp` | Authored | Small |
| **B-26** | Audio | `A_Boss01_Windup_Hum` | `/Game/OneBossFight/Boss01/Audio/A_Boss01_Windup_Hum` | Authored | Small |
| **B-27** | VFX | `NS_Boss01_Sprint_Runup` | `/Game/OneBossFight/Boss01/Effects/NS_Boss01_Sprint_Runup` | Authored | Small |
| **B-28** | Audio | `A_Boss01_Sprint_Warning` | `/Game/OneBossFight/Boss01/Audio/A_Boss01_Sprint_Warning` | Authored | Small |
| **B-29** | VFX | `NS_Boss01_Shockwave_Ring` | `/Game/OneBossFight/Boss01/Effects/NS_Boss01_Shockwave_Ring` | Authored | Medium |
| **B-30** | Material | `M_ShockwaveDecal` | `/Game/OneBossFight/Boss01/Materials/M_ShockwaveDecal` | Authored | Small |
| **B-31** | Audio | `A_Boss01_Shockwave_Impact` | `/Game/OneBossFight/Boss01/Audio/A_Boss01_Shockwave_Impact` | Authored | Small |
| **B-32** | Audio | `A_Boss01_Shockwave_Travel` | `/Game/OneBossFight/Boss01/Audio/A_Boss01_Shockwave_Travel` | Authored | Small |
| **B-33** | AnimNotify | `ANS_SetDesiredRotation_C` | `/Game/AdvancedARPGCombat/.../ANS_SetDesiredRotation_C` | Reused Pack | Small |

---

### Phase P2: Attack Repertoire & Pacing (15 Assets)
*Goal: Author A2 overhead slam trio, variable hold apex variants, motion warp lunges, and pacing fallbacks.*

| Asset ID | Category | Asset Name | Engine Target Path | Replaced / Reused | Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B-34** | Animation | `AN_Boss01_A2_Raise` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_Raise` | Authored | Medium |
| **B-35** | Animation | `AN_Boss01_A2_ApexHold` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_ApexHold` | Authored | Medium |
| **B-36** | Animation | `AN_Boss01_A2_Slam` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_Slam` | Authored | Medium |
| **B-37** | Montage | `AM_Boss01_A2_OverheadSlam` | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2_OverheadSlam` | Authored | Medium |
| **B-38** | Audio | `A_Boss01_A2_ReleaseCue` | `/Game/OneBossFight/Boss01/Audio/A_Boss01_A2_ReleaseCue` | Authored | Small |
| **B-39** | Animation | `AN_Boss01_A2_VariableApex_Base` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_VariableApex_Base` | Authored | Medium |
| **B-40** | Animation | `AN_Boss01_A2_VariableApex_Short`| `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_VariableApex_Short`| Authored | Medium |
| **B-41** | Animation | `AN_Boss01_A2_VariableApex_Long` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_VariableApex_Long` | Authored | Medium |
| **B-42** | VFX | `NS_ApexHold_Glow` | `/Game/OneBossFight/Boss01/Effects/NS_ApexHold_Glow` | Authored | Small |
| **B-43** | Audio | `A_ApexHold_Whirr` | `/Game/OneBossFight/Boss01/Audio/A_ApexHold_Whirr` | Authored | Small |
| **B-44** | Animation | `AN_Boss01_LungeWarp_Attack` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_LungeWarp_Attack` | Authored | Med-Lrg |
| **B-45** | Animation | `AN_Boss01_Turn_L90` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Turn_L90` | Authored | Small |
| **B-46** | Animation | `AN_Boss01_Turn_R90` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Turn_R90` | Authored | Small |
| **B-47** | Animation | `AN_Boss01_Fallback_PacingWalk` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Fallback_PacingWalk` | Authored | Small |
| **B-48** | Animation | `AN_Boss01_Fallback_Flourish` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Fallback_Flourish` | Authored | Small |

---

### Phase P3: Fair Boss Defenses, Posture & Reactions (19 Assets)
*Goal: Implement and prove guard block, directional dodge, and proactive parry, reusing pack assets where viable.*

| Asset ID | Category | Asset Name | Engine Target Path | Replaced / Reused | Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B-49** | Ability | `GA_AI_BlockGuard` | `/Game/AdvancedARPGCombat/.../GA_AI_BlockGuard` | Reused Pack | Small |
| **B-50** | Montage | `Ability_AI_Block2_Montage` | `/Game/AdvancedARPGCombat/.../Ability_AI_Block2_Montage` | Reused Pack | Small |
| **B-51** | Montage | `Deflect_InPlace_AI_Montage` | `/Game/AdvancedARPGCombat/.../Deflect_InPlace_AI_Montage` | Reused Pack | Small |
| **B-52** | Ability | `GA_EnemyBlockReaction` | `/Game/AdvancedARPGCombat/.../GA_EnemyBlockReaction` | Reused Pack | Small |
| **B-53** | Ability | `GA_EnemyDodge` | `/Game/AdvancedARPGCombat/.../GA_EnemyDodge` | Reused Pack | Small |
| **B-54** | Montage | `Dodge_To_Idle_Montage` | `/Game/AdvancedARPGCombat/.../Dodge_To_Idle_Montage` | Reused Pack | Small |
| **B-55** | Ability | `GA_EnemyParried` | `/Game/AdvancedARPGCombat/.../GA_EnemyParried` | Reused Pack | Small |
| **B-56** | AnimNotify | `ParryFramesNS` | `/Game/AdvancedARPGCombat/.../ParryFramesNS` | Reused Pack | Small |
| **B-57** | Animation | `AN_Boss01_Guard_Enter` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Guard_Enter` | Authored | Medium |
| **B-58** | Animation | `AN_Boss01_Guard_Loop` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Guard_Loop` | Authored | Medium |
| **B-59** | Animation | `AN_Boss01_Guard_Exit` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Guard_Exit` | Authored | Medium |
| **B-60** | Animation | `AN_Boss01_Guard_Stagger` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Guard_Stagger` | Authored | Medium |
| **B-61** | Animation | `AN_Boss01_Parry_Startup` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Parry_Startup` | Authored | Medium |
| **B-62** | Animation | `AN_Boss01_Parry_Deflect` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Parry_Deflect` | Authored | Medium |
| **B-63** | Animation | `AN_Boss01_Parry_CounterSlash` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Parry_CounterSlash` | Authored | Medium |
| **B-64** | Animation | `AN_Boss01_Parry_Whiff` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Parry_Whiff` | Authored | Medium |
| **B-65** | Animation | `AN_Boss01_Dodge_Back` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Dodge_Back` | Authored | Medium |
| **B-66** | Animation | `AN_Boss01_Dodge_Left` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Dodge_Left` | Authored | Medium |
| **B-67** | Animation | `AN_Boss01_Dodge_Right` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Dodge_Right` | Authored | Medium |

---

### Phase P4: Adaptive Memory Tells (3 Assets)
*Goal: Provide player feedback when boss adapts utility weights based on accumulated combat habits.*

| Asset ID | Category | Asset Name | Engine Target Path | Replaced / Reused | Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B-68** | Animation | `AN_Boss01_Adapt_Tell` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Adapt_Tell` | Authored | Small |
| **B-69** | VFX | `NS_AdaptationGlow` | `/Game/OneBossFight/Boss01/Effects/NS_AdaptationGlow` | Authored | Small |
| **B-70** | Audio | `A_AdaptationHum` | `/Game/OneBossFight/Boss01/Audio/A_AdaptationHum` | Authored | Small |

---

### Phase P7: Grab Fail-Safe & Edge Case Recovery (6 Assets)
*Goal: Paired two-actor grab attack with bulletproof abort, stagger release, and victim alignment.*

| Asset ID | Category | Asset Name | Engine Target Path | Replaced / Reused | Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B-71** | Ability | `GA_EnemyGrabStart` | `/Game/AdvancedARPGCombat/.../GA_EnemyGrabStart` | Reused Pack | Small |
| **B-72** | Ability | `GA_EnemyGrabAttack` | `/Game/AdvancedARPGCombat/.../GA_EnemyGrabAttack` | Reused Pack | Small |
| **B-73** | DataAsset | `DefaultGrabAttackData` | `/Game/AdvancedARPGCombat/.../DefaultGrabAttackData` | Reused Pack | Small |
| **B-74** | Ability | `GA_GrabVictim` | `/Game/AdvancedARPGCombat/.../GA_GrabVictim` | Reused Pack | Small |
| **B-75** | Animation | `AN_Boss01_Grab_Attack` | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Grab_Attack` | Authored | Med-Lrg |
| **B-76** | Animation | `AN_Player_Grab_Victim` | `/Game/OneBossFight/.../AN_Player_Grab_Victim` | Authored | Med-Lrg |

---

## 3. Automated Coverage Verification

The python script [`check_ag9_coverage.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/check_ag9_coverage.py) executes a 100% loss-less audit across all input briefs:
```bash
python -I Docs/BossCombatReview/Execution/Antigravity/check_ag9_coverage.py
```
**Verification Output:**
```
[CheckCoverage] Total rows in CSV: 76
OK: All 26 assets from AG1 present in CSV.
OK: All 23 assets from AG2 present in CSV.
OK: All 5 assets from AG3 present in CSV.
OK: All 4 assets from AG4 present in CSV.
OK: All 5 assets from AG5 present in CSV.
OK: All 13 assets from AG12 present in CSV.

SUCCESS: All 76 assets verified. 100% coverage across AG1, AG2, AG3, AG4, AG5, AG12. Valid program phases verified.
```

---

## 4. Evidence and Limits Table

| Backlog Component | Evidence Source | Status | Offline Boundary / Limit |
| :--- | :--- | :--- | :--- |
| **Canary Assets (B-01 to B-23)** | `Docs/BossCombatReview/Execution/Antigravity/AG2_CANARY_CONTENT_SPEC.md` | Reconciled in CSV | Authored specifications; binary `.fbx` and `.uasset` generation awaiting execution phase. |
| **Telegraphs & RV-01 (B-24 to B-32)** | `AG3_TELEGRAPH_READABILITY_SPEC.md`, `AG4_SHOCKWAVE_CUE_SPEC.md` | Reconciled in CSV | Niagara systems and float curves designed; parameter verification requires editor session. |
| **A2 Authored Trio (B-34 to B-38)** | `AG5_A2_INTEGRATION_SPEC.md` | Reconciled in CSV | Section durations matched to sidecar targets; composite montage assembly awaiting cutover. |
| **Reused Pack Assets (B-49 to B-56, B-71 to B-74)** | `Docs/BossCombatReview/Execution/Claude/Evidence/exports/` | Reconciled in CSV | Confirmed via CDO exports; runtime execution on Ember Warden requires project style binding. |
| **Parry Deficit Confirmation** | File search in `Blueprints/Abilities/AI/` | Reconciled in CSV | Proactive parry confirmed missing from pack; custom clips retained (B-61 to B-64). |
