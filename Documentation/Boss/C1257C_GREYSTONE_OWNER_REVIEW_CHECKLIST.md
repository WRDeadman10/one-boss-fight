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

## 3. Pre-Populated Capture & Clip Routing (`BC-A24`, `[C-1289]` Status)

- **Root-Motion Paired Evidence (`[C-1289]` Run 4 — `P_C1282_GREYSTONE_RM4_*`):**
  - **Root Fix & Re-Author Verified:** `A_C1285_GREYSTONE_ROOTFIX/fix_write_editor_status.txt` (`FIX_editor pass=True`) updated `RTG_ERFit_Greystone` Root FK to `GLOBALLY_SCALED` and emitted `Saved/ERFitRM_20261111_023747.json` (`AN_ER_Backstep_Mixamo_V2_Fit_GreystoneRM`: source root `156.75 cm`, output root `180.81 cm`, `root_ratio = 1.15346`). `B_C1286_GREYSTONE_RM` recreated the five C-1282 wrapper/BP assets on the `*_RM` sequences (`SAVED_COUNT=5`, readback `0`, `replace_write pass=True`).
  - **RM4 Paired Gate Numbers (`finished=True route_verified=True`):**
    - **Mannequin Control (`P_C1282_GREYSTONE_RM4_MANNEQUIN`):** Backstep `5/5` (`79.89–86.48 cm`, mean **`83.83 cm`**, montage end `74.99–81.15 cm`); Quick Roll `5/5` (`260.30–271.73 cm`, mean **`264.28 cm`**, `5/5` in `215–290 cm`).
    - **Greystone (`P_C1282_GREYSTONE_RM4_GREYSTONE`):** Backstep (`AM_ER_Backstep_Mixamo_V2_Fit_Greystone`) **`5/5`** at **`98.03–100.20 cm`** (mean **`99.35 cm`**, montage end `91.12–94.11 cm`). Quick Roll (`Dodge_Small_Forward_Roll_Montage_Grey`) `4/5` at **`0.00 cm`** + trial 5 `MONTAGE_NOT_OBSERVED` (pack `_Grey` remains pelvis-baked until `BK-1`).
  - **`[C-1289]` Decision 1 (Skeleton-Scaled Pairing Gate):** Keep `GLOBALLY_SCALED` (no foot sliding); evaluate Greystone distance in the scaled band (`Mannequin band × root_ratio = 97–113 cm` backstep, `248–334 cm` quick roll) and pairing `<= 10%` after dividing by `root_ratio` (`99.35 / 1.15346 = 86.13 cm` vs `83.83 cm`, **`+2.75%`**; `~+2.8%` rounded: **Backstep Gate PASS**). **Quick Roll Gate: OPEN** until Codex `BK-1` re-retargets the Greystone pack roll/dodge sequences.
  - **Greystone Blocker — `KI-052` `GetMainAnimBP` Log Flood (`[C-1284]`):** `457` `"Accessed None"` warnings (`281` before first press) from `ABP_UnarmedLayer_Grey` / `ABP_CombatAnimLayersBase_Grey` (absent in mannequin arm); tracked prior to Owner clip capture (`[C-1289]` Decision 3 runs clip capture after `BK-1`).
- **Owner 8-Slot Visual Review Frames / Reel Destination (`BC-A21..A23` -> `BD-A21..A22`):**
  - Target folder: `D:/FightVideo/greystone_review/` (**PENDING CAPTURE** — scheduled after `BK-1` `[C-1289]` Decision 3; stitched clip never staged in git).
  - Pre-mapped clip slots (`01–08` matching Section 2 above): `01_Idle`, `02_Run`, `03_LightAttack`, `04_HeavyAttack`, `05_Roll` (`248–334 cm` scaled / `215–290 cm` normalized), `06_Backstep` (`97–113 cm` scaled / `84–98 cm` normalized — RM4 **PASS**), `07_GuardCounter`, `08_Plunge`.

---

## 4. Prerequisite Gates Before Switch Activation

1. **Root-Motion PIE Fidelity Gate (`[C-1289]` Decision 1):**
   - Paired mannequin vs `(Greystone / root_ratio)` travel difference must be `<= 10%` (`root_ratio` read from `Saved/ERFitRM_*.json`, e.g. `1.15346` -> scaled bands `97–113 cm` backstep **PASS**, `248–334 cm` roll **OPEN until `BK-1`**) with zero play-rate hacking.
2. **Owner Review & Sign-Off:**
   - Owner explicitly reviews the captured footage across the 8 slots above (seeing both normalized and raw scaled measurements per `[C-1289]` Decision 1) and confirms acceptance.
3. **Fail-Closed Default:**
   - Until both gates are formally satisfied and approved (`[C-1289]` Decision 3), the player character remains the default Mannequin.
