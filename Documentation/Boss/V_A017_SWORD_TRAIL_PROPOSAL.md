# V-A017: Sword Trail Proposal (Boss & Player)

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-05  
**Scope:** Architecture proposal, material design, and GPU cost estimation for weapon blade ribbon trails on Boss and Player.

---

## 1. Executive Summary

- **Proposal:** Introduce dynamic ribbon particle trails attached along weapon sockets during active trace damage windows.
- **Objectives:**
  - Enhance boss attack readability (telegraphing swing arcs, swing speed, and exact spatial coverage).
  - Clarify player attack commitment and swing trajectories.
  - Distinguish Phase 1 (steel/silver air-distortion ribbon) from Phase 2 (blazing ember/flame ribbon).
- **Target Assets:**
  - Boss: `/Game/OneBossFight/VFX/NS_Boss_SwordTrail`
  - Player: `/Game/OneBossFight/VFX/NS_Player_SwordTrail`
- **Estimated GPU Cost:** **0.06 – 0.09 ms total** on RTX 2060 Super at 1080p (well within the < 0.20 ms visual polish budget).

---

## 2. Technical Design & Socket Layout

1. **Emitter Type:**
   - Niagara Ribbon Emitter (`RibbonRenderer`) sampling two sockets along the weapon mesh:
     - Root Socket: `Weapon_Hilt` / `Blade_Base`
     - Tip Socket: `Weapon_Tip` / `Blade_Tip`
   - Ribbon width: 140 cm (matching blade span).
2. **Activation Gating (Zero Drift / Zero Idle Cost):**
   - Ribbon emitters are deactivated by default.
   - Spawn / emission is enabled **strictly** between `AnimNotify_ActiveStart` and `AnimNotify_ActiveEnd`.
   - Ribbon lifetime: **0.18 s – 0.24 s** (creates a tight 90°–120° trailing arc behind the blade that dissolves immediately as swing completes).
3. **Phase-Specific Visual Profiles:**
   - **Phase 1 (Neutral / Physical):**
     - Translucent ribbon with subtle refractive refraction (`M_SwordTrail_AirDistortion`).
     - Faint white/silver edge glow (`Emissive: 2.0`).
   - **Phase 2 (Ember Warden Awakening, 60% HP):**
     - Saturated fire ribbon (`M_SwordTrail_Ember`).
     - Multi-octave scrolling flame noise with trailing smoke particles.
     - Emissive intensity: `12.0` (orange-red).

---

## 3. Performance & Budget Breakdown

| Component | Emitter Complexity | Vertices per Swing | GPU Cost (1080p) | Memory Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Boss Ribbon** | 1 Ribbon Emitter (32 segments) | ~64 dynamic vertices | ~0.04 ms | < 128 KB |
| **Player Ribbon**| 1 Ribbon Emitter (24 segments) | ~48 dynamic vertices | ~0.03 ms | < 96 KB |
| **Phase 2 Ember Particles** | 1 GPU Sprite Emitter (20 particles/sec) | 80 sprite quads | ~0.02 ms | < 64 KB |
| **Combined Total** | — | — | **~0.09 ms max** | **< 300 KB** |

---

## 4. Implementation Steps (Post-Owner Go)

1. **Step 1:** Author base ribbon material `M_SwordTrail_Master` with parameter switches (`IsPhaseTwo`, `TrailColor`, `DistortionStrength`).
2. **Step 2:** Assemble `NS_Boss_SwordTrail` and `NS_Player_SwordTrail` Niagara systems using socket-location modules.
3. **Step 3:** Hook into `URPGAttackTracker` and `URPGPlayerMovesSubsystem` active trace windows via Development CVar `rpg.Art.SwordTrails`.
4. **Step 4:** Maintain strict D5 parity contract by defaulting soft references to `nullptr`.
