# SFX Batch 8 Candidate Specification: Combat UI & Player Feedback Audio

**Document Version:** 1.0  
**Authority:** Claude Lead Directives `[C-1197]`, `[C-1229]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** PROPOSED (Spec-Only; Awaiting Owner Audition Selection; No Wiring).  
**Scope:** Tasks `SFX-36` through `SFX-40` (Batch 8: Combat UI & Player Feedback Audio, Priority e) in [`Documentation/Boss/QUEUE_SFX.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md).

---

## 1. Executive Summary & Design Principles

Per directive `[C-1229]`, this document specifies candidate audio assets for **Batch 8 (Combat UI & Feedback Audio)** covering lock-on targeting mechanics, low stamina exhaustion cues, critical health auditory tension, and defeat stingers.

### Discipline Constraints
1. **Repository Assets Only:** 100% of selected candidates exist directly within project content (`AdvancedARPGCombat`, `RealisticSwordSoundEffects`, `ParagonGreystone`, `ParagonSevarog`). Zero external downloads.
2. **Opt-In / No Runtime Wiring:** Strictly spec-only. No blueprints, anim notifies, C++ triggers, or sound cues are wired or modified until the project owner makes selections from audition reels.
3. **Auditory Clarity & Pacing:** UI and feedback cues must provide immediate tactile feedback without cluttering combat telegraphs or masking boss attack whooshes.

---

## 2. Candidate Selection Matrix: Combat UI & Player Feedback Audio (Batch 8)

| Task ID | Gameplay Event | Target Trigger / Hook Site | Candidate Options (In Repo) | Asset Path | Dynamic Character & Acoustic Profile |
|---|---|---|---|---|---|
| **SFX-36** | **Target Lock-On Acquire** | Lock-on engage event (`IA_LockOn`) / `WBP_LockOn` focus | **Option A (Preferred):** Crisp Tactile Select Click<br>**Option B:** Positive Locking Confirm Tone<br>**Option C:** Subtle High-Register Metallic Chime | `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select01`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Box_Confirm`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue` | Immediate, precise high-frequency click confirming camera target lock<br>Fuller, resonant affirmative UI tone indicating successful lock acquisition<br>Tactile metallic snap adding grounded martial flavor to targeting |
| **SFX-37** | **Target Lock-On Retarget** | Target switch input / cycle target event | **Option A (Preferred):** Smooth Spatial Transition Swoosh<br>**Option B:** Subtle Pneumatic Retarget Glide<br>**Option C:** Rapid Clean Directional Snap | `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Hover`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue` | Soft directional air displacement confirming target retargeting<br>Lightweight UI glide audio for rapid retarget cycling<br>Crisp brief transient marking retarget flick |
| **SFX-38** | **Player Low Stamina Panting** | Player stamina < 20% / HUD stamina exhaustion trigger | **Option A (Preferred):** Knight Heavy Exertion Panting Loop<br>**Option B:** Deep Labored Breathing Cycle<br>**Option C:** Spectral Exertion Rasp Fallback | `/Game/ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingRun`<br>`/Game/ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingLowHealth`<br>`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_BreathingRun` | Natural, rhythmic breath cadence conveying intense physical strain<br>Heavier, ragged breath cycle emphasizing severe exhaustion<br>Deeper raspy breath bed for darker tonal profile |
| **SFX-39** | **Player Critical Health Heartbeat** | Player health < 25% / low health post-process vignette | **Option A (Preferred):** Muffled Low-Frequency Heartbeat Pulse<br>**Option B:** Dark Resonant Pulse Decay<br>**Option C:** Subdued Ominous Pulsing Bed | `/Game/ParagonGreystone/Audio/Cues/Greystone_Health_Low`<br>`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Critical`<br>`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Low` | Heavy muffled systolic/diastolic thumping loop heightening tension<br>Dark cavernous thud with high dynamic headroom<br>Steady rhythmic sub-bass pulse simulating impending death |
| **SFX-40** | **Player Defeat Stinger** | Player death ability trigger (`GA_PlayerDeath`) | **Option A (Preferred):** Dark Orchestral Defeat Stinger<br>**Option B:** Finality Collapse & Decay Stinger<br>**Option C:** Deep Spectral Descent Stinger | `/Game/ParagonGreystone/Audio/Cues/Greystone_Status_Defeat`<br>`/Game/ParagonGreystone/Audio/Cues/Greystone_Death`<br>`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Status_Defeat` | Somber, heavy brass and percussion stinger marking duel loss<br>Subdued collapse with trailing dark resonance<br>Hollow spectral fall stinger emphasizing mortality |

---

## 3. Acoustic Profiles & Gain Staging Recommendations

1. **Lock-On Cues (`SFX-36`, `SFX-37`):**
   - Routing: `SC_UI` / UI SoundClass.
   - Volume: \(-6.0\text{ dB}\) to \(-8.0\text{ dB}\) relative to Master.
   - Spatialization: 2D non-diegetic (centered in player stereo space).
   - Behavior: Bounded by concurrency limit of 1 instance with instant voice stealing to prevent audio buildup during rapid lock switching.

2. **Low Stamina & Critical Health Loops (`SFX-38`, `SFX-39`):**
   - Routing: `SC_Foley` / Player Audio Submix with ducking send to ambient bed.
   - Volume: \(-12.0\text{ dB}\) base, dynamically ducking background music and ambient loops by \(-3.0\text{ dB}\) when active.
   - Fade In / Out: Smooth \(0.5\text{ s}\) crossfade on threshold entry/exit to avoid sudden audio pops.

3. **Player Defeat Stinger (`SFX-40`):**
   - Routing: `SC_Music` / Combat Event Submix.
   - Volume: \(0.0\text{ dB}\) (full prominence), ducking gameplay combat SFX by \(-12.0\text{ dB}\) over \(1.0\text{ s}\) to cleanly signal encounter end.

---

## 4. Disk Verification & Asset Integrity

All 15 candidate assets verified present on local disk under `Content/`:
- `AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select01.uasset` (PASS)
- `AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Box_Confirm.uasset` (PASS)
- `RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue.uasset` (PASS)
- `RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue.uasset` (PASS)
- `AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Hover.uasset` (PASS)
- `RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue.uasset` (PASS)
- `ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingRun.uasset` (PASS)
- `ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingLowHealth.uasset` (PASS)
- `ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_BreathingRun.uasset` (PASS)
- `ParagonGreystone/Audio/Cues/Greystone_Health_Low.uasset` (PASS)
- `ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Critical.uasset` (PASS)
- `ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Low.uasset` (PASS)
- `ParagonGreystone/Audio/Cues/Greystone_Status_Defeat.uasset` (PASS)
- `ParagonGreystone/Audio/Cues/Greystone_Death.uasset` (PASS)
- `ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Status_Defeat.uasset` (PASS)
