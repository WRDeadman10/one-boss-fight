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

## 3. Prerequisite Gates Before Switch Activation

1. **Root-Motion PIE Fidelity Gate (C-1257b):**
   - Paired mannequin vs Greystone-child travel difference must be within <= 10% (backstep 84–98 cm, roll 215–290 cm) with zero play-rate hacking.
2. **Owner Review & Sign-Off:**
   - Owner explicitly reviews the captured footage across the 8 slots above and confirms acceptance.
3. **Fail-Closed Default:**
   - Until both gates are formally satisfied and approved, the player character remains the default Mannequin.
