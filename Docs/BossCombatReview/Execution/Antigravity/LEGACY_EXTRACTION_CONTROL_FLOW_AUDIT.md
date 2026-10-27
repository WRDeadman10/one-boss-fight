# AG17: Legacy Extraction Control-Flow Precheck Audit (Rev 02)

**Document Date:** 2026-10-27  
**Author:** Antigravity (Pair Programming AI Assistant)  
**Task Classification:** Work Order 17 (AG17) — Independent Legacy-Extraction Control-Flow Precheck for Future Packet B (Rev 02 Bounded Corrections)  
**Governing Inputs:**
- Acceptance Directive: [`Docs/BossCombatReview/Execution/Codex/AG16_A144_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG16_A144_ACCEPTANCE.md) (`SHA256: 5f81ae76cd86203b279e5ce59d5d1350cd0951962100e291726a1d338c49da66`)
- Packet Specification: [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/04_REPLACEMENT_IMPLEMENTATION_PACKETS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/04_REPLACEMENT_IMPLEMENTATION_PACKETS.md) (`SHA256: dfb97e4c4214d91258efb157485931f9a8afd81f5d87f2b30e2fff2af4991d94`)
- Witness Specification: [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/06_LEGACY_ATTACH_WITNESS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/06_LEGACY_ATTACH_WITNESS.md) (`SHA256: 4e02fe630eb999fa8c82f4d63382441c6d9f3389d0e3e2d157e90eb7d227e6d9`)
- Review & Corrections Directive: [`Docs/BossCombatReview/Execution/Codex/AG17_A145_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG17_A145_REVIEW.md) (`SHA256: ae06d451eb8c7b6873a4c856b13d02b8517372bd67640119aa2372a4a8078b13`)
- Candidate Probes Record: [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/ag17_candidate_review_probes.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/ag17_candidate_review_probes.json) (`SHA256: 297f366707f2c8fe13ab52f405b5aa7fd5c138c2f85cd2ed7d8f18ad3d265949`)
- Mailbox Directives: `[X-218]`, `[X-219]`, `[X-220]`, and `[X-221]` (2026-10-27 06:55:12 +05:30)

---

## 1. Executive Summary & Audit Scope

This audit provides an independent static control-flow precheck of the legacy pawn component attachment implementation in [`URPGPlayerMovesSubsystem`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h), supporting the future mechanical **Packet B** (legacy boss attachment extraction) without generating candidate patches, modifying engine code, or commencing Step 2b operations.

### Key Precheck Findings & Bounded Scope:
1. **Dual Attachment Triggers & Registration Lifecycle:**
   Attachment is invoked via two distinct paths:
   - Dynamic spawn trigger: `OnActorSpawned` via `World->AddOnActorSpawnedHandler` registered in `PostInitialize()`.
   - Placed/Pre-spawned world-begin trigger: `OnWorldBeginPlay` iterating `TActorIterator<APawn>(&InWorld)`.
   Both paths funnel into the private const helper `Attach(AActor* Pawn)`. Subsystem cleanup in `Deinitialize()` unregisters the spawn delegate and restores fixed frame rates via `URPGInputTestUtils::RestoreFixedFrameRate()`.
2. **Actor Classification & Branch Coupling:**
   Classification operates via string-based class hierarchy walks (`GetSuperClass()`):
   - `IsPackPlayer`: matches `BP_CombatPlayerCharacter_C`.
   - `IsPackBoss`: matches `BP_ExampleGreatSwordBoss_C`.
   In `Attach(AActor* Pawn)`, actor footsteps and boss music are branched via `if (IsPackPlayer(Pawn)) ... else if (IsPackBoss(Pawn))`. Following audio, 9 player component creation sites and 19 boss component creation sites evaluate separate `if` statements. In source text, there are **10 syntactic call sites** for `IsPackPlayer` and **18 syntactic call sites** for `IsPackBoss`. Runtime evaluation counts are path-dependent due to short-circuiting.
3. **Component Construction Modes:**
   The 21 ordered boss attachment operations utilize two primary construction mechanisms:
   - Direct inline creation: 18 components use `NewObject<T>(Pawn, TEXT("..."))->RegisterComponent()`.
   - Dedicated factory/helper wrappers:
     * `AddFootsteps(Pawn, true)`: local static function in subsystem with custom scale/audio configuration.
     * `URPGBossDeath::Attach(Pawn, ERPGBossDeathMode::OwnClip)`: static factory method in `RPGBossDeath.cpp:41-56` returning existing component if present.
     * `URPGDamageResolver::FindOrAdd(Pawn)`: static factory method in `RPGDamageResolver.cpp:20-34` returning existing component if present.
4. **Ordering & Idempotence Invariants:**
   - **Death-before-Look:** `URPGBossDeath::Attach` (event 8) must precede `URPGBossLook` (event 9) in source order to ensure death clip and ragdoll suppression take precedence over mesh cosmetics.
   - **Legend-Last:** `URPGBossLegend` (event 21) must remain strictly last in source order, as it polls previously registered components (tracker, phases, stagger, HUD).
   - **Idempotence Across All 21 Components:** Every single boss component is guarded against duplicate attachment—either via explicit `!Pawn->FindComponentByClass<T>()` checks in `Attach`, or internally inside the static factory helper. Returning an existing component prevents duplicate instantiation, but does not reset existing configuration or prove zero repeated-callback side effects.
5. **Lexical Witness Limits & Candidate Mode Probes:**
   The offline lexical witness ([`legacy_attach_witness.mjs`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/legacy_attach_witness.mjs)) verifies token sequence, whole-method fingerprints, line mapping, and hook calls. However, as demonstrated by two synthetic probes in [`ag17_candidate_review_probes.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/ag17_candidate_review_probes.json), **candidate mode exit 0 checks event order and hook patterns only**; it does not enforce body token hash equality or trigger token equality. Exit 0 does not verify configuration defaults, guard equivalence, or runtime idempotence.

---

## 2. Inspected Input Receipts

The audit scope is strictly bounded to the subsystem source, implementation packet definitions, helper implementations, and offline witness artifacts:

| File Path | SHA256 Hash | Bytes | Role in Packet B Precheck |
|:---|:---|:---:|:---|
| [`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h) | `ab75575c7fcde9e18e7be75f42676f6a0ad0fecfd7bcc32d438cac86c1a9cd02` | 1,132 | Subsystem declaration, trigger hooks, classification signatures |
| [`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp) | `1b036b03aec269e5b3e906d8adaedac709c33f6a3c15413d0454b9c354523712` | 11,645 | Full `Attach` implementation, 21 boss events, 9 player events, `AddFootsteps` |
| [`Source/OneBossFight/Player/RPGBossDeath.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.h) | `1fe249f97b707921c16ca5061b78acb5845e1b85745982076683df025fb4c64d` | 11,784 | `URPGBossDeath` declaration, `Attach` signature, `ERPGBossDeathMode` |
| [`Source/OneBossFight/Player/RPGBossDeath.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.cpp) | `a6f73587473d31c11136c7c1ebeac65f1f9b95b1503089d1c3816e553bdd60c4` | 18,250 | `URPGBossDeath::Attach` implementation (`cpp:41-56`), idempotence guard |
| [`Source/OneBossFight/Player/RPGDamageResolver.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.h) | `a5dd7de41aec0224bc6de96c55d64897db5529a2f5da90caf515060c83eebd30` | 8,874 | `URPGDamageResolver` declaration, `FindOrAdd` factory signature |
| [`Source/OneBossFight/Player/RPGDamageResolver.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.cpp) | `82da0dd3400a049d92bd96409f90db58a319fd7db73e44f7b46b766e938a6bca` | 8,234 | `URPGDamageResolver::FindOrAdd` implementation (`cpp:20-34`), idempotence guard |
| [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/04_REPLACEMENT_IMPLEMENTATION_PACKETS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/04_REPLACEMENT_IMPLEMENTATION_PACKETS.md) | `dfb97e4c4214d91258efb157485931f9a8afd81f5d87f2b30e2fff2af4991d94` | 12,680 | Packet B mechanical extraction scope and constraints |
| [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/06_LEGACY_ATTACH_WITNESS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/06_LEGACY_ATTACH_WITNESS.md) | `4e02fe630eb999fa8c82f4d63382441c6d9f3389d0e3e2d157e90eb7d227e6d9` | 2,599 | Witness methodology, candidate exit-code boundary, event order |
| [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/legacy_attach_witness.mjs`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/legacy_attach_witness.mjs) | `995376c1f0ca8a2c81a4d6032a1cf00f8df730bd883f2ea48b66afab7e42fe01` | 6,615 | Offline lexical test script, 11 internal self-tests, AST limit notices |
| [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/LEGACY_ATTACH_BASELINE_2026-10-26.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/LEGACY_ATTACH_BASELINE_2026-10-26.json) | `02a72c7a2aaa1c076c9e6ed8a6bfb9dae705304847d031bffbf3bc1bedfe9d51` | 2,402 | Pinned historical lexical baseline (21 boss events, token hashes) |
| [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/ag17_candidate_review_probes.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/ag17_candidate_review_probes.json) | `297f366707f2c8fe13ab52f405b5aa7fd5c138c2f85cd2ed7d8f18ad3d265949` | 2,287 | Synthetic false-acceptance probes (changed music path, duplicate spawn hook) |
| [`Docs/BossCombatReview/Execution/Codex/AG17_A145_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG17_A145_REVIEW.md) | `ae06d451eb8c7b6873a4c856b13d02b8517372bd67640119aa2372a4a8078b13` | 4,639 | Codex AG17 review directive, candidate exit-code limits, source corrections |
| [`Docs/BossCombatReview/Execution/Codex/AG16_A144_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG16_A144_ACCEPTANCE.md) | `5f81ae76cd86203b279e5ce59d5d1350cd0951962100e291726a1d338c49da66` | 6,073 | Codex AG16 acceptance & AG17 assignment terms |
| [`Docs/BossCombatReview/Execution/Antigravity/RESET_STATE_OWNERSHIP_AUDIT.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/RESET_STATE_OWNERSHIP_AUDIT.md) | `a8c8566cfa67aec72beacedb0dbc933673259501aca57c4b096381ccff8710de` | 32,104 | AG16 Rev 03 report with precision citations applied |

---

## 3. Legacy Attachment Architecture & Control Flow Mapping

### 3.1. Attachment Triggers & Lifecycle Hooks
The subsystem hooks into actor creation through two distinct paths:
1. **Dynamic Spawn Trigger (`OnActorSpawned`):**
   - Registered in `PostInitialize()`:
     ```cpp
     SpawnHandle = World->AddOnActorSpawnedHandler(
         FOnActorSpawned::FDelegate::CreateUObject(this, &URPGPlayerMovesSubsystem::OnActorSpawned));
     ```
   - Callback: `OnActorSpawned(AActor* Actor)` directly invokes `Attach(Actor)`.
   - Triggers immediately whenever an actor is spawned into the world at runtime.
2. **Placed/Pre-Spawned World-Begin Trigger (`OnWorldBeginPlay`):**
   - Executed on world initialization:
     ```cpp
     for (TActorIterator<APawn> It(&InWorld); It; ++It)
     {
         Attach(*It);
     }
     ```
   - Iterates all existing `APawn` actors placed in the map or created prior to `OnWorldBeginPlay`.
3. **Subsystem Teardown (`Deinitialize`):**
   - Unregisters spawn handler: `World->RemoveOnActorSpawnedHandler(SpawnHandle);`.
   - Invokes `URPGInputTestUtils::RestoreFixedFrameRate()`.

### 3.2. Classification Logic & Class Hierarchy Walks
Both classification methods avoid hard class dependencies by walking the `UClass` inheritance chain via `GetSuperClass()` and comparing string names:
- **`IsPackPlayer(const AActor* Actor)` (`cpp:80-91`):**
  Walks `Class = Class->GetSuperClass()` checking `Class->GetName() == TEXT("BP_CombatPlayerCharacter_C")`.
- **`IsPackBoss(const AActor* Actor)` (`cpp:93-103`):**
  Walks `Class = Class->GetSuperClass()` checking `Class->GetName() == TEXT("BP_ExampleGreatSwordBoss_C")`.
- **Null Safety:** `Actor ? Actor->GetClass() : nullptr` ensures that passing `nullptr` returns `false` without dereferencing or crashing.

### 3.3. Control Flow Branching & Syntactic Call Sites
In `Attach(AActor* Pawn)`:
- **Audio Coupling:** Lines 139–159 employ an `if ... else if` structure:
  ```cpp
  if (IsPackPlayer(Pawn)) { AddFootsteps(Pawn, false); }
  else if (IsPackBoss(Pawn)) { AddFootsteps(Pawn, true); /* Attach URPGBossMusic */ }
  ```
- **Independent Component Evaluations:** Following audio setup, lines 161–283 evaluate separate, independent `if` statements.
  - Player components evaluate `if (IsPackPlayer(Pawn) && !Pawn->FindComponentByClass<T>())`.
  - Boss components evaluate `if (IsPackBoss(Pawn) && !Pawn->FindComponentByClass<T>())`.
- **Syntactic Call Sites vs Runtime Evaluations:**
  - In source text, there are **10 syntactic call sites** for `IsPackPlayer` and **18 syntactic call sites** for `IsPackBoss`.
  - Actual runtime evaluation count is strictly path-dependent: on a player pawn, line 143 (`else if (IsPackBoss)`) is skipped, evaluating `IsPackPlayer` 10 times and `IsPackBoss` 17 times. On a boss pawn, lines 139 and 143 are both evaluated, followed by 9 player checks (which evaluate false on `IsPackPlayer`) and 17 subsequent boss checks.
  - If an actor matches neither, all checks evaluate false and exit without modifying the actor.

### 3.4. Complete 21-Event Boss Attachment Inventory

The table below catalogs the 21 ordered boss construction events, documenting line numbers, construction modes, and idempotence mechanisms:

| Event Index | Event Identifier | Source Line | Creation / Attachment Expression | Configuration & Inline Defaults | Idempotence Guard Mechanism |
|:---:|:---|:---:|:---|:---|:---|
| 1 | `Footsteps` | 145 | `AddFootsteps(Pawn, true)` | `PitchScale=0.62f`, `VolumeScale=1.5f`, `AudibleRange=4500.f`, `JogSpeed=200.f`, `RunSpeed=420.f`, loads 4 concrete boot cues | Guarded inside helper: `if (Pawn->FindComponentByClass<URPGFootsteps>()) return;` |
| 2 | `URPGBossMusic` | 148 | `NewObject<URPGBossMusic>(Pawn, TEXT("RPGBossMusic"))` | Loads `MX_Boss01_Phase1` (falls back to `Starter_Music_Cue` if missing) and `MX_Boss01_Phase2` | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossMusic>())` |
| 3 | `URPGBossStagger` | 197 | `NewObject<URPGBossStagger>(Pawn, TEXT("RPGBossStagger"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossStagger>())` |
| 4 | `URPGBossPhases` | 202 | `NewObject<URPGBossPhases>(Pawn, TEXT("RPGBossPhases"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossPhases>())` |
| 5 | `URPGBossEncounter` | 207 | `NewObject<URPGBossEncounter>(Pawn, TEXT("RPGBossEncounter"))` | Standard constructor defaults (`int32 Generation = 1`) | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossEncounter>())` |
| 6 | `URPGBossDormantWake` | 212 | `NewObject<URPGBossDormantWake>(Pawn, TEXT("RPGBossDormantWake"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossDormantWake>())` |
| 7 | `URPGBossPosture` | 216 | `NewObject<URPGBossPosture>(Pawn, TEXT("RPGBossPosture"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossPosture>())` |
| 8 | `Death.OwnClip` | 221 | `URPGBossDeath::Attach(Pawn, ERPGBossDeathMode::OwnClip)` | Static helper assigns `Death->DeathMode = Mode;` | Guarded inside helper (`RPGBossDeath.cpp:48`): returns existing component without resetting mode |
| 9 | `URPGBossLook` | 225 | `NewObject<URPGBossLook>(Pawn, TEXT("RPGBossLook"))` | Standard constructor defaults (attaches cosmetic pieces) | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossLook>())` |
| 10 | `URPGBossBleed` | 229 | `NewObject<URPGBossBleed>(Pawn, TEXT("RPGBossBleed"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossBleed>())` |
| 11 | `URPGAttackTracker` | 233 | `NewObject<URPGAttackTracker>(Pawn, TEXT("RPGAttackTracker"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGAttackTracker>())` |
| 12 | `URPGBossCloseClipSwap`| 238 | `NewObject<URPGBossCloseClipSwap>(Pawn, TEXT("RPGBossCloseClipSwap"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossCloseClipSwap>())` |
| 13 | `URPGBossShockwave` | 242 | `NewObject<URPGBossShockwave>(Pawn, TEXT("RPGBossShockwave"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossShockwave>())` |
| 14 | `URPGBossLowSweep` | 247 | `NewObject<URPGBossLowSweep>(Pawn, TEXT("RPGBossLowSweep"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossLowSweep>())` |
| 15 | `URPGBossHealPunish` | 252 | `NewObject<URPGBossHealPunish>(Pawn, TEXT("RPGBossHealPunish"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossHealPunish>())` |
| 16 | `DamageResolver` | 257 | `URPGDamageResolver::FindOrAdd(Pawn)` | Static factory helper | Guarded inside helper (`RPGDamageResolver.cpp:26`): returns existing component |
| 17 | `URPGTraceGuard` | 260 | `NewObject<URPGTraceGuard>(Pawn, TEXT("RPGTraceGuard"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGTraceGuard>())` |
| 18 | `URPGTraceAudit` | 264 | `NewObject<URPGTraceAudit>(Pawn, TEXT("RPGTraceAudit"))` | Standard constructor defaults (empty in Shipping) | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGTraceAudit>())` |
| 19 | `URPGBossHud` | 269 | `NewObject<URPGBossHud>(Pawn, TEXT("RPGBossHud"))` | Standard constructor defaults | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossHud>())` |
| 20 | `URPGCombatDebug` | 275 | `NewObject<URPGCombatDebug>(Pawn, TEXT("RPGCombatDebug"))` | Attaches and registers unconditionally on boss; presentation gated by `rpg.Debug > 0` | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGCombatDebug>())` |
| 21 | `URPGBossLegend` | 281 | `NewObject<URPGBossLegend>(Pawn, TEXT("RPGBossLegend"))` | Presentation layer (camera shake, hit stop); polls earlier components | Guarded in caller: `if (!Pawn->FindComponentByClass<URPGBossLegend>())` |

---

## 4. Lexical Witness Scope & Invariant Limitations

### 4.1. What the Lexical Witness Proves and Does Not Enforce
The offline tool [`legacy_attach_witness.mjs`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/legacy_attach_witness.mjs) executes 11 internal script self-tests (testing tokenization, escaped quotes, and regex matching; these are not Unreal automation tests) and checks source code against [`LEGACY_ATTACH_BASELINE_2026-10-26.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/LEGACY_ATTACH_BASELINE_2026-10-26.json):
1. **Unchanged-Source Mode:** Verifies raw file hash (`1b036b03...`), whole-method body token fingerprint (`60ce6e36...`), trigger token fingerprints, and the ordered sequence of 21 boss construction events.
2. **Candidate Mode (`--candidate`) Limitations:**
   In line 60 of `legacy_attach_witness.mjs`:
   ```javascript
   if (!report.orderMatches || !hooks.spawnCallsAttach || !hooks.worldBeginCallsAttach || (!args.includes('--candidate') && !report.sourceHashUnchanged)) process.exitCode = 1;
   ```
   Candidate mode evaluates exit 0 based **solely** on:
   - `report.orderMatches === true` (all 21 events present in sequence)
   - `hooks.spawnCallsAttach === true` (body contains `Attach(Actor)`)
   - `hooks.worldBeginCallsAttach === true` (body contains `Attach(*It)`)
   It **does not fail** on `triggerTokensUnchanged === false`, and **does not enforce** that `bodyTokenSHA256` matches the historical baseline.

### 4.2. Concrete Synthetic Candidate False-Acceptance Probes
As recorded in [`ag17_candidate_review_probes.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/ag17_candidate_review_probes.json):
- **Probe 1 (Changed Music Asset Path):**
  Altered the asset path string for `MX_Boss01_Phase1` inside `Attach`.
  *Outcome:* Helper returned `exit 0` and `orderMatches: true`, even though `bodyTokenSHA256` changed to `de3575a8...19558`.
- **Probe 2 (Duplicated Spawn Attach Call):**
  Added a duplicate `Attach(Actor)` call inside `OnActorSpawned`.
  *Outcome:* Helper returned `exit 0` and `orderMatches: true`, even though `triggerTokensUnchanged` evaluated to `false`.

**Core Takeaway:** Candidate `exit 0` proves only that 21 recognized tokens appear in order and hook patterns exist. It does **not** prove configuration equivalence, default preservation, or trigger token equality. In addition, `AddFootsteps` and static helper implementations (`URPGBossDeath::Attach`, `URPGDamageResolver::FindOrAdd`) reside outside the `Attach` method token fingerprint and require independent source inspection.

### 4.3. Lexical Analysis Invariant Limitations
As documented in [`06_LEGACY_ATTACH_WITNESS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/06_LEGACY_ATTACH_WITNESS.md):
1. **Not a C++ AST:** It does not model C++ abstract syntax trees, expression evaluation, operator precedence, scope boundaries, or preprocessor branches (`#if !UE_BUILD_SHIPPING`).
2. **No Guard Equivalence Proof:** Matching token order does not prove that guard conditions (e.g. `!Pawn->FindComponentByClass<T>()` or `IsPackBoss(Pawn)`) remain identical in semantics, short-circuit order, or evaluation count if refactored.
3. **No Class Hierarchy Verification:** Does not execute or validate polymorphic type matching via `GetClass()` / `GetSuperClass()`.
4. **No Runtime Lifecycle or Registration Proof:** Matching `NewObject` and `RegisterComponent` tokens in source does not prove engine component registration, `BeginPlay()` invocation order, tick group scheduling, or garbage collection behavior.
5. **No Two-Trigger Idempotence Proof:** Lexical scanning cannot verify that invoking both `OnActorSpawned` and `OnWorldBeginPlay` on the same actor produces zero runtime side effects, duplicate state, or leaks.
6. **Player Branch Ignored:** The lexical witness explicitly focuses on the 21 boss events, leaving the 9 player component attachments to manual diff review (`playerPathRequiresManualDiff: true`).

---

## 5. Mechanical Extraction Risks & Review Obligations

A purely mechanical extraction of the boss attachment bundle (Packet B) into a dedicated helper function (e.g. `AttachLegacyBossBundle(AActor* Boss)`) carries specific structural risks:

### 5.1. Risk 1: Guard Evaluation and Short-Circuit Scope
- **Current Behavior:** `IsPackBoss(Pawn)` appears at 18 syntactic call sites in separate `if` statements.
- **Refactoring Hazard:** Factoring out `if (IsPackBoss(Pawn)) { AttachLegacyBossBundle(Pawn); }` alters the interleaving of class checks and component registration. Packet B must preserve original short-circuiting, branch independence, evaluation/registration interleaving, and scope until a separately reviewed choice permits change.
- **Null Safety:** Preserving the existing call structure is inherently null-safe because `IsPackPlayer(nullptr)` and `IsPackBoss(nullptr)` return `false`. Introducing arbitrary new null guards or consolidating checks without authorization is outside Packet B scope.
- **Review Obligation:** Ensure any extracted helper preserves every component's `!Boss->FindComponentByClass<T>()` check and does not alter evaluation order.

### 5.2. Risk 2: Player and Boss Branch Decoupling (Hypothetical Overlap)
- **Current Behavior:** Lines 139–159 couple footsteps and music via `if (IsPackPlayer) ... else if (IsPackBoss)`. However, subsequent component attachments are completely independent.
- **Refactoring Hazard:** If an extraction moves all boss logic into an `else if (IsPackBoss)` block that wraps both footsteps/music and all 19 subsequent components, it would alter behavior for any hypothetical actor matching both player and boss class criteria.
- **Review Obligation:** Maintain the decoupling: keep player component attachment evaluated independently from boss component attachment, preserving the exact original branching structure.

### 5.3. Risk 3: Default Values and Inline Configuration Drift
- **Current Behavior:**
  - `AddFootsteps` configures 5 float scales and loads 4 concrete sound cues.
  - `URPGBossMusic` contains custom load logic with fallback to `Starter_Music_Cue`.
  - `URPGBossDeath::Attach` passes explicit enum `ERPGBossDeathMode::OwnClip`.
- **Refactoring Hazard:** A mechanical extraction could inadvertently drop sound paths, omit warning logs, alter pitch/volume scales, or default-construct components without copying inline properties.
- **Review Obligation:** Perform a strict character-for-character before/after diff of all property assignments, asset paths, and load flags across footsteps, music, and death mode.

### 5.4. Risk 4: Order Invariants (Death-before-Look & Legend-Last)
- **Death-before-Look Invariant:**
  - `URPGBossDeath::Attach` (event 8) must strictly precede `URPGBossLook` (event 9) in source order.
  - Rationale: `URPGBossDeath` configures ragdoll suppression and death clip handling on the mesh before `URPGBossLook` attaches external cosmetic skeletal meshes (crown, mantle, gauntlets, greatsword).
- **Legend-Last Invariant:**
  - `URPGBossLegend` (event 21) must strictly remain the final component registered in source order.
  - Rationale: Source explicitly notes that `URPGBossLegend` is the presentation layer (camera shake, hit stop, slow motion) that polls stagger, phases, attack tracker, and HUD. Registering it earlier could invert initialization or tick polling order.
- **Review Obligation:** Verify that candidate extraction preserves the exact sequence: Footsteps -> Music -> Stagger -> Phases -> Encounter -> DormantWake -> Posture -> Death -> Look -> Bleed -> AttackTracker -> CloseClipSwap -> Shockwave -> LowSweep -> HealPunish -> DamageResolver -> TraceGuard -> TraceAudit -> HUD -> Debug -> Legend. Note: preserving lexical source order is a necessary prerequisite, not a proof of runtime `BeginPlay()` execution or tick group scheduling.

### 5.5. Risk 5: Two-Trigger Idempotence & Repeated Callbacks
- **Current Behavior:** A placed boss pawn in the level is processed during `OnWorldBeginPlay` and may also receive an `OnActorSpawned` event if re-spawned or triggered by level scripts.
- **Helper Implementation Semantics:**
  - In `RPGBossDeath.cpp:48`, `URPGBossDeath::Attach` returns `Existing` if found, bypassing `DeathMode` assignment.
  - In `RPGDamageResolver.cpp:26`, `URPGDamageResolver::FindOrAdd` returns `Existing` if found.
  - In `RPGPlayerMovesSubsystem.cpp:115`, `AddFootsteps` returns early if `URPGFootsteps` is found.
  - The other 18 components check `!Pawn->FindComponentByClass<T>()` before `NewObject`.
- **Refactoring Hazard:** While duplicate instantiation is prevented by these guards, returning existing components does not prove zero repeated-callback side effects if components have registered delegates or stateful initialization.
- **Review Obligation:** Verify that all 21 components retain their idempotence guards, and that candidate extraction does not execute redundant re-initialization.

---

## 6. Minimal Future Witness Plan

To separate offline lexical verification from future runtime proof without executing unapproved tests or inventing nonexistent test APIs, the following minimal verification matrix is specified:

| Test Identifier | Category | Verification Focus | Evaluation Method / Expected Invariant |
|:---|:---|:---|:---|
| **Witness-1** | Offline Lexical | Extracted Boss Helper Order & Token Parity | Run `node legacy_attach_witness.mjs --candidate <source>`. Must confirm 21/21 events match expected sequence and hooks remain bound. Note: exit 0 must be paired with manual diff review of configuration defaults and hook fingerprints. |
| **Witness-2** | Runtime Lifecycle | Trigger A (Dynamic Spawn) | Spawn a supported boss character post-world initialization via actual engine spawn API; observe that required boss component classes are added to the actor. |
| **Witness-3** | Runtime Lifecycle | Trigger B (World-Begin Placement) | Place a supported boss character in map prior to `OnWorldBeginPlay`; observe that required boss component classes are added to the actor. |
| **Witness-4** | Runtime Idempotence | Duplicate Trigger Execution | Execute attachment triggers twice sequentially on an actor with known initial state; verify that existing component instances are retained and no duplicate components of the same class are created. |
| **Witness-5** | Runtime Classification | Supported Player Isolation | Supply an actor derived from `BP_CombatPlayerCharacter_C`; verify that required player component classes are added, and zero boss components are added. |
| **Witness-6** | Runtime Classification | Supported Boss Isolation | Supply an actor derived from `BP_ExampleGreatSwordBoss_C`; verify that required boss component classes are added in order, and zero player components are added. |
| **Witness-7** | Edge Case Controls | Null Actor & Generic Pawn Handling | Pass `nullptr` to trigger (verify graceful no-op without null dereference); supply standard `APawn` without pack inheritance (verify zero components added). |
| **Witness-8** | Edge Case Controls | Partial Pre-Attachment Handling | Supply a boss actor with an already existing `URPGBossStagger` component; verify that the existing component instance is preserved without re-instantiation, and remaining unattached components are added normally. |

*Note: All witnesses in Section 6 remain UNRUN and planned for future execution under an approved fixture; no test execution, new fixture asset, or class policy change is authorized by this precheck.*

---

## 7. Conclusion & Scope Verification

- **Offline Control-Flow Precheck Complete (Rev 02):** Revised with candidate probe false-acceptance outcomes, syntactic call site distinctions, helper implementation pins, and bounded future witness definitions.
- **Zero Forbidden Edits:** No edits to `Source/`, `Config/`, `Scripts/`, Unreal assets, or Codex drafts. Baseline JSON was not overwritten or regenerated.
- **Zero Prohibited Executions:** No Unreal Editor, PIE, build, packaging, or `UnrealPak` commands were executed.
- **Git Authority Preserved:** In strict accordance with `RULE[c:\UnrealProject\OneBossFight\AGENTS.md]`, no git commits or pushes were performed.
