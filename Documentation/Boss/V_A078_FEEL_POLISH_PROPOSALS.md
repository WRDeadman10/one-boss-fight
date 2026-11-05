# V-A078: Combat Feel Polish Proposals

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-A078`, `V_A076`, `V_A077`, `V_A016`, `V_A017`

---

## 1. Executive Summary

Based on the archetype comparison refresh ([`V_A077`](./V_A077_EMBER_WARDEN_COMPARISON_REFRESH.md)), the mechanical timing, reaction windows, and damage rules of the duel are fully certified. 

To bridge the final gap between *mechanical accuracy* and *exhilarating Soulslike game feel*, we propose **four targeted, lightweight feel enhancements**. All four are strictly cosmetic, consume less than 0.15 ms GPU in aggregate, and require zero modifications to core combat C++ classes.

---

## 2. The Four Feel Polish Proposals

### Proposal 1: Scythe Weapon Ribbon Trail (`NS_WeaponTrail_Sevarog`)
- **Visual Description:** A wispy, dark-smoke ribbon trail emitting from the tip and blade sockets of Sevarog's scythe.
- **Activation Scope:** Active strictly while `ANS_CollisionTrace` or `RPGAttackTracker` reports an active damage window. Instantly cuts off upon recovery entry.
- **Player Feel Benefit:** Provides distinct spatial trajectory reading so players can clearly perceive the arc of incoming swings (especially in close-quarters camera angles).
- **Performance Budget:** Single GPU compute ribbon emitter, fixed bounds, **< 0.08 ms GPU**.

### Proposal 2: Sub-Bass "Impact Thump" on Parry Confirmation
- **Audio Description:** A brief 50 Hz sub-bass sine transient (duration 0.12 s, volume -4 dB) mixed into the parry sound cue.
- **Player Feel Benefit:** Combines with the 80 ms hit-stop dilation to deliver a physical, tactile "kick" through player subwoofers and headphones.
- **Performance Budget:** **0.00 ms GPU, 0 CPU** (standard audio cue layering).

### Proposal 3: Camera Shake Decay Smoothing
- **Problem:** Current `CS_Slam_CameraShake` cuts off abruptly when the 0.8 s shake duration expires.
- **Action:** Adjust the camera shake oscillation curve from flat decay to a smooth exponential ease-out (`DecayRate=2.5`).
- **Player Feel Benefit:** Eliminates jarring camera pop at the end of A2 and A6 ground slams, maintaining smooth combat orientation.
- **Performance Budget:** **0.00 ms GPU**.

### Proposal 4: Ground Dust Puffs on Directional Dodge Rolls (`NS_Combat_DodgePuff`)
- **Visual Description:** A small, low-opacity dust burst emitted at the player's feet upon initiating `IA_Dodge`.
- **Player Feel Benefit:** Provides immediate visual acknowledgment of dodge roll input startup on frame 0, eliminating any perception of input lag before the mannequin torso begins rolling.
- **Performance Budget:** 12 GPU sprites with 0.3 s lifetime, **< 0.02 ms GPU**.

---

## 3. Implementation Decision Gate

These proposals are non-destructive and modular. They can be created as preview assets or staged in Queue W pending Owner aesthetic sign-off.
