# V-A057: Phase-Two Aura & Emissive Ramp Timing Analysis

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-A057`, `V-C034`, `TIER2_ART_OWNER_BRIEF.md`, `[C-927]`
**Sources:** Content/OneBossFight/Boss01/Animations/AM_Boss01_PhaseTransition.uasset, Source/OneBossFight/Boss/RPGSevarogDirector.cpp:212-225

---

## 1. Overview & Objectives

In Phase 2 of the boss duel (triggered at <= 60% HP), Sevarog enters an invulnerable roar transition (`AM_Boss01_PhaseTransition` / `AN_Boss01_Roar`, total length **3.500 s** / 105 frames @ 30 FPS). Under the optional Tier 2 presentation suite (`rpg.Art.Tier2=1`), this transition triggers:
1. `NS_Boss_PhaseTwoAura`: A lingering ethereal dark-fire ribbon and ember emitter attached to Sevarog's mantle/shoulder sockets.
2. `PhaseTwoGlowParameter`: A scalar parameter in `MPC_BossVisuals` driving emissive core intensity on Sevarog's armor carvings.

This document establishes the exact microsecond-level synchronization between the animation notify timeline, camera shake, visual VFX ignition, and gameplay vulnerability.

---

## 2. Transition Timeline & Event Synchronization

| Timestamp (s) | Frame @ 30fps | Animation Pose Phase | Audio / Camera Event | Tier 2 Visual Event (`rpg.Art.Tier2=1`) | Gameplay / Director State |
|---|:---:|---|---|---|---|
| **0.000 s** | 0 | Boss halts movement; begins gathering crouch | Background music begins ducking (-3 dB) | Aura dormant (`Inactive`) | Boss invulnerable; incoming attacks bounce; stance locked |
| **0.700 s** | 21 | Boss arches backward; chest cavity begins expanding | Roar vocal cue begins; sub-bass swell | Emissive ramp starts (`0.0 -> 0.3` pre-glow) | Phase 2 state flag latched in Director |
| **1.200 s** | 36 | **Roar Apex:** Jaws wide, scythe raised high | Roar peak volume; `CS_Roar_CameraShake` triggers (0.8s duration) | **`NS_Boss_PhaseTwoAura` Ignites!** Initial burst of 80 ash motes + ribbon trails activate | Radial knockback pulse deters hugging players |
| **1.500 s** | 45 | Sustained roar scream | Camera shake decaying | `PhaseTwoGlowParameter` hits peak value (`1.0`) | Emissive rim lighting fully saturated |
| **2.200 s** | 66 | Boss begins descending scythe; vocal taper | Roar vocal fades out; Phase 2 intense music stem starts | Aura settles into looping steady-state (12 motes/s, < 0.05 ms GPU) | Stance recovery initiated |
| **2.800 s** | 84 | Scythe settles at side; blend-out to combat stance begins | Standard combat mix restored | Looping aura attached to `spine_03` and `FX_Mantle_Socket` | Invulnerability window ends; player hitboxes active |
| **3.500 s** | 105 | **Full Neutral Idle Reached** | Phase 2 music at full volume | Steady-state aura maintained continuously until boss death | AI Move Selection unlocks; Phase 2 move pool active |

---

## 3. Teardown & Edge-Case Safety Rules

1. **Boss Defeat in Phase 2:**
   - When boss HP hits 0, `URPGSevarogDirector::ClearPhaseTwoVisuals()` executes on the first frame of death montage initiation (`D1` gate).
   - `NS_Boss_PhaseTwoAura` deactivates particle emission immediately; existing motes fade out over 0.40 s natural life.
   - `PhaseTwoGlowParameter` smoothly decays to `0.0` over 0.25 s.
2. **Player Death / Encounter Reset:**
   - `ResetEncounter()` invokes `ClearPhaseTwoVisuals()`.
   - The Niagara component is destroyed immediately (`DestroyComponent`), leaving zero orphaned particle systems in the arena.
3. **Stagger Interruption Deferral:**
   - Per `BOSS-PHS-002`, phase-two transition cannot trigger while the boss is in a stance-break stagger. The transition waits until stagger recovery completes, guaranteeing the 3.500 s timeline plays cleanly.
