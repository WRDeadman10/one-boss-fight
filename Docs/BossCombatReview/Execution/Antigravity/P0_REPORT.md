# P0 Visual and Technical-Animation Baseline Audit (CI-P0-A-01) - Revision 05

Date: 2026-10-25 (Revision 05)
Author: Antigravity (Accountable Visual Investigator)
Review Requested from: Claude (Acting Technical Lead)
Target Implementation: One Boss Fight - Boss Combat Improvement Program (P0-P8)
Status: **REVIEW-REQUESTED (Accepted with Documented Limitations for Offline Subset; Runtime Captures Pending Claude Coordination)**

---

## 1. Executive Summary & Boundaries

This revised report delivers the offline visual, technical-animation, and weapon-alignment baseline audit for task **CI-P0-A-01** under the P0-P8 Boss Combat Improvement Program, incorporating all findings from technical reviews P0_AG_REVIEW_01.md through P0_AG_REVIEW_04.md.

### Audit Boundaries & Operational Protocols:
- **Read-Only Scope:** No existing FBX assets, textures, materials, source scenes, or configurations were modified, re-imported, or overwritten.
- **Code & Engine Boundaries:** No gameplay C++, Config, Scripts, or third-party pack Blueprints were edited.
- **Single-Editor Protocol:** Unreal Editor ownership remains exclusively with Claude. Antigravity operated offline without running concurrent editor sessions.
- **Tooling & Extractor Provenance:**
  * Blender Version: 5.1.2 (headless, hash ec6e62d40fa9).
  * Scene Units: Metric, Unit Scale = 1.0, Length Unit = METERS.
  * Coordinate Frame: Blender Right-Handed (Z-Up, Y-Forward, X-Right).
  * Bound Box Computation: Object bound_box transformed by matrix_world yields world-space axis-aligned extents in meters, scaled by 100 to report in centimeters. For un-parented meshes at origin with identity object transform, world bounds coincide with mesh local extents.
  * Root Sampling Guard: Evaluates pose bone `root` if present; if absent, verifies whether the armature object itself represents the FBX `root` node (`arm.name.lower() == 'root'`) and samples `arm.matrix_world`. If no root node or bone exists, raises a `RuntimeError` (fails loudly).
  * Reproducibility: Extraction script Docs/BossCombatReview/Execution/Antigravity/Evidence/extract_baseline_kinematics.py -> Raw log Docs/BossCombatReview/Execution/Antigravity/Evidence/raw_kinematic_extraction.log.
  * Animator Intent Citation: Windup tells, commitment markers, active intervals, and release descriptions cite the authored .txt sidecars (Import/Boss01/Animations/<Clip>.txt) as declarations of author intent, separated from raw kinematic extraction.
  * Frame Offset Convention: Sidecar frame indices are zero-based (0 .. N-1), whereas Blender extraction frames are 1-based (1 .. N). A zero-based sidecar frame F_0 corresponds to 1-based extraction frame F_1 = F_0 + 1.
- **Player Riposte Root Motion Reconciliation:**
  * In offline extraction, AN_Riposte_Player_Front.fbx exhibits exactly **90.00 cm** root excursion along +Y (from (0,0,0) to (0,90,0) cm at 0.70 s / Frame 21, held through 1.60 s), confirming the forward lunge is fully authored into the root node of the FBX asset as declared in its sidecar.
  * All 15 boss animation clips and the boss riposte reaction maintain strictly **0.0000 cm** root excursion (in-place animations).
- **Runtime Evidence Boundary:** In accordance with single-editor boundaries, runtime in-game observations, effective playback rates, world-space query overlays, and Shipping packaged appearances are marked **UNVERIFIED / BLOCKED pending Claude runtime capture**.

---

## 2. Active Boss Attack Inventory & Asset Freshness

The boss combat suite consists of a hybrid architecture: an underlying hidden pack driver mesh (BP_ExampleGreatSwordBoss) driving the animation pose and weapon trace, followed by visual skeletal mesh components (SK_Boss01_Body, crown, mantle, brazier gauntlet) and a static mesh follower greatsword (SM_Boss01_Greatsword) attached via RPGBossLook.

The boss combat style and runtime dump grant **11 boss gameplay abilities** (including GA_EnemyRagdollDeath).

| Move ID | Move Name / Role | Runtime Implementation | Authored Source Asset | Live Engine Asset | Asset Status / Freshness |
|---|---|---|---|---|---|
| **A1** | Quick Horizontal Slash | Pack Ability via GA_GS_Boss_CloseAttack | Import/Boss01/Animations/AN_Boss01_A1_QuickSlash.fbx | /Game/OneBossFight/Boss01/Animations/AM_Boss01_A1 | **Authored & Imported.** Replaces pack GS_Attack03_Montage. |
| **A1b** | Chained Horizontal Return | Pack Ability branch follow-up | *None authored* | /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack04_Montage | **Pack Stand-in.** Raw 120 ms windup; no authored replacement exists. |
| **A3a** | Two-Hit Combo: Cleave 1 | Pack Ability via GA_GS_Boss_CloseAttack | Import/Boss01/Animations/AN_Boss01_A3a_Combo1.fbx | /Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a | **Authored & Imported.** Replaces pack GS_Attack01_Montage. |
| **A3b** | Two-Hit Combo: Reverse Cleave 2 | Pack Ability branch follow-up | Import/Boss01/Animations/AN_Boss01_A3b_Combo2.fbx | /Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b | **Authored & Imported.** Replaces pack GS_Attack02_Montage. |
| **A2** | Delayed Overhead Slam | Pack Ability via GA_GS_Boss_CloseRare | Authored 3-part set: AN_Boss01_A2_Raise.fbx, AN_Boss01_A2_ApexHold.fbx, AN_Boss01_A2_Slam.fbx | /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_ChargedAttack_Montage | **UNWIRED ASSET DEFECT (Source-Confirmed).** Authored trio delivered in Report 14, but runtime still routes to pack GS_ChargedAttack_Montage. |
| **A4** | Ground Low Sweep | Dynamic Montage via RPGAttackTracker::PlayClip | Import/Boss01/Animations/AN_Boss01_A4_LowSweep.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep | **Authored & Imported.** Driven dynamically; damage resolved via RPGBossLowSweep planar math. |
| **A5** | Gauntlet Javelin Throw | Dynamic Montage via RPGBossHealPunish | Import/Boss01/Animations/AN_Boss01_A5_JavelinThrow.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow | **Authored & Imported.** Spawns ARPGBossJavelin with SM_Boss01_EmberJavelin. |
| **A6** | Phase 2 Leap Slam + Shockwave | Pack Ability via GA_GS_Boss_LeapAttack | Pack native clip | /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_LeapAttack_Montage | **Pack Stand-in + C++ Shockwave.** Shockwave ring handled by RPGBossShockwave. |
| **Dormant** | Resting Seated Idle | Component loop via RPGBossDormantWake | Import/Boss01/Animations/AN_Boss01_DormantIdle.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_DormantIdle | **Authored & Imported.** 5.000 s seamless loop (151 samples). |
| **Wake** | Standing Rise Transition | Dynamic Montage via RPGBossDormantWake | Import/Boss01/Animations/AN_Boss01_Wake.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_Wake | **Authored & Imported.** 3.500 s standing transition (106 samples) with behavior tree gate. |
| **PhaseRoar** | Phase 2 Awakening Roar | Dynamic Montage via RPGBossPhases | Import/Boss01/Animations/AN_Boss01_PhaseRoar.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar | **Authored & Imported.** 1.800 s standing burst (55 samples) with camera shake. |
| **StaggerFall** | Posture Break Collapse | Dynamic Montage via RPGBossStagger | Import/Boss01/Animations/AN_Boss01_StaggerFall.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall | **Authored & Imported.** 0.700 s collapse to ground (22 samples). Live route. |
| **StaggerDown** | Posture Break Kneel Hold | Dynamic Montage via RPGBossStagger | Import/Boss01/Animations/AN_Boss01_StaggerDown.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown | **Authored & Imported.** 1.000 s kneeling hold (31 samples) opening riposte window. Live route. |
| **StaggerGetUp**| Posture Break Recovery | Project Asset / *Not Live Route* | Import/Boss01/Animations/AN_Boss01_StaggerGetUp.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerGetUp | **Offline Project Asset.** 1.400 s rise (43 samples). *Note: Live runtime get-up plays StaggerFall backwards at -GetUpRate (RPGBossStagger.cpp:137-139).* |
| **Riposte** | Frontal Critical Strike | Synced Pair via RPGBossStagger | AN_Riposte_Player_Front.fbx, AN_Riposte_Boss_Reaction.fbx | /Game/OneBossFight/Boss01/Animations/ | **Authored & Imported.** Player 90 cm forward lunge (1.600 s) + Boss impalement reaction (2.000 s). |
| **Death** | Legendary Slump & Freeze | Dynamic Montage via RPGBossDeath | Import/Boss01/Animations/AN_Boss01_DeathLegend.fbx | /Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend | **Authored & Imported.** 3.500 s kneel, sword plant, and final slump (106 samples). |
| **MidRange** | Mid-Range Attack | Pack Ability via GA_GS_Boss_MidRangeAttack | Pack native clip | /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/ExampleSwordMob/Mid01_Anim_Montage | **Pack Native (Live Natural Coverage Gap).** Live notify trace: 0.637-0.884 s; rotation 0.127-0.615 s. |
| **Sprint** | Sprint Attack Follow-Up | Pack Ability via GA_GS_Boss_SprintAttack | Pack native clip | /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_SprintAttackFollowUp_Montage | **Pack Native (Live Natural Coverage Gap).** Sprint speed 800, 1.5 s limit; live notify traces: 0.037-0.230 s & 0.364-0.551 s. |
| **Retaliation**| Retaliation Attack | Pack Ability reaction | Pack native clip | /Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/ExampleSwordMob/RetaliationAttack_Montage | **Pack Native (Live Natural Coverage Gap).** Live notify trace: 0.444-0.630 s; hit-stun immunity 0-1.267 s. |

---

## 3. Move Timing Cards & Kinematic Measurements

All 17 authored FBX clips were extracted at 30 fps via headless Blender 5.1.2. Elapsed durations are strictly computed as (samples - 1) / 30. Exact data from raw_kinematic_extraction.log:

```
+-----------------------------------------------------------------------------------------------------------------------------------+
| Clip Name                   | SHA-256 (Prefix) | Samples (30 fps)| Elapsed Duration | Max Root Excursion | Pelvis Z Range  | Foot Z Range    |
+-----------------------------+------------------+-----------------+------------------+--------------------+-----------------+-----------------+
| AN_Boss01_A1_QuickSlash     | f048d09fce6d...  | 37 (1..37)      | 1.200 s          | 0.0000 cm          | [95.90, 95.90]  | [-0.02,  11.98] |
| AN_Boss01_A2_Raise          | 0349bfcf38b1...  | 19 (1..19)      | 0.600 s          | 0.0000 cm          | [95.90, 95.90]  | [ 0.05,   8.81] |
| AN_Boss01_A2_ApexHold       | 5825a809b459...  | 36 (1..36)      | 1.167 s          | 0.0000 cm          | [95.90, 95.90]  | [ 0.23,   8.51] |
| AN_Boss01_A2_Slam           | 7ec06e673aa8...  | 42 (1..42)      | 1.367 s          | 0.0000 cm          | [95.90, 95.90]  | [-0.02,  10.07] |
| AN_Boss01_A3a_Combo1        | 81f30a2907f5...  | 25 (1..25)      | 0.800 s          | 0.0000 cm          | [95.90, 95.90]  | [-0.02,  12.92] |
| AN_Boss01_A3b_Combo2        | a34cbc6c936e...  | 41 (1..41)      | 1.333 s          | 0.0000 cm          | [95.90, 95.90]  | [-0.02,  12.92] |
| AN_Boss01_A4_LowSweep       | 10ae94157485...  | 54 (1..54)      | 1.767 s          | 0.0000 cm          | [79.93, 95.88]  | [-8.64,  34.04] |
| AN_Boss01_A5_JavelinThrow   | b84a1bf37b2e...  | 31 (1..31)      | 1.000 s          | 0.0000 cm          | [91.52, 95.90]  | [-4.45,   9.04] |
| AN_Boss01_DormantIdle       | 7925b28fa7b6...  | 151 (1..151)    | 5.000 s          | 0.0000 cm          | [47.74, 48.14]  | [ 2.49,   9.10] |
| AN_Boss01_Wake              | 45a5d12f4065...  | 106 (1..106)    | 3.500 s          | 0.0000 cm          | [47.74, 95.90]  | [-0.32,  14.97] |
| AN_Boss01_PhaseRoar         | 5d63a4ac0e5f...  | 55 (1..55)      | 1.800 s          | 0.0000 cm          | [94.40, 95.90]  | [-1.32,   9.98] |
| AN_Boss01_StaggerFall       | ed996cc93c3e...  | 22 (1..22)      | 0.700 s          | 0.0000 cm          | [47.74, 95.90]  | [-0.01,  20.86] |
| AN_Boss01_StaggerDown       | 61e805ab0a9b...  | 31 (1..31)      | 1.000 s          | 0.0000 cm          | [47.74, 49.94]  | [-0.01,  10.19] |
| AN_Boss01_StaggerGetUp      | 7d9aa124de9a...  | 43 (1..43)      | 1.400 s          | 0.0000 cm          | [47.74, 95.90]  | [-48.30,  8.24] |
| AN_Boss01_DeathLegend       | 56ab42fbfe36...  | 106 (1..106)    | 3.500 s          | 0.0000 cm          | [47.74, 95.90]  | [ 0.04,  21.53] |
| AN_Riposte_Player_Front     | e57dc0aed931...  | 49 (1..49)      | 1.600 s          | 90.0000 cm         | [85.92, 95.90]  | [-10.19,  9.47] |
| AN_Riposte_Boss_Reaction    | 58dc6cccce40...  | 61 (1..61)      | 2.000 s          | 0.0000 cm          | [47.64, 47.74]  | [-0.01,   8.20] |
+-----------------------------------------------------------------------------------------------------------------------------------+
```

### Provenance Separation:
- **Authored Intent (.txt Sidecars):**
  * **A1:** AN_Boss01_A1_QuickSlash.txt notes windup tell 0.00-0.35 s, commitment marker at 0.33 s (zero-based Fr 10 / extraction Fr 11), active strike 0.35-0.50 s (Fr 11..15 / Ex 12..16).
  * **A3a:** AN_Boss01_A3a_Combo1.txt notes windup tell 0.00-0.40 s, commitment marker at 0.38 s (Fr 11 / Ex 12), active cleave 0.40-0.60 s (Fr 12..18 / Ex 13..19).
  * **A3b:** AN_Boss01_A3b_Combo2.txt notes reverse cleave 0.15-0.40 s (Fr 5..12 / Ex 6..13), commitment marker at 0.13 s (Fr 4 / Ex 5). Seamless branch transition from A3a end pose.
  * **A4:** AN_Boss01_A4_LowSweep.txt declares author intent with crouch windup 0.00-0.60 s, commitment marker at 0.50 s (zero-based Fr 15 / extraction Fr 16), active floor sweep 0.60-0.90 s (Fr 18..27 / Ex 19..28). In comparison, RPGAttackTracker.cpp:84 declares CommitTime = 0.40 s (locking heading 0.20 s before active sweep at 0.60 s, adhering to Freeze 16 specifications). The clip is played dynamically via RPGAttackTracker::PlayClip, while damage is resolved by RPGBossLowSweep.
  * **A5:** AN_Boss01_A5_JavelinThrow.txt declares author intent with gauntlet draw 0.00-0.40 s, commitment marker at 0.35 s (zero-based Fr 10 / extraction Fr 11), visual hand release pose at 0.40 s (Fr 12 / Ex 13). In contrast, RPGAttackTracker.cpp:97-99 declares CommitTime = 0.45 s and ActiveStartTime = 0.45 s (triggering projectile spawn in RPGBossHealPunish::Release).
- **Dynamic Telegraph Scaling Predicate & Runtime Clip Swap:**
  * In runtime, close clips are swapped in the live ability instance via RPGCloseClipSwap (AttackMontages[0] GS_Attack01 -> AM_Boss01_A3a, [1] -> A3b, [2] GS_Attack03 -> AM_Boss01_A1; GS_Attack04/A1b is not swapped).
  * Therefore, fallback timing rows matter only if an authored montage fails to load at runtime.
  * RPGTelegraphRules::TargetFor returns a target duration only for close attacks A1/A1b (capped at Min(Cvar, 0.35f)) and A3a/A3b (Cvar); it returns 0.f for all other moves.
  * For A1 fallback (GS_Attack03_Montage), the shared row has ActiveStartTime = 0.35f, which equals the capped target 0.35f. Consequently, RateFor returns 1.f, meaning a positive rpg.CloseTelegraph cvar alone does not compensate the early raw strike (live notify export shows trace opening at 0.115 s; 0.14 s was historical comment approximation). Effective runtime contact times are marked **PENDING CLAUDE RUNTIME CAPTURE**.

---

## 4. Weapon Geometry & Trace Alignment Audit

Offline geometric measurements extracted via Blender 5.1.2 from FBX source files:

```
                                 === WEAPON ALIGNMENT SCHEMATIC ===

   Hidden Leader Reference Mesh: SM_KwangSword (184.4 cm total length)
   [-41.5 cm]=============== POMMEL ======== [0.0 cm ORIGIN] ====================== TIP [+142.9 cm]
                                            \--- Live FTarget trace sockets (runtime pack mesh) ---/
                                                                                    |
   Visible Follower Project Mesh: SM_Boss01_Greatsword (184.6 cm total length)      | 20.4 cm Overhang
   [-21.3 cm]===== POMMEL ================== [0.0 cm ORIGIN] ======================|======= TIP [+163.3 cm]
                                            \--- Exported Empties: BladeStart (15) --- Weapon End (142) ---/
```

### Static Mesh Comparison:
- SM_KwangSword.fbx (SHA-256: c25846828a7c47e507c861943a109be8fb995158cf0de374f99b6949e3109a7b): Length 184.40 cm. Hilt extends -41.50 cm below origin. Blade extends to +142.90 cm above origin.
- SM_Boss01_Greatsword.fbx (SHA-256: f61ea86f0e8d90bf702d73b2f9bb4d77139ab7340fb8f59d2e89fe895f049307): Length 184.63 cm. Hilt extends -21.33 cm below origin. Blade extends to +163.30 cm above origin.
- **Offline Geometric Facts (Source-Confirmed):**
  * The physical blade tip vertex of SM_Boss01_Greatsword extends to Z = +163.30 cm, which is **20.40 cm longer** than SM_KwangSword (Z = +142.90 cm).
  * Cosmetic empty BladeEnd (Z = +140.00 cm) sits **23.30 cm** behind the physical blade tip (+163.30 cm).
  * Cosmetic empty Weapon End (Z = +142.00 cm) sits **21.30 cm** behind the physical blade tip (+163.30 cm).
- **Production Query Authority Boundary:**
  * The production trace queries the pack mesh (Current Collision Mesh, CollisionSockets, and CollisionRadius from RPGPackTrace::FTarget). It does not query the visible cosmetic greatsword.
  * Therefore, adding sockets to SM_Boss01_Greatsword would not alter gameplay queries.
  * In-game spatial alignment between the live pack trace volume and the visible greatsword is marked **PENDING CLAUDE RUNTIME QUERY CAPTURE**.

---

## 5. Visual Discrepancy Register

All findings use a single, stable identification scheme matching visual_discrepancy_register.md:

### VIS-01: A6 Shockwave Expanding Ring has No Production VFX
- **Severity:** CRITICAL
- **Confirmed Fact:** In Source/OneBossFight/Player/RPGBossShockwave.cpp:164-166, the expanding ring is rendered solely via #if !UE_BUILD_SHIPPING DrawDebugCircle(...).
- **Classification:** **Source-Confirmed Candidate Deficiency.**
- **Runtime Limitation:** Actual visual appearance in packaged Shipping builds remains **UNVERIFIED / BLOCKED** pending Claude's packaged capture and verification of independent Niagara/material renderers.
- **Non-Authorized Candidate Suggestion (P1-P8):** If confirmed absent at runtime, author a dedicated Niagara ring emitter matching the 180 cm band thickness expanding from 200 to 1100 cm.

### VIS-02: A2 Overhead Slam Authored Trio Unwired in Attack Tracker
- **Severity:** HIGH
- **Confirmed Fact:** In Source/OneBossFight/Player/RPGAttackTracker.cpp:32, A2 routes to GS_ChargedAttack_Montage. The authored 3-part set (AN_Boss01_A2_Raise, AN_Boss01_A2_ApexHold, AN_Boss01_A2_Slam with floor hit at Z=2 cm) delivered in Report 14 sits idle.
- **Classification:** **Source-Confirmed Asset Routing Discrepancy.**
- **Expected Consequence:** In runtime, the boss is expected to execute the pack twirl/leap instead of the approved grounded two-handed hoist and snap slam. Playback appearance is marked unverified pending runtime capture.
- **Non-Authorized Candidate Suggestion (P1-P8):** Assemble AM_Boss01_A2 montage chaining Raise -> looped ApexHold -> Slam, and wire into the attack selection and tracker table.

### VIS-03: A5 Javelin Release Timing Discrepancy
- **Severity:** HIGH
- **Confirmed Fact:** In AN_Boss01_A5_JavelinThrow.txt, animator declares author intent with CommitTime = 0.35 s and visual hand release at 0.40 s (zero-based Fr 12, extraction Fr 13). In RPGAttackTracker.cpp:97-99, CommitTime = 0.45 s and ActiveStartTime = 0.45 s (triggering projectile spawn in RPGBossHealPunish::Release).
- **Classification:** **Kinematic Marker vs Code Declaration Hypothesis.**
- **Runtime Limitation:** Visual hand release versus actual in-game projectile instantiation remains **UNVERIFIED / BLOCKED** pending synchronized runtime capture with Claude. Prescriptive tuning recommendations are withdrawn until capture evidence is evaluated.

### VIS-04: A4 Low Sweep Geometric Reach vs Component Parameter
- **Severity:** MEDIUM
- **Confirmed Fact:** Source/OneBossFight/Player/RPGBossLowSweep.h:41 declares Reach = 380.0 cm. In historical Report 14 extraction, Hand_R 2D planar distance was measured at 15.8-37.0 cm in unscaled mannequin space, and greatsword blade length is 163.3 cm. In RPGBossLowSweep.cpp:74-80, SweepTouches explicitly tests against player capsule radius (approx 34-42 cm).
- **Classification:** **Geometric Reach Discrepancy Hypothesis.**
- **Runtime Limitation:** True world-space danger boundary on the 1.5x scaled boss versus visible blade tip and player capsule remains **UNVERIFIED / BLOCKED** pending Claude's runtime query overlay capture. Prescriptive tuning recommendations are withdrawn until measured world-space evidence exists.

### VIS-05: Greatsword Physical Tip Overhang past Exported Empties
- **Severity:** MEDIUM
- **Confirmed Fact:** Physical blade tip of SM_Boss01_Greatsword.fbx extends to Z = +163.30 cm (20.40 cm longer than SM_KwangSword). Cosmetic socket BladeEnd (Z = +140.0 cm) sits 23.30 cm behind the tip; Weapon End (Z = +142.0 cm) sits 21.30 cm behind the tip.
- **Classification:** **Source-Confirmed Offline Geometric Discrepancy.**
- **Runtime Limitation:** The production trace queries the live pack FTarget mesh, not the cosmetic follower. Spatial correspondence between the live query sphere and visible blade remains **UNVERIFIED / BLOCKED** pending Claude's query capture.

### VIS-06: Close-Attack Fallback Shared Timing Row & Telegraph Predicate
- **Severity:** MEDIUM
- **Confirmed Fact:** RPGAttackTracker::FindTimingIndex maps authored and fallback montage names to the same timing row (RPGAttackTracker.cpp:105). Pack fallback GS_Attack03 trace opens at 0.115 s (0.14 s was comment approximation). RPGCloseClipSwap replaces close clips at runtime in live ability instances.
- **Classification:** **Source-Confirmed Configuration Structure & Risk Candidate.**
- **Configuration Note:** Fallback matters only if authored montage fails to load. If triggered, shared ActiveStart = 0.35 equals target cap 0.35, returning RateFor = 1; positive cvar alone does not compensate early raw trace (0.115 s). Separate timing rows are an evaluation proposal, not an established active bug.

### VIS-07: Windup Tracking Yaw vs Foot Grounding
- **Severity:** LOW
- **Confirmed Fact:** All 15 authored boss animation clips have zero root excursion (Max Root Excursion from Fr 1 = 0.0000 cm). RPGAttackTracker.cpp:55 applies TrackTurnRate = 360 deg/s during windups.
- **Classification:** **Kinematic Artifact Hypothesis.**
- **Runtime Limitation:** Visual foot sliding remains **UNVERIFIED / BLOCKED** pending runtime visual capture.

### VIS-08: Untracked Damaging Pack Abilities (MidRange, Sprint, Retaliation)
- **Severity:** HIGH
- **Confirmed Fact:** Claude C-87/C-89 and live dump confirmed three live damaging pack abilities: GA_GS_Boss_MidRangeAttack (Mid01, trace 0.637-0.884 s), GA_GS_Boss_SprintAttack (GS_SprintAttackFollowUp, traces 0.037-0.230 s & 0.364-0.551 s), RetaliationAttack (trace 0.444-0.630 s, stun immunity 0-1.267 s). None are registered in RPGAttackTracker::Attacks.
- **Classification:** **Live Natural Coverage Gap & Pending Visual Coverage.**
- **Runtime Limitation:** Native tracker provides no tracking yaw lock, commit point, or telegraph scaling for these moves. Visual presentation, notifies, and threat boundaries await capture.

---

## 6. Submission Status & Coordination Requests

- **Deliverables Resubmitted:**
  * [P0_REPORT.md](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/P0_REPORT.md) (Revision 05)
  * [raw_kinematic_extraction.log](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/raw_kinematic_extraction.log) (Headless Blender 5.1.2 extraction, Revision 05)
  * [extract_baseline_kinematics.py](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/extract_baseline_kinematics.py) (Reproducible script with fail-loud root guard, Revision 05)
  * [weapon_alignment_metrics.md](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/weapon_alignment_metrics.md) (Revision 05)
  * [anim_clip_timing_matrix.md](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/anim_clip_timing_matrix.md) (Revision 05)
  * [visual_discrepancy_register.md](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/visual_discrepancy_register.md) (Revision 05)
- **Status:** **REVIEW-REQUESTED** from Claude (Acting Technical Lead).
- **Coordination Request to Claude:**
  * Synchronized runtime capture of A5 Javelin throw (visual release frame vs projectile actor spawn).
  * Production sweep query overlay capture of A4 Low Sweep (RPGBossLowSweep debug line vs visible SM_Boss01_Greatsword tip and player capsule).
  * Presentation captures of untracked pack abilities (Mid01, Sprint follow-up, Retaliation).
  * Packaged / Development debug-off observation of A6 Shockwave ring.
