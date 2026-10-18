# One Boss Fight — Project Execution Plan

How we build `IDEA.md`. Decisions locked: UE 5.5.4, custom C++ combat (no GAS), weighted C++ boss selector + thin StateTree, Fab/free assets, Windows, 1080p / 120 FPS target on RTX 2060 Super.

## 1. Who does what

| Actor | Does | Cannot / should not |
|---|---|---|
| **Claude (files)** | C++ gameplay code, `Build.cs`/`Target.cs`, `.ini` config, Data Asset schemas, automation tests, docs, build/package scripts | Judge game feel; buy assets; run on your GPU for you |
| **Claude via Unreal MCP** | Create/edit Blueprints, Anim BPs, montages' notify setup, Enhanced Input assets, materials, level layout, Data Assets, place actors | Anything the plugin has no tool for (fall back to Editor Python) |
| **Claude via Blender MCP** | Prep meshes: scale/pivot fixes, weapon socket reference points, placeholder meshes, FBX export | Replace animation authoring |
| **You** | Download/buy assets (account + payment actions are yours), playtest feel, approve tuning, run final profiling on the target PC | — |

Loop for every feature: **spec → C++ → headless compile → editor wiring (MCP) → automated test → you playtest → commit.**

## 2. Working rules

- Branches per milestone (`m1-foundation`, `m2-player-combat`, ...), merge to `main` when the exit gate passes. Commit after each working slice.
- Git LFS covers `.uasset`/`.umap`/art/audio (done). `*.blend1` ignored. Source art lives in `SourceArt/`, not the project root (`CuteDragon.blend` should move there).
- Compile from CLI with Unreal Build Tool so the editor need not be closed for header-only logic work; use Live Coding only for small tweaks. Structure changes need an editor restart.
- Anything pure logic (attack selector, attribute rules, hit-tracking, reset invariants) gets an **Automation spec test**. Feel/animation timing gets a **PIE checklist** you run.
- Every milestone has an exit gate (below). No next milestone until the gate passes.
- Docs kept current: `DECISIONS.md`, `PERFORMANCE_LOG.md`, `ASSET_LICENSES.md`, `TEST_PLAN.md`, `KNOWN_ISSUES.md` under `Documentation/`.
- Coding workflow: your `codex-aider-bridge` skill requires the bridge MCP, `code-review-graph` and Ollama/Aider, none of which are connected in this session. Until that's fixed or you waive it, I will not write source files. See §6.

## 3. Milestones

### M0 — Toolchain and project skeleton (days 1–3)
1. C++ module `OneBossFight` (`Source/OneBossFight/`, Target/Editor.Target.cs, game module class), `.uproject` Modules entry.
2. First headless build via UBT. Result decides whether MSVC 14.51 is OK or we install 14.38.
3. Verify the Unreal MCP tools are loaded in a fresh session; Blender MCP smoke test.
4. Folder structure and naming per `IDEA.md`; `Documentation/` stubs; `DECISIONS.md` filled with today's decisions.
5. `Config/DefaultEngine.ini` performance-first defaults: no ray tracing, baked GI for static, TSR/TAA candidates, Enhanced Input default classes.

**Gate:** project builds clean from CLI, opens in editor with the module loaded, MCP reaches both tools.

### M1 — Foundation and benchmark (weeks 1–2)
- Third-person character in C++ (`ARPGCharacterBase`, `ARPGPlayerCharacter`), Enhanced Input assets, camera boom, sprint/jump.
- Greybox circular arena (primitives) + a **benchmark map** with scripted camera path and frame-time logging.
- Packaging script (`Scripts/Package.ps1`) for a Development build; capture script using `stat unit` / Unreal Insights trace args.
- **First baseline on your RTX 2060 Super** logged in `PERFORMANCE_LOG.md`.

**Gate:** movement feels right, packaged benchmark runs, baseline numbers recorded.

### M2 — Asset pipeline proof (week 2, in parallel with M1)
Prove **one** player + **one** boss + animations before anything else is bought.
- You download free candidates (Paragon boss/hero, Game Animation Sample, Megascans). I inspect them via MCP: skeleton, anim list, root motion.
- Retarget to UE5 mannequin using IK Retargeter where needed; test idle/run/dodge/attack/hit/death on each.
- Record in `ASSET_LICENSES.md`. Decide if a paid melee animation pack is needed for weapon variety.

**Gate:** player and boss each play a full set of core animations in the editor.

### M3 — Player combat (weeks 3–5)
Order matters; each step ends in a passing test.
1. `UAttributeComponent` — health/stamina/poise, regen + delay, single authoritative values. *(automation spec)*
2. `UCombatComponent` — logical state machine (Locomotion/Attacking/ComboWindow/Recovery/Dodging/Blocking/Staggered/Dead), explicit cancel windows. *(spec)*
3. Hit detection — socket-to-socket sweep traces in active window, per-swing hit list, single damage path, debug draw. *(spec + dummy test)*
4. Dodge with i-frames, stamina once per dodge.
5. Lock-on (`UTargetLockComponent`) with camera and target switching.
6. Weapon #1 via `UWeaponData` Data Asset: light/heavy, combo montage sections, anim notify states (`ANS_HitWindow`, `ANS_ComboWindow`, `ANS_IFrames`, `ANS_CancelWindow`).
7. Hit reactions, poise break, death, block/parry (gated if anims missing).
8. Training dummy map + dev debug overlay.

**Gate:** beat a dummy; no duplicate hits per swing; no stuck states after interrupts; high-FPS hit test (uncapped) passes.

### M4 — Boss and encounter loop (weeks 6–8)
1. `ARPGBossCharacter` shares the attribute/damage interfaces with the player.
2. `UBossAttackData` fields: range, arc, phase, weights, cooldown, repeat limit, startup/active/recovery, damage/poise, tracking rules.
3. `UBossCombatComponent` weighted selector: filter by distance/phase/cooldown/history → weight → reaction delay → commit. *(spec: distribution, no infinite repeat, phase gating)*
4. Thin StateTree: Dormant → Entrance → Combat → PhaseTransition → Dead.
5. Six attacks in order of animation availability: sweep, slam, lunge, 3-hit combo, shockwave, lightning (phase 2). Debug draw for ranges/arcs.
6. Phase transition once at threshold (guard against same-frame multi-hit).
7. `UEncounterSubsystem`: trigger, entrance, boss bar, defeat, victory, **reset** with invariants (timers, hit lists, lock-on, AI state, volumes).
8. Boss UI, player death/retry UI.

**Gate:** fight can be won and lost repeatedly in the greybox; reset leaves no stale state over 10 consecutive cycles.

### M5 — Content and weapons (weeks 9–11)
- Remaining weapon categories via Data Assets only (proves the pipeline).
- Arena from licensed modular assets, materials, baked lighting, fog.
- Lightning VFX in Niagara with a low-cost fallback; hit sparks, trails, dust.
- Audio: swings, hits, footsteps, boss telegraphs, phase change, music.
- Entrance and death presentation. UI polish. Blender MCP used for socket/prop fixes.

**Gate:** visually complete, no undocumented placeholders.

### M6 — Optimization and tuning (weeks 12–15)
- Profile worst phase in a packaged build (you run, I read the traces/logs). One variable changed per iteration, logged.
- Candidates: shadow casters, fog, Niagara overdraw, animation cost, texture streaming, Nanite vs LODs, Lumen only if budget allows.
- Tune damage, stamina, poise, recovery, boss timings for fairness.

**Gate:** average ≥120 FPS and 99th percentile ≤8.33 ms in the agreed benchmark, or the gap is documented honestly.

### M7 — Hardening (weeks 16–18)
- Add a test weapon through data only; add a second boss config on shared systems.
- Settings/save if in scope, controller/rebinding polish, 10-minute soak with resets, Shipping build.
- Final docs and license register; full acceptance matrix run.

**Gate:** release candidate; extension path documented and proven.

## 4. Verification strategy

| Layer | Tool | Covers |
|---|---|---|
| Logic | UE Automation specs (headless via `UnrealEditor-Cmd`) | attributes, state machine, selector, hit tracking, reset invariants, phase-once |
| Integration | Functional test maps + MCP-driven scene checks | dodge vs boss attacks, lock-on edge cases, encounter lifecycle |
| Feel | Your PIE playtests with a checklist per milestone | timing, camera, readability, fairness |
| Performance | Packaged benchmark + Unreal Insights, you run, I analyze | frame-time percentiles, memory growth |

## 5. Biggest risks and early mitigations

| Risk | Mitigation |
|---|---|
| MSVC 14.51 breaks UE 5.5 build | Test in M0; fallback install 14.38 |
| Free assets lack animations for 6 attacks or 3–4 weapons | M2 inspection before design lock; design attacks around available animations; buy one melee pack only if needed |
| Combat timing bugs at 120 FPS | Sweep traces, notify-driven windows, uncapped hit tests in M3 |
| Unfair boss | Tracking limits, telegraph fields in data, fairness checklist per attack |
| Stale state after reset | Reset invariants as automation tests from M4 |
| Plugin/MCP limits | Editor Python fallback; keep logic in C++ so it is testable without the editor |
| 120 FPS not reachable | Profile from M1 on the real GPU; baked lighting first; report honestly |

## 6. Decisions and actions needed from you

1. **Coding workflow.** Your `codex-aider-bridge` skill blocks me from writing source until its MCP (`bridge_health`), `code-review-graph` and a working Aider/Ollama model are connected. Choose: (a) fix those and I follow the pipeline, or (b) waive it for this project so I write C++ directly.
2. **Restart the session** so the `unrealclaude` MCP tools load.
3. **Boss concept.** There is a `CuteDragon.blend` in the project root. Is the boss a dragon, or something else? This changes attack roster and asset search.
4. **Asset downloads.** When M2 starts I'll give an exact checklist; you do the Fab downloads (free first).
5. **MSVC.** Only if the M0 build fails: install the 14.38 component.
6. **Remote.** `origin` points to `WRDeadman10/one-boss-fight`; confirm whether the new `OneBossFight` folder should keep pushing there before any push.
