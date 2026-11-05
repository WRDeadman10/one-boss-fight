# V-A018: Death Dissolve Polish Proposal

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-05  
**Scope:** Architecture proposal for smooth material dissolve transition and ember monument solidification on Boss defeat.
**Sources:** Source/OneBossFight/Player/RPGLegend.cpp:438-454, Content/OneBossFight/Boss01/Remains/ [PROPOSAL]

---

## 1. Executive Summary

- **Proposal:** Polish the climax defeat sequence where the Ember Warden falls to one knee, solidifies into a blackened stone monument, and dissolves with rising ash and ember flurries.
- **Current Production Components:**
  - `URPGBossDeath`: Plays `AN_Boss01_DeathLegend` (fatal knee collapse, 2.80 s) and suppresses default ragdoll.
  - `URPGBossRemains`: Spawns static mesh `SM_Boss01_CorpseStatue` with material `M_Boss01_Remains`.
  - Dissolve Mask: Procedural noise ramp `T_Boss01_DissolveNoise` driven over 2.50 s.
- **Identified Polish Areas:**
  1. **Seam Hard-Cut:** Current transition swaps skeletal mesh to static mesh at frame 72 with a single-frame shadow pop.
  2. **Ember Evaporation:** The dissolve edge lacks rising ash particles along the dissolve burn threshold.
  3. **Dissolve Curve:** Linear material parameter ramp causes premature edge erosion before the kneeling pose settles.

---

## 2. Technical Polish Plan

1. **Non-Linear Dissolve Curve:**
   - Replace linear 0.0 -> 1.0 ramp with an S-curve easing:
     - \(0.00\text{ s} - 1.20\text{ s}\): Pose settles; stone solidification parameter ramps from 0.0 to 1.0 (skin turns to charred granite).
     - \(1.20\text{ s} - 3.20\text{ s}\): Dissolve noise threshold sweeps upward from bottom to crown.
     - \(3.20\text{ s} - 4.00\text{ s}\): Lingering embers cool from glowing orange to cold soot.
2. **Burn-Edge Niagara Emitter (`NS_Boss_DeathDissolve`):**
   - Mesh-reproduction particle emitter spawning embers exclusively along vertices where `DissolveThreshold - 0.05 < VertexNoise < DissolveThreshold + 0.05`.
   - Emits 80–120 rising ash motes that drift upward into the arena ceiling with low turbulence.
3. **Shadow Seam Mitigation:**
   - Keep the skeletal mesh visible with `CastShadow=true` while static monument spawns invisibly, performing a 3-frame crossfade (`DitherTemporalAA`) to eliminate shadow popping under Virtual Shadow Maps.

---

## 3. Cost & Complexity Analysis

- **Shader Overhead:** 4 additional ALU instructions in `M_Boss01_Remains` for non-linear ease curve.
- **GPU Particles:** ~0.05 ms during the 2.0 s dissolve window (runs only once after boss defeat; zero combat impact).
- **Parity Guard:** Controlled via `URPGBossRemains::bEnhancedDissolve` (default `false` in production until lead signoff).
