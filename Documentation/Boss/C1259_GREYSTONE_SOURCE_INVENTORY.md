# C1259 Greystone Source Animation & Montage Inventory

**Authority:** Claude Lead Directive `[C-1259]` / C-1259a (2026-11-10)  
**Status:** Read-only Source Inventory Deliverable (Zero engine use, zero asset mutations)  
**Purpose:** Precise enumeration of every montage and sequence asset the Greystone child player character will play, distinguishing existing assets from those requiring new montage wrappers, citing exact `git ls-files` paths and verified on-disk `/Game/OneBossFight/GreystonePack/` asset paths.

---

## 1. Inventory Classification & Packaging Rules

Per `Documentation/Boss/SWITCH_PLAN.md` and repository `.gitignore` rules:
1. **Tracked FitTest Assets (`git ls-files`):** Retargeted Elden Ring candidate sequences live under `Content/OneBossFight/Player/FitTest/Greystone/` and are tracked in git. They are raw `AnimSequence` assets; none currently have an authored montage wrapper.
2. **On-Disk GreystonePack Assets (`.gitignore:115`):** The 238 retargeted pack animations live on disk under `Content/OneBossFight/GreystonePack/` (`/Game/OneBossFight/GreystonePack/`). Per project discipline (2026-10-20 third-party pack rule), these stay off git remote tracking, but are loaded at runtime by the child Blueprint.
3. **Packaging / Cook Coverage:** Cook coverage is provided via `ProjectPackagingSettings` (`DirectoriesToAlwaysCook`).

---

## 2. Tracked FitTest ER Sequences (`git ls-files`) & Proposed Montage Wrappers

These 4 sequences were produced by the C-1227 fit pipeline and won unanimous blind selection (Candidate_A = Greystone, 47/48, 97.9%).

| Action / Slot | Tracked Source Sequence (`git ls-files`) | Game Object Path | Proposed Target Montage Wrapper | Wrapper Status | Override Property on `URPGDodgeTiming` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Neutral Backstep** | `Content/OneBossFight/Player/FitTest/Greystone/AN_ER_Backstep_Mixamo_V2_Fit_Greystone.uasset` | `/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Backstep_Mixamo_V2_Fit_Greystone` | `AM_ER_Backstep_Mixamo_V2_Fit_Greystone` | **NEEDS WRAPPER** | `URPGDodgeTiming.BackstepMontage` |
| **Air Light Attack** | `Content/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_Air_Light_Fit_Greystone.uasset` | `/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_Air_Light_Fit_Greystone` | `AM_ER_Attack_Air_Light_Fit_Greystone` | **NEEDS WRAPPER** | `URPGDodgeTiming.AirLightMontage` |
| **Air Heavy Plunge** | `Content/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_Air_Heavy_Plunge_Fit_Greystone.uasset` | `/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_Air_Heavy_Plunge_Fit_Greystone` | `AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone` | **NEEDS WRAPPER** | `URPGDodgeTiming.AirHeavyMontage` |
| **Guard Counter** | `Content/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_GuardCounter_Fit_Greystone.uasset` | `/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_GuardCounter_Fit_Greystone` | `AM_ER_Attack_GuardCounter_Fit_Greystone` | **NEEDS WRAPPER** | `URPGDodgeTiming.GuardCounterMontage` |

### Additional Tracked FitTest Support Assets (`git ls-files`):
- `Content/OneBossFight/Player/FitTest/Greystone/BlockLoop_Fit_Greystone.uasset` (Pack block loop control sequence)
- `Content/OneBossFight/Player/FitTest/Greystone/Dodge_Small_Forward_Roll_Fit_Greystone.uasset` (Pack forward roll control sequence)
- `Content/OneBossFight/Player/FitTest/Greystone/IK_Fit_Greystone.uasset` (Greystone IK Rig)
- `Content/OneBossFight/Player/FitTest/Greystone/RTG_ERFit_Greystone.uasset` (Mannequin-to-Greystone IK Retargeter)

---

## 3. Existing On-Disk GreystonePack Combat Montages & Sequences

All assets below exist physically on disk under `Content/OneBossFight/GreystonePack/` (`/Game/OneBossFight/GreystonePack/`).

### 3.1 Dodge & Roll Montages (`GA_Player_Dodge.DodgeMontage` Map)

| Role / Input | Existing Montage Asset Path | Underlying Sequence Path | Asset Status |
| :--- | :--- | :--- | :--- |
| **Quick Roll (Directional)** | `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey` | `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Grey` | **EXISTS** |
| **Dodge to Idle (Full / Recover)** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Grey` | **EXISTS** |

*Note on Dodge Timing Integration:* When possessed, `URPGDodgeTiming` overrides `QuickMontage` with `Dodge_Small_Forward_Roll_Montage_Grey` and `FullMontage` with `Dodge_To_Idle_Montage_Grey`. Neutral tap inserts the proposed `AM_ER_Backstep_Mixamo_V2_Fit_Greystone` into the map.

---

### 3.2 Primary Weapon Attacks (`1Handed` Melee Attacks)

| Attack Action | Existing Montage Asset Path | Underlying Sequence Path | Asset Status |
| :--- | :--- | :--- | :--- |
| **Light Attack 1 (Primary A)** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Anim_Grey` | **EXISTS** |
| **Light Attack 2 (Primary B)** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryB_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryB_Anim_Grey` | **EXISTS** |
| **Light Attack 3 (Primary C)** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryC_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryC_Anim_Grey` | **EXISTS** |
| **Heavy / Strong Attack (D Med)** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Attack_D_Med_MSA_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Attack_D_Med_MSA_Anim_Grey` | **EXISTS** |
| **Charged Attack** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/ChargedAttack_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/ChargedAttack_Anim_Grey` | **EXISTS** |
| **Special Ability E** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Ability_E_Anim_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Ability_E_Anim_Grey` | **EXISTS** |

---

### 3.3 Defense, Guard & Deflect

| Action | Existing Montage Asset Path | Underlying Sequence Path | Asset Status |
| :--- | :--- | :--- | :--- |
| **Block Idle / Loop** | *(Loop played via AnimBP state)* | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Defend/BlockLoop_Grey` | **EXISTS** |
| **Deflect / Guard Impact** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Defend/Deflect_InPlace_Anim_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Defend/Deflect_InPlace_Anim_Grey` | **EXISTS** |
| **AI / Heavy Block 2** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/AI/Defend/Ability_AI_Block2_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/AI/Defend/BlockLoop_Grey` | **EXISTS** |

---

### 3.4 Flask / Potion Consumption

| Action | Existing Montage Asset Path | Underlying Sequence Path | Asset Status |
| :--- | :--- | :--- | :--- |
| **Drinking Potion / Flask** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/DrinkingPotion_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/DrinkingPotion_Anim_Grey` | **EXISTS** |

*Note:* Monitored by `ARPGFrameworkBossCharacter::TickFlask()` for heal punish reaction windows.

---

### 3.5 Hit Reactions (`1Handed`)

| Direction | Existing Montage Asset Path | Underlying Sequence Path | Asset Status |
| :--- | :--- | :--- | :--- |
| **Hit React Front** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Front_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Front_Anim_Grey` | **EXISTS** |
| **Hit React Back** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Back_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Back_Anim_Grey` | **EXISTS** |
| **Hit React Left** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Left_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Left_Anim_Grey` | **EXISTS** |
| **Hit React Right** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Right_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/HitReactions/HitReact_Right_Anim_Grey` | **EXISTS** |

---

### 3.6 Death Sequences & Montages

| Direction | Existing Montage Asset Path | Underlying Sequence Path | Asset Status |
| :--- | :--- | :--- | :--- |
| **Death Forward** | `/Game/OneBossFight/GreystonePack/MagicCombatSystem/Animations/Death/Death_Fwd_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MagicCombatSystem/Animations/Death/Death_Fwd_Grey` | **EXISTS** |
| **Death Backward** | `/Game/OneBossFight/GreystonePack/MagicCombatSystem/Animations/Death/Death_Back_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MagicCombatSystem/Animations/Death/Death_Back_Grey` | **EXISTS** |

---

### 3.7 Weapon Equip & Sheath

| Action | Existing Montage Asset Path | Underlying Sequence Path | Asset Status |
| :--- | :--- | :--- | :--- |
| **Draw Sword** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Equip/DrawSword_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Equip/LightWeaponDraw_Anim_Grey` | **EXISTS** |
| **Sheath Sword** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Equip/SheathSword_Montage_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Equip/LightWeaponSheath_Anim_Grey` | **EXISTS** |
| **Quick Cycle Shield** | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/1Handed/Equip/QuickCycleShield_Montage_Grey` | — | **EXISTS** |

---

## 4. Summary Matrix: Existing vs Needing Wrappers

| Category | Total Assets | Already Exists as Montage | Needs Montage Wrapper | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **ER Overrides (C-1227)** | 4 | 0 | **4** | Sequences tracked in git; wrappers must be authored with notify readback |
| **Dodge / Roll** | 2 | **2** | 0 | `Dodge_Small_Forward_Roll_Montage_Grey`, `Dodge_To_Idle_Montage_Grey` |
| **1H Melee Attacks** | 6 | **6** | 0 | Primary A/B/C, Heavy D, Charged, Ability E |
| **Defense / Deflect** | 2 | **2** | 0 | BlockLoop (AnimBP), Deflect_InPlace_Anim_Montage_Grey |
| **Flask / Potion** | 1 | **1** | 0 | `DrinkingPotion_Montage_Grey` |
| **Hit Reactions** | 4 | **4** | 0 | Front, Back, Left, Right |
| **Death** | 2 | **2** | 0 | Forward, Backward |
| **Equip / Sheath** | 3 | **3** | 0 | Draw, Sheath, QuickCycle |
| **Total** | **24** | **20** | **4** | Only the 4 ER override sequences require new montage wrappers |

---

## 5. Next Steps for Implementation (C-1257 / Codex)

1. **Montage Wrapper Authoring:**
   - Author the 4 proposed montage wrappers under `Content/OneBossFight/Player/Greystone/` (or matching directory):
     - `AM_ER_Backstep_Mixamo_V2_Fit_Greystone`
     - `AM_ER_Attack_Air_Light_Fit_Greystone`
     - `AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone`
     - `AM_ER_Attack_GuardCounter_Fit_Greystone`
   - Preserve authored notify windows (`ANS_iFrames`, `ANS_InputBuffer`, `ANS_CollisionTrace`, `ANS_DisableMovement`).
2. **Child Blueprint Assignment:**
   - Assign the 4 new montages to `URPGDodgeTiming` on `BP_GreystoneERPlayer`.
   - Assign `QuickMontage` -> `Dodge_Small_Forward_Roll_Montage_Grey` and `FullMontage` -> `Dodge_To_Idle_Montage_Grey`.
3. **Execution of Technical Gates:**
   - Run C-1257b paired root-motion PIE tests (mannequin vs Greystone <= 10% distance difference).
   - Capture owner review video reel and evaluate against `C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md`.
