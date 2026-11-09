# SFX Batch 6: Posture, Stagger & Execution Audio Candidate Specification

**Document Version:** 1.0  
**Authority:** Claude Lead Directives `[C-1197]`, `[C-1211]`, `[C-1212]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** PROPOSED (Spec-Only; Awaiting Owner Audition Selection; No Wiring).  
**Scope:** Tasks SFX-26 through SFX-30 in [`Documentation/Boss/QUEUE_SFX.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md).

---

## 1. Candidate Selection Matrix

| Task ID | Gameplay Event | Anim Montage / Hook Site | Candidate Options (In Repo) | Asset Path | Dynamic Character & Acoustic Profile |
|---|---|---|---|---|---|
| **SFX-26** | **Boss Posture Damage Threshold Warning** | Subdued warning cue when<br>Boss Posture < 25% | **Option A (Preferred):** Metallic Structural Stress Groan<br>**Option B:** Deep Warning Cosmic Sub-Pulse<br>**Option C:** Pressurized Steam/Stress Hiss | `/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_2_Cue`<br>`/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift02`<br>`/Game/StarterContent/Audio/Steam01_Cue` | Searing structural blade/armor creak indicating imminent guard collapse<br>Subtle sub-bass warning throb marking critical posture vulnerability<br>Escaping steam/thermal hiss communicating internal mechanical failure |
| **SFX-27** | **Boss Heavy Stagger Breathing / Groan** | Looped audio during<br>vulnerable stagger window | **Option A (Preferred):** Grux Exhausted Guttural Breathing<br>**Option B:** Grux Heavy Pain Grunt<br>**Option C:** Steel Armored Exertion Strain | `/Game/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundWaves/Grux_Effort_BreathingLowHealth_01`<br>`/Game/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundWaves/Grux_Effort_PainHeavy_01`<br>`/Game/ParagonSteel/Audio/Wavs/Steel_Effort_PainHeavy_010` | Grux: Deep, ragged monstrous breathing loop (Ember Warden distinct from Sevarog)<br>Grux: Heavy guttural pain groan on posture break collapse<br>Steel: Armored titan heavy breath strain |
| **SFX-28** | **Critical Execution / Riposte Impale** | Execution strike contact<br>hit frame / Riposte hit | **Option A (Preferred):** Massive Blade Cleave & Impale<br>**Option B:** Deep Armor Piercing Strike<br>**Option C:** Catastrophic Flesh & Armor Rupture | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpactLarge1`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_12_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpactLarge4` | Enormous blade impale shock with deep metal-flesh crunch<br>Violent piercing strike cutting through boss plate into core<br>Heavy brutal shock impact with trailing sub-bass resonance |
| **SFX-29** | **Boss Stagger Recovery Stance Re-assertion** | `URPGBossStagger::EndStagger`<br>recovery frame | **Option A (Preferred):** Metallic Snap & Blade Re-assertion<br>**Option B:** Heavy Arena Concrete Ground Stomp<br>**Option C:** Concussive Stance Re-settle | `/Game/RealisticSwordSoundEffects/Cues/Sword_Unsheathe/Sword_Unsheathe_3_Cue`<br>`/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue` | Sharp metallic blade-lock notifying player vulnerability window closed<br>Massive footfall stomp shaking arena floor on recovery<br>Dense sub-bass guardian impact re-grounding boss poise |
| **SFX-30** | **Player Stance Break / Guard Break** | Player posture exhaustion /<br>Shield blowout | **Option A (Preferred):** Massive Shield Deflection Blowout<br>**Option B:** Violent Shield Collapse Shock<br>**Option C:** Heavy Armor Blade Blow-Through | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact4`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact3`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_11_Cue` | Violent iron shield blowout and recoil reverberation<br>High-energy shield deflection shock indicating zero stamina<br>Aggressive steel blow-through pushing guard aside *(strictly non-vocal foley)* |

---

## 2. Character Independence & Voice Safeguards (C-1175 / C-1212)

1. **Player Voice Exclusion Rule (`[C-1212]`):**
   - The player character model remains open pending the `C-1174` fit test (Greystone vs Steel vs Grux).
   - In strict compliance with Lead directive `[C-1212]`, **all Player Stance Break candidates (`SFX-30`) are non-vocal foley** (shield deflection blowouts, armor buckles, and blade blow-throughs). Zero character-locked voice assets are included in the wired set.
2. **Boss Character Separation (`C-1175` / `C-1208`):**
   - Ember Warden (`Boss01`) stagger vocalizations (`SFX-27`) utilize monstrous/titan audio from Grux and Steel rather than native Sevarog voice assets, ensuring the upcoming Sevarog boss (`Boss02`) retains a completely distinct vocal profile.

---

## 3. Posture & Execution Gameplay Feedback Hierarchy

1. **Pre-Stagger Telegraphing (`SFX-26`):**
   - In FromSoftware Soulslike encounters, high-level players rely on subtle audio tells before posture breaks occur. Option A provides a metallic groaning creak when posture drops below $25\%$, signaling the opportunity for an aggressive stagger finish.
2. **The Execution Peak (`SFX-28`):**
   - The critical riposte / execution hit is the auditory climax of the posture system. It pairs heavy sub-bass impact with sharp blade cutting crunch, delivering maximum visceral satisfaction.
3. **Pacing the Vulnerability Window (`SFX-27` & `SFX-29`):**
   - While staggered, the boss emits heavy, labored breathing (`SFX-27`), audio-marking the damage window. The recovery snap (`SFX-29`) sharply announces that the vulnerability frame has expired, warning the player to disengage or prepare for counter-attacks.
