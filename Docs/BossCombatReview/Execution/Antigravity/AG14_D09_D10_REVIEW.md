# AG-14: Adversarial Review of Codex D09 and D10 (Revision 02)

**Document ID:** `AG14_D09_D10_REVIEW` (Rev 02)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Work Orders:** `ANTIGRAVITY_WORK_ORDER_03.md` (`AG-14`), `ANTIGRAVITY_WORK_ORDER_04.md` (`AG-19`)  
**Status:** DELIVERED (Revision 02: Pinned Exact Line Citations for Findings 1 & 4 per Claude [C-117])  

---

## 1. Executive Summary

In accordance with the adversarial review mandate of `ANTIGRAVITY_WORK_ORDER_03.md` and `ANTIGRAVITY_WORK_ORDER_04.md` (`AG-19`), Antigravity conducted a rigorous cross-examination of Codex's D09 design briefs and D10 implementation matrix against live engine asset exports, animation mechanics, and pack reuse evidence.

Revision 02 formally pins the exact file and line numbers for Finding 1 (`CDO_GA_EnemyDodge.t3d:7`) and Finding 4 (`D09_DEF-005.md:3` vs `D10_IMPLEMENTATION_MATRIX.md:86`), restating Finding 4 per Claude's DEF-005 phase-splitting ruling (`[C-120]`).

---

## 2. Verified Adversarial Findings

### FINDING 1: Pack Dodge Reusability Blindspot (`D09_DEF-005.md:16` & `D09_PACK_REUSE_DELTA.md:15` vs `CDO_GA_EnemyDodge.t3d:7`)
- **Citation:** `D09_DEF-005.md:16` states: *"Minimal profile uses existing supported capabilities with later approved content"*, and `D09_PACK_REUSE_DELTA.md:15` lists `GA_EnemyDodge` as a conditional reuse candidate for dodging.
- **The Defect:** In `Docs/BossCombatReview/Execution/Claude/Evidence/exports/CDO_GA_EnemyDodge.t3d` at **Line 7**, the class default object literally contains:
  ```t3d
  Line 7:    DodgeMontage=()
  Line 9:    bIsDirectional?=False
  ```
  The pack ability `GA_EnemyDodge` has an **empty montage array** (`DodgeMontage=()`) and directional dodging is completely disabled. It does not provide working evasive displacement.
- **Consequence:** Codex treats `GA_EnemyDodge` as a ready-to-wrap execution capability in `RPGDefenseActionExecutor`. In reality, calling `GA_EnemyDodge` without authoring and binding animation montages fails silently. It cannot reduce authoring scope without explicit montage authoring.

---

### FINDING 2: Proactive AI Parry Equivocation (`D09_DEF-005.md:18` & `D09_PACK_REUSE_DELTA.md:16` vs Pack Class Hierarchy)
- **Citation:** `D09_DEF-005.md:18` mandates: *"Parry: startup/finite active window, attack-type restrictions, whiff cost/recovery and failure to normal hit"*, while `D09_PACK_REUSE_DELTA.md:16` cites `GA_EnemyParried` and `GA_PlayerParry` as reuse candidates.
- **The Defect:** In `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Abilities/AI/`, `GA_EnemyParried` is strictly an intake stagger reaction triggered when the **player parries the AI**, and `GA_PlayerParry` is a player-controlled ability requiring player input components.
- **Consequence:** There is **zero proactive AI parry logic** in the third-party pack. Suggesting that `GA_EnemyParried` or player parry can be conditionally reused for boss proactive parrying is a category error. Proactive boss parry requires 100% scratch C++ decision logic and authored boss animation clips (`AN_Boss01_Parry_*`).

---

### FINDING 3: Kinematic Greatsword Conflict in Reused Grab (`D09_HIT-012.md:14` & `D09_PACK_REUSE_DELTA.md:20` vs `CDO_GA_EnemyGrabAttack.t3d`)
- **Citation:** `D09_PACK_REUSE_DELTA.md:20` downgrades HIT-012 to a *"MEDIUM-LARGE candidate"* on the assumption that `GA_EnemyGrabAttack` and `DefaultGrabAttackData` can be reused.
- **The Defect:** `DefaultGrabAttackData` in the pack is authored for unarmed/bipedal creature grabs (using two open hands to seize the victim). The Ember Warden (`BP_ExampleGreatSwordBoss`) holds a 205 cm two-handed greatsword attached to socket `hand_r` / `RPGLookWeapon`. 
- **Consequence:** Executing the pack grab montage without modifying the weapon attachment results in the greatsword floating through the victim's torso or clipping grotesquely through the boss's own skull. Because no weapon-sheathing or weapon-stow animation exists on `SK_CombatMannequin`, a greatsword boss **cannot** reuse unarmed grab animations. HIT-012 requires custom greatsword-in-hand grab animations.

---

### FINDING 4: D10 Lists Only P6 for Boss Defenses, Conflating Mechanics with Decision Policies (`D10_IMPLEMENTATION_MATRIX.md:86` vs `MASTER_EXECUTION_PLAN.md:38,41`)
- **Citation:** In `Docs/BossCombatReview/Execution/Codex/D10_IMPLEMENTATION_MATRIX.md` at **Line 86** (and CSV Line 87), Codex schedules `BOSS-DEF-005` entirely in **Phase P6**:
  ```markdown
  Line 86: | BOSS-DEF-005 | Boss defense: Fallible directional/costed block/parry/dodge | Boss.DefenseProfile | RPGDefenseActionExecutor | P6 | ...
  ```
- **The Defect:** In `Docs/BossCombatReview/Execution/Codex/D09_DEF-005.md` at **Line 3**, Codex notes:
  ```markdown
  Line 3: P6 after WP4 accepted actions, P3 shared defense/damage and P5 recovery; networking alongside, P8 final integration.
  ```
  Per Claude's ruling (`[C-120]`) and `MASTER_EXECUTION_PLAN.md`:
  - `MASTER_EXECUTION_PLAN.md:38` assigns core damage and defense semantics (resolver, guard/parry/iframe state, outcomes) strictly to **Phase P3** (*"Defenses, Reaction Budget & Posture"*).
  - `MASTER_EXECUTION_PLAN.md:41` assigns decision and movement intelligence (when AI chooses to defend, evasion tactics) to **Phase P6** (*"Player Builds, Weapons & Secondary Bosses"*).
- **Consequence:** D10 line 86 lists only P6, conflating P3 defense state/resolver mechanics with P6 AI decision policies. Scheduling the entire row in P6 omits defense state/resolver mechanics from Phase P3 delivery. The row must be split or explicitly dual-phased: Phase P3 for defense resolution mechanisms, and Phase P6 for AI decision logic.

---

### FINDING 5: Omission of Existing Yaw Tracking in Warping Design (`D09_ANM-006.md:16-24` vs `montage_notifies_2026-10-25.txt`)
- **Citation:** `D09_ANM-006.md:16` specifies a ground-up `RPGWarpExecutor` and `RPGMotionOwnershipController` to handle all telegraph alignment and translation.
- **The Defect:** Codex fails to acknowledge that rotational yaw alignment during telegraph is **already implemented and operational** in the pack via `ANS_SetDesiredRotation_C` (e.g. `GS_Attack01_Montage` lines 4-6: `ANS_SetDesiredRotation_C at 0.000s for 0.317s`).
- **Consequence:** By treating all alignment as an unbuilt warping problem, Codex over-engineers the requirement. The real missing technical capability in ANM-006 is **bounded root-motion translation warping**, not rotation. Recognizing `ANS_SetDesiredRotation_C` allows the team to isolate warping development strictly to position clamping.

---

### FINDING 6: Absence of Visual/Acoustic Fairness Cues in Adaptation Matrix (`D10_IMPLEMENTATION_MATRIX.md:24` vs `D09_AWR-008.md`)
- **Citation:** In `D10_IMPLEMENTATION_MATRIX.md:24`, the acceptance evidence for `BOSS-AWR-008` is restricted entirely to internal data: *"D09_AWR-008 tests; NEW Ref.BOSS-AWR-008: Observable repeated patterns alter capped preference after delay, then decay; target/reset isolation; hard eligibility unchanged"*.
- **The Defect:** While `D09_AWR-008.md:18` briefly mentions "observable cue", D10 omits all perceptual and visual/audio acceptance criteria from the primary tracking matrix.
- **Consequence:** Soulslike boss adaptation without clear sensory feedback feels like arbitrary input reading to players. For `AWR-008` to satisfy its fairness requirement, the acceptance contract in D10 must explicitly mandate the visual/audio tell (e.g. `AN_Boss01_Adapt_Tell`, dorsal brazier flare `NS_AdaptationGlow`, and audio hum `A_AdaptationHum`).

---

## 3. Evidence and Limits Table

| Finding | Cited Codex Passage | Physical Proof / Repository Verification | Impact / Correction |
| :--- | :--- | :--- | :--- |
| **1. Empty Pack Dodge** | `D09_DEF-005.md:16`, `D09_PACK_REUSE_DELTA.md:15` | `CDO_GA_EnemyDodge.t3d:7`: `DodgeMontage=()`, line 9: `bIsDirectional=False`. | Dodge cannot execute without authored montage arrays. |
| **2. AI Parry Deficit** | `D09_DEF-005.md:18`, `D09_PACK_REUSE_DELTA.md:16` | Inspection of `Blueprints/Abilities/AI/`: only `GA_EnemyParried` (victim reaction). | Proactive AI parry requires 100% custom C++ & animation. |
| **3. Greatsword Grab Clash**| `D09_HIT-012.md:14`, `D09_PACK_REUSE_DELTA.md:20` | `SM_Boss01_Greatsword` on `hand_r`; no sheath/stow anim on `SK_CombatMannequin`. | Unarmed pack grab unusable with two-handed greatsword. |
| **4. Defense Phase Contradiction**| `D10_IMPLEMENTATION_MATRIX.md:86` (P6) | `D09_DEF-005.md:3` cites P3/P5; Program assigns Defenses to P3. | Move DEF-005 primary delivery phase from P6 to P3. |
| **5. Uncredited Yaw Notifies** | `D09_ANM-006.md:16-24` | `montage_notifies_2026-10-25.txt`: `ANS_SetDesiredRotation_C` at 0.000s. | Isolate warping scope to translation; reuse yaw notify. |
| **6. Missing Adaptation Tell**| `D10_IMPLEMENTATION_MATRIX.md:24` | Acceptance text lists only internal pattern decay, omitting player-facing cues. | Add perceptual cues (`AN_Boss01_Adapt_Tell`) to D10. |
