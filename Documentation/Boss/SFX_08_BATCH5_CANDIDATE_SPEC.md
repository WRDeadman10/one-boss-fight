# SFX Batch 5: Player Defense & Combat Foley Candidate Specification

**Document Version:** 1.0  
**Authority:** Claude Lead Directives `[C-1197]`, `[C-1211]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** PROPOSED (Spec-Only; Awaiting Owner Audition Selection; No Wiring).  
**Scope:** Tasks SFX-21 through SFX-25 in [`Documentation/Boss/QUEUE_SFX.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md).

---

## 1. Candidate Selection Matrix

| Task ID | Gameplay Event | Anim Montage / Hook Site | Candidate Options (In Repo) | Asset Path | Dynamic Character & Acoustic Profile |
|---|---|---|---|---|---|
| **SFX-21** | **Player Shield Standard Block** | `BlockImpactEffect`<br>(Standard Hit Reaction) | **Option A (Preferred):** Shield Concussive Impact Cue<br>**Option B:** Heavy Metallic Deflection<br>**Option C:** Greystone Vocal Block Reaction Cue | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpacts_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact2`<br>`/Game/ParagonGreystone/Audio/Cues/Greystone_Effort_Block` | Solid iron-on-shield heavy thud with damped metal ring<br>Crisp high-mass rim deflection crack<br>Player effort vocal grunt layered with shield shock |
| **SFX-22** | **Player Deflect / Glancing Blow** | `URPGPlayerMovesSubsystem`<br>(Deflect / Partial Block) | **Option A (Preferred):** High-Speed Blade Deflect Friction<br>**Option B:** Rough Friction Spark Scrape<br>**Option C:** Precision Edge Deflection Contact | `/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Fast_Speed_Cue`<br>`/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_1_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact1` | Searing metal-on-metal spark scrape with sharp transient<br>Coarse, grinding blade-slide friction hiss<br>Tight edge-to-edge glancing collision click |
| **SFX-23** | **Player Healing Flask Recovery** | Flask Consumption Event /<br>`BP_ReplenishmentCue` | **Option A (Preferred):** Health/Mana Recovery Shimmer<br>**Option B:** Mystic Replenishment Chime<br>**Option C:** Radiant Light Ascension Stinger | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Character_Heal_Mana_Cue`<br>`/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue`<br>`/Game/StarterContent/Audio/Light01_Cue` | Ethereal liquid chug followed by warm restorative bloom<br>Magical resonance chime indicating stat restoration<br>Clean, luminous high-register restorative chime |
| **SFX-24** | **Player Dodge Roll Armor Foley** | `AM_ER_Backstep_*` /<br>Roll Recovery Frame | **Option A (Preferred):** Concrete Boot Land & Armor Settle<br>**Option B:** Dirt Ground Contact & Roll Scrape<br>**Option C:** Heavy Armor Footstep Transient | `/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue`<br>`/Game/Essential_Foosteps_SK/CUE/Dirt/Footstep_Dirt_Boots_Land_1_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/Character/A_Character_Step01` | Heavy leather/plate compression and arena stone thud<br>Abrasive gravel/dirt ground contact roll rustle<br>Damped heel-to-toe tactical armor adjustment foley |
| **SFX-25** | **Player Weapon Draw & Sheathe** | Combat Stance Entry / Exit<br>`DrawSword_Montage` | **Option A (Preferred):** Realistic Sword Unsheathe Draw<br>**Option B:** Pack Metallic Scrape Draw Cue<br>**Option C:** Pack Weighted Leather Sheathe Cue | `/Game/RealisticSwordSoundEffects/Cues/Sword_Unsheathe/Sword_Unsheathe_1_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/DrawDisarm/SwordDraw1_Cue`<br>`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/DrawDisarm/SwordSheath2_Cue` | Searing surgical steel ring drawn from scabbard<br>Heavy battlefield steel slide across crossguard<br>Weighted leather-throated scabbard lock with final click |

---

## 2. Soulslike Defense & Audio Hierarchy

1. **Standard Block vs Parry Contrast:**
   - Standard block (`SFX-21`) must sound heavy, exhausting, and absorptive (damped sub-thud), contrasting sharply with the crystal-clear high-frequency bell ring and reward boom of the successful Parry (`GAP-01` / `A_Guardian_ImpactL_Cue`).
   - A Glancing Blow (`SFX-22`) communicates partial stamina loss through blade-to-blade friction rather than blunt shield absorption.
2. **Healing Flask Audio Pacing:**
   - Soulslike healing requires distinct auditory stages: the physical initiation (liquid intake/chug) followed by the restorative shimmer stinger (`SFX-23`). This rewards the player's vulnerable commitment window with unambiguous confirmation of HP restoration.
3. **Weight & Armor Foley Integration:**
   - The dodge roll (`SFX-24`) must ground Greystone's knight archetype without obscuring boss telegraphs. The foley focuses on low-mid leather/plate settles on the recovery frames.
4. **Draw & Sheathe Immersion:**
   - `SFX-25` marks combat stance state transitions cleanly, providing tactile feedback when entering or disengaging from boss duel lock-on.

---

## 3. Integration & Concurrency Boundaries

1. **No-Pack Asset Mutation Rule:**
   - Standard block and draw/sheathe cues will hook through project anim montage notifies (`OneBossFight/Player/Animations/`) or C++ delegate hooks in `URPGPlayerMovesSubsystem` without touching `/Game/AdvancedARPGCombat/`.
2. **Concurrency & Ducking:**
   - Shield impacts (`SFX-21`) share a concurrency voice cap of 2 to prevent audio stacking during multi-hit boss combos.
   - Healing recovery (`SFX-23`) is prioritized over footstep/foley channels ($+3\text{ dB}$) to guarantee player feedback in intense combat.
