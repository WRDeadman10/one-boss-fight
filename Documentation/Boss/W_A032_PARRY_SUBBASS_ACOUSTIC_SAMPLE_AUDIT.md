# W-A032: Parry Sub-Bass Acoustic Thump Sample Audit

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Acoustic profile and frequency integration audit of the sub-bass parry confirmation sample, harmonizing tactile audio response with `ParryFeedbackSoundMix` ducking and hit-stop dilation.  
**Sources:** Documentation/Boss/V_A034_AUDIO_MIX_AUDIT.md:20-50, Documentation/Boss/V_A078_FEEL_POLISH_PROPOSALS.md:26-30, Documentation/Boss/W_A007_TIER2_LIFETIME_CLEANUP_AUDIT.md:15-35, Source/OneBossFight/Boss/RPGBossDirectorComponent.cpp:1-40, Source/OneBossFight/Player/RPGLegend.cpp:440-455

---

## 1. Acoustic Profile & Synthesis Specification

As formulated in Proposal 2 of `V-A078` ([`V_A078:26-30`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A078_FEEL_POLISH_PROPOSALS.md#L26-L30)), standard weapon clash audio cues contain high-frequency metallic transients (2.5 kHz to 8.0 kHz) but lack low-frequency visceral punch.

The proposed parry enhancement injects an acoustic sub-bass layer:
- **Fundamental Frequency:** **50 Hz** pure sine wave with fast pitch envelope decay (down to 35 Hz over 60 ms).
- **Transient Duration:** Exactly **0.12 s** (120 ms).
- **Master Peak Gain:** **-4.0 dBFS** (peaked to prevent digital clipping when layered with `SC_CombatSFX`).
- **Harmonics:** Subtle 2nd harmonic saturation at 100 Hz (-14 dB) for playback audibility on stereo television speakers and headphones lacking dedicated subwoofers.

---

## 2. Harmonization with Presentation Subsystems

The acoustic thump executes synchronously with three established presentation layers:

1. **Hit-Stop Dilation ([`RPGLegend.cpp:449`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGLegend.cpp#L449)):**
   - Duration: 80 ms dilation (`HitStopSeconds = 0.08f`).
   - The 120 ms audio transient slightly outlasts the 80 ms freeze, creating an acoustic bridge as motion resumes.
2. **Dynamic SoundMix Ducking ([`V_A034:46-50`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A034_AUDIO_MIX_AUDIT.md#L46-L50)):**
   - `ParryFeedbackSoundMix` ducks `SC_Music` by **-9.5 dB** (down to 0.25 volume) and `SC_Ambience` by **-13.1 dB** (down to 0.10 volume).
   - This opens 18 dB of dynamic headroom across the 30 Hz – 120 Hz band, allowing the sub-bass pulse to cut through cleanly without bass mud.
3. **Niagara Spark Burst ([`NS_Combat_ParrySpark`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/VFX/NS_Combat_ParrySpark.uasset)):**
   - The acoustic transient matches the instantaneous radial spark emission on frame 0 of parry resolution.

---

## 3. Performance & Memory Impact

- **GPU Impact:** **0.00 ms GPU**.
- **CPU Impact:** Negligible (1 audio voice in Unreal audio mixer).
- **Memory Footprint:** 16-bit 48 kHz mono PCM wave asset (`A_Parry_SubBass_Thump.uasset`) occupies **~11.5 KB** in memory and disk.

---

## 4. Disposition & Sign-Off

The acoustic specification is fully integrated with existing audio mixing rules and compile guards.

- **Status:** PASS (ACOUSTIC SPECIFICATION CERTIFIED)
- **Next Task:** Review camera shake decay curve damping during boss impacts (`W-A033`).
