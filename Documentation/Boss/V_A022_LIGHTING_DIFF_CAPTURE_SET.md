# V-A022: Visual Diff Capture Set for Lighting Profiles

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Specification and coordinate checklist for owner-session visual difference captures across lighting profiles.

---

## 1. Executive Summary

- **Context:** Automated agent captures run in headless/nullrhi mode and render as black frames. Therefore, visual verification of lighting changes requires owner-session high-resolution screenshots.
- **Objective:** Provide an exact 4-shot camera trajectory checklist to visually compare baseline lighting (12 shadow braziers) against Profile L1 (4 cardinal shadows) and Profile L2 (radius contraction).

---

## 2. Capture Viewpoints Checklist

| Shot ID | Name | Camera Location (X, Y, Z) | Camera Rotation (Pitch, Yaw, Roll) | Subject & Visual Check Focus |
| :--- | :--- | :--- | :--- | :--- |
| **`SHOT-L01`** | **Arena Wide Duel View** | `(0, -1800, 350)` | `(-12.0, 90.0, 0.0)` | Overall arena illumination, sky reflection on wet stone, contrast between center circle and perimeter. |
| **`SHOT-L02`** | **Boss Radial Shadow** | `(150, -450, 120)` | `(-8.0, 75.0, 0.0)` | Boss standing at `(0, 0, 0)`; inspect multi-directional shadow legs on stone floor from cardinal braziers. |
| **`SHOT-L03`** | **Perimeter Wall & Brazier**| `(1200, 1200, 180)` | `(-5.0, 225.0, 0.0)` | Brazier 03 (East); check local flame glow, stonework normal map relief, and transition into unshadowed neighbor. |
| **`SHOT-L04`** | **Player Jump Silhouette** | `(0, -300, 150)` | `(5.0, 90.0, 0.0)` | Player jumping at center circle; verify jump clearance readability against dusk sky and shockwave ring band. |

---

## 3. Owner Execution Protocol

1. Launch editor or standalone Development build:
   ```powershell
   Saved\StagedBuilds_Development\Windows\OneBossFight.exe -game -ResX=1920 -ResY=1080 -WINDOWED
   ```
2. In the console (`~`), apply profile and teleport camera:
   - Baseline:
     ```text
     rpg.Perf.FireShadows 12; rpg.Perf.FireRadiusScale 1.0
     shot SHOT-L01-Baseline.png
     ```
   - Profile L1:
     ```text
     rpg.Perf.FireShadows 4; rpg.Perf.FireRadiusScale 1.0
     shot SHOT-L01-ProfileL1.png
     ```
   - Profile L2:
     ```text
     rpg.Perf.FireShadows 4; rpg.Perf.FireRadiusScale 0.65
     shot SHOT-L01-ProfileL2.png
     ```
3. Archive captures to `Docs/BossCombatReview/Execution/Owner/LightingDiff/`.
