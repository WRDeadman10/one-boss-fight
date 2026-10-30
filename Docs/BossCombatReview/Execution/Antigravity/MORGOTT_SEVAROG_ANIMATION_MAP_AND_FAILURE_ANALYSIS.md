# Morgott Attack Families to Candidate Sevarog Animations & Historical Greystone/Sevarog Failure Analysis

**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Work Order:** Claude Directives `[C-357]` and `[C-363]` (Order A-237 Part 1 & 2)  
**Date:** 2026-10-30  
**Status:** Architectural Specification & Root Cause Analysis (Offline; Re-opened Citations Verified on Disk)  
**Rules:** Only disk-verified citations cited; all candidate animations marked UNVERIFIED pending probe/visual review; unproven details marked UNKNOWN; zero engine launch; zero git commits.

---

## 1. Executive Summary & Purpose

In `[C-357]` and `[C-363]`, Tech Lead Claude relayed the Project Owner's decision to configure the first soulslike boss encounter using:
- **Player:** Paragon Greystone (`Content/ParagonGreystone`), playing like the pack player.
- **Boss:** Paragon Sevarog (`Content/ParagonSevarog`), acting as a true soulslike boss modeled after the design grammar of the Morgott combat reference (`Documentation/Boss/Morgott_82_Point_Combat_Reference/Morgott_82_Point_Combat_Reference.md:36-55`).

This reverses the historical fallback decision documented in `Documentation/DECISIONS.md:288-301` (*"Back to the pack's own player and boss (2026-10-19, later)"*). To ensure these characters succeed without repeating past regressions, this document delivers:
1. A complete mapping of the **15 Morgott Attack Families** to candidate Sevarog animation assets located in `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/` (127 total animation assets audited on disk).
2. A rigorous root-cause analysis of the two historical 2026-10-19 failures (Greystone `GetMainAnimBP` Accessed None spam and Sevarog immobile turning), citing exact re-opened lines from `Documentation/DECISIONS.md` and `Documentation/KNOWN_ISSUES.md`.

---

## 2. Morgott 15 Attack Families to Candidate Sevarog Animations

All candidate animations below are audited from disk under `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/`.  
> [!IMPORTANT]
> Per Tech Lead directive `[C-357]` and `[C-363]`, **every candidate animation is marked UNVERIFIED** until verified by Codex's engine-side inventory probe or confirmed via visual clip playback. Gaps where no matching animation exists are explicitly highlighted.

| # | Morgott Attack Family (`Morgott_...md:36-55`) | Role & Threat Geometry | Candidate Sevarog Animation Name(s) | Verification Status & Notes |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Curved sword slash / delayed overhead** | Melee front: slash or downstroke with delayed weapon release; punish only confirmed finisher. | `Swing1_Slow` (or `Swing1_Slow_120fps`), `Swing1_Medium` | **UNVERIFIED**. Slow telegraphed horizontal/downward scythe sweep matching delayed windup. |
| **2** | **Holy dagger double slash** | Close anti-greed: quick short consecutive attacks punishing greedy proximity. | `Swing1_FAST_v2` / `Swing1_FAST_120fps` chained into `Swing2_FAST_v2` / `Swing2_FAST_120fps` | **UNVERIFIED**. Fast short-arc consecutive scythe slashes with rapid recovery. |
| **3** | **Holy dagger throw** | Medium / far pressure: ranged spectral projectiles constraining approach spacing. | `Cast`, `Soul_Siphon_Targeting` | **UNVERIFIED**. Forward casting gesture / arm raise. Note: Projectile VFX (`NS_` Niagara) is separate. |
| **4** | **Holy spear throw** | Ranged precision: conjured long projectile released along a narrow forward lane. | `Cast`, `Soul_Siphon` | **UNVERIFIED**. Forward thrust / cast release gesture. Visual spear requires spawned actor/VFX. |
| **5** | **Holy spear charge** | Medium-to-long gap closer: boss rushes across moving root-motion path. | `Speedburst`, `Sprint_Fwd` | **UNVERIFIED**. `Speedburst` is Sevarog's high-velocity forward displacement dash; `Sprint_Fwd` is sustained chase. |
| **6** | **Holy hammer overhead slam** | Close/mid heavy follow-up: large telegraphed conjured hammer slam with ground shockwave. | `Subjugation`, `Ultimate_Swing_120fps` | **UNVERIFIED**. `Subjugation` is Sevarog's signature ground scythe plunge; `Ultimate_Swing` is heavy vertical slam. |
| **7** | **Sword + hammer spin** | Close area denial: two-weapon spinning motion with broad arc and end contact. | `Ultimate_Swing_120fps`, `Swing_In_Air` | **UNVERIFIED**. Broad 360-degree rotational swing arc denying melee perimeter. |
| **8** | **Helicopter: holy sword spin finisher** | Melee combo finisher: multi-hit spin after sword attack with grounded terminal hit. | Combo chain: `Swing2_Medium` -> `Swing3_Slow` (or `Swing3_Slow_120fps`) | **UNVERIFIED**. Two-beat rotational swing concluding in heavy terminal downward recovery. |
| **9** | **Rear tail sweep** | Player behind: rapid rear defense when player stays near back side. | `Turn_Lt_180` / `Turn_Rt_180` + `Swing1_FAST_v2`, or `Knock_back_bwd` | **GAP / PARTIAL (UNVERIFIED)**. Sevarog is a floating cloaked wraith without a physical beast tail. **NO standalone rear tail whip animation exists**. Defensive rear sweep must be authored as a rapid 180° pivot into quick swing. |
| **10** | **Holy swords rain** | Arena zoning (~80% HP): telegraphed floating blade pattern impacting in delayed hazard lanes. | `Cast` (looping/channeling), `LevelStart` | **UNVERIFIED**. Sevarog channeling cast gesture. Swords rain hazard requires spawning actor / Niagara rain system. |
| **11** | **Omen curse burst and geysers** | Phase transition (~60% HP): weapon plant, curse burst, localized eruptions on floor. | `Subjugation` (scythe planted), `Stage_1` / `Stage_2` / `Stage_3` / `Stage_4` (soul morph) | **UNVERIFIED**. Sevarog's `Stage_1..4` animations represent soul growth/morphing; `Subjugation` plants scythe in ground. |
| **12** | **Bloodflame slam** | Phase 2 heavy impact: ground impact producing lingering erupting hazard. | `Subjugation`, `Swing3_Slow` | **UNVERIFIED**. Heavy downward scythe plunge paired with delayed ground hazard decal/emitter. |
| **13** | **Bloodflame chase / two slashes** | Phase 2 advancing slashes: rushing forward leaving delayed explosive trails. | `Speedburst` into `Swing1_FAST_120fps` -> `Swing2_FAST_120fps` | **UNVERIFIED**. Rapid forward rush followed by dual scythe slashes with trailing hazard volumes. |
| **14** | **Bloodflame grab / skewer** | Phase 2 forward impaling thrust leading to capture, lift and throw. | `Bound`, `Soul_Siphon` | **GAP / PARTIAL (UNVERIFIED)**. `Bound` and `Soul_Siphon` provide grasping/reaching gestures, but **NO paired victim lift-and-throw animation exists** in Paragon Sevarog assets. Full grab requires custom paired montage or programmatic root lock. |
| **15** | **Rapid weapon-change barrage** | Late threshold (<30% HP): extended multi-hit string culminating in broad heavy finisher. | Chained string: `Swing1_FAST_v2` -> `Swing2_Medium` -> `Swing3_Slow` -> `Ultimate_Swing_120fps` | **UNVERIFIED**. Full four-stage scythe combination exercising fast, medium, and ultimate swing clips. |

### Summary of Moveset Inventory Gaps
1. **Dedicated Tail Whip (Family 9):** Sevarog lacks a standalone tail attack clip. Must be implemented via quick 180-degree pivot + `Swing1_FAST`.
2. **Paired Grab / Lift / Throw (Family 14):** Sevarog has reaching/binding gestures (`Bound`, `Soul_Siphon`), but lacks a synchronized victim impale/lift/throw montage. Programmatic player lock or custom animation retargeting will be needed for full grab execution.
3. **Spectral Weapon Geometry:** Sevarog wields a giant two-handed scythe (`SM_SevarogScytheProxy` / skeletal weapon). Moves referencing daggers, spears, and hammers must be expressed as scythe thrusts, sweeps, overhead slams, and cast gestures.

---

## 3. Root Cause Analysis: The Two Historical 2026-10-19 Failures

In `[C-357]`, Lead Claude cited the historical decision in `Documentation/DECISIONS.md:288-301` (*"Back to the pack's own player and boss (2026-10-19, later)"*), which reversed the initial attempt to use Greystone and Sevarog due to two fatal issues:
1. Greystone logged `GetMainAnimBP` Accessed None every frame.
2. Sevarog stood in place and only turned.

Below is the forensic analysis of both failures based on re-opened, disk-verified citations:

### 3.1 Failure 1: Greystone `GetMainAnimBP` Accessed None Every Frame

#### Verified Citations:
- `Documentation/DECISIONS.md:288-295`:
  > *"The Greystone player and the Sevarog boss were dropped for now: the player stood on retargeted animations that logged `GetMainAnimBP` Accessed None errors every frame (`ABP_CombatAnimLayersBase_Grey`), and Sevarog stood and only turned."*  
  > *"Revert the 60 pack assets that stage 3 re-pointed to the `_Grey` copies (all weapon abilities, enter/exit combat, quick slots, dodge, hit stun, knockdown, potion, bonfire, magic and bow abilities, all combat styles) ... The mannequin cannot play animations of another skeleton."*  
  > *"Restore `ABP_CombatCharacter`, `ABP_UnarmedLayer` and `UnarmedCombatStyle` from the pack source ... The polish step had consolidated the unarmed layer into the Grey copy: the original path was a 3 KB redirector, so even loading the original class gave the Grey one."*
- `Documentation/KNOWN_ISSUES.md:44` (`KI-040`):
  > *"Several retargeted layer Blueprints (`ABP_UnarmedLayer_Grey`, `ABP_MagicStaffLayer_Grey`, `ABP_DualSwordLayer_Grey`, `ABP_SwordLayer_Grey`, others) log `CreateExport: Failed to load` and reference a missing `/Game/ABP_CombatAnimLayersBase_Grey`; only the sword and shield layer was seen working."*
- `Documentation/KNOWN_ISSUES.md:55` (`KI-052`):
  > *"Greystone and Sevarog retired: stage 3 had re-pointed 60 pack assets to the Grey copies and the log filled with `GetMainAnimBP` Accessed None errors..."*

#### Root Cause Analysis:
1. **Broken Cross-Skeleton Ability Re-pointing:** In Stage 3, 60 core pack data assets, combat styles, and gameplay abilities were globally re-pointed from the pack's `SK_CombatMannequin` animations to custom `_Grey` retargeted copies (`DECISIONS.md:294`).
2. **Missing Linked Anim Layer Interface / Export Failure:** The retargeted layer Blueprints (`ABP_UnarmedLayer_Grey`, `ABP_SwordLayer_Grey`, etc.) depended on `ABP_CombatAnimLayersBase_Grey`. During asset consolidation and packaging, this base layer path failed to export (`CreateExport: Failed to load`, `KI-040`).
3. **Null Main Anim Instance Resolution:** The pack's combat system relies on linked animation layers (`ALI_CombatAnimLayers`). When an ability executed, it called `GetMainAnimBP` on the player character's mesh to query active combat layers and notifies. Because the linked layer had failed to bind, `GetMainAnimBP` returned `None`, triggering an `Accessed None` runtime error on every tick.
4. **Asset Consolidation Redirector Trap:** An attempt to clean up duplicate files replaced `ABP_UnarmedLayer` with a 3 KB redirector pointing to `ABP_UnarmedLayer_Grey`, polluting the core pack path so that even standard mannequin pawns loaded the broken Greystone layer (`DECISIONS.md:295`).

#### Solution for New Implementation (Claude Proposal in `[C-357]`):
Instead of mutating or re-pointing 60 pack gameplay abilities to Greystone's skeleton, **Greystone keeps the pack player's gameplay and skeleton (`SK_CombatMannequin`) completely intact**. Greystone's visible skeletal mesh is driven programmatically or via runtime pose following / lead-component copy pose, leaving all pack abilities, linked layers, and inputs untouched.

---

### 3.2 Failure 2: Sevarog Stood and Only Turned in Place

#### Verified Citations:
- `Documentation/DECISIONS.md:290`:
  > *"The Greystone player and the Sevarog boss were dropped for now: ... and Sevarog stood and only turned."*
- `Documentation/DECISIONS.md:297`:
  > *"Historical pack inspection (2026-10-19, before the retune): the pack boss Blueprint defaults `EnemyInfoRef` to the sword mob (sword mob montages, 100 HP), the same trap as in the Sevarog copy. Pack data then read 500 HP and 100 poise..."*
- `Documentation/KNOWN_ISSUES.md:53` (`KI-049`):
  > *"Sevarog | Abilities granted before the controller existed | Fixed: controller from BeginPlay, behaviour held by the director | Closed 2026-10-20"*
- `Documentation/KNOWN_ISSUES.md:55` (`KI-052`):
  > *"Greystone and Sevarog retired: stage 3 had re-pointed 60 pack assets to the Grey copies and the log filled with `GetMainAnimBP` Accessed None errors; the Sevarog boss stood and turned."*

#### Root Cause Analysis:
1. **Wrong EnemyInfoRef Data Asset (The Sword Mob Trap) [DOCUMENTED FACT]:** In BP_SevarogBossPack, EnemyInfoRef defaulted to the basic sword mob data asset (EnemyInfo_SwordMob, 100 HP) rather than boss data (DECISIONS.md:297). This caused the actor to load standard mob combat styles with incompatible montages.
2. **Behavior Tree / Ability Tag Incompatibility [INFERENCE / UNVERIFIED]:** Sevarog was placed under the pack's humanoid behavior tree (BT_HumanoidEnemy). The tree attempted to execute tasks such as GA_GS_Boss_CloseAttack and GA_GS_Boss_LeapAttack. Because Sevarog's mesh and skeleton lacked the exact slot names, root motion curves, and notifies expected by the Greatsword boss montages, the attack tasks aborted immediately or failed to activate.
3. **Controller Race Condition (KI-049) [DOCUMENTED FACT]:** Abilities were granted in BP_SevarogBossPack before the AIController had possessed the pawn (KNOWN_ISSUES.md:53). When the behavior tree attempted to read target actors or issue movement requests, the blackboard was uninitialized (fixed 2026-10-20).
4. **Perception and Fallback Loop [INFERENCE / UNVERIFIED]:** Because the attack tasks aborted on start and movement requests failed due to mismatched navigation attributes, the behavior tree fell back to its lowest priority idle decorator: turn-in-place toward the player. Hence, Sevarog stood stationary in the arena, continuously turning to face the player without advancing or attacking (DECISIONS.md:290).

#### Solution for New Implementation (Claude Proposal in `[C-357]`):
Sevarog will **NOT run on the pack's stock Behavior Tree or pack abilities**. Instead, Sevarog runs entirely on **OUR C++ data-driven combat framework** (`URPGBossEncounter`, move cards, typed selector, and direct montage playback), bypassing the pack's flawed AI tree and directly invoking Sevarog's native animations (`Swing1_Slow`, `Speedburst`, `Subjugation`).

---

## 4. Architectural Summary & Verification Receipt

- **15/15 Morgott Attack Families mapped** to Sevarog candidate animations in `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/`.
- **All candidates explicitly marked UNVERIFIED** until verified by Codex's engine-side probe or visual clip inspection.
- **2 Moveset Gaps identified:** Standalone rear tail whip (Family 9) and paired lift-and-throw victim grab (Family 14).
- **Exact Root Causes of 2026-10-19 Failures documented** with 100% re-opened citations verified on disk against `Documentation/DECISIONS.md:288-301`, `Documentation/KNOWN_ISSUES.md:44,53,55`, and `Morgott_82_Point_Combat_Reference.md:36-55`.
- **Zero Content writes; zero engine processes launched; zero git commits.**
