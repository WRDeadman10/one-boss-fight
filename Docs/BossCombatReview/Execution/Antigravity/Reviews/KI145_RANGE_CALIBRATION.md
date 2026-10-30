# KI-145: Move Card Range Calibration and Geometric Reach Review

**Document Version:** 1.0.0  
**Date:** 2026-10-31  
**Author:** Antigravity (Relayed to Claude & Owner)  
**Lead Order Reference:** `Documentation/TEAM_MAILBOX.md` `[C-461]`  
**Target Issue:** KI-145 (Card ranges exceeding measured reach and lateral offset clipping)  
**Applicable Authority:** `Docs/BossCombatReview/Execution/Antigravity/MoveCards/REACH_TO_RANGE_RULES.md`

---

## 1. Executive Summary

This review executes the comprehensive offline calibration of weapon strike ranges across all 10 existing move cards in the framework combat system (`move_cards_f5_set.json`, `move_cards_f7_baked.json`, and `move_cards_f7_phase2_set.json`). 

Using empirical weapon reach data from `Claude/F5/reach_run1/reach_summary.json`, exact baked trajectory samples (`BakedSamples`), measured pack player capsule radius ($R_{\text{target}} = 42.0\text{ cm}$), and framework boss capsule radius ($R_{\text{boss}} = 60.0\text{ cm}$), we evaluated 2D segment-to-point contact geometry against a centered player capsule $(X=0, Y=D)$.

### Key Findings:
1. **Critical HeavySlam Dead Zone ($[108.6, 180.0]\text{ cm}$):**  
   `Move_Sevarog_HeavySlam` (`Swing3_Slow`, $R_{\text{blade}} = 25.0\text{ cm}$) has an authored range of $[90.0, 180.0]\text{ cm}$. Due to severe lateral displacement ($X \in [-99.49, -59.20]\text{ cm}$), the blade smashes empty air to the left of a centered target at any distance $D > 108.5\text{ cm}$. Over $71\text{ cm}$ ($>79\%$) of its authored range is a complete dead zone where it will ALWAYS MISS. Against a centered target, the non-penetrating physical hit window is only $[102.0, 108.5]\text{ cm}$ (a tiny $6.5\text{ cm}$ sliver).
2. **SwingMedium Dead Zone ($[149.1, 180.0]\text{ cm}$):**  
   `Move_Sevarog_SwingMedium` (`Swing2_Medium`, $R_{\text{blade}} = 15.0\text{ cm}$) has an authored range of $[90.0, 180.0]\text{ cm}$. The geometric contact ceiling is $149.0\text{ cm}$. At $D = 160.0\text{ cm}$ and $D = 167.0\text{ cm}$, the attack misses cleanly (closest approach $67.28\text{ cm}$ and $74.05\text{ cm}$, exceeding threshold $57.0\text{ cm}$).
3. **Sub-Physical Floor Violation ($D < 102.0\text{ cm}$):**  
   All 10 cards author minimum ranges of $90.0\text{ cm}$ or $100.0\text{ cm}$. However, the rigid capsule non-penetration floor between boss ($R_{\text{boss}} = 60.0\text{ cm}$) and player ($R_{\text{target}} = 42.0\text{ cm}$) is $102.0\text{ cm}$. Authors allowing selection at $90.0\text{ cm}$ permit the AI to fire attacks while character collision volumes are interpenetrating.
4. **Viable In-Place Slices:**  
   `Swing1_Slow` (authored $[100, 200]\text{ cm}$, geometric reach $207.5\text{ cm}$) and `Swing1_FAST_v2` / `AntiGreed` (authored $[90, 185]\text{ cm}$, geometric reach $190.5\text{ cm}$) have valid upper bounds that physically connect when clamped to the physical floor ($D \ge 102.0\text{ cm}$).

---

## 2. Geometric & Physical Contact Model

### 2.1 Coordinate Conventions & Setup
* **Component Space:** $+Y$ is forward, $X$ is lateral ($+X$ Right, $-X$ Left), $+Z$ is vertical.
* **Centered Player Capsule:** Centered along boss attack heading at location $(0, D)$ in horizontal plane.
* **Target Radius:** $R_{\text{target}} = 42.0\text{ cm}$ [MEASURED, pack player capsule].
* **Boss Radius:** $R_{\text{boss}} = 60.0\text{ cm}$ [MEASURED, `RPGBossFrameworkProfile` fixture].
* **Physical Non-Penetration Distance:**
  $$D_{\text{phys\_min}} = R_{\text{boss}} + R_{\text{target}} = 60.0 + 42.0 = 102.0\text{ cm}$$

### 2.2 Swept Blade Segment to Target Distance
At each key pose (and dense sub-step between consecutive samples), the blade forms a 3D line segment between base $\mathbf{A} = (X_a, Y_a, Z_a)$ and tip $\mathbf{B} = (X_b, Y_b, Z_b)$ with swept sphere radius $R_{\text{blade}}$.

In the horizontal plane, contact with a vertical cylinder centered at $(0, D)$ of radius $R_{\text{target}}$ occurs if and only if the minimum 2D distance from $(0, D)$ to the segment $\overline{\mathbf{A}\mathbf{B}}$ satisfies:
$$\text{dist}_{2\text{D}}((0, D), \text{Segment}((X_a, Y_a), (X_b, Y_b))) \le R_{\text{target}} + R_{\text{blade}} = \text{Threshold}$$

Where:
* For Swing moves (`Swing1_Slow`, `Swing2_Medium`, `Swing1_FAST_v2`): $R_{\text{blade}} = 15.0\text{ cm} \implies \text{Threshold} = 42.0 + 15.0 = 57.0\text{ cm}$.
* For Heavy moves (`Swing3_Slow`): $R_{\text{blade}} = 25.0\text{ cm} \implies \text{Threshold} = 42.0 + 25.0 = 67.0\text{ cm}$.

---

## 3. Ten-Card Calibration Census & Evaluation Table

Recomputed deterministically via `Docs/BossCombatReview/Execution/Antigravity/Reviews/compute_ki145_ranges.py`:

| MoveId | Set | Sequence | Blade R | Authored [Min, Max] | Swept Geom [Min, Max] | Physical Hit [Min, Max] | Proposed Calibrated | Identified Dead Zones |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Move_Sevarog_SwingSlow_F5** | F5 | `Swing1_Slow` | 15 cm | [100, 200] cm | [29.0, 207.5] cm | [102.0, 207.5] cm | **[105, 200] cm** | Sub-physical [100, 102] cm |
| **Move_Sevarog_SwingMedium_F5** | F5 | `Swing2_Medium` | 15 cm | [90, 180] cm | [10.0, 149.0] cm | [102.0, 149.0] cm | **[105, 140] cm** | **Upper [149.1, 180.0] cm**; Sub-phys [90, 102] cm |
| **Move_Sevarog_AntiGreed_F5** | F5 | `Swing1_FAST_v2` | 15 cm | [90, 185] cm | [10.0, 190.5] cm | [102.0, 190.5] cm | **[105, 185] cm** | Sub-physical [90, 102] cm |
| **Move_Sevarog_HeavySlam_F5** | F5 | `Swing3_Slow` | 25 cm | [90, 180] cm | [24.0, 108.5] cm | [102.0, 108.5] cm | **[102, 108] cm\*** | **Upper [108.6, 180.0] cm**; Sub-phys [90, 102] cm |
| **Move_Sevarog_SwingSlow_F7** | F7 | `Swing1_Slow` | 15 cm | [100, 200] cm | [29.0, 207.5] cm | [102.0, 207.5] cm | **[105, 200] cm** | Sub-physical [100, 102] cm |
| **Move_Sevarog_SwingMedium_F7** | F7 | `Swing2_Medium` | 15 cm | [90, 180] cm | [10.0, 149.0] cm | [102.0, 149.0] cm | **[105, 140] cm** | **Upper [149.1, 180.0] cm**; Sub-phys [90, 102] cm |
| **Move_Sevarog_AntiGreed_F7** | F7 | `Swing1_FAST_v2` | 15 cm | [90, 185] cm | [10.0, 190.5] cm | [102.0, 190.5] cm | **[105, 185] cm** | Sub-physical [90, 102] cm |
| **Move_Sevarog_HeavySlam_F7** | F7 | `Swing3_Slow` | 25 cm | [90, 180] cm | [24.0, 108.5] cm | [102.0, 108.5] cm | **[102, 108] cm\*** | **Upper [108.6, 180.0] cm**; Sub-phys [90, 102] cm |
| **Move_Sevarog_SwingMedium_F7_P2** | Phase2 | `Swing2_Medium` | 15 cm | [90, 180] cm | [10.0, 149.0] cm | [102.0, 149.0] cm | **[105, 140] cm** | **Upper [149.1, 180.0] cm**; Sub-phys [90, 102] cm |
| **Move_Sevarog_AntiGreed_F7_P2** | Phase2 | `Swing1_FAST_v2` | 15 cm | [90, 185] cm | [10.0, 190.5] cm | [102.0, 190.5] cm | **[105, 185] cm** | Sub-physical [90, 102] cm |

*\*Note on HeavySlam:* Against a centered player ($X=0$), the physical hit interval is only $6.5\text{ cm}$ wide. See Section 4.1 for architectural solutions.

---

## 4. In-Depth Dead Zone Proofs

### 4.1 Case Study 1: HeavySlam Lateral Clipping (`Swing3_Slow`)
* **Geometry:** The active strike window of `Swing3_Slow` ($t \in [0.475, 0.5333]\text{ s}$) brings the scythe down heavily on the boss's left side.
* **Empirical Coordinates from `reach_summary.json` & `BakedSamples`:**
  * Sample at peak forward reach ($t = 0.5167\text{ s}$):
    * $\text{BaseCS}: (-88.91, 130.30, 128.26)\text{ cm}$
    * $\text{TipCS}: (-64.36, 90.14, 103.42)\text{ cm}$
  * Across the entire window, the minimum lateral offset of any blade vertex is $|X| = 59.20\text{ cm}$.
* **The Centered Player Conflict:**
  * Target capsule is centered at $(0, D)$ with radius $42.0\text{ cm}$.
  * The right edge of the blade volume reaches $X = -64.36 + 25.0 = -39.36\text{ cm}$.
  * The left edge of the player capsule reaches $X = -42.0\text{ cm}$.
  * Lateral overlap is at most:
    $$42.0\text{ cm} - 39.36\text{ cm} = 2.64\text{ cm}$$
  * This tiny overlap only intersects when the forward distance $D$ places the player directly next to the tip ($Y \approx 90\text{ cm}$).
  * At $D = 130.0\text{ cm}$, the distance from $(0, 130)$ to the segment is $75.70\text{ cm}$, which strictly exceeds $\text{Threshold} = 67.0\text{ cm}$.
  * **Proof:** At $D \in [108.6, 180.0]\text{ cm}$, `HeavySlam` can NEVER hit a player standing directly in front of the boss.

### 4.2 Case Study 2: SwingMedium Reach Ceiling (`Swing2_Medium`)
* **Geometry:** `Swing2_Medium` active window ($t \in [0.1917, 0.2667]\text{ s}$) has peak forward reach $Y = 103.20\text{ cm}$ at $X = -49.77\text{ cm}$.
* **Geometric Maximum:**
  * The farthest point along the center line ($X=0$) reachable within the $57.0\text{ cm}$ threshold is $D = 149.0\text{ cm}$.
  * At $D = 160.0\text{ cm}$, minimum distance is $67.28\text{ cm}$ (Margin $-10.28\text{ cm} \implies \text{MISS}$).
  * At $D = 167.0\text{ cm}$, minimum distance is $74.05\text{ cm}$ (Margin $-17.05\text{ cm} \implies \text{MISS}$).
  * **Proof:** Authored range $[90.0, 180.0]\text{ cm}$ contains a $30.9\text{ cm}$ dead zone ($[149.1, 180.0]\text{ cm}$) on a centered target.

### 4.3 Sub-Physical Floor Analysis
* In both F5 and F7 cards, `MinRangeCm` was set to $90.0\text{ cm}$ (or $100.0\text{ cm}$ for `SwingSlow`).
* In engine physics, two rigid cylinders cannot be closer than $R_{\text{boss}} + R_{\text{target}} = 60.0 + 42.0 = 102.0\text{ cm}$ without capsule overlapping.
* Setting `MinRangeCm < 102.0 cm` does not cause a whiff, but it causes the move selector to consider the card when the boss is pushing or colliding with the player.
* Recommended physical floor: `MinRangeCm = 105.0 cm` (providing a $3.0\text{ cm}$ clearance margin above $102.0\text{ cm}$).

---

## 5. PIE Verification Prediction Matrix (Lead Claude Check)

For verification by Lead Claude in PIE across the 3 canonical F7 cards at $D \in \{100.0, 130.0, 160.0\}\text{ cm}$ (plus the $167.0\text{ cm}$ boundary probe):

```
+-----------------------------+-----------------+-----------+-----------+-----------+-----------+
| Move Card                   | Sequence / R_b  | D = 100cm | D = 130cm | D = 160cm | D = 167cm |
+-----------------------------+-----------------+-----------+-----------+-----------+-----------+
| Move_Sevarog_SwingSlow_F7   | Swing1_Slow     |   HIT     |   HIT     |   HIT     |   HIT     |
|                             | R_blade = 15cm  | (0.09 cm) | (2.22 cm) | (11.07cm) | (17.27cm) |
+-----------------------------+-----------------+-----------+-----------+-----------+-----------+
| Move_Sevarog_SwingMedium_F7 | Swing2_Medium   |   HIT     |   HIT     |   MISS    |   MISS    |
|                             | R_blade = 15cm  | (11.90cm) | (38.18cm) | (67.28cm) | (74.05cm) |
+-----------------------------+-----------------+-----------+-----------+-----------+-----------+
| Move_Sevarog_HeavySlam_F7   | Swing3_Slow     |   HIT     |   MISS    |   MISS    |   MISS    |
|                             | R_blade = 25cm  | (64.15cm) | (75.70cm) | (91.35cm) | (95.00cm) |
+-----------------------------+-----------------+-----------+-----------+-----------+-----------+
```
*(Values in parentheses indicate minimum 2D distance to segment center-line; threshold is 57.0 cm for Swing, 67.0 cm for Heavy).*

---

## 6. Architectural Recommendations

1. **Card Range Updates:**
   * Update `Move_Sevarog_SwingSlow` cards: `MinRangeCm = 105.0`, `MaxRangeCm = 200.0`.
   * Update `Move_Sevarog_SwingMedium` cards: `MinRangeCm = 105.0`, `MaxRangeCm = 140.0`.
   * Update `Move_Sevarog_AntiGreed` cards: `MinRangeCm = 105.0`, `MaxRangeCm = 185.0`.
2. **HeavySlam Architectural Options:**
   * **Option 1 (Profile Band Restriction):** If retained as in-place centered attack, set `MinRangeCm = 102.0`, `MaxRangeCm = 108.0`, but this window is fragile.
   * **Option 2 (Yaw Offset / Aim Adjustment):** During HeavySlam commit, rotate the boss facing by $\approx -35^\circ$ (so the boss aims the left-side slam directly at the player). This expands effective range to $[105.0, 160.0]\text{ cm}$.
   * **Option 3 (Shockwave Radial Damage):** Augment HeavySlam with a ground impact radial sphere ($R \approx 80.0\text{ cm}$) at the point of impact on the ground plane, turning it into a true AoE slam.
3. **Framework Profile Bands (`DA_Sevarog_FrameworkProfile`):**
   * Default proof profile band $[120.0, 160.0]\text{ cm}$ is compatible with `SwingSlow` and `AntiGreed`, but exceeds `SwingMedium` ($>140.0\text{ cm}$) and `HeavySlam` ($>108.0\text{ cm}$).
   * Calibrated profile proof band: $[110.0, 135.0]\text{ cm}$ allows all non-Heavy cards to hit reliably within the sweet spot.

---

## 7. Unverified Items & Boundary Conditions

Per Lead Order `[C-461]`, the following items cannot be fully verified offline and require engine/PIE confirmation:
1. **Dynamic Root Motion:** All cards declare `bUsesRootMotion: false`. If montage translation is injected at runtime, forward reach will increase.
2. **Dynamic Target Velocity:** Calculations assume a stationary player centered at $(0, D)$. Lateral player strafing, dodging, or sprinting during active frames changes the contact outcome.
3. **Live Socket Blending:** The analysis evaluates the exact baked poses (`BakedSamples`). If live procedural bone blending or physics animation is enabled without baking, socket positions may differ slightly.
4. **Non-Flat Terrain:** Calculations assume a flat planar arena floor ($Z=0$). Vertical elevation changes in `L_SevarogArena` would affect 3D capsule-segment distance.
5. **Boss Tracking Yaw Clamping:** During the commit window, the boss tracks player yaw. If the player is positioned at an angle within `FrontConeDegrees`, the lateral offset to HeavySlam varies.
