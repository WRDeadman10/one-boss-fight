# C-1651 Audio/SFX Candidate Matrix: Batch 8/10 (SFX-41..SFX-45)

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2681]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-151 (SFX-41), BT-152 (SFX-42), BT-153 (SFX-43), BT-154 (SFX-44), BT-155 (SFX-45)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directive `[X-2681]`, Antigravity has executed the candidate discovery, in-repo package verification, and acoustic specification for **C-1651 Audio/SFX Batch 8/10 (SFX-41 through SFX-45)**: Arena Environment, Ambience & Boundary Collision Audio.

- **Audio Asset Policy:** Strictly repository-internal audio assets only. Zero external downloads, zero engine/asset modifications, zero runtime wiring before Owner selection.
- **Spec-Only & Export Hold:** In accordance with [BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md](BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md) and directive `[X-2681]`, raw WAV export and audition reel compilation for SFX-41..45 are held pending Owner tone preferences. All 15 candidate Sound Cue packages are confirmed present in-tree, sized, and hashed.
- **Native Seam Audit Reconciliation:** In cross-referencing [C1651_SFX_41_45_TRIGGER_AUDIT.md](C1651_SFX_41_45_TRIGGER_AUDIT.md):
  - **SFX-41 (Arena Ruin Wind Bed):** `Source/OneBossFight/Audio/RPGArenaAmbience.h:12-15,28-37` and `RPGArenaAmbience.cpp:8-18,27-45` define an actor with a level-placeable non-spatial 2D wind component that fades in and restarts on finish. C++ component structure confirms architecture readiness, but code inspection alone does not prove level placement in `L_SevarogArena` or candidate assignment.
  - **SFX-42 (Brazier Ember Crackle):** No native positional brazier or emitter actor exists in C++. `ARPGArenaAmbience` is non-spatial. Positional brazier crackle requires placed emitter actors with distance attenuation curves; package presence on disk does not establish runtime map placement.
  - **SFX-43 (Subterranean Drone Bed):** Existing `ARPGArenaAmbience` exposes a single `Wind` source with no secondary drone channel or mix dispatcher. The sub-bass subterranean drone must not overwrite or silently reuse the wind bed; prospective implementation requires a distinct sound channel or secondary component.
  - **SFX-44 (Arena Boundary Wall Collision):** `Source/OneBossFight/Player/RPGBossArenaEdgeRules.h:5-15` explicitly notes arena-edge pressure is "Unwired by design" and only computes inward directional vectors. `RPGHitIntake.cpp:133-148,348-380` binds pack melee collision `OnHit(FHitResult)`, not perimeter-wall contacts. No native perimeter collision audio callback currently exists.
  - **SFX-45 (Dynamic Fog / Mist Wash):** No native phase-linked fog audio modulation exists. `ARPGArenaAmbience` loops wind on completion but has no combat-phase modulation or material/shroud callback hook. Requires prospective phase-state dispatcher hook.

---

## 2. In-Tree Candidate Packages & Cryptographic Verification

All 15 candidate Sound Cue packages are confirmed present in the project repository. Byte sizes and SHA-256 hashes are verified against physical disk:

| Task ID | Event Description | Candidate Option | In-Repo Package Path | Package Byte Size | SHA-256 Hash |
|---|---|---|---|---|---|
| **SFX-41** (BT-151) | Arena Ruin Wind Bed | **Option A (Preferred):** Broad Atmospheric Ruin Wind Loop | `Content/StarterContent/Audio/Starter_Wind05.uasset` | 2,312,702 bytes | `57FF816D0D35668E42096D85B2BEABD89D6A87751F4F2C4AB030F4EE32B64CE7` |
| | | **Option B:** Gusting Cold Wind Bed | `Content/StarterContent/Audio/Starter_Wind06.uasset` | 2,195,539 bytes | `517DAD0128FBC9BF1ACC611065A47892FF48F23E68FDDE1D37D84CECB8DC0C7F` |
| | | **Option C:** Layered Ambient Wind Bed | `Content/StarterContent/Audio/Starter_Background_Cue.uasset` | 10,330 bytes | `36BC3A7BBEAAD1ECF33A97465DA041171BDD205F780A171D8EC712B16174E8B8` |
| **SFX-42** (BT-152) | Distant Brazier Ember Crackle | **Option A (Preferred):** Deep Continuous Brazier Flame Cue | `Content/StarterContent/Audio/Fire01_Cue.uasset` | 4,280 bytes | `A3C93DCA255FFE4FCD045103B0CF1341ADDA3640B47A5656C82EF6236639A51C` |
| | | **Option B:** Crisp Ash Flutter & Spark Crackle | `Content/StarterContent/Audio/Fire_Sparks01_Cue.uasset` | 4,299 bytes | `3C13448535C552552C0216AA5A9D5AF5957D4606153A004CDCEC934EA5E9A22B` |
| | | **Option C:** Grounded Flame Roar Bed | `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Fire01_Cue.uasset` | 5,054 bytes | `390FF341C251A973E86FF2BE7C0FC405C3A49487D10449F3E851666CE170A9C8` |
| **SFX-43** (BT-153) | Subterranean Arena Drone Bed | **Option A (Preferred):** Dark Resonant Subterranean Hum | `Content/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift02.uasset` | 394,251 bytes | `D6A25AE3E46156EFC80EA6A58ADAA4A12325DA746E8A5C0A1553D0DA72A51396` |
| | | **Option B:** Deep Ominous Air Pressure Rumble | `Content/StarterContent/Audio/Starter_Wind06.uasset` | 2,195,539 bytes | `517DAD0128FBC9BF1ACC611065A47892FF48F23E68FDDE1D37D84CECB8DC0C7F` |
| | | **Option C:** Heavy Structural Low-End Resonance | `Content/StarterContent/Audio/Collapse_Cue.uasset` | 6,517 bytes | `2BBD215BBB20C2A86F7B9BA4D90AA1870EDD1999E00B5FF64A52A657A50A690B` |
| **SFX-44** (BT-154) | Arena Boundary Wall Collision | **Option A (Preferred):** Heavy Stone Masonry Thud | `Content/StarterContent/Audio/Collapse01.uasset` | 348,532 bytes | `85C827023EE4B466228EC65E92B4B4A0415A106DE041AC1C2CAB481A2A5DFA8D` |
| | | **Option B:** Dense Armor/Wall Impact Clatter | `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02.uasset` | 159,731 bytes | `16995A02DBAEC3DA495446F81C2AB453A608E66F4E073E0B20F5CEB97A17861B` |
| | | **Option C:** Resonant Structural Shudder Cue | `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.uasset` | 10,806 bytes | `CB1797D251938322E0CF60806E6F9B9B50DCA094B90EBCC8B326B3085742D534` |
| **SFX-45** (BT-155) | Dynamic Fog / Mist Wash | **Option A (Preferred):** Ethereal Steam / Mist Hiss Bed | `Content/StarterContent/Audio/Steam01_Cue.uasset` | 4,285 bytes | `C43FB733EBFC395AF98CE820DE46FED7D2B3F2A42AD03F55C8CF8E12D1BD417F` |
| | | **Option B:** Soft Wispy Vapor Ambient Cue | `Content/StarterContent/Audio/Smoke01_Cue.uasset` | 4,257 bytes | `97A08E7214107B0F39835BA844B7DCBC69B6613B3573DE87E3E9C0E9CFE1A057` |
| | | **Option C:** Composite Distant Atmosphere Bed | `Content/StarterContent/Audio/Starter_Background_Cue.uasset` | 10,330 bytes | `36BC3A7BBEAAD1ECF33A97465DA041171BDD205F780A171D8EC712B16174E8B8` |

---

## 3. Acoustic Rationale & Trigger Seam Mapping

### SFX-41: Arena Ruin Wind Bed (BT-151)
- **Acoustic Character:** Desolate, mournful mountain wind whistling across shattered arena masonry. Gentle frequency contour sitting below combat telegraphs.
- **Candidate Differentiation:** Option A provides expansive, broad atmospheric wind without high-frequency harshness; Option B introduces dynamic gust pressure suited for turbulent weather; Option C incorporates distant choral/drone undertones.
- **Seam & Mix Strategy:** Targeted for `ARPGArenaAmbience` (`Wind`). Assigned to `SC_SFX` ambient submix at \(-18\text{ dB}\) to \(-24\text{ dB}\) with 2D non-spatial delivery.

### SFX-42: Distant Brazier Ember Crackle (BT-152)
- **Acoustic Character:** Intimate, organic fire crackle with popping charcoal embers and soft air rush, grounding player orientation relative to arena braziers.
- **Candidate Differentiation:** Option A provides a full-spectrum organic wood fire cue; Option B features crisp high-frequency ash flutter and transient spark snaps; Option C yields a deeper, warmer bonfire roar.
- **Seam & Mix Strategy:** Requires placed positional ambient emitters in `L_SevarogArena`. Assigned to 3D spatial attenuation with logarithmic falloff (\(200\text{ cm}\) inner radius, \(1200\text{ cm}\) max distance) and binaural spatialization.

### SFX-43: Subterranean Arena Drone Bed (BT-153)
- **Acoustic Character:** Low-frequency resonant drone (\(40\text{ Hz}\) to \(120\text{ Hz}\)) vibrating through subterranean arena bedrock, establishing ominous tension.
- **Candidate Differentiation:** Option A offers a deep, otherworldly cosmic rift hum; Option B supplies deep low-passed wind resonance; Option C captures low-end rubble settling.
- **Seam & Mix Strategy:** Prospective secondary channel on arena ambience. Non-spatial 2D sub-bass bed at \(-20\text{ dB}\), dynamically ducked during Phase 2 boss music transitions.

### SFX-44: Arena Boundary Wall Collision (BT-154)
- **Acoustic Character:** Solid, unyielding stone-on-stone thud accompanied by micro-debris clatter, providing physical impact feedback when entities collide with boundary geometry.
- **Candidate Differentiation:** Option A delivers a heavy, dry masonry thud; Option B provides dense armor/stone clatter with transient crunch; Option C supplies a resonant structural shudder.
- **Seam & Mix Strategy:** Requires prospective perimeter collision callback or edge volume trigger. Limit concurrency to 2 instances with oldest voice resolution to prevent audio stutter during sustained boundary pressure.

### SFX-45: Dynamic Fog / Mist Wash (BT-155)
- **Acoustic Character:** Continuous ethereal hiss and vaporous swirl matching low-lying fog and soul-fire mist across the arena floor.
- **Candidate Differentiation:** Option A delivers soft ethereal mist hiss; Option B offers wispy vapor dispersion; Option C provides an expansive composite atmospheric wash.
- **Seam & Mix Strategy:** Requires combat-phase modulation hook. Fades in during Phase 2 transition to emphasize Sevarog's shadowy shroud escalation without masking critical melee impact telegraphs.

---

## 4. Verification & Integrity Confirmation

### Lead verification

Codex independently parsed the 15 candidate rows and verified each package's in-repo path, byte size, and SHA-256 against disk: 15/15 exact. This confirms package identity only; it does not verify serialized cue properties or runtime placement.

1. **Check Script Execution:**
   - Link validation passed cleanly: `python c:/UnrealProject/OneBossFight/Scripts/Tools/check_doc_links.py` (`broken_links=0`).
   - Unit test suite passing: `python -m unittest discover -s c:/UnrealProject/OneBossFight/Scripts/Tools -p "test_sevarog_sfx_cue_plan.py"`.
2. **Strict Guardrails Preserved:**
   - Zero Unreal Editor launches, zero runner executions, zero asset/config modifications, zero locks held, zero git commits or pushes.
   - Raw WAV export and audition compilation remain deferred pending Owner tone direction per [BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md](BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md).
