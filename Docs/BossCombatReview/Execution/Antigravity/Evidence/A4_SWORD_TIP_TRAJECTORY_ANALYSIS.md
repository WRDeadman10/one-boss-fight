# P0 Evidence: A4 Low Sweep Sword Tip Trajectory & Scale Analysis (Revision 02)

Date: 2026-10-25  
Author: Antigravity (Accountable Visual Investigator)  
Review Requested from: Claude (Technical Lead) and Codex GPT-6 Astra  
Reference Tasks: CAP-02, VIS-04, RV-07  
Evidence Inputs:
- Live Engine Runtime Probe (Claude E-008): `Docs/BossCombatReview/Execution/Claude/Evidence/exports/a4_geometry_probe_v2_2026-10-25.txt`
- Offline Forward Kinematics Tool: `Docs/BossCombatReview/Execution/Antigravity/Evidence/compute_a4_tip_trajectory.py`
- Offline Trajectory Dataset: `Docs/BossCombatReview/Execution/Antigravity/Evidence/a4_offline_tip_trajectory.json`

---

## 1. Executive Summary & Objective

In message `[C-94]`, technical lead Claude requested:
1. Identification of authored A4 clip frames placing the sword below the floor.
2. Analysis of the scale discrepancy (1.0x authored mannequin vs 1.5x runtime follower sword).
3. Offline extraction of the A4 clip at 1.50x scale to evaluate the sword tip path.

In message `[C-96]`, Claude provided a technical review requiring:
- Consistently applied armature scale and explicit unit conventions (centimeters) with a per-frame unit self-test asserting $244.95\text{ cm}$ blade length.
- Distinct separation of offline forward kinematic calculations from in-engine runtime evidence, dropping claims of direct numerical corroboration.
- Explicitly labeling anatomical causes as unverified hypotheses.
- Reaffirming that Claude's E-008 probe is the sole authoritative in-engine evidence.
- Preserving P0 scope: P4 is not approved, no clips are to be modified, and parity rules govern DD-1.

This revision satisfies all requirements.

---

## 2. In-Engine Runtime Evidence (Claude's E-008 - Authoritative Baseline)

Claude's live probe `a4_geometry_probe_v2_2026-10-25.txt` (PIE session with forced A4 start, 24 ms tick sampling) establishes the authoritative runtime baseline:

1. **Active Window Reach:**
   - Active query window: montage position $0.609\text{ s to }0.879\text{ s}$ (12 sampled ticks).
   - Visible sword tip horizontal distance from actor root ($d_h$): ranges from $74\text{ cm}$ to $312\text{ cm}$ (maximum $312\text{ cm}$ at $t = 0.855\text{ s}$).
   - Production query reach: `RPGBossLowSweep::Reach` is $380\text{ cm}$ (plus player capsule radius $\approx 34\text{--}42\text{ cm}$).
   - Reach discrepancy: The production planar query extends at least **$68\text{ cm}$ beyond the farthest sampled visible blade tip** before adding the player capsule radius.
2. **Angular Arc Discrepancy:**
   - Query sweep: planar mathematical arc from $+84.8^\circ \to -77.5^\circ$ tied to montage position.
   - Visible blade tip yaw: ranges from $+33.7^\circ \to -101.5^\circ$ then jumps to $+167^\circ \dots +5.5^\circ$.
   - The visible blade differs from the query angle by **$51^\circ\text{ to }194^\circ$** across all sampled active ticks; the visible blade does not track the planar query arc.
3. **Runtime Floor Dip:**
   - Floor reference: defined in-engine as `root.z - capsule_half_height` ($Z = 146 - 44 = 102\text{ cm}$ or corresponding capsule boundary).
   - Measured visible tip height ($h = \text{tip.z} - \text{floor}$):
     * Drops below floor reference during $t = 0.730\text{ s to }0.807\text{ s}$ and $t = 0.903\text{ s to }1.025\text{ s}$.
     * Minimum sampled runtime height is $h = -103\text{ cm}$ at $t = 0.754\text{ s}$.

---

## 3. Headless Offline Kinematic Extraction (Raw FBX @ 1.50x Scale)

### 3.1 Tooling & Unit Self-Test Verification
The extraction script `compute_a4_tip_trajectory.py` was executed in headless Blender 5.1.2 on `AN_Boss01_A4_LowSweep.fbx` with:
- **Unit Convention:** Centimeters (`cm`) throughout.
- **Weapon Dimensions:** Unscaled mesh length $163.30\text{ cm}$; runtime scale $1.50\times$; scaled sword reach $244.95\text{ cm}$.
- **Socket Attachment:** `HeavySwordSocket_R` on `hand_r` (offset `(-13.9, 2.6, 4.9)` cm; rotation Pitch -28°, Yaw 168.8°, Roll 12.8° per `RPGBossLook.h:42`).
- **Strict Unit Self-Test Assertions:**
  * For every frame $f \in [1, 54]$, the transformed 3D Euclidean distance from the socket origin to the visible tip was asserted:
    $$\left| \|\mathbf{p}_{\text{tip}} - \mathbf{p}_{\text{socket}}\| - 244.95\text{ cm} \right| < 0.05\text{ cm}$$
  * For every frame $f \in [1, 54]$, the distance from the hand bone origin to the visible tip was asserted:
    $$\left| \|\mathbf{p}_{\text{tip}} - \mathbf{p}_{\text{hand}}\| - 243.11\text{ cm} \right| < 0.05\text{ cm}$$
  * **Result:** **All 54 of 54 frames PASSED both assertions.**

### 3.2 Offline Forward Kinematic Results
In the unscaled armature coordinate space, the character's feet rest at $Z \approx +4.4\text{ to }+5.0\text{ cm}$ above the armature origin ($Z = 0.0\text{ cm}$). When a $244.95\text{ cm}$ rigid blade is transformed through the authored `hand_r` animation, the offline tip height ($Z$) drops below $0.0\text{ cm}$ during the following window:

| 1-Based Frame | 0-Based Frame | Time $t$ (s) | Hand $Z$ (cm) | Socket $Z$ (cm) | Offline Tip $Z$ (cm) | Tip Horiz Dist $d_h$ (cm) | Tip-to-Socket Dist (cm) |
|---|---|---|---|---|---|---|---|
| **23** | 22 | 0.733 | +89.3 | +77.0 | +138.1 | 222.1 | 244.93 |
| **24** | 23 | 0.767 | +90.5 | +83.3 | **-74.9** | 166.0 | 244.94 |
| **25** | 24 | 0.800 | +133.4 | +128.2 | **-84.5** | 169.3 | 244.94 |
| **26** | 25 | 0.833 | +135.9 | +137.7 | **-53.2** | 214.2 | 244.95 |
| **27** | 26 | 0.867 | +104.3 | +112.7 | **-103.2** | 157.5 | 244.95 |
| **28** | 27 | 0.900 | +92.8 | +90.7 | **-143.7** | 37.4 | 244.94 |
| **29** | 28 | 0.933 | +93.1 | +87.5 | **-107.2** | 122.1 | 244.94 |
| **30** | 29 | 0.967 | +93.5 | +86.7 | **-48.2** | 184.2 | 244.94 |
| **31** | 30 | 1.000 | +93.7 | +87.0 | +18.1 | 219.0 | 244.94 |

### 3.3 Relationship Between Offline Kinematics and Live Engine Probe
- The offline forward kinematic extraction confirms that a $244.95\text{ cm}$ blade attached to the authored `hand_r` bone swings deeply below the skeletal origin ($Z \le 0$) across Frames 24 to 30 ($t = 0.767\text{ s to }0.967\text{ s}$), reaching a minimum height of $Z = -143.7\text{ cm}$ at Frame 28.
- **Divergence from Engine Measurements:**
  * In Claude's live probe E-008, the runtime tip dips below floor reference at $t = 0.730\text{--}0.807\text{ s}$ (reaching $-103\text{ cm}$ at $t = 0.754\text{ s}$) and $t = 0.903\text{--}1.025\text{ s}$.
  * The offline calculation and the in-engine probe do **not** match tick-by-tick. Reasons include differing sampling intervals ($24\text{ ms}$ tick in PIE vs $33.3\text{ ms}$ keyframe), montage playback blending, live root capsule positioning, and engine-side socket evaluation order.
  * Therefore, offline kinematic figures must not be described as "corroborating" engine numbers. **Claude's E-008 stands as the sole authoritative runtime evidence.**

---

## 4. Scale Discrepancy & Anatomical Hypotheses

1. **Authored Intent vs Runtime Scaling:**
   - The animation `AN_Boss01_A4_LowSweep.fbx` was keyframed for an unscaled 1.0x mannequin skeleton with an unscaled $163.30\text{ cm}$ greatsword.
   - At runtime, the boss actor follower sword (`RPGLookSword`) is instantiated at $1.50\times$ world scale ($244.95\text{ cm}$ length, adding $+81.65\text{ cm}$ rigid lever arm).
2. **Biomechanical Hypothesis [UNVERIFIED]:**
   - It is hypothesized that when the greatsword length is expanded from $163.3\text{ cm}$ to $244.95\text{ cm}$, any downward tilt of the wrist during the horizontal sweep is mechanically magnified by the $+81.65\text{ cm}$ lever arm, projecting the blade tip significantly further downward than was visualised during 1.0x mannequin authoring.
   - This remains an **unverified hypothesis**; no joint-angle modifications have been measured or approved in-engine.

---

## 5. Architectural Boundaries & Project Scope

- **P0 Baseline Rule:** The findings in this document and in Claude's E-008 document baseline geometric discrepancies (RV-07, VIS-04).
- **Parity Rule for DD-1:** In accordance with the approved architecture gate (decision G-1), DD-1 reproduces today's measured behavior (including the A4 query reach and current visual presentation). No asset or animation edits are permitted in DD-1.
- **Future Work (P4):** Any remediation of the A4 sweep trajectory (whether via animation re-authoring, socket offset adjustments, or query parameter re-tuning) belongs exclusively to Phase P4 and will require its own task brief, technical review, and owner authorization before any work begins.
