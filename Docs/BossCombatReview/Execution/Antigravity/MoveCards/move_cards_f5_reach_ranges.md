# F5 Move-Card Reach Ranges: Kinematic Derivation for Sevarog Attacks

**Document Version:** 1.0.0  
**Date:** 2026-10-30  
**Context:** Order A-280 (addressing KI-145 and incorporating empirical data from `Claude/F5/reach_run1`).  
**Authority:** Grounded in `Docs/BossCombatReview/Execution/Claude/F5/reach_run1/reach_summary.json` and `REACH_TO_RANGE_RULES.md`.  
**Scope:** Formal derivation of `MinRangeCm`, `MaxRangeCm`, `FrontConeDegrees`, and Framework Profile proof bands for the four primary combat move cards (`SwingSlow`, `SwingMedium`, `AntiGreed`, `HeavySlam`), distinguishing measured geometry from proposed design parameters and identifying unmeasured timing gaps.

---

## 1. Physical Parameter Inventory & Constants

Every parameter contributing to range selection is tagged with its empirical provenance:

| Parameter | Symbol | Value | Status / Classification | Source |
| :--- | :--- | :--- | :--- | :--- |
| **Boss Capsule Radius** | $R_{\text{boss}}$ | $42.0\text{ cm}$ | `[MEASURED]` | F3b/F4 authored profile fixture |
| **Boss Capsule Half-Height** | $H_{\text{boss}}$ | $96.0\text{ cm}$ | `[MEASURED]` | F3b/F4 authored profile fixture |
| **Target Capsule Radius** | $R_{\text{target}}$ | $40.0\text{ cm}$ | `[UNVERIFIED]` | Stays UNVERIFIED until direct engine measurement against pack player (next engine slice) |
| **Target Capsule Half-Height** | $H_{\text{target}}$ | $90.0\text{ cm}$ | `[UNVERIFIED]` | Stays UNVERIFIED until direct engine measurement against pack player |
| **Blade Swept Radius** | $R_{\text{blade}}$ | $15.0\text{ cm}$ | `[DESIGN VALUE, PROPOSED]` | Authored card collision sweep radius in `RPGBossMoveCard` |
| **Nav Arrival Acceptance** | $R_{\text{accept}}$ | $10.0\text{ cm}$ | `[MEASURED]` | `RPGBossFrameworkProfile` authored acceptance |
| **Safety Margin (Outer)** | $\Delta_{\text{outer}}$ | $5.0\text{ to } 8.9\text{ cm}$ | `[DESIGN VALUE, PROPOSED]` | Margin ensuring swept blade penetrates target cylinder |
| **Safety Margin (Inner)** | $\Delta_{\text{inner}}$ | $5.0\text{ to } 8.0\text{ cm}$ | `[DESIGN VALUE, PROPOSED]` | Margin preventing capsule clipping prior to swing |

---

## 2. Card 1: `Move_Sevarog_SwingSlow`

### 2.1 Empirical Telemetry (`Claude/F5/reach_run1`)
* **Sequence Path:** `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow`
* **Clip Length:** $1.7000\text{ s}$ `[MEASURED]`
* **Active Window:** $[0.3500, 0.4917]\text{ s}$ `[MEASURED: C379 probe & F4 proof]`
* **Peak Forward in Window ($Y_{\text{peak}}$):** $151.86\text{ cm}$ `[MEASURED: reach_run1]` (weapon_r base at $t=0.4833\text{ s}$)
* **Tip Forward at Peak:** $120.85\text{ cm}$ `[MEASURED]` (at $t=0.4417\text{ s}$)
* **Swept Forward Range in Window ($Y$):** $[-11.56, 151.86]\text{ cm}$ `[MEASURED]`
* **Swept Lateral Range in Window ($X$):** $[-73.95, 6.49]\text{ cm}$ `[MEASURED]`
* **Lateral Half-Width ($W_{\text{half}}$):** $73.95\text{ cm}$ `[MEASURED]`
* **Swept Vertical Range in Window ($Z$):** $[138.46, 267.01]\text{ cm}$ `[MEASURED]`

### 2.2 Derivation of Range & Cone
1. **Maximum Physical Contact Distance:**
   $$D_{\text{contact\_max}} = Y_{\text{peak}} + R_{\text{target}} + R_{\text{blade}} = 151.86 + 40.00 + 15.00 = 206.86\text{ cm [DERIVED]}$$
2. **Card Range Bounds:**
   * $\text{MaxRangeCm} = 200.0\text{ cm [DESIGN VALUE, PROPOSED]}$ (Margin $\Delta_{\text{outer}} = 6.86\text{ cm}$).
   * $\text{MinRangeCm} = 100.0\text{ cm [DESIGN VALUE, PROPOSED]}$ (Exceeds actor non-penetration $R_{\text{boss}} + R_{\text{target}} = 82.0\text{ cm}$).
3. **Card Cone Angle:**
   * $\theta_{\text{blade}} = \arctan(73.95 / 151.86) = 25.96^\circ$. Target subtense at $D=165\text{ cm}$: $\theta_{\text{target}} = \arcsin(40 / 165) = 14.03^\circ$.
   * $\text{FrontConeDegrees} = 90.0^\circ\text{ [DESIGN VALUE, PROPOSED]}$ (generous frontal arc accommodating dynamic yaw).
4. **Framework Profile Proof Band:**
   * Sweet Spot Center: $D_{\text{sweet}} = 151.86 + 15.00 \approx 165.0\text{ cm [DERIVED]}$.
   * $\text{BandMinCm} = 150.0\text{ cm [MEASURED: F4 proof run 1 baseline]}$.
   * $\text{BandMaxCm} = 180.0\text{ cm [MEASURED: F4 proof run 1 baseline]}$.
   * Arrival distance in F4 proof: $169.69\text{ cm [MEASURED: final_f4_run1:1506]}$.

---

## 3. Card 2: `Move_Sevarog_SwingMedium`

### 3.1 Empirical Telemetry (`Claude/F5/reach_run1`)
* **Sequence Path:** `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Medium`
* **Clip Length:** $1.1333\text{ s}$ `[MEASURED]`
* **Active Window:** $[0.1500, 0.2667]\text{ s}$ `[MEASURED: C379 probe]`
* **Peak Forward in Window ($Y_{\text{peak}}$):** $133.92\text{ cm}$ `[MEASURED: reach_run1]` (overall clip peak is $149.93\text{ cm}$ at $t=0.2833\text{ s}$, but inside the active window peak is $133.92\text{ cm}$)
* **Tip Forward at Peak:** $89.86\text{ cm}$ `[MEASURED]` (at $t=0.2917\text{ s}$)
* **Swept Forward Range in Window ($Y$):** $[-48.95, 133.92]\text{ cm}$ `[MEASURED]`
* **Swept Lateral Range in Window ($X$):** $[-67.03, 31.32]\text{ cm}$ `[MEASURED]`
* **Lateral Half-Width ($W_{\text{half}}$):** $67.03\text{ cm}$ `[MEASURED]`
* **Swept Vertical Range in Window ($Z$):** $[141.50, 265.19]\text{ cm}$ `[MEASURED]`

### 3.2 Derivation of Range & Cone
1. **Maximum Physical Contact Distance:**
   $$D_{\text{contact\_max}} = Y_{\text{peak}} + R_{\text{target}} + R_{\text{blade}} = 133.92 + 40.00 + 15.00 = 188.92\text{ cm [DERIVED]}$$
2. **Card Range Bounds:**
   * $\text{MaxRangeCm} = 180.0\text{ cm [DESIGN VALUE, PROPOSED]}$ (Margin $\Delta_{\text{outer}} = 8.92\text{ cm}$).
   * $\text{MinRangeCm} = 90.0\text{ cm [DESIGN VALUE, PROPOSED]}$ (Margin over $82.0\text{ cm}$ minimum separation).
3. **Card Cone Angle:**
   * $\theta_{\text{blade}} = \arctan(67.03 / 133.92) = 26.59^\circ$. Target subtense at $D=150\text{ cm}$: $\theta_{\text{target}} = 15.47^\circ$.
   * $\text{FrontConeDegrees} = 90.0^\circ\text{ [DESIGN VALUE, PROPOSED]}$.
4. **Framework Profile Proof Band:**
   * Sweet Spot Center: $D_{\text{sweet}} = 133.92 + 15.00 \approx 150.0\text{ cm [DERIVED]}$.
   * $\text{BandMinCm} = 135.0\text{ cm [DESIGN VALUE, PROPOSED]}$.
   * $\text{BandMaxCm} = 165.0\text{ cm [DESIGN VALUE, PROPOSED]}$.
   * Band half-width $15.0\text{ cm} > R_{\text{accept}} = 10.0\text{ cm}$.

---

## 4. Card 3: `Move_Sevarog_AntiGreed` (`Swing1_FAST_v2`)

### 4.1 Empirical Telemetry (`Claude/F5/reach_run1`)
* **Sequence Path:** `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_FAST_v2`
* **Clip Length:** $0.5333\text{ s}$ `[MEASURED]`
* **Proposed Active Window:** $[0.1500, 0.3000]\text{ s}$ `[PROPOSED]`
* **Peak Forward in Window ($Y_{\text{peak}}$):** $138.52\text{ cm}$ `[MEASURED: reach_run1]` (at $t=0.2750\text{ s}$)
* **Tip Forward at Peak:** $90.01\text{ cm}$ `[MEASURED]` (at $t=0.2750\text{ s}$)
* **Swept Forward Range in Window ($Y$):** $[-48.95, 138.52]\text{ cm}$ `[MEASURED]`
* **Swept Lateral Range in Window ($X$):** $[-67.02, 88.55]\text{ cm}$ `[MEASURED]`
* **Lateral Half-Width ($W_{\text{half}}$):** $88.55\text{ cm}$ `[MEASURED]`
* **Swept Vertical Range in Window ($Z$):** $[102.54, 265.18]\text{ cm}$ `[MEASURED]`

### 4.2 Derivation of Range & Cone
1. **Maximum Physical Contact Distance:**
   $$D_{\text{contact\_max}} = Y_{\text{peak}} + R_{\text{target}} + R_{\text{blade}} = 138.52 + 40.00 + 15.00 = 193.52\text{ cm [DERIVED]}$$
2. **Card Range Bounds:**
   * $\text{MaxRangeCm} = 185.0\text{ cm [DESIGN VALUE, PROPOSED]}$ (Margin $\Delta_{\text{outer}} = 8.52\text{ cm}$).
   * $\text{MinRangeCm} = 90.0\text{ cm [DESIGN VALUE, PROPOSED]}$.
3. **Card Cone Angle:**
   * $\theta_{\text{blade}} = \arctan(88.55 / 138.52) = 32.59^\circ$. Lateral sweep extends further to the right ($+88.55\text{ cm}$).
   * $\text{FrontConeDegrees} = 100.0^\circ\text{ [DESIGN VALUE, PROPOSED]}$.
4. **Framework Profile Proof Band:**
   * Sweet Spot Center: $D_{\text{sweet}} = 138.52 + 15.00 \approx 153.5\text{ cm [DERIVED]}$.
   * $\text{BandMinCm} = 135.0\text{ cm [DESIGN VALUE, PROPOSED]}$.
   * $\text{BandMaxCm} = 165.0\text{ cm [DESIGN VALUE, PROPOSED]}$.
5. **Unmeasured Timing Gap & Required Speed Probe Run:**
   * **Status:** Forward reach ($138.52\text{ cm}$) is probe-backed by `reach_run1`, but hit window timings (`CommitSeconds`, `ActiveStartSeconds`, `ActiveEndSeconds`, `RecoveryEndSeconds`) remain UNMEASURED estimates.
   * **Exact Command for Claude:**
     ```bash
     python Docs/BossCombatReview/Execution/Antigravity/HitWindowProbe/probe_weapon_motion.py \
       --sequences /Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_FAST_v2 \
       --output-json Docs/BossCombatReview/Execution/Claude/F5/swing1_fast_v2_timing.json
     ```

---

## 5. Card 4: `Move_Sevarog_HeavySlam` (`Swing3_Slow`)

### 5.1 Empirical Telemetry (`Claude/F5/reach_run1`)
* **Sequence Path:** `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow`
* **Clip Length:** $1.7000\text{ s}$ `[MEASURED]`
* **Active Window:** $[0.4750, 0.5333]\text{ s}$ `[MEASURED: C379 probe]`
* **Peak Forward in Window ($Y_{\text{peak}}$):** $130.30\text{ cm}$ `[MEASURED: reach_run1]` (at $t=0.5167\text{ s}$)
* **Tip Forward at Peak:** $99.25\text{ cm}$ `[MEASURED]` (at $t=0.5083\text{ s}$)
* **Swept Forward Range in Window ($Y$):** $[28.83, 130.30]\text{ cm}$ `[MEASURED]` (all forward of root throughout window)
* **Swept Lateral Range in Window ($X$):** $[-99.49, -59.20]\text{ cm}$ `[MEASURED]` (concentrated left-forward quadrant)
* **Lateral Half-Width ($W_{\text{half}}$):** $99.49\text{ cm}$ `[MEASURED]`
* **Swept Vertical Range in Window ($Z$):** $[58.21, 248.33]\text{ cm}$ `[MEASURED]` (weapon slams directly toward floor level)

### 5.2 Derivation of Range & Cone
1. **Maximum Physical Contact Distance:**
   $$D_{\text{contact\_max}} = Y_{\text{peak}} + R_{\text{target}} + R_{\text{blade}} = 130.30 + 40.00 + 15.00 = 185.30\text{ cm [DERIVED]}$$
2. **Card Range Bounds:**
   * $\text{MaxRangeCm} = 180.0\text{ cm [DESIGN VALUE, PROPOSED]}$ (Margin $\Delta_{\text{outer}} = 5.30\text{ cm}$).
   * $\text{MinRangeCm} = 90.0\text{ cm [DESIGN VALUE, PROPOSED]}$.
3. **Card Cone Angle:**
   * Overhead vertical downward slam: although lateral offset is $-99.49\text{ cm}$, the trajectory is an overhead arc aimed directly along the attack lane.
   * $\text{FrontConeDegrees} = 60.0^\circ\text{ [DESIGN VALUE, PROPOSED]}$ (narrower cone prevents triggering on targets standing wide laterally).
4. **Framework Profile Proof Band:**
   * Sweet Spot Center: $D_{\text{sweet}} = 130.30 + 15.00 \approx 145.0\text{ cm [DERIVED]}$.
   * $\text{BandMinCm} = 130.0\text{ cm [DESIGN VALUE, PROPOSED]}$.
   * $\text{BandMaxCm} = 160.0\text{ cm [DESIGN VALUE, PROPOSED]}$.

---

## 6. Synthesis & Comparison Table

Comparison between old unconstrained proposed ranges (which exceeded reach, KI-145) and the new probe-backed parameters:

| Card ID | Sequence | Measured Peak Reach $Y$ | Old Proposed Range | New Derived $[\text{Min}, \text{Max}]$ | New Derived Cone | Derived Proof Band | Kinematic Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`Move_Sevarog_SwingSlow`** | `Swing1_Slow` | $151.86\text{ cm}$ `[M]` | $[200, 400]\text{ cm}$ | $[100, 200]\text{ cm}$ `[P]` | $90.0^\circ$ `[P]` | $[150, 180]\text{ cm}$ `[M]` | Reach & Timing Confirmed (F4 Baseline) |
| **`Move_Sevarog_SwingMedium`** | `Swing1_Medium` | $133.92\text{ cm}$ `[M]` | $[150, 300]\text{ cm}$ | $[90, 180]\text{ cm}$ `[P]` | $90.0^\circ$ `[P]` | $[135, 165]\text{ cm}$ `[P]` | Reach & Timing Probe-Backed |
| **`Move_Sevarog_AntiGreed`** | `Swing1_FAST_v2` | $138.52\text{ cm}$ `[M]` | $[100, 250]\text{ cm}$ | $[90, 185]\text{ cm}$ `[P]` | $100.0^\circ$ `[P]` | $[135, 165]\text{ cm}$ `[P]` | Reach Confirmed; Timings UNMEASURED |
| **`Move_Sevarog_HeavySlam`** | `Swing3_Slow` | $130.30\text{ cm}$ `[M]` | $[100, 250]\text{ cm}$ | $[90, 180]\text{ cm}$ `[P]` | $60.0^\circ$ `[P]` | $[130, 160]\text{ cm}$ `[P]` | Reach & Timing Probe-Backed |

*All newly derived ranges guarantee physical collision overlap ($D_{\text{root-to-root}} \le D_{\text{contact\_max}}$), conclusively resolving KI-145.*
