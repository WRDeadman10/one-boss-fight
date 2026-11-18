# C-1651 Audio/SFX Candidate Matrix: Batch 7/10 (SFX-36..SFX-40)

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2680]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-145 (SFX-36), BT-146 (SFX-37), BT-147 (SFX-38), BT-148 (SFX-39), BT-149 (SFX-40)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directive `[X-2680]`, Antigravity has executed the candidate discovery, in-repo package verification, and acoustic specification for **C-1651 Audio/SFX Batch 7/10 (SFX-36 through SFX-40)**: Combat UI & Player Feedback Audio.

- **Audio Asset Policy:** Strictly repository-internal audio assets only. Zero external downloads, zero engine/asset modifications, zero runtime wiring before Owner selection.
- **Spec-Only & Export Hold:** In accordance with [BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md](BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md) and directive `[X-2680]`, raw WAV export and audition reel compilation for SFX-36..40 are held pending Owner tone preferences. All 15 candidate Sound Cue packages are confirmed present in-tree, sized, and hashed.
- **Native Seam Audit Reconciliation:** In cross-referencing [C1651_SFX_36_40_TRIGGER_AUDIT.md](C1651_SFX_36_40_TRIGGER_AUDIT.md):
  - **SFX-36 & SFX-37 (Targeting De-duplication):** `RPGCameraRig.cpp` continuously updates camera framing and eases yaw toward `LockOnTarget`. Lock acquire and target retarget must trigger exclusively on discrete user input edges, never per-tick camera updates.
  - **SFX-38 & SFX-39 (Loop State Semantics):** Low-stamina panting and critical-health heartbeat require explicit start/stop hysteresis threshold crossing edges, stopping immediately on stamina recovery, health flask consumption, player death, or encounter reset.
  - **SFX-40 (Terminal Defeat Edge):** Player defeat stinger is owned by `GA_PlayerDeath` (distinct from native `RPGBossDeath`); requires a single terminal edge coordinated with combat music ducking.

---

## 2. Event-by-Event Candidate Matrix

### 2.1. SFX-36: Target Lock-On Acquire (BT-145)
- **Combat Context:** Player presses lock-on input (`IA_LockOn`), successfully engaging camera tracking on the boss. Demands an immediate, tactile confirm click.
- **Hook Site:** Lock-on engage input edge / `WBP_LockOn` focus event (distinct from continuous `RPGCameraRig` framing).
- **Candidate Options:**
  - **Option A (Preferred - Crisp Tactile Select Click):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select01`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select01.uasset`
    - Size: 390,791 bytes | SHA-256: `FE5E79EAB660154D6AB6ECF6D5222FDEFD44A0E931E2AAC6E78A86B47801AEEF`
    - Acoustic Profile: Immediate, precise high-frequency click confirming camera target lock.
  - **Option B (Positive Locking Confirm Tone):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Box_Confirm`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Box_Confirm.uasset`
    - Size: 9,920 bytes | SHA-256: `0981899E14F644A38F698A409DE284308438B0DE4205C50F82B93C3527DBCBC7`
    - Acoustic Profile: Fuller, resonant affirmative UI tone indicating successful lock acquisition.
  - **Option C (Subtle High-Register Metallic Chime):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue.uasset`
    - Size: 4,423 bytes | SHA-256: `882D6253B32B3548C39EBBD7B082381D8134AEED8D96EECAA99FCF597CD88839`
    - Acoustic Profile: Tactile metallic snap adding grounded martial flavor to targeting.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.2. SFX-37: Target Lock-On Retarget (BT-146)
- **Combat Context:** Player flicks right stick / inputs target cycle to switch focus points. Requires a subtle directional glide or snap confirming the switch.
- **Hook Site:** Target cycle input edge (not camera yaw interpolation).
- **Candidate Options:**
  - **Option A (Preferred - Smooth Spatial Transition Swoosh):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue.uasset`
    - Size: 4,339 bytes | SHA-256: `AD4430F81A293CC2D411609FC052B14F2C6A38DAFCC2121E5A74C865A0A3B7F0`
    - Acoustic Profile: Soft directional air displacement confirming target retargeting.
  - **Option B (Subtle Pneumatic Retarget Glide):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Hover`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Hover.uasset`
    - Size: 12,866 bytes | SHA-256: `618FB39D6B5BD6FCC6927DE405D42E4677AFDA67E2E4D0E10AF01E5C5BBE567D`
    - Acoustic Profile: Lightweight UI glide audio for rapid retarget cycling.
  - **Option C (Rapid Clean Directional Snap):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue.uasset`
    - Size: 4,423 bytes | SHA-256: `7D02E64C8FDEC3AAE742A64FA9166BF52E1AD23154159EF21EB03337C80274D2`
    - Acoustic Profile: Crisp brief transient marking retarget flick.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.3. SFX-38: Player Low Stamina Panting (BT-147)
- **Combat Context:** Player stamina drops below critical threshold (< 20%), warning player that rolls and blocks are limited. Demands a looped exertion breathing cue.
- **Hook Site:** Stamina threshold crossing edge (< 20%), stopping when stamina > 35% or upon death.
- **Candidate Options:**
  - **Option A (Preferred - Knight Heavy Exertion Panting Loop):**
    - UE Package: `/Game/ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingRun`
    - File: `Content/ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingRun.uasset`
    - Size: 10,818 bytes | SHA-256: `35F5223669648773766284692B4268FE4664E54AE20E76CBF4BFCAE543BBF58E`
    - Acoustic Profile: Natural, rhythmic breath cadence conveying intense physical strain through plate armor.
  - **Option B (Deep Labored Breathing Cycle):**
    - UE Package: `/Game/ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingLowHealth`
    - File: `Content/ParagonGreystone/Audio/Cues/Greystone_Effort_BreathingLowHealth.uasset`
    - Size: 10,873 bytes | SHA-256: `406B4F1433454EF949CBCC95C719E903A8E6E21424ED2B130D1DF6520888858B`
    - Acoustic Profile: Heavier, ragged breath cycle emphasizing severe exhaustion.
  - **Option C (Spectral Exertion Rasp Fallback):**
    - UE Package: `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_BreathingRun`
    - File: `Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_BreathingRun.uasset`
    - Size: 4,362 bytes | SHA-256: `4D81DAB12ED3473ACFBAF9F8F73F3AC513B44293C31F4CEDE5780DDABA653559`
    - Acoustic Profile: Deeper raspy breath bed for darker tonal profile.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.4. SFX-39: Player Critical Health Heartbeat (BT-148)
- **Combat Context:** Player HP drops below 25%, entering critical mortality danger. Requires a rhythmic, muffled low-frequency systolic heartbeat pulse to heighten tension.
- **Hook Site:** Health threshold crossing edge (< 25%), stopping immediately on flask heal (> 25%), defeat, or reset.
- **Candidate Options:**
  - **Option A (Preferred - Muffled Low-Frequency Heartbeat Pulse):**
    - UE Package: `/Game/ParagonGreystone/Audio/Cues/Greystone_Health_Low`
    - File: `Content/ParagonGreystone/Audio/Cues/Greystone_Health_Low.uasset`
    - Size: 8,011 bytes | SHA-256: `8E99E2847D407F4C3EB05101A8EAFA4F92EAF7861AC836B0C34E59D0E0965181`
    - Acoustic Profile: Heavy muffled systolic/diastolic thumping loop heightening mortal danger.
  - **Option B (Dark Resonant Pulse Decay):**
    - UE Package: `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Critical`
    - File: `Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Critical.uasset`
    - Size: 4,340 bytes | SHA-256: `DA44E7E436CB6A56AAE74698C43E9BF6445C823EECCE59E6488BC3D18461425A`
    - Acoustic Profile: Dark cavernous thud with high dynamic headroom.
  - **Option C (Subdued Ominous Pulsing Bed):**
    - UE Package: `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Low`
    - File: `Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Low.uasset`
    - Size: 4,310 bytes | SHA-256: `589303B25145D48600940A866BB40292DB63E53754DABAC7009BA363C8C2719F`
    - Acoustic Profile: Steady rhythmic sub-bass pulse simulating impending death.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.5. SFX-40: Player Defeat Stinger (BT-149)
- **Combat Context:** Player health reaches 0, triggering the death animation and "YOU DIED" state. Demands a somber, definitive defeat stinger marking duel termination.
- **Hook Site:** Terminal `GA_PlayerDeath` trigger (coordinated with combat BGM ducking).
- **Candidate Options:**
  - **Option A (Preferred - Dark Orchestral Defeat Stinger):**
    - UE Package: `/Game/ParagonGreystone/Audio/Cues/Greystone_Status_Defeat`
    - File: `Content/ParagonGreystone/Audio/Cues/Greystone_Status_Defeat.uasset`
    - Size: 8,041 bytes | SHA-256: `8491BFBC8DFBC89BF9163C52430BEDD2E7119C335AB60BA2441D34AD92891B6F`
    - Acoustic Profile: Somber, heavy brass and percussion stinger marking duel loss.
  - **Option B (Finality Collapse & Decay Stinger):**
    - UE Package: `/Game/ParagonGreystone/Audio/Cues/Greystone_Death`
    - File: `Content/ParagonGreystone/Audio/Cues/Greystone_Death.uasset`
    - Size: 13,281 bytes | SHA-256: `981B0110E197B1843FE3861F4EB39C7827BEA66780981AC8E45374D40922B5F2`
    - Acoustic Profile: Subdued collapse with trailing dark resonance.
  - **Option C (Deep Spectral Descent Stinger):**
    - UE Package: `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Status_Defeat`
    - File: `Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Status_Defeat.uasset`
    - Size: 8,165 bytes | SHA-256: `02467CCD3E8725C0654EF6013386B36256E6F521C0227AB5D82398D8E3A0D03E`
    - Acoustic Profile: Haunting spectral descent into silence.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

## 3. Verification & Compliance Checklist

1. **Repository Isolation:** Only project-internal audio assets referenced. Zero external assets downloaded.
2. **Immutability:** Zero `.uasset` packages or config files modified.
3. **Engine Safety:** 0 Unreal Editor instances started. Both C-1155 locks remain untouched and absent.
4. **Git Safety:** 0 git commits, 0 git pushes performed.
5. **Hold Compliance:** In accordance with `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`, zero WAV files were exported and zero audition reels were built; candidates remain spec-only.
6. **Task Board Status:** All five tasks (`BT-145`, `BT-146`, `BT-147`, `BT-148`, `BT-149`) advanced to `review`.
