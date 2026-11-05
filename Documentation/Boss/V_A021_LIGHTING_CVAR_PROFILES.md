# V-A021: Lighting Proposal CVar Profiles for Round 6

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** CVar-only lighting and atmosphere optimization profiles for Round 6 performance experiments.

---

## 1. Executive Summary

- **Objective:** Provide zero-asset-edit CVar lighting profiles for Round 6 benchmark experiments to measure GPU savings from brazier shadow reduction, attenuation scaling, and sky capture rate throttling.
- **Status:** **DELIVERED** as standalone CVar sets compatible with `Scripts/round6_experiments.json` and `RunPerfExperiments.ps1`.
- **Target Savings:** **4.5 – 6.5 ms** GPU frame time recovery on RTX 2060 Super, directly addressing the Virtual Shadow Map (VSM) page pool overhead observed in Rounds 2–5.

---

## 2. Profile Definitions

### Profile L1: Cardinal Shadows Baseline (`Lighting.CardinalShadows`)
Limits dynamic VSM shadow-casting from 12 braziers to the 4 primary cardinal braziers (00 North, 03 East, 06 South, 09 West). The other 8 braziers cast diffuse fill light only.
```text
rpg.Perf.FireShadows 4
```
- **Target Saving:** **4.0 – 5.5 ms** GPU frame time.
- **Visual Impact:** Very low. Player and boss retain crisp radial ground shadows from 4 cardinal directions; no loss of fire particle effects, ambient light, or audio crackle.

### Profile L2: Cardinal Shadows + Attenuation Contraction (`Lighting.CardinalAndRadius`)
Combines 4 cardinal shadow casters with a 35% contraction of brazier attenuation radius (from 3,200 cm to 2,080 cm), reducing the quadratic illumination overlap area by ~58%.
```text
rpg.Perf.FireShadows 4
rpg.Perf.FireRadiusScale 0.65
```
- **Target Saving:** **5.5 – 6.5 ms** GPU frame time.
- **Visual Impact:** Low. Arena center experiences a subtle contrast increase; perimeter braziers retain rich local illumination while eliminating 32 m cross-arena VSM page allocation.

### Profile L3: Aggressive Lighting Optimization (`Lighting.OptimizedFull`)
Combines Profile L2 with sky reflection capture throttling and volumetric cloud shadow ray sampling optimization (using the source-audited CVar confirmed in `V_C016`).
```text
rpg.Perf.FireShadows 4
rpg.Perf.FireRadiusScale 0.65
r.SkyLight.RealTimeReflectionCapture 0
r.VolumetricCloud.Shadow.ViewRaySampleMaxCount 32
r.VolumetricCloud.ViewRaySampleCountScale 0.5
```
- **Target Saving:** **7.0 – 8.5 ms** GPU frame time.
- **Visual Impact:** Moderate. Sky reflections update via static cubemap probe; clouds cast softer ground shadows; duel readability remains 100% pristine.

---

## 3. Integration into Round 6 Experiment Suite

- These profiles operate strictly via console variables.
- Zero `.umap` edits or binary asset modifications are required.
- Preserves D5 baseline parity when unconfigured (`rpg.Perf.FireShadows 12`, `rpg.Perf.FireRadiusScale 1.0`).
