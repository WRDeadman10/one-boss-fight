# SFX Batch 4: Phase Transition & Roar Audio Candidate Specification

**Document Version:** 1.0  
**Authority:** Claude Lead Directives `[C-1197]`, `[C-1207]`, `[C-1208]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** PROPOSED (Spec-Only; Awaiting Owner Audition Selection; No Wiring).  
**Scope:** Tasks SFX-16 through SFX-20 in [`Documentation/Boss/QUEUE_SFX.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md).

---

## 1. Candidate Selection Matrix

| Task ID | Gameplay Event | Anim Montage / Hook Site | Candidate Options (In Repo) | Asset Path | Source Character & Style |
|---|---|---|---|---|---|
| **SFX-16** | **Boss Phase 2 Awakening Vocal Roar / Screech** | `URPGTier2BossPresentation`<br>Trigger / `AM_SevPack_Roar` | **Option A (Preferred):** Grux Primal Beast Roar<br>**Option B:** Steel Guttural War Cry<br>**Option C:** Sevarog Spectral Shriek *(Archetype Caution)* | `/Game/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundCues/Grux_Effort_Ability_Ultimate`<br>`/Game/ParagonSteel/Audio/Cues/Steel_Effort_Ability_Primary_Swing`<br>`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Ultimate` | **Grux:** Monstrous, deep primal bellow (keeps Boss01 distinct from Sevarog)<br>**Steel:** Armored titan heavy exertion roar<br>**Sevarog:** Ghostly wraith scream *(Caution: shares voice with future Sevarog boss)* |
| **SFX-17** | **Phase 2 Ember Aura Ignite Burst** | `PhaseTwoAuraEffect`<br>Component Spawn Event | **Option A (Preferred):** Detonation Impact Burst<br>**Option B:** Fiery Ignition Blast<br>**Option C:** Arcane Concussive Explosion | `/Game/StarterContent/Audio/Explosion_Cue`<br>`/Game/StarterContent/Audio/Fire_Sparks01_Cue`<br>`/Game/AdvancedARPGCombat/RangedCombatSystem/DemoAssets/Effects/ExampleExplosion/ExampleExplosionImpact_Cue` | Detonation with heavy initial transient & low rumble<br>Fiery burst crackle with searing high-frequency spark<br>Focused concussive blast with sharp shockwave onset |
| **SFX-18** | **Persistent Fiery Aura Ambient Loop** | `PhaseTwoAuraComponent`<br>(Continuous Low-Pass Loop) | **Option A (Preferred):** Continuous Roaring Flame<br>**Option B:** Subtle Melee Pack Fire Loop<br>**Option C:** Low Vapor / Steam Hiss | `/Game/StarterContent/Audio/Fire01_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Fire01_Cue`<br>`/Game/StarterContent/Audio/Steam01_Cue` | Rich, broad spectrum burning embers & low roar<br>Tight, lower-volume intimate fire crackle<br>Subdued pressurized vapor/steam undertone |
| **SFX-19** | **Phase 2 Transition Ground Rupture Crackle** | `NS_Boss_ShockwaveRing`<br>Floor Crack Emergence | **Option A (Preferred):** Extended Ground Rupture<br>**Option B:** Stone Collapse & Debris<br>**Option C:** Deep Earth Tremor Shockwave | `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_04_2s_Cue`<br>`/Game/StarterContent/Audio/Collapse_Cue`<br>`/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_02_2s_Cue` | Long 2.0s tearing rock fissure & concussive wave<br>Heavy structural crumble with falling debris stones<br>Deep subsonic floor rumble with punchy leading edge |
| **SFX-20** | **Phase Transition Stinger / Combat Shift** | Tier 2 Boss Presentation<br>State Entry Stinger | **Option A (Preferred - In-Engine):** Cosmic Void Swell<br>**Option B (Orchestral):** Starter Battle Orchestral Swell<br>**Option C (Mystic Chime):** Ethereal Ascension Riser | `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift_Cue`<br>`/Game/StarterContent/Audio/Starter_Music_Cue`<br>`/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue` | Deep atmospheric void swell with sub-bass drop<br>Full orchestral brass/string dramatic accent<br>High-register mystical chime riser & shimmer |

---

## 2. Character Independence & Voice Architecture (C-1175 / C-1208)

1. **Boss Separation Rule:**
   - Per Lead directive `[C-1208]` and architecture decision `[C-1175]`, boss characters are strictly independent.
   - The primary boss in the current arena is the **Ember Warden** (`Boss01`), built upon the Greystone vs Sevarog duel framework.
   - The native Sevarog voice lines in `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/` are reserved for the future standalone Sevarog encounter (`Boss02`).
2. **Ember Warden Vocal Palette:**
   - To avoid voice-sharing collisions between Boss01 and Boss02, Option A (Grux Bellow) and Option B (Steel Titan Exertion) provide powerful monstrous/heavy-armor vocal identities distinct from Sevarog.
   - Option C (Sevarog Spectral Shriek) is cataloged for completeness and Owner review, with the explicit caveat noted that selecting it shares vocal profile with the upcoming Sevarog boss.

---

## 3. Stinger Presentation Philosophy (SFX-20)

Per Lead directive `[C-1208]`, both stinger styles are offered for Owner evaluation:
- In-Engine Dark Void Swell (Option A): Retains an immersive, diegetic soundscape where the shift into Phase 2 feels driven by raw elemental forces (deep sub-bass drop and planar tear).
- Orchestral Dynamic Accent (Option B): Offers a traditional Soulslike / cinematic musical surge (`Starter_Music`) marking the elevated combat stakes.
- Mystic Ascension Chime (Option C): Focuses on spectral escalation without low-end clutter, leaving sonic space for the ground rupture (`SFX-19`) and ignite blast (`SFX-17`).

---

## 4. Hook Architecture & Sound Concurrency

1. **URPGTier2BossPresentation Trigger:**
   - `SFX-16` (Awakening Roar) and `SFX-20` (Transition Stinger) execute at $T=0$ of the phase transition montage / presentation trigger.
2. **Aura Component & Particle Synchronization:**
   - `SFX-17` (Ignite Burst) fires on the exact frame `NS_Boss_PhaseTwoAura` spawns.
   - `SFX-18` (Ambient Fiery Loop) is spawned as an attached looping audio component with an explicit $0.5\text{ s}$ fade-in, volume-scaled ($0.35-0.50$) and routed through a low-pass filter to prevent combat fatigue.
3. **Decal & Rupture Alignment:**
   - `SFX-19` (Rupture Crackle) triggers synchronously with `NS_Boss_ShockwaveRing` and ground decal emergence.
4. **Volume Balancing & Concurrency Grouping:**
   - All Batch 4 audio assets will share a dedicated `PhaseTransition_Concurrency` setting (Max Voice Count = 2, Ducking = $-6\text{ dB}$ on ambient foley) to guarantee zero clipping or distortion during the multi-layered transition event.

---

## 5. Offline Contract Verification

A companion test script (`Scripts/Editor/test_sfx_batch4_candidates_contract.py`) asserts:
1. Every cited asset path exists on disk as a valid `.uasset`.
2. Tasks `SFX-16` through `SFX-20` are fully mapped with exactly 3 distinct candidate options each.
3. Voice character origin labels (Grux, Steel, Sevarog) are explicitly preserved.
4. Zero pack files are modified (`refuse-if-pack-path` contract).
