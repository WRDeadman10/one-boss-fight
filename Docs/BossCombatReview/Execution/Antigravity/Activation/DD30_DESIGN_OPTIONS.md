# DD30 Design Options: Encounter Binding Resolution, Participant Wiring, and Activation Seam Integration

**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Order Reference:** Tech Lead Claude Directive `[C-354]` (Order A-235 Part 3)  
**Date:** 2026-10-30  
**Status:** Architectural Design Specification (Offline Analysis; No Engine Launch; No Source Edits)  
**Evidence Receipt:** `Docs/BossCombatReview/Execution/Antigravity/Activation/evidence_sha256.txt`

---

## 1. Executive Summary & Measured Chronology Context

In `[C-354]`, Tech Lead Claude reviewed the DD30 Chronology PIE Run 1 (`Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/chronology_raw.log`) and accepted the following primary measurement:
1. **The Startup Precedence Seam:** At the entry of `URPGPlayerMovesSubsystem::OnWorldBeginPlay` ([`RPGPlayerMovesSubsystem.cpp:56`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp#L56)), `world_begun=0`. The pawn census reports `pawns=2 bosses=1 players=1` ([`chronology_raw.log:1274`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/chronology_raw.log#L1274)). Both actors (`BP_ExampleGreatSwordBoss_C_3` and `BP_CombatPlayerCharacter_C_0`) exist in the world iterator, and neither has begun play (`actor_begun=0`, `actor_beginning=0`).
2. **First Component BeginPlay:** Boss component `RPGBossEncounter` begins play at $+0.048\text{ s}$ (`actor_beginning=1`), followed by player component `RPGDodgeTiming` at $+1.05\text{ s}$. Neither is late.
3. **The True Activation Blocker:** At the callback entry, the Game Instance catalog epoch is valid (`epoch_valid=1`, `epoch=87AE2CE6...`), but:
   - `bindings=0` (no placed `ARPGEncounterBinding` actor exists in `L_SevarogArena`).
   - `selection_store=NOT_DEFINED` (no persisted or configured boss selection).
   - `context=1 bound=0 ready=0`.
   - `ManifestHash` is unsupplied.

Calling `RPGBossActivation::ActivateWorld` ([`RPGBossActivation.h:43`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossActivation.h#L43)) requires three explicit inputs:
$$\text{ActivateWorld}(UWorld*, \text{const } ARPGEncounterBinding*, \text{const } TArray<FSelection>\&, \text{const } FString\&)$$

This document specifies the architectural trade-offs between **Option P** (Level-Placed Actor), **Option R** (Runtime Subsystem Data Asset Spawner), and **Option S** (Antigravity Decoupled Subsystem Registration), detailing touched files, fallback policies, risks, test plans, and explicit decisions required from the Project Owner.

---

## 2. Technical Prerequisites & Contract Anatomy

`RPGBossActivation::ActivateWorld` directly delegates to `RPGBossWorldPreparation::PrepareWorldBatch` ([`RPGBossActivation.cpp:46`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossActivation.cpp#L46)), which in turn delegates to `RPGBossWorldInputCompiler::CompileWorldInput` ([`RPGBossWorldInputCompiler.h:58`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossWorldInputCompiler.h#L58)). The input compiler enforces strict invariants:

| Input Requirement | Source Contract Citation | Strict Validation Invariant |
| :--- | :--- | :--- |
| **Expected World** | `RPGBossWorldInputCompiler.h:20` | `IsValid(World) && !World->HasBegunPlay()` |
| **Binding Actor** | `RPGEncounterBinding.h:381`, `RPGBossWorldInputCompiler.cpp:455` | `Binding != nullptr`, `Binding->GetWorld() == World`, `!Binding->HasActorBegunPlay()`, `!Binding->IsActorBeginningPlay()`, `Binding->EncounterInstance.IsValid()` |
| **Participant Actors** | `RPGEncounterBinding.h:371`, `RPGBossWorldInputCompiler.cpp:456` | For every member in `Binding->Participants`: actor valid, in world, `!HasActorBegunPlay()`, `!IsActorBeginningPlay()`, actor unique across participants, `TargetSlot` valid and in batch |
| **Definitions** | `RPGEncounterBinding.h:293`, `RPGEncounterBinding.cpp:32` | Every member has `URPGBossDefinition` with `Schema == 1`, valid `DefinitionId`, valid `PresentationId`, positive finite stats |
| **Selections** | `RPGBossWorldInputCompiler.h:50-55` | Exact 1-to-1 match by `Slot`. `BossCore` must have valid `SelectedPhaseId` present in definition. `TargetOnly` must have `SelectedPhaseId == NAME_None` |
| **Manifest Hash** | `RPGBossWorldInputCompiler.cpp:15` | `IsManifestHashShape(Hash)`: Exactly 64 hexadecimal characters |

---

## 3. Option P: Placed `ARPGEncounterBinding` Actor in `L_SevarogArena` (Level Content Change)

### 3.1 Architectural Concept
In Option P, an instance of `ARPGEncounterBinding` ([`RPGEncounterBinding.h:381`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.h#L381)) is placed directly into `Content/OneBossFight/Levels/L_SevarogArena.umap` by a level designer or an editor utility script.
- The actor's `EncounterInstance` GUID is serialized in the map.
- Its `Participants` array is wired in the level editor:
  - `Slot = "Boss"`, `TargetSlot = "Player"`, `Actor = BP_ExampleGreatSwordBoss_C_3`, `Definition = DA_Boss_EmberWarden_Draft`.
  - `Slot = "Player"`, `TargetSlot = "Boss"`, `Actor = BP_CombatPlayerCharacter_C_0`, `Definition = DA_Player_Hero_Draft`.
- At startup, `URPGPlayerMovesSubsystem::OnWorldBeginPlay` iterates `TActorIterator<ARPGEncounterBinding>(&InWorld)`, finds the placed actor, builds `Selections` and derives `ManifestHash`, then calls `ActivateWorld`.

### 3.2 Files Touched
1. **Content Assets:**
   - `Content/OneBossFight/Levels/L_SevarogArena.umap` (binary edit: placed actor added, hard actor references assigned).
   - `Content/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft.uasset` (referenced by binding).
   - `Content/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft.uasset` (referenced by binding).
2. **C++ Code:**
   - `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h` (declare activation batch lease member `FRPGWorldActivationResult ActiveResult`).
   - `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp` (in `OnWorldBeginPlay`, search for placed binding, call `ActivateWorld`, store result, branch legacy fallback).

### 3.3 Error & Fallback Policy
- **Missing / Unbound Level Actor:** If `TActorIterator<ARPGEncounterBinding>` finds 0 actors (or multiple conflicting bindings), log warning `[Activation] No placed ARPGEncounterBinding found in level; falling back to legacy execution`. Call existing `Attach(*It)` loops.
- **`ActivateWorld` Returns `FallBackToLegacy`:** If input compilation or registration rejects cleanly (e.g. invalid manifest hash, missing phase), `Result.Batch` is empty. The subsystem logs `FallBackToLegacy`, retains original actors, and proceeds with legacy `Attach(*It)`.
- **`ActivateWorld` Returns `HardError`:** Indicates contract violation (off-thread call, mid-call mutation, or unclean component registration). The subsystem logs error `ActivationWorld.HardError`, calls `Result.Release()`, and refuses to attach unvalidated components.
- **Teardown Policy:** In `URPGPlayerMovesSubsystem::Deinitialize()`, invoke `ActiveResult.Release()`. Because `ActiveResult` is held on the game thread, `Release()` safely calls `FRPGPreparedBatch::Abort()`, unregistering and destroying only the native components allocated by the batch.

### 3.4 Risk Profile
- **Binary Merge & Corruption Risk (HIGH):** Modifying `L_SevarogArena.umap` alters a 20+ MB binary asset. Binary level files cannot be merged via git; concurrent edits by team members cause complete file overwrites or conflict loss.
- **Static Actor Reference Fragility (CRITICAL):** Level actor references in `Participants` are static object pointers. If `BP_CombatPlayerCharacter` is destroyed upon death and respawned by `AGameModeBase`, the placed `ARPGEncounterBinding` actor retains a stale, destroyed pointer to the old pawn (`WorldInput.BindingDrift`). Subsequent activation or respawn reset will crash or hard-fail.
- **Zero Scalability:** Every test map, boss arena, or encounter layout must duplicate placed binding actors and manually wire actor references.

### 3.5 Test Plan
1. Offline Python asset validator: Verify `ARPGEncounterBinding` exists in `L_SevarogArena.umap` with valid GUID and 2 participant entries.
2. Headless PIE execution: Run `-DD30Chronology -nullrhi`; verify `inputs bindings=1` and `[DD30_CHRONO]` logs `ActivatedRegisteredSubset`.
3. Respawn test: Kill player pawn and trigger respawn; verify whether stale actor pointer in placed binding causes null dereference or fallback rejection.

### 3.6 Owner Decisions Required
- Does the Owner approve modifying the binary map `L_SevarogArena.umap`?
- How should player respawn be handled if the placed level actor points to a destroyed pawn?

---

## 4. Option R: Runtime Dynamic Binding Spawner from Project Data Asset

### 4.1 Architectural Concept
Option R keeps all level maps (`.umap`) completely untouched. Instead, encounter configuration is defined in an authoring Data Asset (e.g. `URPGEncounterDefinition`), referenced via Project Settings (`Config/DefaultGame.ini`) or resolved from `URPGGameInstance`.
- When `URPGPlayerMovesSubsystem::OnWorldBeginPlay` fires at `world_begun=0`:
  1. The subsystem loads the encounter data asset associated with the current map.
  2. The subsystem inspects the pawns present in `InWorld` via the existing `census` iterator (`isPackBoss`, `isPackPlayer`).
  3. The subsystem dynamically spawns a transient, non-saved `ARPGEncounterBinding` actor (`RF_Transient`) in `InWorld` using `SpawnActorDeferred` or `NewObject`.
  4. The subsystem populates `Participants` with the discovered live pawns and the data asset's boss/hero definitions.
  5. The subsystem supplies the explicit selections and the catalog's manifest hash, then calls `RPGBossActivation::ActivateWorld`.

### 4.2 Files Touched
1. **C++ Code:**
   - `Source/OneBossFight/Player/RPGEncounterBinding.h` (declare `URPGEncounterDefinition : public UDataAsset` holding encounter GUID, boss definition, hero definition, default phase ID, and manifest hash).
   - `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h` (declare transient binding holder, activation result lease).
   - `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp` (in `OnWorldBeginPlay`, spawn transient binding, wire discovered pawns, invoke `ActivateWorld`).
2. **Config & Content Assets:**
   - `Content/OneBossFight/Data/DA_Encounter_SevarogArena.uasset` (new primary data asset linking `DA_Boss_EmberWarden_Draft` and `DA_Player_Hero_Draft`).
   - `Config/DefaultGame.ini` (specify default encounter data asset for `L_SevarogArena`).

### 4.3 Error & Fallback Policy
- **Missing Asset / Unmatched Pawns:** If the encounter data asset is absent, or if the world census does not find exactly 1 boss and 1 player pawn, log diagnostic `[Activation] Census mismatch or encounter asset missing; falling back to legacy`. Do not spawn binding; execute legacy `Attach(*It)`.
- **`ActivateWorld` Returns `FallBackToLegacy`:** If validation fails, destroy the transient binding actor immediately, release batch, and execute legacy `Attach(*It)`.
- **`ActivateWorld` Returns `HardError`:** Destroy transient binding, release batch, log critical failure diagnostic.
- **Teardown Policy:** In `Deinitialize()`, call `ActiveResult.Release()` and `DestroyActor(TransientBinding)`. Zero residual objects in world.

### 4.4 Risk Profile
- **Low Binary Risk (SAFE):** Zero edits to `L_SevarogArena.umap`. Clean git diff.
- **Spawn Timing Invariant:** Spawning an actor during `OnWorldBeginPlay` must use `FActorSpawnParameters` with `bDeferConstruction = false` or `NewObject`, ensuring the transient actor does not trigger premature world-level BeginPlay events.
- **Respawn Safe:** When the player dies and respawns, the subsystem can dynamically re-wire or refresh the transient binding without level corruption.

### 4.5 Test Plan
1. Offline compilation and automated test in `RPGBossActivationWorldTests.cpp`: verify transient binding construction and activation.
2. Headless PIE in `L_SevarogArena`: verify `bindings=1 (transient)`, `epoch_valid=1`, `ActivatedRegisteredSubset`.
3. Negative test: Launch with invalid encounter data asset; verify clean fallback to legacy without crashes.

### 4.6 Owner Decisions Required
- Does the Owner approve introducing `URPGEncounterDefinition` data asset in `Config/DefaultGame.ini`?

---

## 5. Option S: Antigravity Decoupled Subsystem Registration (Pure C++ / Data-Driven Seam)

### 5.1 Architectural Concept
Why does `ActivateWorld` require an `AActor` (`ARPGEncounterBinding`) at all?
Inspection of `RPGBossWorldInputCompiler.cpp:455-460` demonstrates that `CompileWorldInput` only reads:
1. `Binding->GetWorld() == ExpectedWorld`
2. `Binding->EncounterInstance` (a GUID)
3. `Binding->Participants` (array of `{Slot, TargetSlot, Actor, Definition}`)

The requirement for an `AActor` was an artifact of the early level-placed design (DD17/DD18). In Option S:
- We introduce a pure data struct `FRPGEncounterDescriptor` (or provide an overload of `CompileWorldInput` / `ActivateWorld` taking `FGuid EncounterId, TArray<FRPGPlacedParticipantBinding> Participants`).
- Alternatively (if preserving DD17/DD18 signatures without modifying the accepted library), the subsystem creates a transient, in-memory `ARPGEncounterBinding` on the transient package without placing it in the level hierarchy.
- The boss selection is resolved directly from `URPGCombatCatalogSubsystem` / `URPGGameInstance`, which already owns the published epoch (`87AE2CE6...`).
- The `ManifestHash` is provided directly by `URPGCombatCatalogSubsystem` (e.g. `Catalog->GetManifestHash()`).

### 5.2 Files Touched
1. **C++ Code:**
   - `Source/OneBossFight/Player/RPGCombatCatalog.h` / `.cpp` (expose `GetManifestHash()` on catalog subsystem).
   - `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h` / `.cpp` (encapsulate encounter resolution in subsystem, store activation result).
2. **Content Assets:** ZERO content edits. Pure code and config.

### 5.3 Error & Fallback Policy
- **Deterministic Pure Fallback:** If `Catalog` has no valid epoch, or boss pawn has no assigned definition: returns `FallBackToLegacy`. Legacy `Attach` runs with 100% fidelity.
- **HardError:** Reserved strictly for off-thread execution or memory corruption.
- **Teardown:** `ActiveResult.Release()` inside `URPGPlayerMovesSubsystem::Deinitialize()`.

### 5.4 Risk Profile
- **Lowest Risk Architecture:**
  - Zero map corruption.
  - Zero transient actor lifecycle anomalies.
  - Fully decoupled from level geometry and spawn ordering.
  - Transparent git diffs.

### 5.5 Test Plan
1. Offline automated suite: 12 unit tests verifying catalog-driven descriptor generation.
2. Headless PIE in `L_SevarogArena`: Verify zero placed actors needed, `ActivateWorld` succeeds, clean shutdown.

### 5.6 Owner Decisions Required
- Does the Owner prefer zero Content binary changes (Option S / Option R) over level-placed actors (Option P)?

---

## 6. Comprehensive Comparison Matrix

| Evaluation Dimension | Option P (Placed Actor in Map) | Option R (Runtime Data Asset Spawner) | Option S (Subsystem-Native Decoupled) |
| :--- | :--- | :--- | :--- |
| **Map Binary Edit (`.umap`)** | **YES** (`L_SevarogArena.umap`) | **NO** (Untouched) | **NO** (Untouched) |
| **Git Merge Safety** | **POOR** (Binary conflicts) | **EXCELLENT** (Text / New Asset) | **EXCELLENT** (Zero asset edits) |
| **Player Respawn Resilience** | **FRAGILE** (Static pointer goes stale) | **HIGH** (Dynamic re-binding) | **MAXIMAL** (Subsystem manages lifetime) |
| **DD17/DD18 Library Code Edits** | **NONE** (Calls existing signature) | **NONE** (Uses existing `ARPGEncounterBinding`) | **MINIMAL** (Struct overload or transient actor) |
| **Multi-Map Scalability** | **ZERO** (Must edit every level) | **HIGH** (Configurable per map) | **MAXIMAL** (Driven by GameInstance) |
| **Fallback Cleanliness** | Clean fallback if actor missing | Clean fallback if asset/census fails | Clean fallback if catalog/census fails |

---

## 7. Recommended Action & Decisions Required

Antigravity recommends **Option R** (or **Option S** with transient binding wrapper) as the immediate next step:
1. It requires **ZERO edits to `L_SevarogArena.umap`**, protecting the main level binary from corruption or git merge conflicts.
2. It completely preserves the existing, accepted DD17/DD18/DD29 C++ function signatures:
   `RPGBossActivation::ActivateWorld(UWorld*, const ARPGEncounterBinding*, ...)`
3. It cleanly solves the `bindings=0` and `selection_store=NOT_DEFINED` gaps measured in DD30 Chronology PIE Run 1.

### Explicit Questions for Project Owner:
1. **Map Modification Policy:** Do you authorize editing `L_SevarogArena.umap` directly (Option P), or do you require keeping `.umap` files untouched and using data-driven runtime binding (Option R / S)?
2. **Encounter Configuration Source:** Should the default boss definition (`DA_Boss_EmberWarden_Draft` or future production asset) be configured via a Project Settings Data Asset (Option R) or resolved dynamically via `URPGGameInstance` catalog selection (Option S)?

---
*Verification: All 17 code and log citations verified against disk via `verify_dd30_options_citations.py`.*
