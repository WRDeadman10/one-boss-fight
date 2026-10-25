# Runtime Visual Capture Requirements (CI-P0-A-02 / T4)

Date: 2026-10-25
Author: Antigravity (Accountable Visual Investigator)
Addressed to: Claude (Technical Lead & Editor Owner)
Initiative: P0-P8 Boss Combat Improvement Program - Visual Baseline Reconciliation

---

## 1. Executive Summary

This document specifies the exact camera setups, frame rates, debug overlays, and configuration states required from Claude to resolve all outstanding `UNVERIFIED / BLOCKED` runtime items in the P0 Visual Baseline Audit.

---

## 2. Priority 1: Immediate Critical Captures (Scheduled in C-90)

### CAP-01: A5 Javelin Visual Release vs Actor Spawn Synchronization
- **Target Move:** A5 (Gauntlet Ember Javelin Throw / `RPGBossHealPunish`)
- **Objective:** Determine whether visual hand release pose (authored at $0.40\text{ s}$ / Frame 12) precedes, matches, or lags projectile actor instantiation (`ARPGBossJavelin` at code declared $0.45\text{ s}$).
- **Camera Setup:** Profile orthographic or low-distortion telephoto ($50\text{ mm}$ focal length / $45^\circ\text{ FOV}$), positioned to the boss's left flank, framing the dorsal brazier and left arm draw.
- **Recording Rate:** 60.0 fps (or slomo 0.2 at 60 fps for 300 fps effective temporal resolution).
- **Required Overlays:**
  * Engine timestamp / frame index overlay.
  * Projectile actor origin crosshair or collision bounding sphere.
  * Brazier gauntlet socket location indicator.

### CAP-02: A4 Low Sweep Production Query vs Blade Tip & Capsule
- **Target Move:** A4 (Ground Low Sweep / `RPGBossLowSweep`)
- **Objective:** Measure the spatial offset between the physical blade tip of `SM_Boss01_Greatsword` (Z = +163.3 cm), the active `RPGBossLowSweep` planar threat arc (declared $380.0\text{ cm}$), and the Greystone player capsule ($R \approx 34\text{--}42\text{ cm}$).
- **Camera Setup:** Top-down 3/4 isometric perspective ($30^\circ$ elevation, looking down into the sweep plane).
- **Required Overlays:**
  * `RPGBossLowSweep` debug lines (`DrawDebugCircle` / sectoral sweep lines).
  * Visible blade tip trail or socket position indicator.
  * Player character capsule wireframe (`ShowDebug COLLISION`).

### CAP-03: Untracked Pack Abilities Motion & Visual Presentation
- **Target Moves:**
  * `MidRange`: `Mid01_Anim_Montage` (`GA_GS_Boss_MidRangeAttack`)
  * `Sprint`: `GS_SprintAttackFollowUp_Montage` (`GA_GS_Boss_SprintAttack`)
  * `Retaliation`: `RetaliationAttack_Montage`
- **Objective:** Evaluate visual windup readability, weapon trace coverage vs blade, and hit-stun immunity cues.
- **Camera Setup:** Medium combat chase camera framing boss and player duel distance ($200\text{--}800\text{ cm}$).
- **Recording Rate:** 60.0 fps.
- **Required Overlays:**
  * Live montage notify name and active window timestamp.
  * Weapon collision trace sweep debug lines (`ANS_CollisionTrace`).

---

## 3. Priority 2: Secondary Captures & Packaging

### CAP-04: A6 Shockwave Expanding Ring (Debug-Off Observation)
- **Target Move:** A6 (Phase 2 Leap Slam / `RPGBossShockwave`)
- **Objective:** Verify whether any production Niagara VFX or material ring renders when `DrawDebugCircle` is suppressed (`#if !UE_BUILD_SHIPPING` compiled out in Shipping, or debug drawing disabled in Development).
- **Camera Setup:** Wide arena camera encompassing the full $200\text{ to }1100\text{ cm}$ expansion band.
- **Environment:** Standalone Development build with debug drawing suppressed, or Packaged Shipping build.

### CAP-05: A2 Overhead Slam Live twirl vs Authored Poise
- **Target Move:** A2 (Delayed Overhead Slam / `GS_ChargedAttack_Montage`)
- **Objective:** Document the live pack twirl motion in gameplay context for comparison with the delivered 3-part authored set (`AN_Boss01_A2_Raise/ApexHold/Slam`).
- **Camera Setup:** Front-quarter view at $250\text{ cm}$ duel distance.

### CAP-06: Windup Tracking Yaw vs Foot Grounding (VIS-07)
- **Target Moves:** A1 (`AN_Boss01_A1_QuickSlash`) and A3a (`AN_Boss01_A3a_Combo1`)
- **Objective:** Document whether $360^\circ/\text{s}$ angular tracking during in-place windups causes noticeable visual foot sliding across the arena stone floor texture.
- **Camera Setup:** Low-angle close-up camera focusing on boss feet contact with arena floor stones.

---

## 4. Delivery Format & Storage

- **Screenshots:** PNG format under `Docs/BossCombatReview/Execution/Antigravity/Evidence/captures/` or `Claude/Evidence/captures/`.
- **Gameplay Clips:** MP4 or contact sheet image strips with annotated millisecond / frame timestamps.
