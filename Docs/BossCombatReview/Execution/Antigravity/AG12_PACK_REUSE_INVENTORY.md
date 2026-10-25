# AG-12: Pack Reuse Inventory for the Eight Former-N/A Rows

**Document ID:** `AG12_PACK_REUSE_INVENTORY`  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Work Order:** `ANTIGRAVITY_WORK_ORDER_03.md` (`AG-12`)  
**Status:** DELIVERED  

---

## 1. Executive Summary & Objective

In `[C-110]`, Technical Lead Claude discovered that the third-party pack (`Content/AdvancedARPGCombat/`) contains pre-built enemy-side abilities, reactions, and animation montages corresponding to mechanics previously assumed to require ground-up authoring under `AG1_CONTENT_REQUIREMENTS.md` and `Codex/D05_CONDITIONAL_ROWS_COSTING.md`.

This inventory investigates all candidate pack assets across:
- `HIT-012` (Grab Attack & Victim Reaction)
- `DEF-005` (Guard, Parry, and Dodge)
- `ANM-003` (Variable Hold / Delay Telegraph)
- `ANM-006` (Motion Warping / Alignment)
- `SEL-008` (Idle / Reposition / Retreat)
- `SEL-004`, `AWR-008`, `QA-008` (Phase, Environment, Networking)

### Epistemological Rule
All analyses in this document are based strictly on **offline inspection** (directory listings, binary header signatures, live CDO exports in `Docs/BossCombatReview/Execution/Claude/Evidence/exports/`, and pack documentation `Documentation/ARPG_PACK_INSPECTION.md`). **Zero pack abilities are assumed functional on Ember Warden** until granted via a project-owned combat style and proven in PIE.

---

## 2. Granular Candidate Asset Inventory

### 2.1 HIT-012: Grab Attack & Victim Reactions
*Target Requirement:* Boss grab move with active capture window, paired victim animation, escape/damage resolution, and interrupt/abort safety.

| Asset Path | Asset Type | Inspected CDO / Property Data | Applicable Mechanic | Project Content Replaced in AG1 | Unknowns & Evidence Limits | Required Claude Editor Export |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyGrabStart` | Blueprint Ability | Derived from `GA_EnemyAbility`. Initiates grab query. | Grab Initiation | Custom telegraph/initiation montage | Unknown if spatial query handles non-standard capsule heights. | Full graph text + CDO |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyGrabAttack` | Blueprint Ability | `CDO_GA_EnemyGrabAttack.t3d`: `AbilityTags=(TagName="Ability.Grab.Attack")`, `AttackData=DefaultGrabAttackData`, `BlockGameplayCuesByImpactTags=(ImpactDecision.BlockedHit, DeflectedHit, ParriedHit)`. | Grab Hold & Strike | Custom grab attacker montage | Does not prove victim synchronization, input lockout, or network replication. | Full graph text + LinkedTo endpoints |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/DataAssets/AttackData/DefaultGrabAttackData` | Attack Data Asset | References paired montages and hit timing. | Grab Parameters | Custom DataAsset creation | Asset text unexported; actual montage references unknown. | Full DataAsset text export |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Shared/HitReactions/GA_GrabVictim` | Blueprint Ability | Victim counterpart. Locks player pawn during grab sequence. | Victim Reaction | Custom player victim montage / camera lock | Unknown if input restoration works if boss is killed/staggered mid-grab. | Full graph text + CDO |

**Replaced AG1 Content:**
- Replaces requirement for scratch-authored paired animations (`AN_Boss01_Grab_Attacker`, `AN_Player_Grab_Victim`).
- **Residual Work:** Authoring boss-specific greatsword grab telegraph (if pack montage uses unarmed/claws), C++ reservation token lifecycle, and fail-safe release upon boss death/stagger.

---

### 2.2 DEF-005: Guard, Parry, and Dodge
*Target Requirement:* Boss defensive capabilities: finite guard with posture damage, reactive or proactive parry, and evasive dodge.

| Asset Path | Asset Type | Inspected CDO / Property Data | Applicable Mechanic | Project Content Replaced in AG1 | Unknowns & Evidence Limits | Required Claude Editor Export |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_AI_BlockGuard` | Blueprint Ability | `CDO_GA_AI_BlockGuard.t3d`: `AbilityTags=(Ability.Block)`, `ActivationOwnedTags=(Status.Blocking)`, `BlockingHeldTime=2.0s`, `MaxBlockingDistance(Melee)=350.0`, `CancelAbilitiesWithTags=(Ability.Sprint)`. | Boss Guard / Block | `AN_Boss01_Block_Start`, `AN_Boss01_Block_Loop`, `AN_Boss01_Block_End` | Cost/stamina budget is None (`CostGameplayEffect=None`). Directional blocking angle unknown. | Full graph text + CDO |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/Defend/Ability_AI_Block2_Montage` | AnimMontage | 9,155 bytes. Contains block raise and hold. | Guard Visuals | Custom block montage | Sockets/notifies unverified. Bound to mannequin skeleton. | Montage notify & section export |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/Defend/Deflect_InPlace_AI_Montage` | AnimMontage | 12,079 bytes. Block deflection recoil. | Guard Deflection | Custom block-recoil animation | Deflection window duration unverified. | Montage notify & section export |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/HitReactions/GA_EnemyBlockReaction` | Blueprint Ability | Triggers recoil when block is struck. | Block Intake | Custom hit intake logic | Integration with project poise/hyperarmor component unverified. | Full graph text + CDO |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyDodge` | Blueprint Ability | `CDO_GA_EnemyDodge.t3d`: `AbilityTags=(Ability.Dodge)`, `Cooldown=10.0s`, `DodgeMontage=()`, `bIsDirectional=False`. | Boss Dodge | `AN_Boss01_Dodge_Step` | CDO `DodgeMontage` is empty! Must be populated at runtime or data asset. Directional dodging disabled. | Full graph text + CDO |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage` | AnimMontage | 16,953 bytes. Roll / dodge recovery into idle. | Dodge Visuals | Custom dodge animation | Whether root motion is baked or in-place is unverified. | Montage length, rate, root motion export |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Animation/AnimNotifies/ParryFramesNS` | AnimNotifyState | Defines parry vulnerability / active parry window. | Parry Window Detection | Custom NotifyState | Unknown if pack AI supports proactive parry. | Full Blueprint text export |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyParried` | Blueprint Ability | `CDO_GA_EnemyParried.t3d`: Stagger state when enemy is parried by player. | Stagger on Parry | Custom parry stagger montage | **CRITICAL:** This is a REACTION to being parried, NOT an ability for AI to parry the player! | Full graph text + CDO |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Player/GA_PlayerParry` | Blueprint Ability | Player-side proactive parry. | Proactive Parry Reference | None directly (player ability) | AI cannot use directly without controller adapter. | Full graph text + CDO |

**Replaced AG1 Content:**
- Guard block montages and block-recoil reaction (`Ability_AI_Block2_Montage`, `Deflect_InPlace_AI_Montage`).
- Dodge animation fallback (`Dodge_To_Idle_Montage`).
- **CRITICAL DEFICIT IDENTIFIED:** The pack contains **zero proactive AI parry abilities**. `GA_EnemyParried` is strictly the victim stagger when the player parries the AI. Proactive boss parry remains a **custom gameplay logic requirement**.

---

### 2.3 ANM-003: Variable Hold / Delay Telegraph
*Target Requirement:* Dynamically modifiable telegraph hold duration (e.g. $0.3\text{ s}$ to $1.2\text{ s}$) based on distance, player input, or AI dice rolls.

| Asset Path | Asset Type | Inspected Properties | Applicable Mechanic | Replaced Content | Unknowns & Limits | Required Export |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GS_Attack01_Montage` through `04` | AnimMontage | Section blend times: 0.25s. All pack attacks use static linear playback. | Attack Bases | None directly | Pack does NOT support dynamic variable hold natively. | Section and notify tables |

**Finding:** The pack ships **no variable-hold infrastructure**. Variable hold must be implemented via montage section loops or play-rate scaling (`Montage_SetPlayRate`) driven by C++ / Project BT.

---

### 2.4 ANM-006: Motion Warping / Target Alignment
*Target Requirement:* Mid-telegraph rotation and bounded position warp toward player capsule.

| Asset Path | Asset Type | Inspected Properties | Applicable Mechanic | Replaced Content | Unknowns & Limits | Required Export |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/Game/AdvancedARPGCombat/.../AnimNotifies/ANS_SetDesiredRotation_C` | AnimNotifyState | Present in `GS_Attack01_Montage` (0.000s to 0.317s), `GS_Attack02` (0.000s to 0.236s). | Yaw Tracking during Telegraph | Custom turn notify | Uses simple interpolation toward actor target. | Full notify graph text |
| `T_Explosion_WarpMask` / `SM_Impact_Warp` | Texture / StaticMesh | VFX assets in particle demo folders. | **NONE** | **NONE** | **FALSE POSITIVE:** File names contain "Warp", but are purely visual explosion shaders/meshes. | None (dismissed) |

**Finding:** The pack does **not** include Epic's Motion Warping plugin integration or root-motion translation warping. Pack rotation tracking (`ANS_SetDesiredRotation_C`) can be reused for yaw alignment, but position warping requires custom C++ logic.

---

### 2.5 SEL-008: Idle, Reposition, and Defensive Retreat
*Target Requirement:* Measured defensive circling, repositioning when out of range, and tactical pauses.

| Asset Path | Asset Type | Inspected Properties | Applicable Mechanic | Replaced Content | Unknowns & Limits | Required Export |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/TurnInPlace/` | AnimSequence | Standard turn in place (90L, 90R, 180). | AI Turning | Custom turn animations | Bound to mannequin skeleton. | Sequence lengths and root motion flags |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss` | Behavior Tree | Contains `MoveTo` and `Wait` nodes with selector arbitration. | Reposition Subtree | Scratch BT construction | Needs project-owned decorator to prevent erratic oscillating movement. | Full BT export |
| `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyHeal` | Blueprint Ability | `CDO_GA_EnemyHeal.t3d`: Cooldown 15.0s, `HealGameplayEffect=None`. | **REJECTED** | **NONE** | Non-functional stub; healing is not approved for boss fallback. | Dismissed |

---

## 3. Revised AG1 Content Size & Costing Delta

Based on the discovery of usable pack animations and ability frameworks, the authoring scope in `AG1_CONTENT_REQUIREMENTS.md` is updated conditionally as follows:

| Row ID | Mechanic | Prior Scope (AG1 / D05) | Reused Pack Elements | Retained Custom Work | Revised Effort Size |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HIT-012** | Grab Attack | LARGE (Custom paired anims + logic) | `GA_EnemyGrabAttack`, `GA_GrabVictim`, `DefaultGrabAttackData` | Greatsword telegraph clip, C++ reservation token, interrupt safety | **MEDIUM-LARGE** (Down from LARGE) |
| **DEF-005** | Guard / Dodge / Parry | LARGE (Full custom defense suite) | `GA_AI_BlockGuard`, `Ability_AI_Block2_Montage`, `Deflect_InPlace_AI_Montage`, `Dodge_To_Idle_Montage` | Proactive AI Parry (missing from pack), posture integration, dodge montage binding | **MEDIUM-LARGE** (Conditional; Guard/Dodge reduced, Parry unchanged) |
| **ANM-003** | Variable Hold | MEDIUM | None (Pack montages are static) | Section looping or C++ dynamic rate adjustment | **MEDIUM** (Unchanged) |
| **ANM-006** | Motion Warping | MEDIUM-LARGE | `ANS_SetDesiredRotation_C` (Yaw only) | Position warping, translation clamping | **MEDIUM-LARGE** (Unchanged) |
| **SEL-004** | Phase Transitions | MEDIUM | None (Pack has no phase logic) | C++ health-threshold event listeners & state switching | **MEDIUM** (Unchanged) |
| **SEL-008** | Reposition / Retreat | SMALL-MEDIUM | BT MoveTo / Turn in Place sequences | Project-owned tactical repositioning decorators | **SMALL** (Down from SMALL-MEDIUM) |
| **AWR-008** | Spatial Awareness | MEDIUM | Basic Navmesh queries | Arena perimeter / brazier boundary safety checks | **MEDIUM** (Unchanged) |
| **QA-008** | Server Authority | CROSS-CUTTING LARGE | None (Pack is client/standalone-oriented BP) | Full C++ authority and validation | **LARGE** (Unchanged) |

---

## 4. Prioritized Editor Export Batch for Claude

To confirm candidate asset viability, Editor Owner Claude must run the following export batch:

```python
# Target Export Batch for Claude (Scripts/Editor/export_pack_reuse.py)
EXPORTS_TO_RUN = [
    # HIT-012
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyGrabStart",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyGrabAttack",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/Shared/HitReactions/GA_GrabVictim",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/DataAssets/AttackData/DefaultGrabAttackData",
    # DEF-005
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_AI_BlockGuard",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyDodge",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyParried",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/HitReactions/GA_EnemyBlockReaction",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/Defend/Ability_AI_Block2_Montage",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/Defend/Deflect_InPlace_AI_Montage",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage",
    # Rotation / Alignment
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Animation/AnimNotifies/ANS_SetDesiredRotation",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Animation/AnimNotifies/ParryFramesNS"
]
```

---

## 5. Evidence and Limits Table

| Topic / Asset | Live Evidence Inspected | Offline Finding | Limitation / Boundary |
| :--- | :--- | :--- | :--- |
| **Pack Block Guard** | `CDO_GA_AI_BlockGuard.t3d` | Confirmed `Ability.Block`, `HoldingTime=2.0s`, `MaxMeleeDist=350.0`. | Cannot verify if `Status.Blocking` reduces project damage without live PIE test. |
| **Pack Dodge** | `CDO_GA_EnemyDodge.t3d` | Confirmed `Ability.Dodge`, 10.0s cooldown; `DodgeMontage=()` is empty. | Pack dodge will fail at runtime unless montage array is populated. |
| **Pack Grab Attack** | `CDO_GA_EnemyGrabAttack.t3d` | Confirmed `DefaultGrabAttackData` binding; `Ability.Grab.Attack`. | Paired animation synchronization cannot be verified without data asset export. |
| **Pack Parry Deficit** | File search in `Blueprints/Abilities/AI/` | Found `GA_EnemyParried` (victim reaction), zero proactive AI parry abilities. | Confirms proactive AI parry is NOT supplied by the pack. |
| **Warping False Positive**| Text search for `*Warp*` | Found `T_Explosion_WarpMask` and `SM_Impact_Warp` (VFX only). | Disproves existence of motion warping tools in pack. |
| **Skeleton Compatibility**| `Documentation/ARPG_PACK_INSPECTION.md` | All pack anims built on `SK_CombatMannequin`. | Animations are geometrically compatible with project mannequin. |
