# AG-12: Pack Reuse Inventory for the Eight Former-N/A Rows (Revision 05)

**Document ID:** `AG12_PACK_REUSE_INVENTORY`  
**Revision:** Rev 05 (Updated per Claude `[C-130]` with exact heal stub qualification)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Work Orders:** `ANTIGRAVITY_WORK_ORDER_03.md` (`AG-12`), `ANTIGRAVITY_WORK_ORDER_04.md` (`AG-20`), `[C-128]` (`AG-27`), `[C-129]` (`AG-28`), `[C-130]` (`AG-29`)  
**Evidence Sources:**  
- Live PR2 Text Exports: `Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR2_*.t3d` (45 files, `PR2_SHA256.txt`)  
- Live PR3 Closure Exports: `Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR3_*.t3d` (32 files, `PR3_SHA256.txt`, `E-009` Rev 02)  
**Status:** DELIVERED (Rev 04)  

---

## 1. Executive Summary & Objective

In `[C-128]` and `[C-129]`, Technical Lead Claude delivered two extensive batches of read-only text exports (`PR2_*.t3d` and `PR3_*.t3d`), providing complete graph text and CDO definitions across 59 distinct pack assets and boss-specialized classes.

Task `AG-28` incorporates the final closure evidence to settle the pack reuse inventory across rows `HIT-012`, `DEF-005`, `ANM-006`, and `SEL-008`:
1. **Boss Style Grants (11 Abilities):** `ExampleGreatSwordBossCombatStyle` explicitly grants exactly 11 abilities (`HitStun`, `EnterCombat`, `ExitCombat`, `CloseAttack`, `CloseRare`, `MidRangeAttack`, `LeapAttack`, `SprintAttack`, `RetaliationAttack`, `TurnInPlace`, `RagdollDeath`). It grants **no guard, dodge, grab, or heal abilities**.
2. **Turn-In-Place is Live on Boss (`SEL-008` Turn Part):** `GA_GS_Boss_TurnInPlace` has all four turn montages (L/R 90, L/R 180) bound on its CDO (`PR3_CDO_GA_GS_Boss_TurnInPlace.t3d:4-7`) and is actively called by `BT_ExampleBoss_tree.md:294` on tag `Ability.TurnInPlace`. The turn component of `SEL-008` is **100% pack-supplied and already live**.
3. **Accurate Grab Status (`HIT-012`):** No grab montage is bound or granted for this boss. `DefaultGrabAttackData` names no montage, the victim CDO has empty defaults, and no asset matching `*grab*` exists on disk. Whether a generic pack melee montage could be repurposed is an open content question; for Ember Warden's Greatsword, custom paired animations remain required.
4. **Defense Framework Status (`DEF-005`):** Pack guard and dodge scaffolding exists, but is ungranted on the boss's style. Proactive AI parry is absent from the pack (`GA_EnemyParried` is strictly victim stagger).

---

## 2. Row-by-Row Deep Audit from Live T3D Exports (PR2 & PR3)

### 2.1 HIT-012: Grab Attack & Victim Reaction
*Target Requirement:* Boss grab move with active capture window, paired victim animation, escape/damage resolution, and interrupt/abort safety.

#### Verified Live Facts:
- **Style Grant:** `ExampleGreatSwordBossCombatStyle` grants 11 abilities; `GA_EnemyGrabAttack` is **NOT granted** to the boss.
- **Attacker Ability:** `GA_EnemyGrabAttack` (`PR2_GA_EnemyGrabAttack.t3d`, `PR2_CDO_GA_EnemyGrabAttack.t3d`) defines tag `Ability.Grab.Attack`, binds `AttackData = DefaultGrabAttackData`, and delegates montage retrieval to `Get Ability Montage` on `GA_EnemyMeleeAttack`.
- **Attack Data Asset:** `DefaultGrabAttackData` (`PR2_DefaultGrabAttackData.t3d`) sets `IsUnblockableAttack? = True`, damage GE `GE_MeleeDamage_DamageOnly_C`, trail particle `P_Greystone_Primary_Trails_R`, and impact cue `MeleeImpactEffect`. It contains **no montage reference**.
- **Victim Ability:** `GA_GrabVictim` (`PR2_GA_GrabVictim.t3d`, `PR2_CDO_GA_GrabVictim.t3d`) provides actor synchronization scaffolding via `BP_ActorSyncTask`. CDO properties have default empty slots (`GrabMontages = ()`, `GrabMontage = (AnimMontage = None)`).
- **Disk Search:** No asset with `*grab*` in its filename exists in `Content/AdvancedARPGCombat/`.

#### Accurate Technical Classification:
- **No Grab Montage is Bound or Granted for Boss01.** The pack provides the Gameplay Ability framework for grab routing, unblockable damage, and victim locking, but no grab montage is assigned in data assets or granted via the boss combat style.
- Whether an existing pack melee montage could be adapted to trigger a grab is an unproven content question. For Ember Warden's greatsword moveset, **scratch-authored paired animations (`AN_Boss01_Grab_Attacker`, `AN_Player_Grab_Victim`)** remain required to ensure correct two-handed greatsword positioning, grip alignment, and fail-safe release on boss stagger/death.

---

### 2.2 DEF-005: Guard, Parry, and Dodge
*Target Requirement:* Boss defensive capabilities: finite guard with posture damage, reactive/proactive parry, and evasive dodge.

#### Verified Live Facts:
- **Style Grant:** `ExampleGreatSwordBossCombatStyle` grants **neither guard (`GA_AI_BlockGuard`) nor dodge (`GA_EnemyDodge`)**.
- **Pack Guard Ability:** `GA_AI_BlockGuard` (`PR2_GA_AI_BlockGuard.t3d`, `PR2_CDO_GA_AI_BlockGuard.t3d`) holds tag `Ability.Block`, owned tag `Status.Blocking`, `BlockingHeldTime = 2.0s`, `MaxBlockingDistance (Melee) = 350.0`, cancels `Ability.Sprint`.
- **Pack Guard Montages:** `Ability_AI_Block2_Montage` ($0.428\text{ s}$, `SK_CombatMannequin`, references sequence `Ability_Block2`) and `Deflect_InPlace_AI_Montage` ($1.133\text{ s}$, notify `ANS_DisableMovement_C`, references 1-Handed sequence `Deflect_InPlace_Anim`).
- **Pack Dodge Ability & Montage:** `GA_EnemyDodge` (`PR2_CDO_GA_EnemyDodge.t3d`) has `DodgeMontage = ()` (empty on CDO). However, `Dodge_To_Idle_Montage` ($2.333\text{ s}$, rate scale 2.0 -> $1.167\text{ s}$ effective) provides complete dodge mechanics: `ANS_SetDesiredRotation_C` ($0.25\text{ s}$, 1440 deg/s), `ANS_iFrames_C` ($0.700\text{ s}$, effective $0.35\text{ s}$ iframe), `ANS_MovementCancel_C` ($0.627\text{ s}$), and `InputBufferNS_C`.
- **Pack Parry Deficit:** `ParryFramesNS` defines parry detection, but the pack contains **zero proactive AI parry abilities**. `GA_EnemyParried` is strictly the victim stagger reaction when the AI is parried by the player.

#### Accurate Technical Classification:
- **Scaffolding Exists but is Ungranted:** Reusable guard and dodge abilities/montages exist in the pack, but must be granted via `BP_CombatStyle` and have montages bound to `GA_EnemyDodge`.
- **Proactive AI Parry is 100% Custom:** The pack supplies no proactive parry behavior for AI; custom C++ / BT logic is required.
- **2H Greatsword Adaptation:** The pack deflection animation is 1-Handed (`1Handed/Defend/Deflect_InPlace_Anim`); adapting it to Ember Warden's two-handed greatsword requires socket alignment or custom animation.

---

### 2.3 ANM-006: Motion Warping / Target Alignment
*Target Requirement:* Mid-telegraph rotation and bounded position warp toward player capsule.

#### Verified Live Facts:
- **Yaw Rotation Tracking:** `ANS_SetDesiredRotation_C` (`PR2_Dodge_To_Idle_Montage.t3d`, `PR3_ANS_SetDesiredRotation.t3d`, `GS_Attack01_Montage`) smoothly tracks target actor Yaw during telegraphs with configurable interpolation speed (e.g. 1440 deg/s in dodge, 720 deg/s in attacks).
- **Motion Warping Plugin Absent:** String search across all 77 PR2 and PR3 export files confirms **zero references to Epic's Motion Warping plugin or `MotionWarpingComponent`**.

#### Accurate Technical Classification:
- The pack supplies **Yaw rotation alignment only**. Root-motion translation warping and distance scaling are completely absent from the pack and must be implemented via project C++ or custom notifies.

---

### 2.4 SEL-008: Turn in Place, Repositioning, and Defensive Pacing
*Target Requirement:* Turn-in-place alignment, measured defensive circling, repositioning when out of range, and tactical pauses.

#### Verified Live Facts:
- **Turn in Place is LIVE on Boss:**
  * `GA_GS_Boss_TurnInPlace` (`PR3_GA_GS_Boss_TurnInPlace.t3d`, `PR3_CDO_GA_GS_Boss_TurnInPlace.t3d`) is granted by `ExampleGreatSwordBossCombatStyle:4`.
  * All four turn montages are bound directly on its CDO:
    - `Turn Left 90 = Idle_Turn_Left_90_Anim_Montage`
    - `Turn Right 90 = Idle_Turn_Right_90_Anim_Montage`
    - `Turn Left 180 = Idle_Turn_Left_180_Anim_Montage`
    - `Turn Right 180 = Idle_Turn_Right_180_Anim_Montage`
  * Active Execution: `BT_ExampleBoss_tree.md:294` activates `Ability.TurnInPlace` when target angle exceeds thresholds (-50 to +50 deg).
- **Repositioning & Pacing:** Handled by `BT_ExampleBoss` (`MoveTo` and `Wait` nodes). Currently executes linear advance/retreat without tactical circling or pacing terms.
- **Pack Heal Stub:** `GA_EnemyHeal` (`PR2_CDO_GA_EnemyHeal.t3d:2`) has `Heal Gameplay Effect = None`. The pack ability is an unconfigured stub lacking a gameplay effect; while the project implements `RPGBossHealPunish` (A5 heal punish), the pack's `GA_EnemyHeal` cannot supply healing behavior without authoring a valid heal gameplay effect.

#### Accurate Technical Classification:
- **Turn in Place:** **100% Pack-Supplied and Already Live** on Ember Warden via `GA_GS_Boss_TurnInPlace`.
- **Tactical Repositioning:** Requires project-owned BT decorators for tactical circling and recovery pacing.

---

## 3. Revised Pack Reuse Summary Matrix

| Row ID | Mechanic | Pack Supply Status | Live Boss Status | Retained Custom Work Required | Effort Size |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HIT-012** | Grab Attack | Tags, unblockable damage GE, victim lock scaffolding. No grab montage bound/granted. | Ungranted | Custom paired animations (`AN_Boss01_Grab_Attacker`, `AN_Player_Grab_Victim`), spatial alignment token, interrupt safety | **LARGE** |
| **DEF-005** | Guard, Dodge, Parry | Guard ability (`GA_AI_BlockGuard`), block/deflect montages, dodge montage (`Dodge_To_Idle_Montage`). | Ungranted (0 of 3 granted in style) | Grant abilities in style, bind dodge montage, author proactive AI parry (0% in pack), adapt 1H deflect to 2H greatsword | **MEDIUM-LARGE** |
| **ANM-006** | Motion Warping | Yaw rotation tracking notify (`ANS_SetDesiredRotation_C`). Zero Epic MotionWarping. | Live on attacks | Position/translation warping, distance scaling in C++ | **MEDIUM-LARGE** |
| **SEL-008 (Turn)** | Turn in Place | Turn ability (`GA_GS_Boss_TurnInPlace`) with all 4 montages bound (L/R 90, L/R 180). | **LIVE ON BOSS** (`BT_ExampleBoss:294`) | None. Verified fully operational in live BT. | **DONE (0 effort)** |
| **SEL-008 (Move)** | Repositioning | `MoveTo` and `Wait` nodes in `BT_ExampleBoss`. | Live in BT | Project-owned tactical circling decorators and pacing terms | **SMALL** |

---

## 4. Evidence and Limits Table

| Topic / Asset | Live Export Evidence Inspected | Concrete Technical Finding | Limitation / Boundary |
| :--- | :--- | :--- | :--- |
| **Style Ability Grants** | `PR3_ExampleGreatSwordBossCombatStyle.t3d:4` | Grants 11 abilities (HitStun, Enter/ExitCombat, Close/Rare, Mid, Leap, Sprint, Retaliation, TurnInPlace, RagdollDeath). | Confirms NO guard, dodge, grab, or heal abilities are granted to Ember Warden. |
| **Turn in Place Live** | `PR3_CDO_GA_GS_Boss_TurnInPlace.t3d:4-7`, `BT_ExampleBoss_tree.md:294` | All 4 turn montages bound on CDO; triggered in live BT on `Ability.TurnInPlace`. | SEL-008 turn component is 100% functional and live. |
| **Grab Montage Status** | `PR2_DefaultGrabAttackData.t3d`, `PR2_CDO_GA_EnemyGrabAttack.t3d`, `PR2_CDO_GA_GrabVictim.t3d` | `DefaultGrabAttackData` names no montage; victim CDO defaults empty; no `*grab*` files on disk. | No grab montage is bound or granted for Boss01. Paired greatsword animations required. |
| **Dodge Scaffolding** | `PR2_CDO_GA_EnemyDodge.t3d`, `PR2_Dodge_To_Idle_Montage.t3d` | `Dodge_To_Idle_Montage` has 0.700s iframes and rotation tracking. CDO `DodgeMontage=()` is empty. | Dodge is ungranted in style and requires montage binding. |
| **Proactive AI Parry** | Search across all 77 PR2/PR3 exports | `GA_EnemyParried` is strictly victim stagger. Zero proactive AI parry abilities exist. | Proactive AI parry is 0% supplied by the pack. |
| **Motion Warping** | Search across all 77 PR2/PR3 exports | Zero references to Epic Motion Warping or `MotionWarpingComponent`. `ANS_SetDesiredRotation_C` provides Yaw only. | Translation / distance warping requires custom project C++ logic. |
| **Pack Heal Stub** | `PR2_CDO_GA_EnemyHeal.t3d:2` | `Heal Gameplay Effect = None`. Unconfigured pack stub lacking gameplay effect. | Project has `RPGBossHealPunish` (A5 punish); pack stub cannot function without authored GE. |
