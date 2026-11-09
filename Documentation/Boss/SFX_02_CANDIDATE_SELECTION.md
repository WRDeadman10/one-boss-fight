# SFX-02: Audio Candidate Selection & Sound Profiles

**Document Version:** 1.0  
**Authority:** Project Owner Order & Claude Directive `[C-1169]`  
**Owner:** Antigravity (`Art/Review/Audit`)  
**Scope:** 1–3 repository-native candidate sound cues per top-priority gap with design rationale, duration, volume/pitch profiles, and exact asset paths.

---

## 1. Candidate Selection Matrix

| Gap ID | Gameplay Event | Target Feel & Timing | Candidate Options (In Repo) | Asset Path | Duration / Profile |
|---|---|---|---|---|---|
| **GAP-01** | **Player Parry Success** | Sharp, immediate high-resonance metal deflection clash coinciding with the 0.2s hit-stop / camera pulse. | **Option A (Preferred): Fast Deflect Clash**<br>Option B: Short Blade Ring<br>Option C: Buckler Clatter | `/Game/RealisticSwordSoundEffects/Sword_Sharpening_Fast_Speed_Cue`<br>`/Game/RealisticSwordSoundEffects/Sword_Attack_Short_1_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact4` | ~0.35s, high pitch (1.1x)<br>~0.25s, sharp transient<br>~0.30s, mid-heavy |
| **GAP-02** | **Boss Parry Recoil** | Heavy physical stagger and spectral breath intake as Sevarog stumbles back during the 0.600s `AM_Boss01_ParryRecoil`. | **Option A (Preferred): Wraith Effort Block**<br>Option B: Heavy Pain Stumble<br>Option C: Frustrated Growl | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Block`<br>`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_PainHeavy`<br>`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Frustration` | ~0.55s, deep vocal + whoosh<br>~0.60s, heavy guttural gasp<br>~0.50s, snarling growl |
| **GAP-03** | **Phase 2 Aura Ignite** | Menacing supernatural explosion / dark flame eruption burst that syncs with `NS_Boss_PhaseTwoAura` expanding to $\pm 175\text{ cm}$. | **Option A (Preferred): Dark Energy Burst**<br>Option B: Infernal Concussion<br>Option C: Shockwave Snap | `/Game/Vefects/Easy_Shockwaves_VFX/Audio/SFX_Vefects_Shockwave_04_1s_Cue`<br>`/Game/StarterContent/Audio/Explosion_Cue`<br>`/Game/Vefects/Easy_Shockwaves_VFX/Audio/SFX_Vefects_Shockwave_01_1s_Cue` | ~1.00s, sub-bass + fiery tail<br>~1.20s, low concussion<br>~0.90s, high punch |
| **GAP-04** | **Player Backstep** | Quick, crisp air displacement with subtle fabric/armor rustle as Greystone hops back with i-frames. | **Option A (Preferred): Swift Evasion Whoosh**<br>Option B: Whip Whoosh<br>Option C: Scabbard Slip | `/Game/RealisticSwordSoundEffects/Swoosh_1_Cue`<br>`/Game/RealisticSwordSoundEffects/Swoosh_3_Cue`<br>`/Game/RealisticSwordSoundEffects/Sword_Unsheathe_1_Cue` | ~0.22s, low wind transient<br>~0.18s, high air cut<br>~0.30s, metallic friction |
| **GAP-05** | **Boss Stance Break** | Souls-style resounding posture rupture / armor-cracking glass/stone shatter when poise hits 0. | **Option A (Preferred): Rubble & Poise Collapse**<br>Option B: Iron Guardian Clatter<br>Option C: Disorientation Drone | `/Game/StarterContent/Audio/Collapse_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue`<br>`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_ProfileDizzy_010` | ~1.10s, deep shattering crack<br>~0.85s, massive bell chime<br>~1.20s, ringing pitch |
| **GAP-06** | **Boss Heavy Swings (Mid01 / Sprint)** | Deep, heavy cutting drag distinguishing heavy boss momentum from player light swings. | **Option A (Preferred): Heavy Blade Cleave**<br>Option B: Blunt Weight Whoosh | `/Game/RealisticSwordSoundEffects/Sword_Attack_1_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Hammer_Swing_Cue` | ~0.45s, broad blade drag<br>~0.50s, heavy bass thrum |
| **GAP-07** | **Boss Spectral Movement** | Subtle ethereal glide whisper replacing standard boot footsteps. | **Option A (Preferred): Spectral Robe Whisper**<br>Option B: Low Void Draft | `/Game/StarterContent/Audio/Smoke01_Cue`<br>`/Game/StarterContent/Audio/Starter_Wind05` | Looping / notify-driven, soft<br>Looping ambient bed |

---

## 2. Design Rationale & Mixing Principles

1. **Parry Feedback Hierarchy:**
   - On a successful parry, the game triggers a 0.20s hit-stop, camera pulse, and tier-1/tier-2 visual flash. Audio MUST lead this moment with `Sword_Sharpening_Fast_Speed_Cue` (Option A) at 1.0 volume, followed immediately by Sevarog's staggered vocal `Sevarog_Effort_Block` (Option A) at 0.85 volume. This gives instant, unmistakable tactile satisfaction.
2. **Phase 2 Elevation:**
   - The transition roar (`Sevarog_Ability_Ultimate_Enemy`) provides vocal aggression; layering `SFX_Vefects_Shockwave_04_1s_Cue` underneath injects the explosive physical impact of dark fire bursting from his core.
3. **Opt-In Safety:**
   - Every candidate is designed as an optional data field on existing components (`URPGPlayerParry`, `URPGTier2BossPresentation`, `URPGBossStagger`) defaulting to `nullptr` (silence) until approved by Owner.
