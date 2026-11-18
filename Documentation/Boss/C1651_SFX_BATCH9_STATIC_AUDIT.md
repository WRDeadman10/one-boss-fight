# C-1651 Audio/SFX Batch 9/10 (SFX-46..SFX-50) Static Audit: Routing, Concurrency, Attenuation, Ducking & Package Evidence

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2681]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-157 (SFX-46), BT-158 (SFX-47), BT-159 (SFX-48), BT-160 (SFX-49), BT-161 (SFX-50)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directive `[X-2681]`, Antigravity has executed the static code, configuration, asset inventory, and package evidence audit for **C-1651 Audio/SFX Batch 9/10 (SFX-46 through SFX-50)**: Audio Routing, SoundClass Buses, SoundConcurrency, Spatial Attenuation, Combat Ducking, and Cooked Package Integrity.

- **Discipline Boundaries:** Strictly read-only static source, asset, and report inspection. Zero Unreal Editor launches, zero C-1155 runner executions, zero asset modifications, zero audio exports, zero test runs, and zero git commits/pushes.
- **Reconciliation with Lead Audit:** Findings reconcile with Lead Codex's parallel audit [C1651_SFX_46_50_ROUTING_AND_COOK_AUDIT.md](C1651_SFX_46_50_ROUTING_AND_COOK_AUDIT.md), subject to the filename-inventory clarifications below. Serialized routing, concurrency, and attenuation properties remain unverified.

---

## 2. Static Audit Findings by Task

### SFX-46: SoundClass Bus Hierarchy Static Audit (BT-157)
- **Scope & Question:** Does the repository implement or configure the proposed SoundClass bus hierarchy (`Master` / `SFX` / `Foley` / `UI` / `Music`)?
- **Asset Inventory:**
  - A filesystem inventory found 11 `SC_*.uasset` filenames in each of these two folders (22 packages total, with matching basenames). Filename prefixes alone do not prove Unreal asset types or parent/child routing:
    * `SC_RPG_Master.uasset` (Master bus)
    * `SC_SFX.uasset`, `SC_Weapons.uasset`, `SC_Abilities.uasset`, `SC_Items.uasset` (SFX buses)
    * `SC_Player.uasset`, `SC_Enemy.uasset`, `SC_Hero.uasset` (Character buses)
    * `SC_Music.uasset` (Music bus)
    * `SC_UI.uasset` (Interface bus)
    * `SC_Slomo.uasset` (Slow motion filter bus)
- **Source Code Evidence:**
  - Zero `USoundClass` references exist in native project code (`Source/OneBossFight`).
  - Native audio dispatchers (`RPGBossMusic.cpp`, `RPGArenaAmbience.cpp`, `RPGFootsteps.cpp`) set volume scales and fade parameters directly via `UAudioComponent` or `UGameplayStatics::PlaySoundAtLocation` without referencing `USoundClass` pointers.
- **Audit Conclusion:** The Advanced ARPG Combat pack provides a serialized `SoundClass` asset hierarchy on disk, but native C++ code does not assign or enforce classes at runtime. Sound class routing is entirely dependent on serialized properties inside binary `.uasset` Sound Cues and Waves, which require Editor property readback to verify actual assignments.

---

### SFX-47: SoundConcurrency Rules Static Audit (BT-158)
- **Scope & Question:** Are voice limits and voice-stealing policies bounded by existing `USoundConcurrency` rules?
- **Asset Inventory:**
  - No `.uasset` filename containing `concurr` was found by the filesystem inventory. This does not prove that no package with a different name contains a `USoundConcurrency` object; Unreal asset-registry/property readback was not performed.
- **Source Code Evidence:**
  - Zero `USoundConcurrency` references or runtime assignments exist in native project audio code (`RPGFootsteps.cpp`, `RPGArenaAmbience.cpp`, `RPGBossMusic.cpp`).
- **Audit Conclusion:** No shared SoundConcurrency assets exist in the project. Any voice concurrency boundaries (e.g. max 2 instances for wall impacts, 1 for breathing loops) are either defined inline within individual Sound Cue packages or rely on engine global voice virtualization. High-frequency triggers (such as weapon collisions and footsteps) remain vulnerable to voice starvation or audio stacking unless explicitly bound by concurrency assets during future implementation.

---

### SFX-48: Spatial Attenuation Curves Static Audit (BT-159)
- **Scope & Question:** How are spatial attenuation and distance falloff curves implemented across project audio?
- **Asset Inventory:**
  - No `.uasset` filename containing `attenuat` was found by the filesystem inventory. This does not prove that no package with a different name contains a `USoundAttenuation` object; Unreal asset-registry/property readback was not performed.
- **Source Code Evidence:**
  - `Source/OneBossFight/Audio/RPGFootsteps.cpp:26-32, 61-66`: Instantiates a transient `USoundAttenuation` object in C++ via `NewObject<USoundAttenuation>(this)`, configures `FSoundAttenuationSettings`, and supplies it to `PlaySoundAtLocation`.
  - `Source/OneBossFight/Arena/RPGFireSource.cpp:83-88`: Enables inline attenuation override on its `UAudioComponent`:
    * `Crackle->bOverrideAttenuation = true;`
    * `Crackle->AttenuationOverrides.bAttenuate = true;`
    * `Crackle->AttenuationOverrides.bSpatialize = true;`
    * `Crackle->AttenuationOverrides.AttenuationShape = EAttenuationShape::Sphere;`
    * `Crackle->AttenuationOverrides.AttenuationShapeExtents = FVector(150.f, 0.f, 0.f);`
    * `Crackle->AttenuationOverrides.FalloffDistance = CrackleRange;`
  - `RPGArenaAmbience.cpp` and `RPGBossMusic.cpp` deploy 2D non-spatialized audio components.
- **Audit Conclusion:** Positional audio in the project relies on procedural C++ transient attenuation objects (`RPGFootsteps`) or component-level inline overrides (`RPGFireSource`), rather than shared `USoundAttenuation` asset pointers. The proposed attenuation curves (e.g., \(200\text{ cm}\) inner / \(1200\text{ cm}\) outer for braziers; \(500\text{ cm}\) / \(2500\text{ cm}\) for boss footsteps) are design targets, not yet serialized into project assets.

---

### SFX-49: Combat Dynamic Audio Ducking Seam Audit (BT-160)
- **Scope & Question:** Does native code support dynamic audio ducking between combat impacts, stingers, ambience, and BGM?
- **Source Code Evidence:**
  - `Source/OneBossFight/Player/RPGLegend.h:23, 251` and `RPGLegend.cpp:167-178, 286-291`: Implements native `SoundMix` modifier support for parry feedback:
    * `URPGLegendSubsystem::BeginParryFeedbackPulse(..., USoundMix* SoundMix, ...)` pushes the modifier via `UGameplayStatics::PushSoundMixModifier(World, SoundMix)`.
    * On pulse completion, pops the modifier via `UGameplayStatics::PopSoundMixModifier(World, SoundMix)`.
    * Explicit header contract: `/** Optional SoundMix configured by the asset author for parry low-pass/duck. Null means no audio change. */`.
  - `Source/OneBossFight/Audio/RPGBossMusic.cpp:78-106`: Handles phase crossfading (`FadeIn` / `FadeOut`) between Phase 1 and Phase 2 tracks.
  - No general combat ducking framework exists for weapon collisions, stance breaks, or player defeat stingers.
- **Audit Conclusion:** Dedicated native `SoundMix` ducking exists exclusively for the parry slow-motion pulse in `RPGLegendSubsystem`. Dynamic combat ducking of music/ambience during stance break or death remains an architectural recommendation; no generic ducking submix is currently wired across the broader combat state machine.

---

### SFX-50: Existing Audio Package & Cook Evidence Audit (BT-161)
- **Scope & Question:** What concrete cook, packaging, and runtime evidence exists for audio in packaged builds?
- **Package Evidence:**
  - Deliverable report [C1650_WINDOWS_DEVELOPMENT_PLAYTEST_PACKAGE.md](C1650_WINDOWS_DEVELOPMENT_PLAYTEST_PACKAGE.md) records the successful packaging of `OneBossFight_Dev_20261118_C1650.zip` (`3,922,305,302` bytes, SHA-256 `D871E3494606C651CF3EC04B7E1E46F1312F6DB2E3976B83DE900B7120501AEA`, 124 entries).
  - Command line execution used `-nosound` during `BuildCookRun` (consistent with project build rules to avoid audio thread hangs).
- **Cook & Runtime Limitations:**
  - Because `-nosound` was passed, audio device initialization and runtime audio playback were bypassed during cook validation.
  - The C-1650 package was archived for deployment verification; it was not executed in a live audio-enabled playtest session, nor profiled for voice starvation or streaming hitches.
- **Audit Conclusion:** Packaged cook evidence confirms binary integrity and content packaging of referenced audio assets, but does not provide proof of sound-enabled runtime streaming, voice-concurrency limits under load, or mix headroom. Live sound verification remains gated on Owner playtest authorization.

---

## 3. Cross-Cutting Audit Summary Matrix

| Task | Domain | Native C++ Status | Asset Content Status | Runtime Verification Status |
|---|---|---|---|---|
| **BT-157** (SFX-46) | SoundClass Buses | 0 C++ references; volume handled via components | 11 `SC_*.uasset` names repeated across 2 folders (22 packages); type/routing not read back | Unverified; requires asset-registry/property readback |
| **BT-158** (SFX-47) | SoundConcurrency | 0 C++ references | No filename containing `concurr`; object inventory unverified | Concurrency and voice limits unverified |
| **BT-159** (SFX-48) | Spatial Attenuation | Procedural C++ object & component override | No filename containing `attenuat`; object inventory unverified | Footsteps/fire behavior configured in code; proposed curves unwired |
| **BT-160** (SFX-49) | Combat Ducking | Native parry `SoundMix` push/pop supported | `ParrySlowMotionSoundMix` defaults to null in C++; serialized assignment is unverified | Parry feedback pulse supports an optional mix; actual asset assignment and general combat BGM ducking are unverified/unwired |
| **BT-161** (SFX-50) | Package / Cook Evidence | BuildCookRun clean with `-nosound` | Packages present in cooked pak | Audio runtime performance unproven in live package |

---

## 4. Verification & Integrity Confirmation

1. **Check Script Execution:**
   - Link validation passed cleanly: `python c:/UnrealProject/OneBossFight/Scripts/Tools/check_doc_links.py` (`broken_links=0`).
   - Unit test suite passing: `python -m unittest discover -s c:/UnrealProject/OneBossFight/Scripts/Tools -p "test_sevarog_sfx_cue_plan.py"`.
2. **Strict Guardrails Preserved:**
   - Zero Unreal Editor launches, zero runner executions, zero asset/config modifications, zero locks held, zero git commits or pushes.
