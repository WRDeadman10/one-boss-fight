# V-A034: Audio Mix & Sound Hierarchy Audit

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Audio mix hierarchy, SoundClasses, SoundMixes, volume balancing, spatialization, and dynamic ducking across duel SFX, voice, and music.

---

## 1. Executive Summary

- **Audit Target:** Audio asset routing, SoundClass hierarchy, and mix volume balance in `L_SevarogArena`.
- **Finding:**
  - Core combat cues (`A_Guardian_ImpactL_Cue`, metallic clack, shockwave bass thump) possess high clarity and proper priority.
  - **Identified Improvement:** During parry slow-motion (Feature F1 / `Legend`), background music and ambient rumble should duck by **-6 dB to -10 dB** using `ParrySlowMotionSoundMix` (wired by Codex in `V-C036`) to spotlight the crisp metallic clack and breathing cues.

---

## 2. Audio Mix & Bus Hierarchy

```text
[Master SoundClass]
  |
  +---> [SC_Music] (Volume: 0.75, Low-pass ducking enabled during slow-motion)
  |
  +---> [SC_CombatSFX] (Volume: 1.00, High priority, un-ducked)
  |       |---> Weapon Clashes & Sparks
  |       |---> Parry Clack
  |       +---> Shockwave Ground Thump
  |
  +---> [SC_CharacterVoice] (Volume: 1.00, Boss roar, exertion grunts)
  |
  +---> [SC_Foley] (Volume: 0.65, Footsteps, armor jingle, cloth swish)
  |
  +---> [SC_Ambience] (Volume: 0.45, Wind howl, brazier fire crackle, dusk rumble)
  |
  +---> [SC_Accessibility] (Volume: 1.00, QA-007 dual-channel cues)
```

---

## 3. Dynamic SoundMix Profiling (`ParrySlowMotionSoundMix`)

| SoundClass | Normal Volume | Slow-Motion Volume | Volume Delta | Pitch Multiplier | Mix Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`SC_CombatSFX`** | 1.00 (0 dB) | **1.20 (+1.6 dB)** | +1.6 dB | 0.85 (Heavy resonance) | Sharp metallic parry clack cuts cleanly through duel audio. |
| **`SC_Music`** | 0.75 (-2.5 dB) | **0.25 (-12.0 dB)** | -9.5 dB | 0.70 (Slowed tempo) | Dramatic orchestral ducking elevates player focus. |
| **`SC_Ambience`** | 0.45 (-6.9 dB) | **0.10 (-20.0 dB)** | -13.1 dB | 0.50 (Distant drone) | Removes environmental noise floor. |
| **`SC_Foley`** | 0.65 (-3.7 dB) | **0.30 (-10.5 dB)** | -6.8 dB | 0.80 | Footstep clatter suppressed; blade deflection emphasized. |
| **`SC_Accessibility`** | 1.00 (0 dB) | **1.00 (0 dB)** | 0.0 dB | 1.00 | Accessibility audio feedback is never ducked or muffled. |

---

## 4. Attenuation & Spatialization Settings

1. **Boss Weapon & Shockwave:**
   - Spatialization: 3D Binaural (Binaural spatialization enabled on PC/Headphones).
   - Falloff Distance: Inner radius 400 cm, Outer radius 3,000 cm (covers full arena).
2. **Perimeter Braziers:**
   - Inner radius 150 cm, Outer radius 1,200 cm (prevents 12 overlapping fire loops from muddying arena center).
3. **Footsteps:**
   - Physical surface tracing (`SurfaceType_Stone`, `SurfaceType_Metal`) provides distinct footsteps for stone arena floor vs metal grate.
