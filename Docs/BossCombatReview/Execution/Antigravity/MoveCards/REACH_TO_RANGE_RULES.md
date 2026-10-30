# REACH_TO_RANGE_RULES: Derivation of Move-Card Ranges and Proof Bands from Measured Reach

**Document Version:** 1.1.0  
**Date:** 2026-10-30  
**Context:** Order A-278 (addressing KI-145: card ranges exceeding measured reach).  
**Scope:** Formal rules, mathematical relationships, and classification conventions for deriving `MinRangeCm`, `MaxRangeCm`, `FrontConeDegrees`, and Framework Profile proof bands (`BandMinCm`, `BandMaxCm`) from physical animation reach data extracted via `probe_reach.py`.

---

## 1. Physical Context & Coordinate System

### 1.1 Sevarog Component Space vs. Actor Space
* **Skeletal Mesh Component Space:**
  * **Forward Axis:** $+Y$ [MEASURED, confirmed in `Claude/F3b/run1` and `Claude/F4/final_run1` mesh bounding data: forward extent $+153.56\text{ cm}$].
  * **Lateral Axis:** $X$ [MEASURED: lateral half-width $103.46\text{ cm}$; $+X$ is Right, $-X$ is Left].
  * **Vertical Axis:** $+Z$ [MEASURED: vertical extent $+155.53\text{ cm}$].
* **Actor Space (PIE Runtime):**
  * In `RPGFrameworkBossCharacter`, the skeletal mesh component is mounted with relative rotation `Yaw = -90.0 deg` [MEASURED: `RPGBossFrameworkProfile` authored transform].
  * Rotation transformation: Component $+Y$ maps to Actor Forward $+X$.
* **Range Convention ($S.\text{RangeCm}$):**
  * $S.\text{RangeCm} = \text{Distance2D}(\text{BossActorLocation}, \text{TargetActorLocation})$ [MEASURED: `RPGFrameworkBossCharacter.cpp:77`].
  * It represents the horizontal planar distance between the root centers of the two actors.

---

## 2. Geometric Entities & Dimension Inventory

Every distance and radius contributing to physical weapon contact is classified according to provenance:

| Entity | Parameter | Value | Status / Classification | Provenance |
| :--- | :--- | :--- | :--- | :--- |
| **Boss Capsule Radius** | $R_{\text{boss}}$ | $42.0\text{ cm}$ | `[MEASURED]` | `RPGBossFrameworkProfile` authored fixture, F4 proof run 1 |
| **Boss Capsule Half-Height** | $H_{\text{boss}}$ | $96.0\text{ cm}$ | `[MEASURED]` | `RPGBossFrameworkProfile` authored fixture, F4 proof run 1 |
| **Blade Swept Radius (Swing)** | $R_{\text{blade}}$ | $15.0\text{ cm}$ | `[DESIGN VALUE, PROPOSED]` | Authored card sweep radius in `RPGBossMoveCard` (Swing attacks) |
| **Blade Swept Radius (Heavy)** | $R_{\text{blade,heavy}}$ | $25.0\text{ cm}$ | `[DESIGN VALUE, PROPOSED]` | Authored card sweep radius in `RPGBossMoveCard` (HeavySlam attack) |
| **Target Capsule Radius** | $R_{\text{target}}$ | $42.0\text{ cm}$ | `[MEASURED]` | Pack player capsule radius, measured in F5 engine run (KI-145) |
| **Target Capsule Half-Height** | $H_{\text{target}}$ | $96.0\text{ cm}$ | `[MEASURED]` | Pack player capsule half-height, measured in F5 engine run |
| **Nav Arrival Acceptance** | $R_{\text{accept}}$ | $10.0\text{ cm}$ | `[MEASURED]` | `RPGBossFrameworkProfile` authored acceptance radius, F4 proof run 1 |
| **Safety Margin (Outer)** | $\Delta_{\text{outer}}$ | $5.0\text{ cm}$ | `[DESIGN VALUE, PROPOSED]` | Margin ensuring swept capsule reliably penetrates target surface |
| **Safety Margin (Inner)** | $\Delta_{\text{inner}}$ | $5.0\text{ cm}$ | `[DESIGN VALUE, PROPOSED]` | Margin preventing capsule clipping prior to swing |

---

## 3. Mathematical Contact Model

### 3.1 Planar Contact Boundary
Contact occurs during the attack active window $[t_{\text{start}}, t_{\text{end}}]$ when the swept blade volume intersects the target collision volume.

1. **Forward Reach Envelope ($Y_{\text{reach}}$):**
   At any time $t$, the forward reach of the weapon segment connecting `weapon_r` (base) and `root_weapon_end_r` (tip) in component space is:
   $$Y_{\text{reach}}(t) = \max(Y_{\text{base}}(t), Y_{\text{tip}}(t)) \quad \text{[MEASURED via probe\_reach.py]}$$
   Over the active window:
   $$Y_{\text{peak}} = \max_{t \in [t_{\text{start}}, t_{\text{end}}]} Y_{\text{reach}}(t) \quad \text{[MEASURED]}$$
   $$Y_{\text{min\_base}} = \min_{t \in [t_{\text{start}}, t_{\text{end}}]} Y_{\text{base}}(t) \quad \text{[MEASURED]}$$

2. **Maximum Physical Contact Distance ($D_{\text{contact\_max}}$):**
   The maximum root-to-root distance at which the blade surface touches the target capsule surface when oriented along the attack azimuth is:
   $$D_{\text{contact\_max}} = Y_{\text{peak}} + R_{\text{target}} + R_{\text{blade}}$$
   * For measured $Y_{\text{peak}} = 150.00\text{ cm}$ (`Swing1_Slow`):
     $$D_{\text{contact\_max}} = 151.86\text{ cm [MEASURED]} + 42.00\text{ cm [MEASURED]} + 15.00\text{ cm [PROPOSED]} = 208.86\text{ cm [DERIVED]}$$

3. **Minimum Physical Contact Distance ($D_{\text{contact\_min}}$):**
   Constrained by physical actor non-penetration:
   $$D_{\text{contact\_min}} \ge R_{\text{boss}} + R_{\text{target}} = 42.00\text{ cm [MEASURED]} + 42.00\text{ cm [MEASURED]} = 84.00\text{ cm [DERIVED]}$$

---

## 4. Derivation Rules for Move-Card Parameters

### 4.1 Card `MaxRangeCm`
* **C++ Authority:** `RPGBossMoveModel.cpp:31` (`if (S.RangeCm > Card->Spec().MaxRangeCm) return Refuse("MoveModel.Range")`).
* **Rule:** An in-place attack card MUST NOT be selected if the target is outside physical contact distance.
* **Derivation Formula:**
  $$\text{MaxRangeCm} = Y_{\text{peak}} + R_{\text{target}} + R_{\text{blade}} - \Delta_{\text{outer}}$$
* **Application to `Swing1_Slow`:**
  $$\text{MaxRangeCm} = 151.86\text{ cm [MEASURED]} + 42.00\text{ cm [MEASURED]} + 15.00\text{ cm [DESIGN VALUE, PROPOSED]} - 5.00\text{ cm [DESIGN VALUE, PROPOSED]} = 203.86\text{ cm} \rightarrow 200.00\text{ cm [DESIGN VALUE, PROPOSED]}$$
* **Diagnostic Note on KI-145:**
  * Old proposed `MaxRangeCm = 400.00 cm` was invalid because $400.00\text{ cm} \gg 205.00\text{ cm}$, causing the boss to swing into empty air without contact.
  * Corrected range ceiling for pure in-place `Swing1_Slow` is $\le 200.00\text{ cm}$ (or $250.00\text{ cm}$ only if paired with authored root motion or lunge displacement).

### 4.2 Card `MinRangeCm`
* **C++ Authority:** `RPGBossMoveModel.cpp:31` (`if (S.RangeCm < Card->Spec().MinRangeCm) return Refuse("MoveModel.Range")`).
* **Rule:** An attack card MUST NOT be selected if the target is jammed within the boss capsule or behind the weapon hilt.
* **Derivation Formula:**
  $$\text{MinRangeCm} = \max(R_{\text{boss}} + R_{\text{target}} + \Delta_{\text{inner}},\, Y_{\text{min\_base}} + R_{\text{blade}})$$
* **Application:**
  $$\text{MinRangeCm} = \max(42.00 + 42.00 + 5.00,\, Y_{\text{min\_base}} + 15.00) = \max(89.00\text{ cm},\, Y_{\text{min\_base}} + 15.00\text{ cm})$$
* **Proposed Value for `Swing1_Slow`:** $100.00\text{ cm [DESIGN VALUE, PROPOSED]}$.

### 4.3 Card `FrontConeDegrees`
* **C++ Authority:** `RPGBossMoveModel.cpp:34` (`if (FMath::Abs(S.SignedYawDegrees) > 0.5 * Card->Spec().FrontConeDegrees) return Refuse("MoveModel.Cone")`).
* **Rule:** `FrontConeDegrees` represents the total symmetrical cone angle ($2 \times \theta_{\text{half}}$) within which the target is eligible.
* **Derivation Formula:**
  Let $W_{\text{half}} = \max(|X_{\min}|, |X_{\max}|)$ be the maximum lateral extent of the swept blade during the active window `[MEASURED]`.
  The half-cone subtended by the blade arc at peak reach is:
  $$\theta_{\text{blade}} = \arctan\left(\frac{W_{\text{half}}}{Y_{\text{peak}}}\right)$$
  Accounting for target collision cross-section at distance $D$:
  $$\theta_{\text{target}} = \arcsin\left(\frac{R_{\text{target}}}{D}\right)$$
  $$\text{FrontConeDegrees} \le 2 \times (\theta_{\text{blade}} + \theta_{\text{target}})$$
* **Proposed Values:**
  * Wide horizontal cleave (`Swing1_Slow`, `Swing1_Medium`): $90.00^\circ\text{ to } 120.00^\circ$ `[DESIGN VALUE, PROPOSED]`.
  * Overhead vertical smash (`Swing3_Slow`): $45.00^\circ\text{ to } 60.00^\circ$ `[DESIGN VALUE, PROPOSED]`.

---

## 5. Derivation Rules for Framework Profile Proof Bands

### 5.1 Profile Proof Band (`BandMinCm`, `BandMaxCm`)
* **C++ Authority:**
  * `RPGBossFrameworkProfile.cpp:24`:
    $$\text{BandMinCm} < \text{BandMaxCm}$$
    $$\text{AcceptanceCm} < 0.5 \times (\text{BandMaxCm} - \text{BandMinCm})$$
  * `RPGBossFrameworkProfile.cpp:55`:
    $$\text{MinRangeCm} \le \text{BandMinCm} \quad \text{and} \quad \text{BandMaxCm} \le \text{MaxRangeCm}$$
* **Navigation Placement Goal:**
  * The boss navigation controller walks toward the target until reaching distance $D_{\text{goal}} = 0.5 \times (\text{BandMinCm} + \text{BandMaxCm})$ with acceptance $R_{\text{accept}} = 10.0\text{ cm}$ [MEASURED].
  * Upon stopping, actual distance $S.\text{RangeCm}$ lies within $[\text{BandMinCm}, \text{BandMaxCm}]$.
* **Derivation Formulas:**
  1. **Optimal Sweet Spot Center ($D_{\text{sweet}}$):**
     Place the target center directly in the high-density sweep zone:
     $$D_{\text{sweet}} = Y_{\text{peak}} + R_{\text{blade}} = 150.00\text{ cm [MEASURED]} + 15.00\text{ cm [DESIGN VALUE, PROPOSED]} = 165.00\text{ cm [DERIVED]}$$
  2. **Band Half-Width ($\Delta_{\text{band}}$):**
     Must satisfy $\Delta_{\text{band}} > R_{\text{accept}} = 10.00\text{ cm}$ [MEASURED].
     Set $\Delta_{\text{band}} = 15.00\text{ cm}$ [DESIGN VALUE, PROPOSED].
  3. **Band Extents:**
     $$\text{BandMinCm} = D_{\text{sweet}} - \Delta_{\text{band}} = 165.00 - 15.00 = 150.00\text{ cm [DESIGN VALUE, PROPOSED]}$$
     $$\text{BandMaxCm} = D_{\text{sweet}} + \Delta_{\text{band}} = 165.00 + 15.00 = 180.00\text{ cm [DESIGN VALUE, PROPOSED]}$$
* **Validation against F4 Proof:**
  * F4 proof run 1 authored: $\text{BandMinCm} = 150.00\text{ cm}$, $\text{BandMaxCm} = 180.00\text{ cm}$ [MEASURED].
  * Actual measured arrival distance: $S.\text{RangeCm} = 169.69\text{ cm}$ [MEASURED: `final_f4_run1:1506`].
  * Residual error from sweet spot: $|169.69 - 165.00| = 4.69\text{ cm} < R_{\text{accept}} = 10.00\text{ cm}$.
  * Proof band is strictly nested within card range $[100.00, 250.00]\text{ cm}$ [MEASURED].

---

## 6. Target Candidate Animation Table

Kinematic parameters below are extracted from `reach_summary.json` (`Claude/F5/reach_run1`) and evaluated with measured player target capsule $R_{\text{target}} = 42.0\text{ cm}$:

| Animation Sequence | Clip Len (s) | Active Window (s) | Peak Fwd $Y$ (cm) | Lat Half-W (cm) | Derived Card $[\text{Min}, \text{Max}]$ (cm) | Derived Cone ($^\circ$) | Derived Band $[\text{Min}, \text{Max}]$ (cm) | Status / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`Swing1_Slow`** | $1.7000$ `[M]` | $[0.3500, 0.4917]$ `[M]` | $151.86$ `[M]` | $73.95$ `[M]` | $[90.0, 200.0]$ `[P]` | $90.0^\circ$ `[P]` | $[150.0, 180.0]$ `[M]` | F4 Proof Baseline (contact max $208.9\text{ cm}$) |
| **`Swing1_Medium`** | $1.1333$ `[M]` | $[0.1500, 0.2667]$ `[M]` | $133.92$ `[M]` | $67.03$ `[M]` | $[90.0, 185.0]$ `[P]` | $90.0^\circ$ `[P]` | $[130.0, 160.0]$ `[P]` | Contact max $190.9\text{ cm}$ |
| **`Swing2_Medium`** | $1.1333$ `[M]` | $[0.1917, 0.2667]$ `[M]` | $103.20$ `[M]` | $165.54$ `[M]` | $[90.0, 150.0]$ `[P]` | $90.0^\circ$ `[P]` | $[110.0, 140.0]$ `[M]` | Contact max $160.2\text{ cm}$; verified in Near F6c |
| **`Swing3_Slow`** | $1.7000$ `[M]` | $[0.4750, 0.5333]$ `[M]` | $130.30$ `[M]` | $99.49$ `[M]` | $[90.0, 105.0]$ `[P]` | $45.0^\circ$ `[P]` | $[90.0, 105.0]$ `[P]` | Centered contact max $108.0\text{ cm}$; misses at $129\text{ cm}$ |
| **`Swing1_FAST_v2`**| $0.5333$ `[M]` | $[0.1500, 0.3000]$ `[M]` | $138.52$ `[M]` | $88.55$ `[M]` | $[90.0, 190.0]$ `[P]` | $90.0^\circ$ `[P]` | $[135.0, 165.0]$ `[P]` | Contact max $195.5\text{ cm}$ |
| **`Speedburst`** | $1.2667$ `[M]` | $[0.3000, 0.6000]$ `[M]` | $77.41$ `[M]` | $67.64$ `[M]` | $[90.0, 130.0]$ `[P]` | $90.0^\circ$ `[P]` | $[90.0, 120.0]$ `[P]` | In-place window; dash requires root motion |

*Legend: `[M]` = Measured from engine logs/reach_summary.json; `[P]` = Proposed design value derived mathematically.*

---

## 7. Timeline Segment Clearance & Blend-Out Tail Margin Rule

* **C++ Authority:** `RPGBossFrameworkProfile.cpp:63` (`if (S.RecoveryEndSeconds + P->BlendOutSeconds > OutCard->Metadata().ClipLengthSeconds) return Fail(TEXT("Framework.Profile.CardBandOrBlendTail"))`).
* **Problem Observed in F5b Execution:**
  `author_move_cards.py` validates move cards in isolation without access to runtime Profile parameters (`BlendOutSeconds`). When `SwingMedium_F5` was authored with $\text{RecoveryEnd} = 1.10\text{ s}$ against a clip of $L = 1.1333\text{ s}$, a profile blend-out of $0.04\text{ s}$ resulted in $1.10 + 0.04 = 1.14 > 1.1333$, triggering `Framework.Profile.CardBandOrBlendTail` rejection.
* **Universal Clearance Rule:**
  To guarantee that any authored move card survives standard profile montage blend-out transitions without failure, authored cards MUST enforce:
  $$\text{RecoveryEndSeconds} \le \text{ClipLengthSeconds} - 0.05\text{ s} \quad \text{[DESIGN VALUE, PROPOSED]}$$
  Equivalently, the minimum montage blend-out tail clearance margin is $\Delta_{\text{blend\_tail}} \ge 0.05\text{ s}$. Any candidate card violating this bound must have its $\text{RecoveryEndSeconds}$ pulled back or profile $\text{BlendOutSeconds}$ reduced.


---

## 8. Specific Card Reach Analyses & Range Calibrations

### 8.1 `SwingMedium_F7_P2` (`Swing2_Medium`)
* **Kinematics Source:** `reach_summary.json` (`Claude/F5/reach_run1`).
* **Active Window:** $[0.1917, 0.2667]\text{ s}$.
* **Peak Forward in Window ($Y_{\text{peak}}$):** $103.20\text{ cm}$ (at $t=0.2250\text{ s}$, Base $Y=103.20\text{ cm}$, Tip $Y=68.02\text{ cm}$).
* **Contact Derivation:**
  $$D_{\text{contact\_max}} = Y_{\text{peak}} (103.20) + R_{\text{target}} (42.00) + R_{\text{blade}} (15.00) = 160.20\text{ cm}$$
  $$\text{MaxRangeCm} = D_{\text{contact\_max}} - \Delta_{\text{outer}} (5.00) = 155.20\text{ cm} \rightarrow \mathbf{150.00\text{ cm [PROPOSED]}}$$
  $$\text{MinRangeCm} = \max(R_{\text{boss}} + R_{\text{target}} + \Delta_{\text{inner}},\, Y_{\text{min\_base}} + R_{\text{blade}}) = \max(89.00,\, -41.29 + 15.00) = \mathbf{90.00\text{ cm [PROPOSED]}}$$
* **Diagnostic & Resolution of KI-145:**
  * In F6c baseline runs, `BandMaxCm = 180.0 cm`, boss arrived at $S.\text{RangeCm} \approx 167\text{ cm}$. Authored `MaxRangeCm = 180.0 cm` permitted selection, but $167\text{ cm} > 160.20\text{ cm}$ caused 3/3 clean misses.
  * In `DA_Sevarog_PhaseProofNear_F6c` (band $[110, 140]\text{ cm}$, arrival $\approx 129\text{ cm}$), $129\text{ cm} < 160.20\text{ cm}$; PIE execution confirmed 3/3 ACCEPTED hits with 35 damage.

### 8.2 `HeavySlam_F7` / `HeavySlam_F5` (`Swing3_Slow`)
* **Kinematics Source:** `reach_summary.json` (`Claude/F5/reach_run1`) and `move_cards_f7_baked.json`.
* **Active Window:** $[0.4750, 0.5333]\text{ s}$, $R_{\text{blade}} = 25.0\text{ cm}$.
* **Kinematic Envelope:**
  * Peak base forward: $Y_{\text{base}} = 130.30\text{ cm}$ at $t=0.5167\text{ s}$.
  * Peak tip forward: $Y_{\text{tip}} = 99.25\text{ cm}$ at $t=0.5083\text{ s}$.
  * Lateral asymmetry: The scythe descends exclusively on Sevarog's left flank: $X_{\text{base}} \in [-99.5, -78.7]\text{ cm}$, $X_{\text{tip}} \in [-74.3, -55.6]\text{ cm}$.
* **Physical Contact Geometry against Centered Target ($X=0$):**
  * Target cylinder: centered at $X=0$, radius $R_{\text{target}} = 42.0\text{ cm}$.
  * Because the blade segment is laterally offset ($X \le -55.6\text{ cm}$), the combined cross-section radius is $R_{\text{target}} + R_{\text{blade}} = 42.0 + 25.0 = 67.0\text{ cm}$.
  * Mathematical sweep simulation across target distance $Y \in [50, 200]\text{ cm}$ proves contact occurs **only** for $Y \le 108.0\text{ cm}$.
  * At distance $Y = 129.044\text{ cm}$ (`near_pie_run1`), closest surface distance is $+8.20\text{ cm}$ (miss by $8.2\text{ cm}$).
  * Therefore, **$129\text{ cm}$ is strictly outside the physical reach of the in-place HeavySlam attack**.
* **Proposed Calibration:**
  $$\text{MaxRangeCm} = 108.00 - \Delta_{\text{outer}} (5.00) = 103.00\text{ cm} \rightarrow \mathbf{100.00\text{ cm [PROPOSED]}} \quad (\text{or } 105.00\text{ cm max})$$
  $$\text{MinRangeCm} = \mathbf{90.00\text{ cm [PROPOSED]}}$$
  *(Note: For HeavySlam to engage targets at $130-180\text{ cm}$, root motion or forward step displacement must be enabled in a subsequent movement block).*
