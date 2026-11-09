# Queue SFX - Boss Duel Audio Implementation

**Authority:** Project Owner Order & Claude Directives `[C-1169]`, `[C-1181]`, `[C-1197]` (2026-11-09).
**Owner:** Antigravity (`Art/Review/Audit [A-###]`).  
**Rules:**
- Use **ONLY** content already present in the project repository (`ParagonSevarog`, `ParagonGreystone`, `ParagonGrux`, `ParagonSteel`, `RealisticSwordSoundEffects`, `AdvancedARPGCombat`, `StarterContent`, `Vefects`). No external downloads, no external services.
- Every sound addition is strictly **optional/opt-in data** with baseline silence/existing behavior as default until approved by ear by the project owner.
- Follow `ENGINE_LOCK.json` protocols; launch editor commands with `-nosound` during wiring/verification.
- Off-repo media rule (`[C-1181]`): Raw extracted WAVs and compiled MP4/MP3 audition reels live in `D:/FightVideo/SFX_audition/`. Only code scripts and documentation manifests are tracked in git.
- Priority taxonomy ordered per Claude directive `[C-1197]`: (a) Boss attack whooshes -> (d) Phase transition stingers -> (b) Player defense/foley -> (e) Posture/stagger/UI -> (c) Arena ambiance.

---

## Batch 1 - SFX Foundation & Candidate Audit

| Task | Work | Status | Acceptance Criteria / Deliverable |
|---|---|---|---|
| SFX-01 | **Coverage Table & Gap Audit:** Map every gameplay event (Player, Boss, World) to current audio cue/class and file:line call site; identify and categorize all missing audio gaps. | **DONE** | Complete audit table in [`Documentation/Boss/SFX_01_GAMEPLAY_AUDIO_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/SFX_01_GAMEPLAY_AUDIO_AUDIT.md) citing exact source and asset paths. |
| SFX-02 | **Candidate Selection (1-3 per gap):** Select high-fidelity candidate sound cues from repository asset packs for top-priority gaps (Parry Success, Boss Parry Recoil, Phase 2 Aura Ignite, Backstep Whoosh, Stance Break Shatter). | **DONE** | Documented candidate list with asset paths, durations, volume/pitch profiles, and design rationale in [`Documentation/Boss/SFX_02_CANDIDATE_SELECTION.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/SFX_02_CANDIDATE_SELECTION.md). |
| SFX-03 | **Owner Audition Pack:** Compile candidate audio cues into a labeled audition reel (`.mp4` / `.mp3`) in `D:/FightVideo/SFX_audition/` for Owner review. | **DONE** | Initial 15-candidate reel delivered (`SFX_Audition_Reel.mp4` 1.2MB, `SFX_Audition_Reel.mp3` 609KB). Follow-up C-1186 Parry Addendum Reel compiled with 3 short 0.2-0.6s metallic clangs (`Parry_Addendum_Reel.mp4` 137KB, `Parry_Addendum_Reel.mp3` 242KB). Off-repo at `D:/FightVideo/SFX_audition/`. Manifest in [`Documentation/Boss/SFX_03_AUDITION_MANIFEST.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/SFX_03_AUDITION_MANIFEST.md). |
| SFX-04 | **Wiring Plan (No Apply):** Specify exact integration attachment points (AnimNotifies on Montages, C++ Event Dispatchers, `URPGPlayerParry`, `URPGTier2BossPresentation`, `URPGBossStagger`). | **DONE** | Scripted, fail-closed wiring plan with refuse-if-exists assertions and verification contracts in [`Documentation/Boss/SFX_04_WIRING_PLAN.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/SFX_04_WIRING_PLAN.md). 4/4 contracts PASS. |
| SFX-05 | **Verification & Staged Rollout:** Implement Owner-approved audio cues under `ENGINE_LOCK`; verify playback via diagnostic log markers during Lead PIE. | QUEUED | Live execution logs proving cues trigger at exact frame/timestamp without clipping or hitches. |

---

## Batch 2 - Combat Impact & Reaction Audio

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-06 | Player Guard Counter clash & heavy impact sound. | QUEUED | Auditioned and wired to `GuardCounter` montage impact. |
| SFX-07 | Player Air Plunge crash & ground shockwave audio. | QUEUED | Tied to `AM_ER_Attack_Air_Heavy_Plunge` land frame. |
| SFX-08 | Boss A4 Low Sweep blade ground friction whoosh. | QUEUED | Wired to `AN_Boss01_A4_LowSweep` active blade arc. |
| SFX-09 | Boss A5 Javelin throw summon & release whooshes. | QUEUED | Resolves KI-068 audio placeholder for A5. |
| SFX-10 | Boss Stance Break / Posture Shatter heavy glass/stone impact. | QUEUED | Wired to `URPGBossStagger::StartStagger` entry. |

---

## Batch 3 - Boss Attack Whooshes & Heavy Foley (C-1197 Priority a)

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-11 | Boss A1 Horizontal Slash high-speed blade air whoosh. | QUEUED | Candidates auditioned; wired to `AN_Boss01_A1` blade arc. |
| SFX-12 | Boss A2 Overhead Cleave heavy downward wind pressure whoosh. | QUEUED | Candidates auditioned; wired to `AN_Boss01_A2` downward stroke. |
| SFX-13 | Boss A3 Ground Stomp shockwave sub-bass thud. | QUEUED | Candidates auditioned; wired to `AN_Boss01_A3` footfall frame. |
| SFX-14 | Boss Mid01 Forward Thrust piercing air wake whoosh. | QUEUED | Candidates auditioned; wired to `AN_Boss01_Mid01` thrust apex. |
| SFX-15 | Boss Sprint Gap-Closer sweeping horizontal blade whoosh. | QUEUED | Candidates auditioned; wired to `AN_Boss01_Sprint` strike release. |

---

## Batch 4 - Phase Transition & Roar Audio (C-1197 Priority d)

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-16 | Boss Phase 2 Awakening vocal roar / spectral screech. | QUEUED | Auditioned and wired to `URPGTier2BossPresentation` trigger. |
| SFX-17 | Phase 2 Ember Aura Ignite explosion burst cue. | QUEUED | Attached to `PhaseTwoAuraEffect` spawn timestamp. |
| SFX-18 | Persistent fiery aura ambient loop (low-pass, low volume). | QUEUED | Attached to `PhaseTwoAuraComponent` with smooth fade-in. |
| SFX-19 | Phase 2 transition ground rupture shockwave crackle. | QUEUED | Synchronized with floor decal / crack emergence. |
| SFX-20 | Phase transition stinger musical swell / combat tempo shift. | QUEUED | Subdued opt-in dark stinger marking Tier 2 entry. |

---

## Batch 5 - Player Defense & Combat Foley (C-1197 Priority b)

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-21 | Player Shield Standard Block metallic thud & deflection ring. | QUEUED | Wired to standard block hit reaction. |
| SFX-22 | Player Deflect / Glancing Blow spark hiss. | QUEUED | Wired to partial block / deflection notification. |
| SFX-23 | Player Healing Flask chug & recovery shimmer stinger. | QUEUED | Synchronized with flask consumption event. |
| SFX-24 | Player Dodge Roll armor leather/metal rustle & thud. | QUEUED | Attached to dodge roll start and recovery frames. |
| SFX-25 | Player Weapon Draw & Sheathe metallic scrape foley. | QUEUED | Tied to combat stance entry and exit notifies. |

---

## Batch 6 - Posture, Stagger & Execution Audio (C-1197 Priority e)

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-26 | Boss Posture Damage threshold warning pulse / metallic stress. | QUEUED | Subdued audio cue triggered when posture < 25%. |
| SFX-27 | Boss Heavy Stagger loop breathing / groaning foley. | QUEUED | Looped audio during vulnerable stagger window. |
| SFX-28 | Critical Execution / Riposte impale crack & flesh tear. | QUEUED | Synchronized with execution strike hit frame. |
| SFX-29 | Boss Stagger Recovery armor rattle & stance re-assertion. | QUEUED | Tied to `URPGBossStagger::EndStagger` recovery frame. |
| SFX-30 | Player Stance Break / Guard Break shield pushback groan. | QUEUED | Triggered on player posture exhaustion. |

---

## Batch 7 - Boss Movement & Spectral Foley

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-31 | Boss Heavy Armor Footsteps (walk / run stone impacts). | QUEUED | Wired to `AN_Boss01_Footstep_L/R` anim notifies. |
| SFX-32 | Boss Dash / Teleport spectral ethereal whoosh. | QUEUED | Tied to rapid repositioning movement notifies. |
| SFX-33 | Boss Cape / Tattered Cloth heavy wind flutter. | QUEUED | Attached to rapid turn and swing montage frames. |
| SFX-34 | Boss Idle breathing / subterranean chest rumble foley. | QUEUED | Subdued spatialized loop at boss torso bone. |
| SFX-35 | Boss Ground Skid stone friction deceleration audio. | QUEUED | Triggered on heavy swing recovery ground slide. |

---

## Batch 8 - Combat UI & Feedback Audio (C-1197 Priority e)

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-36 | Target Lock-On Acquire snap/focus click. | QUEUED | Wired to lock-on engage event. |
| SFX-37 | Target Lock-On Switch target sweep whoosh. | QUEUED | Wired to target change event. |
| SFX-38 | Player Low Stamina panting audio loop (< 20% stamina). | QUEUED | Attached to player HUD stamina warning trigger. |
| SFX-39 | Player Critical Health heartbeat muffled thumping loop. | QUEUED | Attached to player low health post-process trigger. |
| SFX-40 | Player Defeat / Death dark low-frequency stinger. | QUEUED | Tied to player death ability entry frame. |

---

## Batch 9 - Arena Environment & Ambience (C-1197 Priority c)

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-41 | Arena Ruin Wind whistling through shattered columns. | QUEUED | Ambient 2D sound loop in `L_SevarogArena`. |
| SFX-42 | Distant Ember Crackle and ash flutter ambient bed. | QUEUED | Positional ambient emitter near arena flame braziers. |
| SFX-43 | Low Frequency Subterranean Arena Drone bed. | QUEUED | Sub-bass spatial rumble enhancing arena tension. |
| SFX-44 | Arena Stone Boundary Wall collision thud. | QUEUED | Tied to player/boss arena perimeter hit reactions. |
| SFX-45 | Dynamic Arena Rain / Fog atmospheric audio wash. | QUEUED | Environmental bed modulated by combat state. |

---

## Batch 10 - Final Mix Balance, Attenuation & Concurrency

| Task | Work | Status | Acceptance Criteria |
|---|---|---|---|
| SFX-46 | SoundClass Bus Hierarchy audit (Master, SFX, Foley, UI, Music). | QUEUED | Clean routing of all added sound cues into proper SoundClasses. |
| SFX-47 | SoundConcurrency rules & instance limit configuration. | QUEUED | Prevent voice voice-stealing and clipping on rapid swings. |
| SFX-48 | Spatial Attenuation curves & 3D falloff distance tuning. | QUEUED | Natural 3D falloff profiles (inner 200cm, outer 2500cm). |
| SFX-49 | Combat Dynamic Audio Ducking profile. | QUEUED | Duck ambient/foley by 3-6dB during parry and execution hits. |
| SFX-50 | Master Packaging Audio Audit & Shipping Cook verification. | QUEUED | 0 missing references, 0 cook warnings, 0 voice starvation. |
