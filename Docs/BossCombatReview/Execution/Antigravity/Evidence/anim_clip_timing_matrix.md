# P0 Evidence: Boss Animation & Gameplay Timing Matrix

Date: 2026-10-25 (Revision 05)
Investigator: Antigravity (Accountable Visual Investigator)
Review Requested from: Claude (Acting Technical Lead)
Reference Tasks: U06, BOSS-ANM-001, BOSS-ANM-002, BOSS-ANM-003, BOSS-PAC-001
Reproducibility: Script extract_baseline_kinematics.py -> Log raw_kinematic_extraction.log

---

## 1. Provenance Separation

This matrix strictly separates:
1. **Authored .txt Sidecar Metadata (Author Intent):** Intended clip length, pose tell description, commitment marker, and active window declared by the animator in Import/Boss01/Animations/<Clip>.txt. Frame labels in .txt sidecars are zero-based (0 .. N-1).
2. **Offline Skeletal Extraction:** Sample counts, 30 fps elapsed duration (samples - 1) / fps, root excursion, and bone bounds extracted via headless Blender 5.1.2. Extraction frames are 1-based (1 .. N). Offset convention: zero-based sidecar frame F_0 corresponds to 1-based extraction frame F_1 = F_0 + 1. Strict guard verifies root sampling mode (`pose_bone` or `armature_object`), failing loudly if absent.
3. **C++ Tracker Declarations:** Nominal montage-local properties declared in Source/OneBossFight/Player/RPGAttackTracker.cpp.
4. **Dynamic Scaling / Telegraph Logic:** UpdateTelegraph play rate scaling governed by RPGTelegraphRules::TargetFor and RateFor:
   - TargetFor(MoveId, CvarValue) returns a target tell duration only for close attacks: A1 and A1b (capped at Min(CvarValue, 0.35f)), and A3a and A3b (CvarValue). A2, A4, A5, A6, and untracked moves receive 0.f (no telegraph scaling).
   - RateFor(ActiveStart, Target, Position) returns 1.f if Target <= ActiveStart. In the A1 fallback (GS_Attack03_Montage), the shared timing row has ActiveStartTime = 0.35f, which equals the capped target 0.35f. Consequently, RateFor returns 1.f regardless of cvar value, meaning a positive rpg.CloseTelegraph cvar alone does not slow down or compensate the early raw strike (live trace opens at 0.115 s; 0.14 s was historical comment approximation) of the A1 fallback.
5. **Runtime Replacement Context:** In runtime, close clips are replaced in the live ability instance via RPGCloseClipSwap (AttackMontages[0] GS_Attack01 -> AM_Boss01_A3a, [1] -> A3b, [2] GS_Attack03 -> AM_Boss01_A1; GS_Attack04/A1b is not swapped). Therefore, fallback timing rows matter only if an authored montage fails to load.
6. **Effective Runtime Hit Time:** Observed in-game contact times, marked **PENDING CLAUDE RUNTIME CAPTURE**.

---

## 2. Timing and Kinematics Matrix

| Move | Source FBX & Sidecar Metadata | Samples & Elapsed Duration (30 fps) | Authored Pose Tell & Commit Marker (.txt Sidecar, Author Intent) | C++ Tracker CommitTime | Authored Active Window (.txt Sidecar, Author Intent) | C++ Tracker Active Window | Dynamic Telegraph Scaling | Effective Runtime Contact |
|---|---|---|---|---|---|---|---|---|
| **A1** | AN_Boss01_A1_QuickSlash.fbx<br>AN_Boss01_A1_QuickSlash.txt<br>*(Fallback: GS_Attack03)* | 37 samples (1..37)<br>1.200 s elapsed<br>Root Excursion: 0.00 cm | Tell: 0.00-0.35 s (right coil, stance drops 11 cm)<br>Commit marker: **0.33 s** (Fr 10 / Ex 11) | **0.33 s** | **0.35-0.50 s** (Fr 11..15 / Ex 12..16, horizontal slash) | **0.35-0.50 s** | Authored clip has bAuthoredWindup=true; runs at 1.0x rate.<br>Fallback GS_Attack03 live trace opens at 0.115 s (0.14 s in code comment); runs at 1.0x | *Pending Claude capture* |
| **A1b** | *No authored clip*<br>GS_Attack04_Montage | Pack native | Tell: 0.00-0.12 s (pack raw)<br>Commit: **0.12 s** | **0.12 s** | Pack native trace: ~0.16-0.46 s | **0.16-0.46 s** | TargetFor caps target at Min(Cvar, 0.35 s); scales windup when rpg.CloseTelegraph > 0 | *Pending Claude capture* |
| **A3a** | AN_Boss01_A3a_Combo1.fbx<br>AN_Boss01_A3a_Combo1.txt<br>*(Fallback: GS_Attack01)* | 25 samples (1..25)<br>0.800 s elapsed<br>Root Excursion: 0.00 cm | Tell: 0.00-0.40 s (high guard raise, stance drops 9 cm)<br>Commit marker: **0.38 s** (Fr 11 / Ex 12) | **0.38 s** | **0.40-0.60 s** (Fr 12..18 / Ex 13..19, diagonal cleave) | **0.40-0.60 s** | Authored clip has bAuthoredWindup=true; runs at 1.0x rate | *Pending Claude capture* |
| **A3b** | AN_Boss01_A3b_Combo2.fbx<br>AN_Boss01_A3b_Combo2.txt<br>*(Fallback: GS_Attack02)* | 41 samples (1..41)<br>1.333 s elapsed<br>Root Excursion: 0.00 cm | Tell: 0.00-0.15 s (snap torque from A3a end pose)<br>Commit marker: **0.13 s** (Fr 4 / Ex 5) | **0.13 s** | **0.15-0.40 s** (Fr 5..12 / Ex 6..13, reverse cleave) | **0.15-0.40 s** | Authored clip has bAuthoredWindup=true; runs at 1.0x rate | *Pending Claude capture* |
| **A2** | Authored Trio:<br>AN_Boss01_A2_Raise.fbx<br>AN_Boss01_A2_ApexHold.fbx<br>AN_Boss01_A2_Slam.fbx<br>*(Live: GS_ChargedAttack)* | Raise: 19 smp (0.600 s)<br>ApexHold: 36 smp (1.167 s)<br>Slam: 42 smp (1.367 s)<br>Root Excursion: 0.00 cm | Hoist: 0.00-0.60 s<br>Apex Hold: Looping strained poise with 4 Hz flutter<br>Slam Snap: 0.00-0.17 s (Fr 0..5 / Ex 1..6) | Tracker nominal: **1.68 s** (for pack montage) | Authored floor impact occurs at Frame 5 of Slam (Z = 2 cm) | Tracker nominal: **1.93-2.11 s** (for pack montage) | TargetFor returns 0.f (no telegraph scaling). **Authored trio is currently UNWIRED in tracker!** | *Pending Claude capture* |
| **A4** | AN_Boss01_A4_LowSweep.fbx<br>AN_Boss01_A4_LowSweep.txt | 54 samples (1..54)<br>1.767 s elapsed<br>Root Excursion: 0.00 cm | Tell: 0.00-0.60 s (crouch torso coil, pelvis drops 16 cm)<br>Commit marker: **0.50 s** (Fr 15 / Ex 16) | **0.40 s** | **0.60-0.90 s** (Fr 18..27 / Ex 19..28, floor sweep) | **0.60-0.90 s** | Played by RPGAttackTracker::PlayClip; RPGBossLowSweep resolves damage. Rate governed by tracker; TargetFor returns 0.f | *Pending Claude capture* |
| **A5** | AN_Boss01_A5_JavelinThrow.fbx<br>AN_Boss01_A5_JavelinThrow.txt | 31 samples (1..31)<br>1.000 s elapsed<br>Root Excursion: 0.00 cm | Tell: 0.00-0.40 s (left arm draw high beside cowl)<br>Commit marker: **0.35 s** (Fr 10 / Ex 11)<br>Visual Hand Release: **0.40 s** (Fr 12 / Ex 13) | **0.45 s** | Kinematic hand follow-through: 0.40-0.43 s (Fr 12..13 / Ex 13..14) | **0.45-0.50 s** | Projectile speed = 2500 cm/s; heading locked at CommitTime; TargetFor returns 0.f | *Pending Claude capture* |
| **A6** | Pack GS_LeapAttack_Montage | Pack native (1.870 s) | Leap and airborne flight: 0.00-0.75 s | **0.16 s** | Central landing impact: 0.75-1.17 s | **0.75-1.17 s** | TargetFor returns 0.f; wave component launches at active window | *Pending Claude capture* |
| **MidRange** | Mid01_Anim_Montage<br>(GA_GS_Boss_MidRangeAttack) | Pack native<br>(ExampleSwordMob) | Pack native mid-range attack | *Untracked* | Live notify trace: **0.637 to 0.884 s**<br>(rotation 0.127 to 0.615 s) | *Untracked* | Untracked by native RPGAttackTracker | *Pending Claude capture* |
| **Sprint** | GS_SprintAttackFollowUp_Montage<br>(GA_GS_Boss_SprintAttack) | Pack native<br>(GreatswordBoss) | Sprint speed 800, 1.5 s limit, 200 follow-up range | *Untracked* | Live notify traces: **0.037 to 0.230 s** and **0.364 to 0.551 s** | *Untracked* | Untracked by native RPGAttackTracker | *Pending Claude capture* |
| **Retaliation** | RetaliationAttack_Montage<br>(Pack reaction) | Pack native<br>(ExampleSwordMob) | Pack native retaliation attack | *Untracked* | Live notify trace: **0.444 to 0.630 s**<br>(hit-stun immunity 0 to 1.267 s) | *Untracked* | Untracked by native RPGAttackTracker | *Pending Claude capture* |
| **Riposte** | AN_Riposte_Player_Front.fbx<br>(Paired with Boss reaction) | 49 samples (1..49)<br>1.600 s elapsed<br>Root Excursion: **90.00 cm** | Advance +Y: (0,0,0) to (0,90,0) cm reached at 0.70 s (Fr 21 / Ex 22) and held | Dynamic | Impact at 0.80 s (Fr 24 / Ex 25); active 0.70-1.10 s | Dynamic | Driven via dynamic montage pair in RPGBossStagger | *Pending Claude capture* |

*Note: In table above, Fr denotes zero-based sidecar frame (0..N-1), Ex denotes 1-based Blender extraction frame (1..N).*

---

## 3. Kinematic Notes & Hypotheses

1. **A5 Release Timing Discrepancy (Hypothesis):** In AN_Boss01_A5_JavelinThrow.txt, the animator declares author intent with CommitTime = 0.35 s and visual hand release at 0.40 s (zero-based Frame 12, extraction Frame 13). In RPGAttackTracker.cpp, CommitTime = 0.45 s and ActiveStartTime = 0.45 s (triggering projectile spawn in RPGBossHealPunish::Release). Whether visual hand release precedes projectile spawn or prop detachment in-game remains an **unverified hypothesis pending synchronized runtime capture with Claude**.
2. **A4 Low Sweep Commitment Comparison:** The authored sidecar metadata (AN_Boss01_A4_LowSweep.txt) declares author intent commitment at 0.50 s (zero-based Frame 15, extraction Frame 16), while the tracker declares CommitTime = 0.40 s (locking heading 0.20 s before active sweep at 0.60 s, adhering to Freeze 16 specifications). This represents a 100 ms difference between code commitment declaration and the author's card, not a functional defect. The clip is played dynamically via RPGAttackTracker::PlayClip, while damage is resolved by RPGBossLowSweep.
3. **Close-Attack Fallback Shared Timing Row & Telegraph Predicate (Configuration Structure & Risk):**
   - RPGAttackTracker::FindTimingIndex maps authored and fallback names to the same timing row (RPGAttackTracker.cpp:105).
   - In runtime, close clips are swapped in the live ability instance via RPGCloseClipSwap (AttackMontages[0] GS_Attack01 -> AM_Boss01_A3a, [1] -> A3b, [2] GS_Attack03 -> AM_Boss01_A1). Thus, fallback rows matter only if an authored montage fails to load.
   - If fallback executes: RPGTelegraphRules::TargetFor targets only A1/A1b/A3a/A3b. For A1 fallback (GS_Attack03_Montage), the shared row has ActiveStartTime = 0.35f. TargetFor caps the target at Min(Cvar, 0.35f) = 0.35f. Because Target (0.35) <= ActiveStart (0.35), RateFor returns 1.f. Thus, setting rpg.CloseTelegraph > 0 does NOT scale down the A1 fallback windup; it executes at raw pack speed (live notify export shows trace opening at 0.115 s; 0.14 s was historical comment approximation), prior to the shared row's CommitTime of 0.33 s.
4. **Player Riposte Root Motion Reconciliation:**
   - In offline extraction, AN_Riposte_Player_Front.fbx exhibits exactly 90.00 cm root excursion along +Y (from (0,0,0) to (0,90,0) cm at 0.70 s / Frame 21, held through 1.60 s), confirming the forward lunge is fully authored into the root node.
   - All 15 boss animation clips and the boss riposte reaction maintain strictly 0.0000 cm root excursion (in-place animations).
