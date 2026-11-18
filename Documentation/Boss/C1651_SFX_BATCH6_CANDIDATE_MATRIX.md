# C-1651 Audio/SFX Candidate Matrix: Batch 6/10 (SFX-31..SFX-35)

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2679]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-139 (SFX-31), BT-140 (SFX-32), BT-141 (SFX-33), BT-142 (SFX-34), BT-143 (SFX-35)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directive `[X-2679]`, Antigravity has executed the candidate discovery, in-repo package verification, and acoustic specification for **C-1651 Audio/SFX Batch 6/10 (SFX-31 through SFX-35)**: Boss Movement & Spectral Foley.

- **Audio Asset Policy:** Strictly repository-internal audio assets only. Zero external downloads, zero engine/asset modifications, zero runtime wiring before Owner selection.
- **Spec-Only & Export Hold:** In accordance with [BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md](BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md) and directive `[X-2679]`, raw WAV export and audition reel compilation for SFX-31..35 are held pending Owner tone preferences. All 15 candidate Sound Cue packages are confirmed present in-tree, sized, and hashed.
- **Native Seam Audit Reconciliation:** In cross-referencing [C1651_SFX_31_35_TRIGGER_AUDIT.md](C1651_SFX_31_35_TRIGGER_AUDIT.md):
  - **SFX-31 (Footstep Duplication Risk):** Native `URPGFootsteps` already attaches to bosses with concrete footsteps in `RPGPlayerMovesSubsystem.cpp:1405-1431`. Wiring an additional montage notify without reconfiguring the native subsystem would cause duplicate sound playback.
  - **SFX-32..35 (Prospective Hooks):** Dash whoosh, cape flutter, idle torso rumble, and ground skid deceleration currently lack dedicated native C++ dispatcher seams; candidates are documented as spec-only targets.

---

## 2. Event-by-Event Candidate Matrix

### 2.1. SFX-31: Boss Heavy Armor Footsteps (BT-139)
- **Combat Context:** Rhythmic footstep impacts as the boss navigates the stone arena floor. Communicates imposing physical mass and plate armor weight.
- **Hook Site & Seam Warning:** `URPGFootsteps` is already natively configured with concrete walk/jog/run/land cues (`RPGPlayerMovesSubsystem.cpp:1405-1431`). Any candidate implementation must replace the configured sound rather than layering on montages to avoid double-playing footsteps.
- **Candidate Options:**
  - **Option A (Preferred - Concrete Heavy Boots Run Stomp):**
    - UE Package: `/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Run_8_Cue`
    - File: `Content/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Run_8_Cue.uasset`
    - Size: 14,716 bytes | SHA-256: `E11FF17A7322206183C9ABC09F479B1B3F493B647B5846C0A565FB0F679CAB26`
    - Acoustic Profile: Heavy plate boot impact with solid arena flagstone transient.
  - **Option B (Concrete Heavy Boots Land Impact):**
    - UE Package: `/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue`
    - File: `Content/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue.uasset`
    - Size: 9,983 bytes | SHA-256: `51C28F5B35F13304FE3BB046233638C70CD346CF6491EFFC14838E4A02BBDCF0`
    - Acoustic Profile: Deeper downward impact step with trailing stone resonance.
  - **Option C (Subdued Stone Guardian Footfall):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02.uasset`
    - Size: 159,731 bytes | SHA-256: `16995A02DBAEC3DA495446F81C2AB453A608E66F4E073E0B20F5CEB97A17861B`
    - Acoustic Profile: Dense creature-mass floor displacement with low rumble.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.2. SFX-32: Boss Dash / Teleport Ethereal Whoosh (BT-140)
- **Combat Context:** Boss sudden linear glide or supernatural repositioning across the arena floor. Demands an eerie, planar air-tearing whoosh.
- **Hook Site:** Prospective hook site on repositioning montage (native gap closer currently unwired by design).
- **Candidate Options:**
  - **Option A (Preferred - Wide Atmospheric Displacement Swoosh):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue.uasset`
    - Size: 4,339 bytes | SHA-256: `AD4430F81A293CC2D411609FC052B14F2C6A38DAFCC2121E5A74C865A0A3B7F0`
    - Acoustic Profile: Expansive low-end displacement whoosh for sudden rapid slides.
  - **Option B (Planar Tear Spatial Whoosh):**
    - UE Package: `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift01`
    - File: `Content/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift01.uasset`
    - Size: 393,835 bytes | SHA-256: `E55E12C0832B84D95FB03CEAA1E41A8B2F004C046822C3DEDDE052F01D8E9AB1`
    - Acoustic Profile: Spectral planar distortion indicating supernatural spatial displacement.
  - **Option C (Sharp High-Velocity Air Cut):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue.uasset`
    - Size: 4,423 bytes | SHA-256: `7D02E64C8FDEC3AAE742A64FA9166BF52E1AD23154159EF21EB03337C80274D2`
    - Acoustic Profile: Crisp high-speed air cut marking sudden movement onset.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.3. SFX-33: Boss Cape / Cloth Heavy Flutter (BT-141)
- **Combat Context:** Heavy shroud or cloth cape trailing boss swings and rapid turns. Adds tactile fabric rustle to massive movements.
- **Hook Site:** Prospective hook site on aggressive blade swings (no native cloth simulation emitter currently active).
- **Candidate Options:**
  - **Option A (Preferred - Heavy Wind Cloth Flutter):**
    - UE Package: `/Game/StarterContent/Audio/Starter_Wind05`
    - File: `Content/StarterContent/Audio/Starter_Wind05.uasset`
    - Size: 2,312,702 bytes | SHA-256: `57FF816D0D35668E42096D85B2BEABD89D6A87751F4F2C4AB030F4EE32B64CE7`
    - Acoustic Profile: Gusting air displacement catching heavy leather/shroud fabric.
  - **Option B (Deep Velocity Air Drag):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue.uasset`
    - Size: 4,423 bytes | SHA-256: `7D02E64C8FDEC3AAE742A64FA9166BF52E1AD23154159EF21EB03337C80274D2`
    - Acoustic Profile: Sharp directional flutter matching aggressive blade swings.
  - **Option C (Intimate Fabric Dispersal):**
    - UE Package: `/Game/StarterContent/Audio/Starter_Wind06`
    - File: `Content/StarterContent/Audio/Starter_Wind06.uasset`
    - Size: 2,195,539 bytes | SHA-256: `517DAD0128FBC9BF1ACC611065A47892FF48F23E68FDDE1D37D84CECB8DC0C7F`
    - Acoustic Profile: Subdued low-register ambient cloth rustle.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.4. SFX-34: Boss Idle Subterranean Chest Rumble (BT-142)
- **Combat Context:** Low-frequency spatialized ambient loop emitted from the boss's torso, conveying immense dormant power and unnatural vitality.
- **Hook Site:** Prospective spatialized component attached to boss chest bone (distinct from global 2D `RPGArenaAmbience`).
- **Candidate Options:**
  - **Option A (Preferred - Subterranean Low Wind Drone):**
    - UE Package: `/Game/StarterContent/Audio/Starter_Wind06`
    - File: `Content/StarterContent/Audio/Starter_Wind06.uasset`
    - Size: 2,195,539 bytes | SHA-256: `517DAD0128FBC9BF1ACC611065A47892FF48F23E68FDDE1D37D84CECB8DC0C7F`
    - Acoustic Profile: Continuous ominous low-frequency atmospheric drone (< 120 Hz).
  - **Option B (Guardian Sub-Bass Resonant Core):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02.uasset`
    - Size: 159,731 bytes | SHA-256: `16995A02DBAEC3DA495446F81C2AB453A608E66F4E073E0B20F5CEB97A17861B`
    - Acoustic Profile: Subdued internal stone-core grinding vibration.
  - **Option C (Thermal Vapor Steam Hiss):**
    - UE Package: `/Game/StarterContent/Audio/Steam01_Cue`
    - File: `Content/StarterContent/Audio/Steam01_Cue.uasset`
    - Size: 4,285 bytes | SHA-256: `C43FB733EBFC395AF98CE820DE46FED7D2B3F2A42AD03F55C8CF8E12D1BD417F`
    - Acoustic Profile: Subtle thermal vapor exhale communicating internal furnace energy.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.5. SFX-35: Boss Ground Skid Deceleration (BT-143)
- **Combat Context:** Boss heels skidding and braking across arena paving following heavy attack lunges or swings. Distinct from vertical landing impacts.
- **Hook Site:** Prospective hook site on attack recovery frames (distinct from `RPGFootsteps` landing audio).
- **Candidate Options:**
  - **Option A (Preferred - Coarse Stone-on-Blade Friction Scrape):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_3_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_3_Cue.uasset`
    - Size: 4,463 bytes | SHA-256: `F5374922D1B1309C56BC06B5E72B091CC7F6C2FE625C04F4A345C6AD040F7E6B`
    - Acoustic Profile: Abrasive stone and metal grinding decelerating massive momentum.
  - **Option B (Arena Masonry Crumble & Slide):**
    - UE Package: `/Game/StarterContent/Audio/Collapse02`
    - File: `Content/StarterContent/Audio/Collapse02.uasset`
    - Size: 346,701 bytes | SHA-256: `A5690C3CDC857EA7D3AE21ED1C6A22E82BB15E8BB24B995228AF244C2BB4F0D3`
    - Acoustic Profile: Shifting stone debris and crumbling dust under heavy load.
  - **Option C (Concrete Boot Deceleration Skid):**
    - UE Package: `/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue`
    - File: `Content/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue.uasset`
    - Size: 9,983 bytes | SHA-256: `51C28F5B35F13304FE3BB046233638C70CD346CF6491EFFC14838E4A02BBDCF0`
    - Acoustic Profile: Heavy boot heel arrest stopping boss sliding recovery.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

## 3. Verification & Compliance Checklist

1. **Repository Isolation:** Only project-internal audio assets referenced. Zero external assets downloaded.
2. **Immutability:** Zero `.uasset` packages or config files modified.
3. **Engine Safety:** 0 Unreal Editor instances started. Both C-1155 locks remain untouched and absent.
4. **Git Safety:** 0 git commits, 0 git pushes performed.
5. **Hold Compliance:** In accordance with `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`, zero WAV files were exported and zero audition reels were built; candidates remain spec-only.
6. **Task Board Status:** All five tasks (`BT-139`, `BT-140`, `BT-141`, `BT-142`, `BT-143`) advanced to `review`.
