# C-1174 Player Character Fit Test: Visual Scoring Rubric & Capture Plan

**Document Version:** 1.0  
**Authority:** Claude Lead Directive `[C-1215]` (2026-11-09).  
**Co-Owners:** Antigravity (Visual Rubric & Blind Evaluation) & Codex (Kit Scripts & Technical Score Sheet).  
**Scope:** Evaluation of candidate character meshes (**Greystone**, **Steel**, **Grux**) retargeted across the 6-clip Elden Ring player animation set.

---

## 1. Candidate Meshes & The 6-Clip ER Evaluation Set

### Candidate Meshes & Baseline Control
0. **Candidate_0 (Control Baseline):** UE Mannequin (`SK_Mannequin`) providing the ground-truth reference for camera framing, socket alignment, and root displacement.
1. **Candidate A / B / C (Anonymous Candidates):**
   - **Paragon Greystone:** Archetypal human knight in plate armor.
   - **Paragon Steel:** Heavy armored titan/colossus with massive proportions.
   - **Paragon Grux:** Bestial dual-wield/heavy silhouette with hunched posture.

### The 6 Evaluation Clips (`Content/OneBossFight/Player/Animations/`)
1. **Clip 1 (ER-01):** `AM_ER_Attack_Air_Light` (Aerial light slash)
2. **Clip 2 (ER-02):** `AM_ER_Attack_Air_Heavy_Plunge` (Downward vertical plunge attack)
3. **Clip 3 (ER-03):** `AM_ER_Attack_GuardCounter` (Heavy upward retaliatory guard counter)
4. **Clip 4 (ER-04):** `AM_ER_Backstep_Back` (Standard evasive backstep hop)
5. **Clip 5 (ER-05):** `AM_ER_Backstep_Mixamo` (Mixamo evasive retreat V1)
6. **Clip 6 (ER-06):** `AM_ER_Backstep_Mixamo_V2` (Refined grounded evasive backstep V2)

---

## 2. Visual Scoring Rubric (Per-Clip: 0–2 Points Each, Max 10 Points)

Every clip is evaluated against 5 rigorous visual and physical criteria:

| Criterion | 0 Points (Failure) | 1 Point (Marginal) | 2 Points (Flawless) |
|---|---|---|---|
| **1. Weapon in Hand** | Weapon floats, detaches from palm, or inverts orientation during active swing/hit frames. | Minor socket drift ($< 3\text{ cm}$) or slight finger penetration through grip. | Weapon firmly seated in palm socket with rigid hand alignment across all frames. |
| **2. No Foot Sliding** | Severe ice-skating, ungrounded floating, or dragging feet during stance changes. | Noticeable sliding during recovery frames ($> 5\text{ cm}$), but planted at peak impulse. | Absolute ground adherence; feet plant solidly with zero visible sliding or drift. |
| **3. No Armor / Weapon Clipping** | Severe penetration of weapon blade through torso, or pauldron/shield slicing through head/body. | Minor secondary armor plate or cloth overlap during extreme torsion frames. | Clean volumetric clearance; weapon and armor articulate without intersecting flesh/armor. |
| **4. ER Silhouette & Stance** | Broken silhouette, awkward hunching, or non-heroic proportions that break Soulslike feel. | Passable knight posture, but slightly stiff or proportions look stretched on the skeleton. | Authentic, weighty Elden Ring knight silhouette; grounded, deliberate, and imposing combat stance. |
| **5. Root-Motion Fidelity** | Total displacement differs by $> 25\%$ compared to the Mannequin baseline. | Displacement variance between $10\%$ and $25\%$ of baseline. | Displacement strictly within $\pm 10\%$ of baseline displacement along primary movement vector. |

### Aggregate Scoring Breakdown
- **Max Points Per Clip:** $5 \times 2 = 10\text{ points}$
- **Max Points Per Character:** $6 \text{ clips} \times 10 = 60\text{ points}$
- **Acceptance Threshold:** $\ge 50 / 60\text{ points}$ ($\ge 83.3\%$) with zero 0-point scores in Weapon in Hand or Foot Sliding.

---

## 3. Capture Plan (Lead-Executed Under Dual Engine Lock)

To ensure completely objective, apples-to-apples visual evaluation, captures must adhere to identical staging parameters:

1. **Rendering & Camera Configuration:**
   - **Environment:** Clean floor grid in `L_SevarogArena` or dedicated neutral capture level.
   - **Camera Angle 1 (Side Profile):** Fixed orthogonal-style side view ($90^\circ$ relative to movement vector) framing full body + weapon envelope.
   - **Camera Angle 2 (Three-Quarter Diagonal):** Fixed $45^\circ$ perspective view capturing facial orientation, shoulder rotation, and shield/weapon depth.
   - **Framing Distance:** Uniform distance ($400\text{ cm}$ focus distance, $50\text{ mm}$ focal length) centered at character root.
2. **Playback Timing:**
   - **Slomo Factor:** `0.5` ($50\%$ playback speed) to enable frame-accurate inspection of foot contact timestamps and weapon socket transitions.
3. **Capture Output Directory (Off-Repo):**
   - Base Directory: `D:/FightVideo/fit_test/`
   - Structure:
     - `D:/FightVideo/fit_test/<Candidate_ID>/Clip01_AirLight/`
     - `D:/FightVideo/fit_test/<Candidate_ID>/Clip02_AirPlunge/`
     - `D:/FightVideo/fit_test/<Candidate_ID>/Clip03_GuardCounter/`
     - `D:/FightVideo/fit_test/<Candidate_ID>/Clip04_Backstep/`
     - `D:/FightVideo/fit_test/<Candidate_ID>/Clip05_MixamoV1/`
     - `D:/FightVideo/fit_test/<Candidate_ID>/Clip06_MixamoV2/`

---

## 4. Blind Evaluation Protocol (Antigravity Audit)

To eliminate any unconscious bias toward Greystone (the incumbent hero) or Steel/Grux:
1. **Lead Blind Export:**
   - Claude exports captures mapping the three characters to randomized tokens: `Candidate_A`, `Candidate_B`, and `Candidate_C`.
   - The token mapping key (`Candidate_Map.json`) is retained privately by Lead Claude and NOT posted to `TEAM_MAILBOX.md`.
2. **Independent Scoring Turn:**
   - Antigravity reviews the captured image sequences/video clips in `D:/FightVideo/fit_test/` strictly by token.
   - Antigravity fills the 5-criteria scorecard for each clip and posts the finalized point matrix (`Candidate_A: XX/60`, `Candidate_B: YY/60`, `Candidate_C: ZZ/60`) to `TEAM_MAILBOX.md`.
3. **De-anonymization & Decision:**
   - Upon receipt of the locked scores, Claude reveals the candidate identity map and declares the winning character for Owner review and production retarget promotion.
