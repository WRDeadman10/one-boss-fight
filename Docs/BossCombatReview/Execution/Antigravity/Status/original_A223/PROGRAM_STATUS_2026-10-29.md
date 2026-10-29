# Program Status Report: One Boss Fight Combat System Migration

**Date:** 2026-10-29  
**Author:** Antigravity (Party Code `A`)  
**Work Order:** `[C-337]` (Order A-223; updated from `[C-335]` / `A-222`)  
**Audience:** Owner, Tech Lead Claude, Implementer Codex  
**Execution Boundary:** STRICTLY OFFLINE. Zero Unreal Engine processes launched; zero Source/Content edits; zero git operations.

---

## Executive Summary

This status report consolidates the total technical state of the One Boss Fight project following the successful execution of **DD27h** (`[X-335]`, `[C-333]`), the delivery of the corrected **Activation Hook Specification** (Order A-219, `[C-332]`), and the completion of the **Performance Gap Analysis for KI-108** (Order A-220 / A-221, `[C-334]`, `[C-335]`).

### Key Program Milestones Achieved:
1. **In-Memory Authoring Pathway Proven (DD27h):** In-editor execution of `draft_boss_profiles.py --apply` under exclusive engine lock proved 100% success across all 3 authored drafts. All 22 typed properties were initialized and read back with zero errors and zero failures. The Ember Warden draft verified 110 of 110 native field rows (`[X-335]`, `[C-333]`).
2. **Authoring Toolkit Expansion & Offline Qualification:** The Authoring Toolkit offline test suite has expanded to **221 unit tests** (221/221 PASS in 1.108s, exit code 0). The toolkit incorporates grounded soft-object (`load_asset`) and soft-class (`load_class(None, path_C)`) conversion routines derived from live engine reflection probes (DD27e, DD27g), protected by strict `RuntimeError` guards against silent-None null reference authoring (`[A-218]`, `[C-330]`).
3. **Core Engine Hydration & Activation Library (DD28 & DD29):** The C++ hydration library includes transactional registration, batch-owned rollback/`Abort()` (`RPGBossHydrationPreparation.cpp:319-381`), and the composed world activation API (`RPGBossActivation::ActivateWorld`). Automated engine unit test coverage stands at **182 unique successes** with zero critical errors (`[C-319]`).
4. **Activation Hook Specification Grounded (A-219):** Corrected `ACTIVATION_HOOK_SPEC.md` addresses all four architectural discrepancies identified in Codex cross-check `[X-332]`. The Prelude and Bundle component inventory is established at 21 potential classes (12 typed + 9 non-typed). Pre-`BeginPlay` timing in `Attach` is formally reclassified as `[UNMEASURED / Unproven for runtime spawns]` due to engine `PostSpawnInitialize` / `BeginPlay` dispatch preceding `OnActorSpawned` (`LevelActor.cpp:733`, `Actor.cpp:4050-4070`).
5. **Performance Gap Root Cause Identified (KI-108 / A-220 / A-221):** The packaged build's 28-29 FPS average on the RTX 3060 is proven to be **100% GPU-bound** (Game thread p99 is 3.68 ms, Render thread p99 is 3.88 ms in Shipping). The idle dressed arena environment accounts for 34 ms of the 40 ms frame time. The strongest measured lead is Virtual Shadow Maps (VSM) on 12 brazier point lights (8.27 ms ProfileGPU in log lines 1402/1794; turning shadows off in Development experiment E18 yielded +23.5 FPS to 71.6 FPS, though round 2 absolute numbers require a clean repeat) and Volumetric Cloud ray marching (5.30 ms ProfileGPU in log line 1862).

---

## 1. Measured Capabilities & Execution Evidence

Every capability cited below is backed by explicit repository evidence, verified test counts, and recorded verification limits:

| Package / Milestone | Focus | Evidence Location | Measured Result | Authored Contract Proved | Recorded Verification Limits (What It Does NOT Prove) |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **DD19** | Bleed Config (7 fields) | `Docs/.../Codex/DD19/` | 135 / 135 Success | `FRPGBleedConfig` validation, scalar boundaries, soft path syntax. | Isolated typed config/reflection/copy only; no native Bleed BeginPlay, no VFX/sound/cook proof, no authored value, no preflight insertion, no complete bundle, no Ready, no legacy suppression, no wiring, no duel or networking proof, no PIE gate, no package, no 83-requirement closure (KI-124). |
| **DD20** | Low Sweep Config (8 fields) | `Docs/.../Codex/DD20/` | 141 / 141 Success | `FRPGLowSweepConfig` ranges, reach, inner radius, angle bounds. | MoveId validates syntax only; native LowSweep depends on legacy tracker; no tracker entry, window or firing proof; no collision, geometry, damage or serialized authoring proof (KI-125). |
| **DD21 + DD22** | Shockwave (8) + Heal Punish (14) | `Docs/.../Codex/DD22/` | 153 / 153 Success | Radii, jump clearance, projectile range, cooldowns, speed limits. | Isolated configuration/copy/reflection only; no native wave/tick/tracker/hit/damage, no Niagara rendering, no javelin projectile spawning, no heal event detection, no arena bounds verification (KI-129). |
| **DD23** | Look Config (5 fields) | `Docs/.../Codex/DD23/` | 159 / 159 Success | Body/Sword soft paths, socket name, pieces array well-formedness. | Required mesh paths prove structure only; no mesh load, no Apply, no socket fit, no skeleton/pose/rendering proof (KI-131). |
| **DD24** | Close Clip Swap (5 fields) | `Docs/.../Codex/DD24/` | 165 / 165 Success | Montage soft paths, ability class names, duplicate detection. | Isolated typed assignment/copy/reflection only; no BeginPlay/Preload, no ability reflection, no live montage swap, permanent-failure guard unresolved (KI-132). |
| **DD25** | Death Config (12 fields) | `Docs/.../Codex/DD25/` | 171 / 171 Success | `ERPGBossDeathMode` enum, timing scalars, clip restart bounds. | Isolated typed assignment/copy/reflection only; no Death BeginPlay/Tick/Attach, no pack ability, no remains, unresolved pack destroys dead boss ~4.35 s after death (KI-133, KI-136). |
| **DD26** | 12-Plan Preflight | `Docs/.../Codex/DD26/` | 171 / 171 Success | 12 plans (110 manifest paths), duplicate path rejection, SHA256 format. | Unregistered in-memory test fixture only; no runtime subsystem component attachment, no BeginPlay initialization, no live encounter context binding, no gameplay execution (`[C-291]`). |
| **DD28** | Encapsulated Registration & Abort | `Docs/.../Codex/DD28/` | 177 / 177 Success | Additive transactional registration, batch-owned rollback and `Abort()` on failure. | Incremental editor build, 0 UHT, 3 warnings; never-begun registration only; no live caller, no BeginPlay/tick/binding proof (KI-137, `[C-315]`). |
| **DD29** | Composed World Activation | `Docs/.../Codex/DD29/` | 182 / 182 Success | `RPGBossActivation::ActivateWorld` composed library execution, caller leases. | Incremental build exit 0; clean fallback vs HardError; library never-begun composition only; no startup/Ready/suppression/gameplay proof (KI-138, `[C-319]`). |
| **DD27g** | Class Reference Engine Probe | `Docs/.../Codex/DD27g/` | Exit 0 (50 lines, 27 SETs) | Proved `unreal.load_class(None, path_C)` succeeds across all 3 soft-class sites. | Read-only reflection probe on throwaway structs; no assets authored or modified (`[C-328]`, `[X-331]`). |
| **DD27h** | In-Memory Authoring Rerun | `Docs/.../Codex/DD27h/` | Exit 0 (0 Failures, 110 Fields) | All 22 typed properties x 3 drafts initialized and read back; 110 rows verified on Ember Warden. | In-memory only; no asset saved to disk (`--save` uncalled); draft definition not yet read by compiler or preflight (`[X-335]`, `[C-333]`). |
| **Toolkit** | Authoring Core Offline Suite | `Docs/.../AuthoringToolkit/` | 221 / 221 PASS | Soft object and class reflection conversion, error guards, manifest consistency. | Offline mock-reflection qualification only; real engine proof requires editor execution (`[A-218]`, `[C-330]`). |
| **KI-108** | Performance Gap Analysis | `Docs/.../Performance/` | Validated in Repo | Confirmed 100% GPU-bound; 12 brazier VSM shadows (8.27 ms) and clouds (5.30 ms) identified. | Diagnostic analysis and single-variable plan only; permanent fix requires level asset baking and physical console verification (`[A-220]`, `[A-221]`, `[C-334]`, `[C-335]`). |

---

## 2. Flat Technical Truths: What Is True vs. What Is Not Yet True

### 2.1 What Is True (Measured Facts):
1. **In-Memory Authoring Pathway Is Fully Proven:** The Authoring Toolkit correctly parses `boss_draft_profiles.json`, nativizes all 22 typed properties across primitives, structs, arrays, soft object pointers, and soft class references, and verifies 100% readback in live engine memory (`DD27h`).
2. **27 / 27 Referenced Asset Packages Exist on Disk:** Complete disk audit confirmed all 27 `/Game` package paths referenced across the 3 draft profiles exist on disk under `Content/` (80 property references in JSON, 0 missing, `ACTIVATION_HOOK_SPEC.md:302-340`).
3. **Prelude and Bundle Class Inventory Total 21 Classes:** Source inspection of `RPGPlayerMovesSubsystem.cpp:139-249` confirms 12 typed component classes and 9 non-typed component classes (`URPGFootsteps`, `URPGBossMusic`, `URPGAttackTracker`, `URPGDamageResolver`, `URPGTraceGuard`, `URPGTraceAudit`, `URPGBossHud`, `URPGCombatDebug`, `URPGBossLegend`).
4. **C++ Gameplay Logic Leaves >12 ms CPU Headroom:** Shipping packaged benchmarks record Game thread p99 at **3.68 ms** and Render thread p99 at **3.88 ms** (`PERFORMANCE_LOG.md:21-36`).
5. **Fire Light Shadows Are the Strongest Measured GPU Lead (Clean Repeat Required):** In single-frame ProfileGPU, VSM takes 8.27 ms and deferred lights take 6.60 ms (`Saved/bench_return/r2/game1_OneBossFight.log:1402-1875`). In Development build experiment `E18`, disabling shadow casting on the 12 fire braziers (`rpg.Perf.FireShadows=0`) dropped frame time from 23.9 ms to 15.3 ms (+23.5 FPS to 71.6 FPS, `PERFORMANCE_LOG.md:46`). However, because round 2 absolute baseline numbers exhibited drift (48.1 FPS rerun vs 29.0 FPS in round 1), this remains the strongest measured lead, not an unreserved proof; a clean physical repeat is required.

### 2.2 What Is Not Yet True (Boundaries & Pending Gates):
1. **No Authored Asset Files Exist on Disk:** Zero authored `.uasset` packages exist under `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/`. DD27h proved in-memory creation only; physical serialization requires Owner approval for DD27i (`--save`).
2. **No Live Runtime Invocation of Typed Activation:** Neither `RPGBossActivation::ActivateWorld` nor `RPGBossHydrationPreflight` is called during actual gameplay. Both exist solely in test fixtures and standalone libraries (`Source/OneBossFight/Tests/`).
3. **Legacy Component Suite Remains Active:** `URPGPlayerMovesSubsystem::Attach` continues to instantiate and register all 12 legacy components on `BP_ExampleGreatSwordBoss` at runtime using hardcoded defaults.
4. **Universal Pre-BeginPlay Timing in `Attach` Is Unproven `[UNMEASURED]`:** In UE 5.5, `LevelActor.cpp:733` dispatches `PostSpawnInitialize` before broadcasting `OnActorSpawned:750`. For runtime spawned actors, `Actor.cpp:4050-4070` can dispatch `BeginPlay()` before the delegate reaches `Attach`, violating `HydrationPreparation.cpp:512-514` (`!World->HasBegunPlay()` and `!Actor->HasActorBegunPlay()`).
5. **EndPlay Abort Teardown Is an Unverified Policy `[UNMEASURED]`:** Calling `FRPGPreparedBatch::Abort()` on begun components skips unregistering them (`line 343`) and flags `Preparation.ContractViolation` (`lines 366-371`). Treating this as a normal teardown pattern is a proposed policy requiring lead approval.
6. **Performance Target on Target Hardware Is Unverified `[UNMEASURED]`:** The 60 FPS / 16.67 ms gate on the physical target hardware (RTX 2060 Super 8GB) has never been tested; all measurements are on an RTX 3060 12GB proxy machine.

---

## 3. Active Decisions & Open Gates

1. **Gate 1: Owner Approval to Save 3 Draft Assets (DD27i):**
   - Implementer Codex has prepared DD27i (`Codex/DD27i/PREPARED_NOT_RELEASED.md`, `[X-336]`).
   - Awaiting explicit Owner authorization to run `draft_boss_profiles.py --apply --save` and write the 3 new asset files to `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/`.
2. **Gate 2: Definition Compilation & Preflight Verification (DD27j):**
   - Source-only plan prepared by Codex (`DD27j_SOURCE_ONLY_PLAN.md`, `[X-336]`).
   - Follows DD27i: loads saved `DA_Boss_EmberWarden_Draft`, runs `CompileParticipant`, and verifies the 12-plan preflight against live authored asset data.
3. **Gate 3: Physical Console Performance Validation (P1-P4 Ready Kit):**
   - Prepared by Codex under `Docs/.../Codex/PerfKit/C334_P1_P4_READY_KIT.md` (`[X-337]`).
   - Requires Owner execution on PC `GANPATIGAMERBOI` (physical console session) using a freshly staged Development package to evaluate baseline drift, fire light shadows (`rpg.Perf.FireShadows=0`), and volumetric clouds (`r.VolumetricCloud=0`).
4. **Gate 4: Runtime Activation Call Site & Teardown Policy (DD30):**
   - Tech Lead Claude and Owner review of seam analysis (`C329_SOURCE_SPAWN_AND_BEGINPLAY.md`, `[X-333]`) to resolve participant spawn synchronization, HardError policy, and lifetime ownership before wiring the first live call site.
5. **Gate 5: Working Tree Working Archive (`Docs/BossCombatReview.zip`):**
   - 32.8 MB archive remains uncommitted in working tree. Awaiting Owner decision on whether to commit, archive externally, or delete.

---

## 4. Cryptographic Evidence Index

| Document / Asset | Location | SHA256 Hash | Bytes |
| :--- | :--- | :--- | :---: |
| **Activation Hook Specification** | `Docs/.../Activation/ACTIVATION_HOOK_SPEC.md` | `46c9c62895aead4397bc2fc2a72dc9ba834935d483ad375a0add580eb5eb5966` | 40,984 |
| **Activation Evidence Receipt** | `Docs/.../Activation/evidence_sha256.txt` | `f00fb01e4aa88feac77729c3752a2c8f4b7d32f2685242a6a080b35194635773` | 313 |
| **Performance Gap Analysis** | `Docs/.../Performance/PERF_GAP_ANALYSIS.md` | `88fe5d4ec41b0e1f154ba41af7885a0f8233fb901b6d828988ac653786931614` | 23,369 |
| **Performance Evidence Receipt** | `Docs/.../Performance/evidence_sha256.txt` | `d98cc54df2fde624786ac11bae82d34d3301b173f68f83f080099872d7408a0b` | 154 |
| **Authoring Core Script** | `Docs/.../AuthoringToolkit/authoring_core.py` | `74101436cc433863dc1829a0528c789ea7490fbda7d25aa29d6f36c4eb458cf1` | 103,034 |
| **Authoring Core Test Suite** | `Docs/.../AuthoringToolkit/test_authoring_core.py` | `6a6b99e09c9bdc7e571ee54f3fa0f5357d00cc62950e68fad6051ccac13df575` | 160,152 |
| **Toolkit Evidence Receipt** | `Docs/.../AuthoringToolkit/evidence_sha256.txt` | `13416f5204cc4c21731ded31d516b2ce1e1925f91e059b66467afe441de239a6` | 1,848 |
| **DD27h Run Report (Codex)** | `Docs/.../Codex/DD27h/RUN_REPORT_TO_CLAUDE.md` | Pinned in receipt `739296386acf...` | Verified |
| **DD27h Raw Editor Output** | `Docs/.../Codex/DD27h/editor_raw.txt` | `4db9ea8ca03c9ecbfa7d7962758b8045fa2c1207a689c61a715fed5ade55a5dd` | Verified |

---

*End of Program Status Report. Staged for Owner and Tech Lead Review.*
