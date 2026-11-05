# Tier 2 Art & Visual Polish Owner Brief (Queue V Task V-A006)

**Target Duel:** The Ember Warden (`BP_ExampleGreatSwordBoss` re-skinned on `SK_CombatMannequin`) vs Player (`BP_CombatPlayerCharacter` on `SK_CombatMannequin`) in `L_SevarogArena`.
**Status:** Prepared for Owner Decision per Lead [C-903], [C-917], and Queue V rules.
**Constraint:** Binding project rule: *Look-changing asset edits (lights, materials, level, Tier 2 art) need the owner's yes; cvar/scalability experiments and DLSS are approved.*

---

## 1. Executive Summary & Goals

With **Tier 1 Art Assets** (`NS_Boss_ShockwaveRing`, `NS_Combat_ParrySpark`, `AM_Boss01_A2`) delivered and wired behind the Development preview switch `rpg.Art.Tier1` (commit `6637ea8`, BUILD-228), Tier 2 focuses on **combat readability, visceral impact, and duel atmosphere**:

1. **Parry Slow-Motion Post-Process (`PPM_ParryDistortion`):**
   - Pairs with Codex's live-verified **F1 parry slow motion** (world dilation drops to 0.30 for 0.35 s on perfect parry).
   - Adds a sharp, high-impact radial chromatic aberration and desaturation shockwave centered on screen, snapping back cleanly as world time normalizes.
2. **Phase Two Boss Aura & Blade Ignition (`NS_Boss_PhaseTwoAura`):**
   - Triggers at **60% Boss HP** alongside the phase 2 transition roar.
   - Surrounds the Warden's mantle and shoulders in smoldering ember motes and ignites the greatsword blade edge with an emissive heat trail.
3. **Boss Parry Recoil Animation (`AM_Boss01_ParryRecoil`):**
   - Replaces the current static hitstop freeze with a 0.60 s physics-grounded blade deflection and minor stagger, making weapon parries feel physically rewarding.

---

## 2. Feature Specifications & Mockups

### Feature 1: Parry Slow-Motion Post-Process (`PPM_ParryDistortion`)

```
[Normal Time Dilation 1.0] -> [Perfect Parry Contact] -> [Dilation 0.30 (0.35 s)] -> [Restore 1.0]
                                         |
                                         v
                            [MPC_CombatFeedback Pulse]
                            - Chromatic Aberration: 0.0 -> 1.8 -> 0.0
                            - Color Desaturation: 0.0 -> 0.4 -> 0.0
                            - Radial Vignette Pulse: 0.0 -> 0.35 -> 0.0
```

- **Asset Path:** `/Game/OneBossFight/Effects/PPM_ParryDistortion`
- **Driving Interface:** `MaterialParameterCollection` `/Game/OneBossFight/Data/MPC_CombatFeedback`
  - Scalar Parameter `ParryPulse`: Driven by a lightweight curve in C++ or Blueprint timeline during `URPGLegend` slow-motion scope.
- **Shader Complexity:** 1 Texture lookup (SceneColor with UV offset based on ScreenPosition from center). Approximate cost: < 0.08 ms on RTX 2060 Super / 3060.
- **Parity & Safe Default:** Defaults to 0.0 (no visual change). If unconfigured or in Shipping without data assignment, post-process material is bypassed entirely.

---

### Feature 2: Phase Two Embers & Blade Ignition (`NS_Boss_PhaseTwoAura`)

- **Asset Path:** `/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura`
- **Visual Structure:**
  - **Emitter 1 (Torso Embers):** GPU sprite particle system emitting low-density rising embers (warm amber `RGB(2.5, 0.8, 0.1)`) attached to socket `spine_03`.
  - **Emitter 2 (Blade Flame Ribbon):** Dual-socket ribbon trail along `SM_Boss01_Greatsword` from socket `Weapon_Base` to `Weapon_Tip`.
  - **Material Ramp:** Emissive scalar parameter `PhaseTwoGlow` ramped from 1.0 to 3.5 on `M_Boss01_Master`.
- **Activation Hook:** Wired to `LogRPGPhases` phase-transition broadcast (`InitialBossPhase` / 60% HP threshold).
- **Parity & Safe Default:** Soft reference on `URPGBossLook` or phase subsystem defaulting to `nullptr`. Preview toggleable via `rpg.Art.Tier2` switch.

---

### Feature 3: Boss Parry Recoil Animation (`AM_Boss01_ParryRecoil`)

- **Current Behavior:** Boss freezes in hitstop during parry window, then recovers or queues next card.
- **Proposed Behavior:**
  - 0.60 s animation on `SK_CombatMannequin` skeleton:
    - Frames 0–8 (0.13 s): Heavy blade rebound backwards and upwards, boss torso recoils back 15 cm.
    - Frames 9–22 (0.23 s): Stumble foot-step recovery, shifting weight onto back foot.
    - Frames 23–36 (0.24 s): Smooth blend-out back into Greatsword Combat Idle.
  - Montage metadata: Root motion disabled, upper body / full body slot assignment matching pack standards.
- **Parity & Safe Default:** Optional montage reference on `URPGBossLowSweep` / `URPGAttackTracker` defaulting to empty (`nullptr`). Current hitstop behavior remains 100% untouched until authored.

---

## 3. Performance & Shipping Impact Assessment

| Asset / Feature | Memory Impact | Render Thread Cost | GPU Pass Time | Shipping ABI Risk |
|---|---|---|---|---|
| `PPM_ParryDistortion` | ~12 KB (Material instance) | 0.0 ms | +0.06 to +0.08 ms (during 0.35 s impulse only) | Zero (Post-process volume array) |
| `MPC_CombatFeedback` | ~4 KB | 0.0 ms | 0.0 ms | Zero (Standard UObject) |
| `NS_Boss_PhaseTwoAura` | ~180 KB | 0.01 ms | +0.12 to +0.18 ms (GPU particles + ribbon) | Zero (Soft reference) |
| `AM_Boss01_ParryRecoil` | ~45 KB (AnimSequence + Montage) | 0.0 ms | 0.0 ms | Zero (Soft montage reference) |

---

## 4. Owner Decision Request

Owner approval is requested on the following options:

* **[Option A] FULL APPROVAL (Recommended):** Approve creation and headless import of all three Tier 2 art assets (`PPM_ParryDistortion`, `NS_Boss_PhaseTwoAura`, `AM_Boss01_ParryRecoil`), wired behind opt-in Development switches (`rpg.Art.Tier2`) with empty defaults preserving D5 parity.
* **[Option B] PARRY VISUALS ONLY:** Approve `PPM_ParryDistortion` and `MPC_CombatFeedback` to finalize parry slow-motion feedback; defer phase 2 boss aura and recoil animation.
* **[Option C] DEFER TIER 2:** Retain current visual baseline (Tier 1 only) until performance optimization (Queue V Lane C Round 6/7) hits the 60 FPS target.
