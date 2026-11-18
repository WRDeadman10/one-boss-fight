# C-1651 Audio/SFX Candidate Matrix: Batch 5/10 (SFX-26..SFX-30)

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2677]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-132 (SFX-26), BT-133 (SFX-27), BT-134 (SFX-28), BT-135 (SFX-29), BT-136 (SFX-30)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directive `[X-2677]`, Antigravity has executed the candidate discovery, in-repo package verification, and acoustic specification for **C-1651 Audio/SFX Batch 5/10 (SFX-26 through SFX-30)**: Posture, Stagger & Execution Audio.

- **Audio Asset Policy:** Strictly repository-internal audio assets only. Zero external downloads, zero engine/asset modifications, zero runtime wiring before Owner selection.
- **Spec-Only & Export Hold:** In accordance with [BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md](BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md) and directive `[X-2677]`, raw WAV export and audition reel compilation for SFX-26..30 are held pending Owner tone preferences. All 15 candidate Sound Cue packages are confirmed present in-tree, sized, and hashed.
- **Character Voice Safeguards:**
  - **Player Voice Exclusion (`[C-1212]`):** All Player Stance Break candidates (`SFX-30`) are strictly non-vocal foley (shield blowouts, plate deformation, edge blow-throughs) to keep audio completely decoupling-safe while player model fit tests remain open.
  - **Boss Identity Separation (`[C-1175]` / `[C-1208]`):** Ember Warden stagger vocalizations (`SFX-27`) utilize monstrous/titan audio from Grux and Steel to maintain acoustic separation from future Sevarog encounters.

---

## 2. Event-by-Event Candidate Matrix

### 2.1. SFX-26: Boss Posture Damage Threshold Warning (BT-132)
- **Combat Context:** Boss posture drops below critical threshold (< 25% remaining), warning the player that stance break is imminent. Needs a subtle structural groaning or sub-pulsing acoustic indicator.
- **Hook Site:** Posture evaluation hook when Boss Posture < 25%.
- **Candidate Options:**
  - **Option A (Preferred - Metallic Structural Stress Groan):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_2_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_2_Cue.uasset`
    - Size: 4,463 bytes | SHA-256: `9A581FA0D8C99300A65AE437257FBA2D7DE038639009BF4DC104990BF8B8F5EA`
    - Acoustic Profile: Searing structural blade/armor creak indicating imminent guard collapse.
  - **Option B (Deep Warning Cosmic Sub-Pulse):**
    - UE Package: `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift02`
    - File: `Content/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift02.uasset`
    - Size: 394,251 bytes | SHA-256: `D6A25AE3E46156EFC80EA6A58ADAA4A12325DA746E8A5C0A1553D0DA72A51396`
    - Acoustic Profile: Subtle sub-bass warning throb marking critical posture vulnerability.
  - **Option C (Pressurized Steam / Stress Hiss):**
    - UE Package: `/Game/StarterContent/Audio/Steam01_Cue`
    - File: `Content/StarterContent/Audio/Steam01_Cue.uasset`
    - Size: 4,285 bytes | SHA-256: `C43FB733EBFC395AF98CE820DE46FED7D2B3F2A42AD03F55C8CF8E12D1BD417F`
    - Acoustic Profile: Escaping thermal steam hiss communicating internal structural failure.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.2. SFX-27: Boss Heavy Stagger Breathing / Groan (BT-133)
- **Combat Context:** Boss posture completely broken, locked in a 2.5s vulnerable stagger animation. Demands an exhausted, ragged vocal loop communicating temporary helplessness.
- **Hook Site:** Looped audio during active vulnerable stagger window (`URPGBossStagger`).
- **Candidate Options:**
  - **Option A (Preferred - Grux Exhausted Guttural Breathing):**
    - UE Package: `/Game/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundWaves/Grux_Effort_BreathingLowHealth_01`
    - File: `Content/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundWaves/Grux_Effort_BreathingLowHealth_01.uasset`
    - Size: 1,069,249 bytes | SHA-256: `7DBBF42E8F7C7F5277FC52A6D7BB13EC80121716876DCEA4D53FB9BCB1BCA1A7`
    - Acoustic Profile: Deep, ragged monstrous breathing loop; keeps Ember Warden audibly distinct from Sevarog.
  - **Option B (Grux Heavy Pain Grunt):**
    - UE Package: `/Game/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundWaves/Grux_Effort_PainHeavy_01`
    - File: `Content/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundWaves/Grux_Effort_PainHeavy_01.uasset`
    - Size: 279,701 bytes | SHA-256: `AAA2BCA18AE36ED503225A308E2F6A4F715E5130128F3771F4A1227362D891BB`
    - Acoustic Profile: Heavy guttural pain groan on posture break collapse.
  - **Option C (Steel Armored Exertion Strain):**
    - UE Package: `/Game/ParagonSteel/Audio/Wavs/Steel_Effort_PainHeavy_010`
    - File: `Content/ParagonSteel/Audio/Wavs/Steel_Effort_PainHeavy_010.uasset`
    - Size: 379,047 bytes | SHA-256: `C938E11765E62CCCDF84FB949D0FA6424F0C66BA985A22167245EDD76931ACEE`
    - Acoustic Profile: Armored titan heavy breath strain through plate helm.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.3. SFX-28: Critical Execution / Riposte Impale (BT-134)
- **Combat Context:** Player presses attack on staggered boss, triggering a devastating high-damage visceral execution strike. Demands an enormous, brutal metal-and-body impale crunch.
- **Hook Site:** Execution strike contact hit frame / Riposte hit registration.
- **Candidate Options:**
  - **Option A (Preferred - Massive Blade Cleave & Impale):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpactLarge1`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpactLarge1.uasset`
    - Size: 120,857 bytes | SHA-256: `3DC94BCAC601CC6806CC93A4B30A15A2FA5830B33D03D921B6823F885264FC57`
    - Acoustic Profile: Enormous blade impale shock with deep metal crunch; maximum kinetic satisfaction.
  - **Option B (Deep Armor Piercing Strike):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_12_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_12_Cue.uasset`
    - Size: 4,386 bytes | SHA-256: `C6E6CA889DC8CDCAE58ADA1180170C811529AFC63E8EEDA27A984D3914080530`
    - Acoustic Profile: Violent piercing strike cutting through boss plate into inner core.
  - **Option C (Catastrophic Armor Rupture):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpactLarge4`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpactLarge4.uasset`
    - Size: 120,124 bytes | SHA-256: `94DA6FC790772811CAC65F8928DD73BFDF22CBCE88D6F6F0A9989048AA20AE66`
    - Acoustic Profile: Heavy brutal shock impact with trailing sub-bass resonance.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.4. SFX-29: Boss Stagger Recovery Stance Re-assertion (BT-135)
- **Combat Context:** Boss 2.5s stagger window concludes; boss regains poise, re-settles stance, and readies weapons. Warns player that vulnerability has terminated.
- **Hook Site:** `URPGBossStagger::EndStagger` recovery frame.
- **Candidate Options:**
  - **Option A (Preferred - Metallic Snap & Blade Re-assertion):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Unsheathe/Sword_Unsheathe_3_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Unsheathe/Sword_Unsheathe_3_Cue.uasset`
    - Size: 4,411 bytes | SHA-256: `3B0BF1E27DA1C389BFA748C01347D978A20A678CDCB326E2532A49AAE526E31B`
    - Acoustic Profile: Sharp metallic blade-lock notifying player vulnerability window is closed.
  - **Option B (Heavy Arena Concrete Ground Stomp):**
    - UE Package: `/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue`
    - File: `Content/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue.uasset`
    - Size: 9,983 bytes | SHA-256: `51C28F5B35F13304FE3BB046233638C70CD346CF6491EFFC14838E4A02BBDCF0`
    - Acoustic Profile: Massive footfall stomp shaking arena floor on recovery.
  - **Option C (Concussive Poise Re-settle):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.uasset`
    - Size: 10,806 bytes | SHA-256: `CB1797D251938322E0CF60806E6F9B9B50DCA094B90EBCC8B326B3085742D534`
    - Acoustic Profile: Dense sub-bass guardian impact re-grounding boss poise.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.5. SFX-30: Player Stance Break / Guard Break (BT-136)
- **Combat Context:** Player stamina completely depleted while blocking, causing shield blowout, guard break stagger, and temporary vulnerability. Strictly non-vocal foley per `[C-1212]`.
- **Hook Site:** Player posture exhaustion / Shield blowout event.
- **Candidate Options:**
  - **Option A (Preferred - Massive Shield Deflection Blowout):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact4`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact4.uasset`
    - Size: 120,276 bytes | SHA-256: `534DD9287A163E4372DBEFC828B09CD25644049BD694B1D697C79766CF0E21D7`
    - Acoustic Profile: Violent iron shield blowout and recoil reverberation; communicates guard failure.
  - **Option B (Violent Shield Collapse Shock):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact3`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact3.uasset`
    - Size: 126,080 bytes | SHA-256: `F071E8AE33EF9B885295103CDFC69E5E418E7F43051BECD7B61DEE302791BD29`
    - Acoustic Profile: High-energy shield deflection shock indicating zero stamina.
  - **Option C (Heavy Armor Blade Blow-Through):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_11_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_11_Cue.uasset`
    - Size: 4,386 bytes | SHA-256: `AA027F19EC6FC30FA6BB4A413D242ACB4F8B4FE59D08260DB0018DD9DF028B7F`
    - Acoustic Profile: Aggressive steel blow-through pushing guard aside *(strictly non-vocal foley)*.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

## 3. Verification & Compliance Checklist

1. **Repository Isolation:** Only project-internal audio assets referenced. Zero external assets downloaded.
2. **Immutability:** Zero `.uasset` packages or config files modified.
3. **Engine Safety:** 0 Unreal Editor instances started. Both C-1155 locks remain untouched and absent.
4. **Git Safety:** 0 git commits, 0 git pushes performed.
5. **Hold Compliance:** In accordance with `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`, zero WAV files were exported and zero audition reels were built; candidates remain spec-only.
6. **Task Board Status:** All five tasks (`BT-132`, `BT-133`, `BT-134`, `BT-135`, `BT-136`) advanced to `review`.
