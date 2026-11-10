# C1257c Greystone Player Character Visual Review Checklist

**Authority:** Claude Lead Directives `[C-1257]`, `[C-1257c]` (2026-11-10)  
**Status:** Plan/Review Checklist only (Read-only; zero runtime wiring, zero asset modification)  
**Context:** C-1227 blind evaluation unanimous winner (Candidate_A = Greystone, 47/48, 97.9%, 0 zeroes). The player character switch remains strictly **HELD fail-closed** pending explicit Owner approval following this visual review and root-motion PIE fidelity verification (C-1257b).

---

## 1. Owner Video Review Evaluation Protocol

For each animation state captured in the Greystone review reel / gameplay showcase, evaluate using the standard 0–2 scoring rubric established in `C1174_PLAYER_FIT_TEST_SCORECARD.md`:
- **Score 2 (Clean / Production Ready):** Natural posture, perfect weapon anchoring, clean foot planting (no skate), zero mesh interpenetration or geometry detachment.
- **Score 1 (Minor Artifact / Acceptable):** Minor clipping during extreme extension, slight cloth jitter, or negligible foot drift not affecting combat feel.
- **Score 0 (Failure / Unacceptable):** Severe mesh self-intersection, floating weapon/shield, significant sliding or broken IK.

---

## 2. Animation Clip Review Checklist

| Animation Slot | Primary Action / ER Archetype | Key Inspection Sites | Success Criteria | Score (0-2) | Notes / Observations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01. Idle** | Neutral Combat Stance | Feet grounding, cloak draping, sword/shield grip | Weight settled on hips; hands correctly grasp sword hilt and shield straps; cloak rests without geometry clipping into legs. | [ ] | Baseline combat ready stance. |
| **02. Run** | Standard Forward Locomotion | Foot contact timing, pelvic sway, torso tilt | No foot skating during acceleration/deceleration; shield and sword hold firm relative to forearm/hand; clean stride cycle. | [ ] | Locomotion fidelity check. |
| **03. Light Attack** | Ground Light Cleave | Hand-to-hilt alignment, slash arc, recovery blend | Sword hilt does not drift from palm; shoulder/breastplate armor does not clip through chest mesh during swing; recovery blends cleanly to idle. | [ ] | Primary melee bread-and-butter. |
| **04. Heavy Attack** | Overhead / Thrust Power Strike | Two-handed or heavy commitment, weapon trail path | Grounded stance during windup; clean apex hold without elbow inversion; forceful follow-through. | [ ] | Heavy punish commitment. |
| **05. Roll** | Forward / Directional Dodge Roll | Tuck phase, shoulder contact, recovery stand | Clean tuck over shoulder; cape/armor does not invert during upside-down frame; roll distance within verified 215–290 cm window; zero floor clipping. | [ ] | Defensive invulnerability window. |
| **06. Backstep** | Neutral Evasion (Mixamo V2) | Initial hop, backward displacement, landing plant | Snappy hop backward; displacement within verified 84–98 cm window; both feet plant solidly without sliding on landing; weapon held ready. | [ ] | Spacing / recovery reset tool. |
| **07. Guard Counter** | Post-Block Riposte Rise | Shield deflection transition into rising heavy strike | Seamless transition from block stance; strong upward swing path; no shield detachment during transition. | [ ] | Defensive-to-offensive conversion. |
| **08. Plunge** | Aerial Downward Plunge Strike | Mid-air descent posture, impact strike, landing recovery | Vertical weapon orientation; cape billows appropriately upwards; high-impact landing compression into ground plane without capsule pop. | [ ] | Verticality / drop attack. |

---

## 3. Pre-Populated Capture & Clip Routing (`BC-A24`, `[C-1282]` Status)

- **Root-Motion Paired Evidence (`[C-1284]` / `[C-1285]` Status):**
  - **Mannequin Reference Baseline (`P_C1282_GREYSTONE_RM3_*` Run 3):** Backstep `5/5` started, **`76.3 cm` mean (`72.1–80.4 cm`) at montage end** (prior `C-1063` measured to rest `96.6–97.8 cm`; driver Run 4 adds idle wait + measure-to-rest `SETTLE`); Quick Roll `2/5` at **`243.6–253.8 cm`** (`215–290 cm` band; roll 3 swallowed while prior roll still blending out -> Run 4 waits for `speed < 5 cm/s` & no active montage).
  - **Greystone Blocker 1 — `0.00 cm` Root Motion (Root Cause Identified `[C-1285]`):** Greystone child possessed `BP_GreystoneERPlayer_C`, played `AM_ER_Backstep_Mixamo_V2_Fit_Greystone` (`i-frames` active `0.095–0.108 s`, matching copied `0.091–0.414 s` window) and `Dodge_Small_Forward_Roll_Montage_Grey`, but displaced `0.00 cm` on `5/5` backsteps and `3/3` quick rolls. Root cause (`P_C1284_GREYSTONE_ROOTBONE`): IK retargeter defaulted `Root` chain FK `TranslationMode = None` (`IKRetargetSettings.h:86`), baking travel into `pelvis` (`180.81 cm` pelvis vs `0.00 cm` root on backstep; `511.64 cm` pelvis vs `0.00 cm` root on `Dodge_Small_Forward_Roll_Grey`). **Mandatory Retarget Contract:** Every Greystone retarget must map `Root -> Root` with FK `TranslationMode = GLOBALLY_SCALED` + prove root XY travel via `AnimationLibrary.get_bone_pose_for_time` (`*_RM` ER sequences + `_Grey` pack sequences) before Owner review clip capture.
  - **Greystone Blocker 2 — `KI-052` `GetMainAnimBP` Log Flood (`[C-1284]`):** `457` `"Accessed None"` warnings (`281` before first press) from `ABP_UnarmedLayer_Grey` / `ABP_CombatAnimLayersBase_Grey` (absent in mannequin arm); tracked as open Greystone visual/log gate prior to Owner clip capture.
- **Owner 8-Slot Visual Review Frames / Reel Destination (`BC-A21..A23` -> `BD-A21..A22`):**
  - Target folder: `D:/FightVideo/greystone_review/` (**PENDING CAPTURE** — blocked on `_RM` re-retarget & `KI-052` triage; stitched clip never staged in git).
  - Pre-mapped clip slots (`01–08` matching Section 2 above): `01_Idle`, `02_Run`, `03_LightAttack`, `04_HeavyAttack`, `05_Roll` (`215–290 cm` gate), `06_Backstep` (`84–98 cm` gate), `07_GuardCounter`, `08_Plunge`.

---

## 4. Prerequisite Gates Before Switch Activation

1. **Root-Motion PIE Fidelity Gate (C-1257b):**
   - Paired mannequin vs Greystone-child travel difference must be within <= 10% (backstep 84–98 cm, roll 215–290 cm) with zero play-rate hacking.
2. **Owner Review & Sign-Off:**
   - Owner explicitly reviews the captured footage across the 8 slots above and confirms acceptance.
3. **Fail-Closed Default:**
   - Until both gates are formally satisfied and approved, the player character remains the default Mannequin.
