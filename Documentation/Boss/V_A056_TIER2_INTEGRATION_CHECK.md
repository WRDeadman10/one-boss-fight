# V-A056: Tier 2 Asset Integration & Preview Switch Verification

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-A056`, `V-C031..V-C036`, `[C-927]`, `[C-928]`
**Sources:** Source/OneBossFight/Boss/RPGSevarogDirector.cpp:480-530, Source/OneBossFight/Player/RPGLegend.cpp:475-515

---

## 1. Executive Summary

This integration audit reviews the wiring of all Tier 2 presentation assets following Codex's C++ hook implementations (`V-C031..V-C036`) and Lead Claude's BUILD-231 / BUILD-232 certifications. 

Every Tier 2 enhancement is strictly decoupled from the core combat logic and gated behind explicit Development console variables. If an asset is unset (`nullptr` / `None`), or if the preview switch is disabled (`0`), the engine executes the proven D5 baseline with zero overhead and zero visual drift.

---

## 2. Preview Switch Hierarchy & CVar Matrix

| Preview Switch | CVar | Default | Configuration Scope | Associated Hook / Asset | Safe Fallback Behavior |
|---|---|:---:|---|---|---|
| **Tier 1 Visual Preview** | `rpg.Art.Tier1` | `0` | Development / Test | `NS_Boss_ShockwaveRing`, `NS_Combat_ParrySpark` | Procedural debug circles or hidden VFX |
| **Tier 2 Presentation Suite** | `rpg.Art.Tier2` | `0` | Development Only (`UE_BUILD_DEVELOPMENT`) | `NS_Boss_PhaseTwoAura`, `PPM_ParryDistortion`, `Mix_ParrySlowMo`, `AM_Boss01_ParryRecoil` | Normal combat animations; standard audio mix; no screen post-process |
| **A2 Authored Montage Preview** | `rpg.AttackTracker.A2PreviewClip` | `0` | Development / Test | `AM_Boss01_A2` (`OptionalTrackerMontagePath`) | Standard pack ability `GS_ChargedAttack_Montage` with dynamic telegraph scaling |
| **Volumetric Fire Shadows** | `rpg.Perf.FireShadows` | `12` | Runtime / Bench | Point light cast shadow toggles | Falls back to unshadowed fill lights |

---

## 3. Component Integration Matrix

### 3.1 A2 Slam Composite Montage (`AM_Boss01_A2`)
- **Hook Point:** `FRPGAttackTiming::OptionalTrackerMontagePath` in `Source/OneBossFight/Player/RPGAttackTracker.cpp`.
- **Integration Mechanism:** When `rpg.AttackTracker.A2PreviewClip=1`, `PlayMoveMontageForTest` loads `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2`.
- **Validation:** Bypasses `rpg.CloseTelegraph` rate dilation; plays at natural rate 1.00.
- **Fail-Closed Gate:** If montage asset is missing or unassigned, `StartMove("A2")` seamlessly falls back to `GS_ChargedAttack_Montage`.

### 3.2 Phase Two Fiery Aura (`NS_Boss_PhaseTwoAura`)
- **Hook Point:** `URPGSevarogDirector::PhaseTwoAuraSystem` (Soft Niagara System).
- **Integration Mechanism:** On phase-two threshold breach (HP <= 60%), if `rpg.Art.Tier2=1`, spawns Niagara component attached to Sevarog's root/spine socket.
- **Fail-Closed Gate:** If soft pointer is null, no component is spawned; boss transition continues unimpeded. Cleans up cleanly on death/reset via `ClearPhaseTwoVisuals()`.

### 3.3 Parry Slow-Motion Radial Distortion (`PPM_ParryDistortion`)
- **Hook Point:** `URPGBossLegend::ParryFeedbackCollection` (`UMaterialParameterCollection*`).
- **Integration Mechanism:** On confirmed parry slow motion, pulses scalar parameter `ParryDistortionStrength` to 1.0.
- **Fail-Closed Gate:** If collection pointer is null, scalar write is skipped. Time-dilation restore path resets parameter to 0.0 upon expiry or cancel.

### 3.4 Boss Parry Recoil Stagger (`AM_Boss01_ParryRecoil`)
- **Hook Point:** `URPGSevarogDirector::ParryRecoilMontage` (`UAnimMontage*`).
- **Integration Mechanism:** Invoked via `OnParryConfirmed` delegate when `rpg.Art.Tier2=1`.
- **Fail-Closed Gate:** If montage is null, boss remains in standard hit reaction state. No ability lockouts leak.

### 3.5 Parry Audio Ducking (`Mix_ParrySlowMo`)
- **Hook Point:** `URPGBossLegend::ParrySlowMotionSoundMix` (`USoundMix*`).
- **Integration Mechanism:** Pushes sound mix modifier onto active audio device stack; ducks music by -9.5 dB and combat ambient by -13.1 dB during slow motion.
- **Fail-Closed Gate:** If pointer is null, audio mix stack remains untouched. Pop routine is idempotent.
