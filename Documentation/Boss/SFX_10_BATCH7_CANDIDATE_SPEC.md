# SFX Batch 7 & Ambience Candidate Specification

**Document Version:** 1.0  
**Authority:** Claude Lead Directives `[C-1197]`, `[C-1212]`, `[C-1213]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** PROPOSED (Spec-Only; Awaiting Owner Audition Selection; No Wiring).  
**Scope:** Tasks SFX-31 through SFX-35 (Batch 7: Boss Movement & Spectral Foley) and SFX-41 through SFX-45 (Batch 9: Arena Environment & Ambience) in [`Documentation/Boss/QUEUE_SFX.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md).

---

## 1. Candidate Selection Matrix: Boss Movement & Spectral Foley (Batch 7)

| Task ID | Gameplay Event | Anim Montage / Hook Site | Candidate Options (In Repo) | Asset Path | Dynamic Character & Acoustic Profile |
|---|---|---|---|---|---|
| **SFX-31** | **Boss Heavy Armor Footsteps** | `AN_Boss01_Footstep_L/R`<br>Stone impacts | **Option A (Preferred):** Concrete Heavy Boots Run Stomp<br>**Option B:** Concrete Heavy Boots Land Impact<br>**Option C:** Subdued Stone Guardian Footfall | `/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Run_8_Cue`<br>`/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02` | Rhythmic heavy plate boot impacts on ancient arena flagstones<br>Deeper, weighty downward step with trailing stone resonance<br>Dense creature-mass floor displacement |
| **SFX-32** | **Boss Dash / Teleport Ethereal Whoosh** | Repositioning movement<br>teleport notifies | **Option A (Preferred):** Wide Atmospheric Displacement Swoosh<br>**Option B:** Planar Tear Spatial Whoosh<br>**Option C:** Sharp High-Velocity Air Cut | `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue`<br>`/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift01`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue` | Expansive low-end displacement whoosh for sudden rapid slides<br>Spectral planar distortion indicating spatial repositioning<br>Crisp high-speed air cut marking sudden dash onset |
| **SFX-33** | **Boss Cape / Cloth Heavy Flutter** | Rapid turn and swing<br>montage frames | **Option A (Preferred):** Heavy Wind Cloth Flutter<br>**Option B:** Deep Velocity Air Drag<br>**Option C:** Intimate Fabric Dispersal | `/Game/StarterContent/Audio/Starter_Wind05`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue`<br>`/Game/StarterContent/Audio/Starter_Wind06` | Gusting air displacement catching heavy leather/shroud fabric<br>Sharp directional flutter matching aggressive blade swings<br>Subdued low-register ambient cloth rustle |
| **SFX-34** | **Boss Idle Subterranean Chest Rumble** | Spatialized loop at boss<br>torso bone | **Option A (Preferred):** Subterranean Low Wind Drone<br>**Option B:** Guardian Sub-Bass Resonant Core<br>**Option C:** Thermal Vapor Steam Hiss | `/Game/StarterContent/Audio/Starter_Wind06`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02`<br>`/Game/StarterContent/Audio/Steam01_Cue` | Continuous ominous low-frequency atmospheric drone ($< 120\text{ Hz}$)<br>Subdued internal stone-core grinding vibration<br>Subtle thermal vapor exhale communicating internal furnace energy |
| **SFX-35** | **Boss Ground Skid Deceleration** | Heavy swing recovery<br>ground friction slide | **Option A (Preferred):** Coarse Stone-on-Blade Friction Scrape<br>**Option B:** Arena Masonry Crumble & Slide<br>**Option C:** Concrete Boot Deceleration Skid | `/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_3_Cue`<br>`/Game/StarterContent/Audio/Collapse02`<br>`/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue` | Abrasive iron and stone grinding decelerating massive momentum<br>Shifting stone debris and crumbling dust under heavy load<br>Heavy boot heel arrest stopping boss sliding recovery |

---

## 2. Candidate Selection Matrix: Arena Environment & Ambience (Batch 9 / Priority c)

To directly fulfill Claude Lead directive `[C-1213]` ("spec batch 7 (arena ambience)"), the arena environmental soundscape in `L_SevarogArena` is specified below:

| Task ID | Gameplay Event | Emitter / World Location | Candidate Options (In Repo) | Asset Path | Dynamic Character & Acoustic Profile |
|---|---|---|---|---|---|
| **SFX-41** | **Arena Ruin Wind Whistling** | 2D World Ambient Bed<br>`L_SevarogArena` | **Option A (Preferred):** Desolate Ruin Mountain Wind<br>**Option B:** Cavernous Low Wind Swell<br>**Option C:** Starter Natural Background Ambient | `/Game/StarterContent/Audio/Starter_Wind05`<br>`/Game/StarterContent/Audio/Starter_Wind06`<br>`/Game/StarterContent/Audio/Starter_Background_Cue` | Howling wind gusting through cracked columns and ancient arches<br>Deep subsonic wind wash filling arena hollows<br>Gentle baseline environmental atmospheric noise bed |
| **SFX-42** | **Distant Brazier Ember Crackle** | Positional 3D Emitters<br>at arena braziers | **Option A (Preferred):** Rich Burning Ember Loop<br>**Option B:** Searing Spark Discharge Cue<br>**Option C:** Intimate Flame Crackle Cue | `/Game/StarterContent/Audio/Fire01_Cue`<br>`/Game/StarterContent/Audio/Fire_Sparks01_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Fire01_Cue` | Deep, continuous wood and coal combustion with gentle pop transients<br>Intermittent high-frequency cinder pops and spark bursts<br>Subdued close-proximity fire bed |
| **SFX-43** | **Subterranean Arena Drone Bed** | Sub-bass environmental bed<br>(Global non-spatial) | **Option A (Preferred):** Deep Planar Void Drone<br>**Option B:** Low Wind Sub-Bass Wash<br>**Option C:** Distant Subterranean Tectonic Throb | `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift02`<br>`/Game/StarterContent/Audio/Starter_Wind06`<br>`/Game/StarterContent/Audio/Collapse_Cue` | Ominous otherworldly throb grounding the arena's cursed lore<br>Smooth rolling subsonic wave sustaining dark tension<br>Low frequency rumble evoking subterranean ruin instability |
| **SFX-44** | **Arena Perimeter Wall Impact** | Arena boundary barrier<br>collision hit frame | **Option A (Preferred):** Ancient Stone Wall Concussion<br>**Option B:** Guardian Dense Impact Thud<br>**Option C:** Heavy Guardian Sub-Bass Strike | `/Game/StarterContent/Audio/Collapse01`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue` | Heavy crumbling masonry shock when combatants strike outer boundary<br>Dense stone resistance absorbing massive knockback<br>Sub-bass shockwave ring reverberating off arena pillars |
| **SFX-45** | **Dynamic Arena Fog / Mist Wash** | Weather / Fog emitter<br>ground layer | **Option A (Preferred):** Atmospheric Vapor Hiss<br>**Option B:** Ambient Smoke Dissipation<br>**Option C:** Broad Ambient Wash Bed | `/Game/StarterContent/Audio/Steam01_Cue`<br>`/Game/StarterContent/Audio/Smoke01_Cue`<br>`/Game/StarterContent/Audio/Starter_Background_Cue` | Ethereal spectral mist whispering across cold arena stones<br>Low density thermal air drift muffling background noise<br>Continuous atmospheric pad subtly expanding dynamic range |

---

## 3. Acoustic Boundaries & Spatialization Guidelines

1. **Attenuation Curves:**
   - Boss Footsteps (`SFX-31`) and Skid Foley (`SFX-35`): Spatialized 3D attenuation (Natural SoundFalloff: $200\text{ cm}$ min, $2500\text{ cm}$ max).
   - Boss Idle Rumble (`SFX-34`): Extremely tight radius ($100\text{ cm}$ min, $600\text{ cm}$ max) so it is only audible when the player is engaged in dangerous close quarters.
   - Arena Ambience (`SFX-41`, `SFX-43`): Non-spatialized 2D stereo beds routed to `SC_Ambience` sub-mix, ducked by $-4\text{ dB}$ whenever Boss attack whooshes or player parries occur.
2. **Zero-Pack Mutation Guarantee:**
   - Environmental audio will be wired exclusively into map actor instances in `L_SevarogArena` and boss anim notifies without modifying any base pack data.
