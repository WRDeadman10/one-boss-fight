# SFX Batch 9 Candidate Specification: Arena Environment, Ambience & Menu Audio

**Document Version:** 1.0  
**Authority:** Claude Lead Directives `[C-1197]`, `[C-1232]` (2026-11-10).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** PROPOSED (Spec-Only; Awaiting Owner Audition Selection; No Wiring).  
**Scope:** Tasks `SFX-41` through `SFX-45` (Batch 9: Arena Environment & Ambience, plus UI/Menu audio considerations) in [`Documentation/Boss/QUEUE_SFX.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md).

---

## 1. Executive Summary & Design Principles

Per directive `[C-1232]`, this document specifies candidate audio assets for **Batch 9 (Arena Environment, Ambience & Menu Audio)** covering ruined arena wind whistling, brazier ember crackle, subterranean low-frequency drone rumble, perimeter wall impact feedback, dynamic fog/mist atmospheric wash, and UI/menu audio interactions.

### Discipline Constraints
1. **Repository Assets Only:** 100% of candidate assets exist directly within project content (`StarterContent`, `AdvancedARPGCombat`). Zero external downloads.
2. **Opt-In / No Runtime Wiring:** Strictly spec-only. No blueprints, level actors, anim notifies, C++ triggers, or sound cues are wired or modified until the project owner makes selections from audition reels.
3. **Acoustic Hierarchy & Headroom:** Environmental ambient beds must provide atmospheric immersion while sitting below dialogue, music, and boss attack cues in the sound mix, leaving dynamic headroom for high-priority combat telegraphs.

---

## 2. Candidate Selection Matrix: Arena Environment & Ambience (Batch 9)

| Task ID | Gameplay / Environment Event | Target Trigger / Hook Site | Candidate Options (In Repo) | Asset Path | Dynamic Character & Acoustic Profile |
|---|---|---|---|---|---|
| **SFX-41** | **Arena Ruin Wind** | Ambient 2D sound loop in `L_SevarogArena` | **Option A (Preferred):** Broad Atmospheric Ruin Wind Loop<br>**Option B:** Gusting Cold Wind Bed<br>**Option C:** Layered Ambient Wind with Distant Tones | `/Game/StarterContent/Audio/Starter_Wind05`<br>`/Game/StarterContent/Audio/Starter_Wind06`<br>`/Game/StarterContent/Audio/Starter_Background_Cue` | Gentle, desolate wind howling through shattered pillars with low high-frequency harshness<br>More dynamic gusts providing subtle pressure variations across the arena<br>Subtle composite bed blending distant air movement and ruined architecture resonance |
| **SFX-42** | **Distant Brazier Ember Crackle** | Positional ambient emitter near arena flame braziers | **Option A (Preferred):** Deep Continuous Brazier Flame Cue<br>**Option B:** Crisp Ash Flutter & Spark Crackle<br>**Option C:** Grounded Flame Roar Bed | `/Game/StarterContent/Audio/Fire01_Cue`<br>`/Game/StarterContent/Audio/Fire_Sparks01_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Fire01_Cue` | Rich, crackling wood fire with organic transient pops suitable for 3D spatial attenuation<br>Higher register sparks and glowing ember pops emphasizing ash flutter<br>Deeper, warmer bonfire bed providing steady low-mid proximity warmth |
| **SFX-43** | **Subterranean Arena Drone Bed** | Sub-bass spatial rumble enhancing arena tension | **Option A (Preferred):** Dark Resonant Subterranean Hum<br>**Option B:** Deep Ominous Air Pressure Rumble<br>**Option C:** Heavy Structural Low-End Resonance | `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift02`<br>`/Game/StarterContent/Audio/Starter_Wind06`<br>`/Game/StarterContent/Audio/Collapse_Cue` | Cavernous sub-harmonic drone conveying subterranean dread and boss presence<br>Low-passed wind resonance simulating underground pressure fluctuations<br>Sub-bass acoustic tail of collapsed stone architecture providing grounding drone |
| **SFX-44** | **Arena Boundary Wall Collision** | Player/boss arena perimeter hit reactions / wall thud | **Option A (Preferred):** Heavy Stone Masonry Thud<br>**Option B:** Dense Armor/Wall Impact Clatter<br>**Option C:** Resonant Structural Shudder Cue | `/Game/StarterContent/Audio/Collapse01`<br>`/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/HitSounds/A_Guardian_Impact02`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue` | Solid, non-hollow stone thud indicating unyielding boundary contact<br>Sharp transient impact with gravel residue suitable for knockback into ruins<br>Full-bodied kinetic shudder emphasizing the weight of boss or player wall impacts |
| **SFX-45** | **Dynamic Fog / Mist Wash** | Environmental atmospheric bed modulated by combat phase | **Option A (Preferred):** Ethereal Steam / Mist Hiss Bed<br>**Option B:** Soft Wispy Vapor Ambient Cue<br>**Option C:** Composite Distant Atmosphere Bed | `/Game/StarterContent/Audio/Steam01_Cue`<br>`/Game/StarterContent/Audio/Smoke01_Cue`<br>`/Game/StarterContent/Audio/Starter_Background_Cue` | Continuous soft vaporous wash matching arena low-lying fog and soul-fire mist<br>Dryer, subtler atmospheric breath suitable for Phase 2 shroud escalation<br>Expansive airy bed providing spatial depth without masking melee swooshes |

---

## 3. UI / Menu Audio Considerations (Directive `[C-1232]` Alignment)

In addition to ambient environmental layers, tactile UI audio candidates for menu navigation and pause/settings confirmation are cataloged to complete interface audio coverage:

| Event | Candidate Option | Asset Path | Acoustic Character |
|---|---|---|---|
| **Menu Hover / Nav** | Subtle Air Tick | `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Hover` | Minimalist non-intrusive navigation click |
| **Menu Select** | Clean Tactile Snap | `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select01` | Positive crisp confirmation transient |
| **Menu Confirm / Apply** | Resonant Heavy Select | `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Box_Confirm` | Weighty acoustic confirmation for settings commit |
| **Menu Back / Cancel** | Subdued Down-Tick | `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/UI/A_UI_Select02` | Softer downward pitch transient for cancellation |

---

## 4. Acoustic Profiles & Gain Staging Recommendations

1. **Ambient Bed Layers (`SFX-41`, `SFX-43`, `SFX-45`):**
   - Routing: `SC_SFX` / Ambient SoundClass submix.
   - Volume: \(-18.0\text{ dB}\) to \(-24.0\text{ dB}\) relative to Master.
   - Behavior: 2D non-spatialized background bed, dynamically ducked by \(-4.0\text{ dB}\) during active boss combat phase transitions (`MX_Boss01_Phase1` / `Phase2`).

2. **Positional Emitters (`SFX-42` Brazier Ember):**
   - Routing: `SC_SFX` with natural logarithmic distance attenuation (Inner Radius: \(200\text{ cm}\), Falloff Distance: \(1200\text{ cm}\)).
   - Volume: \(-12.0\text{ dB}\) at origin.
   - Spatialization: Binaural HRTF spatialization enabled with low-pass filtering beyond \(800\text{ cm}\).

3. **Perimeter Wall Collisions (`SFX-44`):**
   - Routing: `SC_SFX` (Impact submix).
   - Volume: \(-4.0\text{ dB}\) to \(-2.0\text{ dB}\) relative to Master.
   - Concurrency: Limit 2 instances with oldest voice resolution to prevent stutter during rapid wall collisions.

---

## 5. Next Steps & Approval Workflow

- **Status:** Strictly candidate specification only. Zero blueprints, assets, or levels have been modified.
- **Audition Reel:** Pending Owner request, audition reels can be prepared for previewing options.
- **Wiring Hold:** Implementation remains fail-closed until explicit Owner confirmation is recorded in `Documentation/TEAM_MAILBOX.md`.
