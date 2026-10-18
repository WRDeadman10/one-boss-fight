# One Boss Fight — Idea

Consolidated from three overlapping planning docs (`..._Development_Plan.md`, `..._Detailed.md`, `..._v2.md`). Those remain as source material; this file is the single working idea.

## 1. One-line pitch

A polished, single-player, third-person **Soulslike boss duel** in Unreal Engine 5, inspired by the *broad conventions* of Elden Ring (lock-on, stamina, dodge rolls, telegraphed boss, two phases), built on a **reusable, data-driven action-RPG foundation** so future bosses, weapons and arenas are content, not new code.

- Inspired by genre conventions only. **No proprietary Elden Ring code, assets, audio, names, characters or exact encounter content.**
- Ready-made licensed assets (Fab or similar) + custom integration and tuning.

## 2. Targets

| Item | Target |
|---|---|
| Engine | **UE 5.5.4** (pinned; locked 2026-10-18) |
| Platform | Windows PC, packaged build |
| Reference GPU | NVIDIA RTX 2060 Super, 8 GB VRAM |
| Resolution | 1920 × 1080 |
| Performance | Sustained 120 FPS (8.33 ms/frame) in a packaged build, full encounter |
| Schedule (est.) | 12–18 weeks, one experienced dev, compatible assets, no major surprises |

120 FPS is a **goal to be proven by profiling**, not a promise. RTX 2060 Super does not support DLSS Frame Generation; do not rely on it.

## 3. Scope

### Must have
- Third-person controller: camera-relative movement, sprint, jump/fall/land.
- Lock-on with target switching and sensible unlock rules.
- Dodge roll: directional, stamina cost, configurable i-frames.
- Light/heavy attacks, buffered combos, charged attack (if assets allow).
- Health, stamina, poise/stagger, hit reactions, death.
- Blocking and optional parrying (feature-flag if animations missing).
- 3–4 weapon categories with distinct movesets (sword, greatsword, spear, optional axe) — **only after weapon #1 is complete**.
- One boss: 6 attacks, 2 phases, telegraphs, recovery windows, stagger, death.
- Encounter loop: trigger, entrance, boss health bar, music, defeat, victory, **retry without restarting the app**.
- One dark-fantasy circular arena: stone floor, pillars, fog/storm, controlled lightning VFX.
- Audio/feedback for swings, hits, dodges, phase change, victory, defeat.
- Packaged Windows build.

### Should have
Controller support, rebindable input, audio/graphics options, small save/settings system, data-driven difficulty, training dummy/test map, debug overlay.

### Out of scope (v1)
Open world, multiplayer, quests/dialogue, loot/crafting/large inventory, multiple bosses/levels, Elden Ring-scale content, guaranteed 120 FPS before profiling.

## 4. Success definition

1. Player can launch the packaged build and finish the encounter.
2. All required combat actions work.
3. Boss is readable and fair; phase transition works.
4. Retry/reset works repeatedly with no stale state.
5. A new weapon is added mostly through data + assets.
6. A second boss reuses the combat/health/encounter foundation.
7. Performance is measured and reported honestly against the target.

## 5. Tech stack

| Concern | Choice |
|---|---|
| Core | C++ base classes + Blueprint configuration |
| Input | Enhanced Input (no hardcoded key checks) |
| Movement | Character Movement Component |
| Animation | Anim Blueprints, Montages, Anim Notifies; Motion Warping/IK where useful |
| Attributes/abilities | **Custom C++ components, no GAS** (decided). Health/stamina/poise live in one attribute component; combat is frame-data driven (animation-owned hit/cancel/i-frame windows), like Souls games. |
| Boss AI | **Custom C++ weighted action selector** in `UBossCombatComponent` (distance-gated candidate attacks, weights, cooldowns, interrupts) + a **thin StateTree for top-level states only** (decided). No Behavior Tree. |
| Data | Data Assets / Primary Data Assets |
| UI | UMG (event-driven, UI never owns gameplay state) |
| VFX | Niagara |
| Loading | Asset Manager + soft references |
| Profiling | `stat unit/gpu/game/anim/memory`, Unreal Insights |
| Source control | Git + Git LFS, or Perforce |

**Responsibility split (no GAS):** Attribute component = health/stamina/poise values, regen, costs. Combat component = attack state, weapon trace windows, combo routing, per-swing hit tracking, cancel windows. Animation = presentation/timing events (notifies), not sole authority on persistent state. Encounter manager = lifecycle/reset. Boss combat component = attack selection.

**"Exact like Elden Ring" interpretation:** Elden Ring runs on FromSoftware's in-house engine, so the code cannot be copied. We copy the *design*: frame-data combat, i-frames, poise, stamina, and boss AI as weighted, distance-gated action selection with interrupts. Implemented in UE C++, not GAS or Behavior Trees.

**Toolchain (verified 2026-10-18):** UE 5.5.4 at `C:\Program Files\Epic Games\UE_5.5`. Visual Studio 2026 (18.7), MSVC 14.51, Windows SDK 10.0.26100. UE 5.5 prefers MSVC 14.38; 14.51 is treated as VS2022 with a "not preferred" warning and is untested. Fallback: install MSVC 14.38 (17.8) from the VS Installer. Project folder: `Documents\Unreal Projects\OneBossFight`. Editor MCP: UnrealClaude plugin (localhost:3000) via its node bridge. Blender MCP connected.

## 6. Architecture

```text
Source/ActionRPG/
├── Characters/   ARPGCharacterBase, ARPGPlayerCharacter, ARPGBossCharacter
├── Combat/       CombatComponent, TargetLockComponent, HitDetection, DamageTypes
├── Weapons/      WeaponBase, WeaponComponent, WeaponData
├── Attributes/   AttributeComponent (health/stamina/poise)
├── AI/           BossController, BossCombatComponent, BossAttackData
├── Encounters/   EncounterManager/Subsystem, EncounterTrigger
├── Interaction/
└── SaveSystem/

Content/ActionRPG/
  Characters, Animations, Weapons, Bosses, AI, GameplayAbilities,
  GameplayEffects, Data, UI, VFX, Audio, Environment, Levels, Tests
```

Naming: `BP_` `DA_` `PDA_` `ABP_` `M_` `MI_` `NS_` `SFX_` `WBP_` `IA_` `IMC_`.

**One owner per piece of state** (health, stamina, combat state, attack state, encounter state). Boss and player share the same health/damage interfaces — no separate boss damage system. Core combat must not depend on a boss name, arena, or hardcoded threshold.

| System | Owns |
|---|---|
| `ARPGCharacterBase` | Shared health/damage interface, hit reaction, stagger/death hooks |
| `ARPGPlayerCharacter` | Input, movement, camera integration, equipment |
| `UCombatComponent` | Attack state, combo windows, hit windows, combat rules |
| `UTargetLockComponent` | Target selection, retention, switching |
| `UWeaponComponent` | Equip/swap, moveset data |
| `UBossCombatComponent` | Attack selection, cooldowns, telegraphs, recovery, phase coordination |
| `UEncounterSubsystem` | Start / victory / defeat / reset, UI/audio coordination |

## 7. Player combat design

**Logical states:** Locomotion, Attacking, ComboWindow, Recovery, Dodging, Blocking, Parrying, Staggered, Dead. Transitions are explicit (e.g. attack → dodge only inside an authored cancel window; dead never returns to locomotion without reset). This is *logic*, not one Anim BP state per entry.

**Attack lifecycle:** Startup (telegraph, hitbox off) → Active (hit detection on) → Recovery (cannot hit) → Complete/Cancel (guaranteed cleanup).

**Hit detection:**
- Weapon traces between socket positions during active window; sweep, not single overlap, for fast weapons.
- Per-swing hit-actor list, cleared at attack start; one authoritative damage function.
- Multi-hit only as explicit attack property.
- Cleanup on cancel/interrupt/death — never depend on a notify that may not fire.
- Debug draw for traces and results.

**Dodge:** stamina deducted once at start; i-frame start/end configurable; no duplicate invulnerability; buffering rules defined.
**Stamina:** max, per-action cost, regen rate + delay, behaviour at zero, single authoritative value.
**Poise:** separate from health; per-attack poise damage; stagger at threshold; no per-frame retrigger; stagger+death same hit handled.
**Block/Parry:** guard damage reduction + stamina cost, guard-break; narrow parry window with success/fail/recovery; one incoming attack cannot parry twice.

**Weapon Data Asset fields:** name/category, mesh/socket/hand pose, light/heavy/charged attacks, montage + sections, damage, poise damage, stamina cost, startup/active/recovery/combo timings, trace config/reach, guard properties, hit VFX/audio/trails, cancel permissions.

## 8. Boss design

**States:** Dormant → EncounterTriggered → Entrance → CombatActive → Repositioning → Telegraphing → ExecutingAttack → Recovery → Staggered → PhaseTransition → Defeated → Resetting. High-level AI calls the attack system; it never implements traces/damage itself.

**Attack selection per decision:** read distance/target → read phase, health, stagger, cooldowns, history → filter invalid → score by weights → apply repetition limits + small reaction delay → attack or reposition → telegraph and commit per tracking rules.

**Six initial attacks** (matched to whatever animations the boss pack actually has):

| # | Attack | Purpose |
|---|---|---|
| 1 | Horizontal sweep | Close-range space control; dodge through/away from arc |
| 2 | Overhead slam | Slow, high damage, long punish window |
| 3 | Forward lunge | Punishes distance; constrained tracking after commit |
| 4 | Three-hit combo | Forces observing the whole sequence; no infinite chaining |
| 5 | Ground shockwave | Area denial; explicit radius/timing/safe area |
| 6 | Lightning special (phase 2) | Signature move; distinct charge cue, authored danger zone, restrained VFX burst |

**Attack definition fields:** ID, required phase, min/max range, arc requirements, startup/active/recovery, damage, poise damage, cooldown, repetition limit, selection conditions/weights, animation/telegraph/sound/VFX/collision profile, movement/rotation allowed during startup/execution.

**Phases:**
- Phase 1 teaches patterns: readable telegraphs, generous recovery.
- Phase 2: one transition at a health threshold, adds lightning + altered combos/timings — **change patterns and timing, not just inflate damage**. Non-combat transition state, no duplicate transitions from same-frame hits, death-during-transition handled.

**Fairness rules:** every major attack telegraphed; hit geometry matches visuals; limited wind-up tracking; punish windows after big attacks; no unreachable attack picks; no spam of one high-damage move; difficulty tuned via timing/spacing/patterns first, damage last; difficulty is data-driven.

## 9. Encounter lifecycle

- **Start:** trigger/interact → lock state (no double start) → optional arena lock → entrance → boss UI + music → enable AI after entrance.
- **Player defeat:** disable input/hit detection, death sequence, suspend boss, retry/exit UI, cleanup timers/effects, restore player, reset boss (health, phase, cooldowns, AI, transform), restore triggers/UI.
- **Boss victory:** disable boss logic/hit detection, death sequence, stop combat music + victory audio, update UI/state, block post-death damage, restart/menu.
- **Reset invariants:** no stale attack timers, target lock, hit lists, AI tasks/timers or damage volumes; health/stamina/phase/cooldowns/UI at defined values; next encounter starts without app restart.

## 10. Arena and visuals

Dark-fantasy circular stone arena, large pillars, ruined architecture, selected debris (never cluttering the combat surface or hiding hit geometry), atmospheric depth, warm/cool lighting contrast, controlled fog/storm.

Workflow: greybox → verify movement/camera/boss spacing → composition and sightlines → swap in modular assets → materials → lighting/atmosphere → VFX/audio → profile → cull/reduce.

**Lightning VFX:** Niagara and/or spline meshes; emissive; brief controlled flash (must not blow out exposure and hide combat); synced impact + sound; capped particles/lifetimes; spawn on demand, clean up after; lower-cost fallback setting. No continuously active dynamic lights.

**UI:** player health/stamina, boss bar + name, equipped weapon, optional heal count, death/retry, victory, pause/options, dev debug overlay.

## 11. Rendering and performance plan (RTX 2060 Super)

Start simple, add features only when measured performance allows.

| Setting | Start with |
|---|---|
| Resolution | 1920 × 1080 |
| FPS | Uncapped while profiling; 120 cap only after validation; VSync off for raw measurement |
| GI | Baked/static for the static arena; benchmark Lumen separately (Epic's High preset targets ~60 FPS on consoles — don't assume it fits 120) |
| Reflections | Reflection captures + SSR |
| Ray tracing | Off |
| Nanite | Benchmark vs conventional LODs on static meshes |
| Shadows | Limit shadow-casting dynamic lights/casters |
| Volumetric fog | Low quality / localized; test during lightning |
| AA | Benchmark TSR/TAA/alternatives |
| DLSS | Super Resolution optional; **Frame Generation unsupported** |
| Niagara | Cap counts, overdraw, translucency, lifetime |
| Post | Moderate bloom; restrained DoF/motion blur |
| Textures | Mostly 1K–2K; 4K only for hero assets |

**Provisional GPU budget (8.33 ms; planning numbers, replace with measurements):** Lighting 2.2 · Geometry 1.5 · Shadows 1.2 · VFX 0.9 · Post 0.8 · Other 0.8 = 7.4 ms, 0.93 ms headroom. CPU and GPU overlap — never sum thread times to get frame time.

**VRAM:** working target ~6–7 GB of the 8 GB (a target, not a guarantee); texture streaming, LODs, culling, soft refs; stream future bosses/arenas; check for growth across resets; measure in packaged build.

**Release gate (packaged build, target PC, full fight incl. phase 2 + lightning):**
1. Average ≥ 120 FPS.
2. 99th-percentile frame time ≤ 8.33 ms (strict ideal); no recurring disruptive spikes.
3. 10-minute soak with repeated resets: no crashes, no memory growth, no timing bugs.

If missed, **document the real result and gap** — never claim success on average FPS alone.

**Profiling workflow:** baseline capture → reproduce → classify (game thread / render thread / GPU / memory / shader compile / streaming) → change one variable → recapture → log in `PERFORMANCE_LOG.md` → keep only wins. Never optimize from editor FPS.

## 12. Asset strategy

Source: Fab (https://www.fab.com/) — verify current license, engine version, dependencies per asset.

**Buy order:** 1) player + matching animation set, 2) boss + attack set, 3) environment, 4) first weapon's meshes/animations, 5) remaining weapons, 6) VFX/audio.

**Per-asset checklist:** supports pinned UE5 version · includes the real animations needed (not just a mesh) · skeleton compatible/retargetable (and legally so) · root motion vs in-place understood · sockets/hand poses configurable · materials affordable at 1080p/120 · sensible texture/mesh sizes · license covers packaged build · plugin/dependency list known · tested with a small sample first.

**Rule:** do **not** buy multiple big packs before one complete player-to-boss animation pipeline is proven. Biggest schedule risk is incompatible rigs / missing attack animations, not gameplay code. Missing animations → clearly-marked placeholder + recorded dependency.

## 13. Milestones

| M | Weeks | Focus | Exit criteria |
|---|---|---|---|
| 1 | 1–2 | Foundation: pin UE version, C++ project, source control, folders, input/camera/movement, greybox arena, **packaged benchmark + baseline**, decision log, license register | Builds/launches, movement works, repeatable benchmark documented |
| 2 | 3–5 | Player combat: rig/anims, health/stamina, lock-on, dodge, weapon #1, attack state machine, hit detection, hit reactions, death, debug viz | Beat a dummy; no duplicate hits; no stuck states |
| 3 | 6–8 | Boss + encounter loop: rig/anims, state flow, attack data/selection, 6 attacks, phase transition, stagger/death, boss UI, encounter manager, defeat/victory/reset | Fight winnable and losable repeatedly (greybox OK); reset clean; no softlocks |
| 4 | 9–11 | Final content: arena, remaining weapons, materials/lighting, lightning/impact VFX, audio, entrance/death presentation, UI polish | Visually complete; no undocumented placeholders |
| 5 | 12–15 | Optimization/tuning: profile worst phase, optimize, reduce ticks/UI work, tune fairness | Packaged perf measured; target met or gap documented |
| 6 | 16–18 | Hardening: test weapon via data only, test boss config, save/settings, soak, Shipping build, docs | Release candidate; extension path validated |

Profile on the target GPU from week 1, not at the end.

## 14. Acceptance tests (summary)

Movement/camera stability · lock-on · every attack's cost/damage/recovery · no repeated damage per swing · cancel rules only where documented · dodge direction/cost/i-frames vs every boss attack · stamina and poise thresholds · weapon swap safety · all 6 boss attacks reachable and fair · no infinite attack loops · phase transition fires once (single and rapid damage) · encounter start/defeat/victory/reset repeatable · UI reflects authoritative state · VFX aligned and not obscuring · 10-min memory soak · packaged 1080p perf run · new weapon via data only · second boss on shared systems.

Record pass/fail, build ID, hardware, settings, evidence for release-critical tests.

## 15. Engineering rules (for human or AI implementer)

- Inspect the project before changing it; never assume an asset/plugin/class/input action exists until verified.
- Small, testable steps; compile after each coherent C++ change.
- C++ for reusable systems, Blueprint/Data Assets for tuning/presentation; no giant monolithic Blueprints.
- Tunables in Data Assets/tables, not scattered constants.
- Prefer events/timers/notifies over Tick; justify any Tick.
- One authoritative path for damage and hit reactions.
- No expensive rendering features by default; profile first.
- Never claim 120 FPS without packaged-build captures on target hardware.
- Dev-only debug overlay (health, stamina, states, attack phase, lock target, boss state/cooldowns, encounter state, recent hits) and debug draw (traces, arcs, radii, ranges); compile out of Shipping.
- Don't mark a feature done until implemented **and** tested.

**Documentation to keep:** `README.md`, `Documentation/DECISIONS.md` (UE version, module name, GAS vs custom, StateTree vs BT, rigs/retarget, lighting strategy, target PC, test scene/settings), `ASSET_LICENSES.md`, `PERFORMANCE_LOG.md`, `COMBAT_DATA.md`, `BOSS_AUTHORING.md`, `TEST_PLAN.md`, `KNOWN_ISSUES.md`.

## 16. Reuse pipeline (the long-term payoff)

- **New weapon:** import/validate assets → Data Asset → attacks/montages/costs/traces → sockets/FX/audio → regression + perf test.
- **New boss:** import/validate rig+anims → boss config Data Asset → attacks/ranges/cooldowns/phases → AI + encounter sequence → arena/VFX config → combat/reset/perf tests.
- **New arena:** modular assets → collision/nav → lighting/post → profile shadows/fog/VFX → validate boundaries/camera.

## 17. Top risks

| Risk | Mitigation |
|---|---|
| Incompatible player/boss rigs | Test a minimal animation set before committing to packs |
| Missing attack animations | Design attacks around available animations; log custom-animation needs |
| Multi-hit per swing | Per-swing hit list, centralized damage |
| Stuck state after interrupt | Explicit cancel/cleanup paths |
| Stale timers/effects after reset | Centralized reset, test repeated cycles |
| Unfair boss tracking | Limit tracking after commit; test dodge windows |
| Lumen/fog/shadows blow the budget | Start simple, add and profile one at a time |
| Average FPS hides bad pacing | Track percentiles and worst-case captures |
| VRAM spikes | Smaller textures, streaming, packaged peak checks |
| Unclear licenses/dependencies | License register, verify before shipping |
| Engine upgrade breaks assets | Pin version; upgrade only with tested reason |

## 18. Immediate next steps

- [ ] Pick and pin a UE5 minor version after checking asset compatibility.
- [ ] Create the C++ project (module `ActionRPG`) + source control in this repo.
- [ ] Build packaged 1080p benchmark scene; record hardware/driver/settings baseline.
- [ ] Choose one compatible player + boss + animation pipeline; prove it with a tiny test.
- [ ] Implement weapon #1, dodge, lock-on, damage.
- [ ] Finish the greybox boss fight before any final art.
- [ ] Add remaining attacks and weapon categories.
- [ ] Swap in final arena/VFX/audio.
- [ ] Profile, optimize, run acceptance tests, document results.

## 19. References

- Fab: https://www.fab.com/
- UE docs: https://dev.epicgames.com/documentation/en-us/unreal-engine/
- GAS: https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-for-unreal-engine
- StateTree: https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-state-tree-in-unreal-engine
- Profiling: https://dev.epicgames.com/documentation/en-us/unreal-engine/introduction-to-performance-profiling-and-configuration

## 20. Bottom line

Prove the whole loop — **one weapon, one boss, greybox arena, packaged at 1080p** — before spending on final art. Then scale content through data. Biggest threats: incompatible animation assets, unreliable combat timing, unfair boss behavior, expensive rendering settings. Kill those early.
