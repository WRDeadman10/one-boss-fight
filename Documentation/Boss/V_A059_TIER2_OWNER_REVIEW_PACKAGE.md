# V-A059: Tier 2 Presentation Suite — Owner Review Package & Decision Guide

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-A059`, `TIER2_ART_OWNER_BRIEF.md`, `V_A056..V_A058`, `[C-926]`, `[C-928]`
**Sources:** Documentation/Boss/V_A056_TIER2_INTEGRATION_CHECK.md, Source/OneBossFight/Boss/RPGSevarogDirector.h

---

## 1. Overview for the Project Owner

Per project mandate, **no look-changing art assets are applied to the production baseline without explicit Owner approval**. 

All Tier 2 enhancements have been engineered with strict **zero-drift fallback parity**: all C++ properties default to null, all new assets compile out of Shipping builds, and preview switches allow you to inspect the enhanced visuals side-by-side against the baseline with a single toggle.

This review package provides everything needed to evaluate, test, and approve or reject each Tier 2 presentation asset.

---

## 2. The 5 Tier 2 Presentation Enhancements

| Asset / Feature | Description | Baseline (Default Off) | Tier 2 Preview Enabled | Estimated GPU Cost |
|---|---|---|---|:---:|
| **1. Authored A2 Slam (`AM_Boss01_A2`)** | Full 3.134 s composite montage (crouch windup, 1.17 s apex hold, earth-shattering slam). | Pack ability `GS_ChargedAttack_Montage` with dynamic rate dilation. | Authored animation at natural 1.00 rate; matches reference timings within 7 ms. | **0.00 ms** (Animation only) |
| **2. Phase 2 Boss Aura (`NS_Boss_PhaseTwoAura`)** | Ethereal dark-fire ribbon and ember particles trailing from Sevarog's shoulders during Phase 2 (<= 60% HP). | Armor unchanged in Phase 2; standard material glow only. | Dynamic dark flame ribbons and ash motes emphasize boss enrage. | **< 0.05 ms** (GPU compute, fixed bounds) |
| **3. Parry Radial Distortion (`PPM_ParryDistortion`)** | Brief screen-space shockwave distortion pulse centered on the weapon clash during parry slow motion. | Pure time dilation; standard flat post-process. | Cinematic shockwave ripple accentuates impact weight. | **< 0.03 ms** (Procedural screen UV offset) |
| **4. Boss Parry Recoil (`AM_Boss01_ParryRecoil`)** | 0.600 s physical stagger animation where boss flinches backward, exposing chest for player riposte. | Boss remains in standard pack hit-reaction flinch. | Visceral physical reaction; scythe deflected wide right. | **0.00 ms** (Animation only) |
| **5. Parry Audio Ducking (`Mix_ParrySlowMo`)** | Dynamic sound mix modifier that ducks music by -9.5 dB and room tone by -13.1 dB during parry slow-mo. | Music and ambience play at flat volume during slow-motion. | Muffled "underwater" sound design focuses attention on the blade clash. | **0.00 ms** (CPU audio mix) |

---

## 3. How to Test and Toggle Live

### Option A: In the Unreal Editor (PIE)
1. Open `L_SevarogArena` in the Unreal Editor.
2. Press **`~`** (tilde) to open the console and enter:
   ```text
   rpg.Art.Tier2 1
   rpg.AttackTracker.A2PreviewClip 1
   ```
3. Press **Play in Editor (PIE)**.
4. Execute parries and trigger Phase 2 to observe all 5 enhancements.
5. To revert to baseline at any moment, enter:
   ```text
   rpg.Art.Tier2 0
   rpg.AttackTracker.A2PreviewClip 0
   ```

### Option B: Standalone Development Launch
Launch the game with command-line arguments:
```powershell
powershell -ExecutionPolicy Bypass -File Scripts/PlayDevBuild.ps1 -ExecCmds="rpg.Art.Tier2 1; rpg.AttackTracker.A2PreviewClip 1"
```

---

## 4. Owner Decision & Sign-Off Matrix

Please indicate your decision for each feature when ready:

```markdown
- [ ] Feature 1: Authored A2 Slam Montage (`AM_Boss01_A2`)
      [ ] APPROVED for production wiring
      [ ] REVISE (specify notes)
      [ ] REJECT (retain pack ability)

- [ ] Feature 2: Phase 2 Dark-Fire Aura (`NS_Boss_PhaseTwoAura`)
      [ ] APPROVED for import & assignment
      [ ] REVISE (specify particle density/color)
      [ ] REJECT (no aura)

- [ ] Feature 3: Parry Screen Distortion (`PPM_ParryDistortion`)
      [ ] APPROVED for post-process assignment
      [ ] REVISE (specify ripple radius/strength)
      [ ] REJECT (retain flat slow-mo)

- [ ] Feature 4: Boss Parry Recoil Stagger (`AM_Boss01_ParryRecoil`)
      [ ] APPROVED for animation import
      [ ] REVISE (specify flinch severity)
      [ ] REJECT (retain standard hit reaction)

- [ ] Feature 5: Parry Audio Ducking SoundMix (`Mix_ParrySlowMo`)
      [ ] APPROVED for assignment
      [ ] REVISE (specify dB attenuation)
      [ ] REJECT (no audio ducking)
```
