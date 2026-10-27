# P1 Binding Diagnostic False-Confidence Audit

**Document ID:** `P1_BINDING_DIAGNOSTIC_AUDIT`  
**Date:** 2026-10-26  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Work Order:** `Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_07.md` (Task **AG07-1**)  
**Governing Documents & Primary Source Anchors:**  
- Work Order: [`ANTIGRAVITY_WORK_ORDER_07.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_07.md)
- Target Diagnostic Driver: [`Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_encounter_binding.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_encounter_binding.py) (SHA256: `096b265baac1f1ebf4f486cbe36c42eaf50a667e8efd4412eaa3aa245e90dc22`)
- Inert Binding Header: [`Source/OneBossFight/Player/RPGEncounterBinding.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.h) (SHA256: `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80`)
- Inert Binding Source: [`Source/OneBossFight/Player/RPGEncounterBinding.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.cpp) (SHA256: `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc`)
- Inert Binding Tests: [`Source/OneBossFight/Tests/RPGEncounterBindingTests.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGEncounterBindingTests.cpp) (SHA256: `bcdb3b2f40f1795bfd6187523cf98fc8ab2567cae46949065dd3a6908f2d66da`)
- Catalog CVar Implementation: [`Source/OneBossFight/Player/RPGCombatCatalog.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp) (SHA256: `f19f2a2e99fa9b3eeb0c169d2f218a59489fc9333da56ec6ea1c944111326c9f`)
- Coordinator Adversarial Review: [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/07_REGISTRATION_TEARDOWN_ADVERSARIAL_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/07_REGISTRATION_TEARDOWN_ADVERSARIAL_REVIEW.md) (SHA256: `90482cd3ce9daf974c2219b043aa63500f3686bcb2bdafd91e99ad3c9b9c7527`)
- Cleanup & Abort Contract: [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/08_PREPARATION_ABORT_AND_CLEANUP_CONTRACT.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/08_PREPARATION_ABORT_AND_CLEANUP_CONTRACT.md) (SHA256: `b397493212e8d024ff962c28d1719ff36fabf6034b5abcec8e3169ccf7473bcb`)
- Parity Crosswalk: [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/09_FIRST_CLUSTER_TYPED_PARITY_CROSSWALK.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/09_FIRST_CLUSTER_TYPED_PARITY_CROSSWALK.md) (SHA256: `fda0ed8e6468f43760b1b3ceff090a20a5ece30a96d36b78d73e8178de62d327`)

---

## 1. Executive Summary

This audit fulfills Task **AG07-1** of Codex Technical Lead's Work Order 07 (`[X-174]`, reviewed in `[X-178]`).

It performs an independent, adversarial code-level analysis of the dormant diagnostic driver [`pie_encounter_binding.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_encounter_binding.py), dissecting every assertion to expose:
1. **Vacuous Invalid-Mode False Acceptance:** Proof that `invalid == 1` checks (lines 67–68) pass vacuously on a level where 0 participants exist. (Note: earlier valid-mode checks legitimately fail their non-zero bound count assertions; the vacuity is isolated to the invalid-mode rejection predicates).
2. **Missing Encounter Association Proof:** Proof that verifying $\ge 4$ unique string keys does not establish association with two distinct encounter instances or valid slot targeting.
3. **CVar State Isolation Vulnerabilities:** Proof that the driver fails to save or restore `rpg.CatalogPath` and `rpg.CatalogTestFourth`, risking cross-test contamination and hard crashes across startup modes if a preceding session crashed or exited without cleanup.
4. **Boundary Distinction:** Clearly separating expected missing-fixture failures from latent false passes that create unearned confidence.

> [!IMPORTANT]
> **Boundary Notice:** This audit is conducted purely via static code inspection and offline analysis. The driver was **not executed in editor**, no PIE sessions were launched, and no live source or configuration files were modified.

---

## 2. Source-Pinned Assertion Audit Table

The following table analyzes every check performed in [`pie_encounter_binding.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_encounter_binding.py):

| Line | Assertion Call | Necessary Preconditions | What It Actually Proves | Potential False Acceptance (Failure Mode) | Required Independent Witness | Phase & Approval Boundary |
|---|---|---|---|---|---|---|
| **54** | `check(mode + " PIE world", w is not None)` | Editor Level Subsystem is responsive; PIE begins within 20s. | An active `UWorld` exists in PIE. | **Map Ambiguity:** Does not prove the target fixture map loaded; passes on default entry map or an empty level. | Witness `w.GetMapName()` matches expected fixture path. | Step 2a Infrastructure |
| **58** | `check(mode + " context available", ctx is not None)` | `URPGCombatContextSubsystem` class is compiled and registered in engine. | Subsystem collection instantiated the world subsystem. | **Inert Shell:** Subsystem exists in memory, but may have 0 registered adapters, 0 records, and no live functionality. | Witness subsystem internal registration table and epoch lease. | Step 2a Infrastructure |
| **62** | `check(mode + " fresh world session", bool(session) and session not in previous_sessions)` | `URPGCombatContextSubsystem::Initialize()` invoked `FGuid::NewGuid()`. | Subsystem generated a non-empty GUID distinct from previous iterations. | **Memory Independence Unproven:** Generates a new GUID, but does not prove unmanaged memory, static delegates, or leaked UObjects from previous sessions were torn down. | Witness clean GC collection and zero cross-session actor leaks. | Step 2a Teardown Contract |
| **67** | `check("strict invalid publishes no ready stack", ctx.get_ready_count() == 0)` *(when invalid == 1)* | Map has opened under `CatalogTestInvalid = 1`. | Context reports `ReadyCount == 0`. | **VACUOUS PASS:** If map has 0 participants or failed to spawn any encounter, `ReadyCount` is 0 vacuously. It passes on an empty level without testing invalid rejection at all. | Precondition assertion: `len(participants) >= 4` or explicit `ctx.get_rejected_count() > 0`. | Step 2b Error Handling |
| **68** | `check("strict invalid no participant fallback", not any(c.is_ready() for c in participants))` *(when invalid == 1)* | `participants` list retrieved via `get_components_by_class`. | None of the collected component proxies report `IsReady() == True`. | **VACUOUS PASS:** If `participants == []` (empty list), `not any([])` evaluates to `True`! Passes completely unexercised on any map lacking participant components. | Precondition assertion: `len(participants) > 0` before checking component states. | Step 2b Error Handling |
| **70** | `check(mode + " explicit two-encounter fixture present", ctx.get_bound_count() >= 4)` *(when invalid == 0)* | Two-encounter fixture map loaded; actors registered with context. | Context has $\ge 4$ internal `FRecord` entries. | **Association Blindness:** Does not prove two encounters exist. Passes if 1 encounter registered 4 participants, or 4 independent single-slot encounters exist. | Witness `len(set(r.EncounterInstance for r in records)) == 2`. | Step 2b Multi-Encounter |
| **71** | `check(mode + " every bound participant ready", ctx.get_ready_count() == ctx.get_bound_count() and ctx.get_ready_count() >= 4)` | Context executed component plans. | All tracked internal records have `bHydrated == true`. | **Gameplay Disconnect:** `bHydrated = true` in subsystem only proves plan callback returned true; it does not prove the actor's live gameplay components (Attributes, AI, Mesh) were successfully initialized. | Witness live actor attribute readback (e.g. `Attribute.Health == 2000`). | Step 2b Adapter Parity |
| **72** | `check(mode + " participant component count", len(participants) == ctx.get_bound_count())` | Level contains actor components matching subsystem bound count. | Number of actor components in level matches records. | **Orphan Equivalence:** Passes if an unrelated component was spawned while an intended participant failed to register. | Verify 1:1 bi-directional actor pointer mapping between level actors and subsystem records. | Step 2a Registry |
| **74** | `check(mode + " keys unique", len(keys) >= 4 and len(keys) == len(set(keys)))` | `URPGCombatParticipant::GetKeyDiagnostic()` returns formatted strings. | String diagnostic representations of keys are mutually unique. | **False Topology:** Unique keys do not prove encounter topology. Keys differ if slot names differ (`SlotA`, `SlotB`, `SlotC`, `SlotD`) even if all belong to a single broken encounter. | Verify exact pairing: Encounter 1 has `(Boss, Player)` and Encounter 2 has `(Boss, Player)`. | Step 2b Multi-Encounter |
| **75** | `check(mode + " every participant ready", bool(participants) and all(c.is_ready() for c in participants))` | `participants` list is non-empty. | `URPGCombatParticipant::IsReady()` returns true for all components. | **Shallow Readiness:** `IsReady()` only checks `Snapshot.IsValid() && Context.IsValid() && !Context->IsPoisoned()`. Does not verify live montage readiness or combat catalog state. | Witness ability system readiness and catalog binding. | Step 2b Lifecycle |
| **78** | `check(mode + " ready after real GC", ctx.get_ready_count() >= 4 and all(c.is_ready() for c in participants))` | `collect_garbage()` executed and yielded 0.5s. | Components and context survived garbage collection. | **Static Persistence:** Surviving GC in an undisturbed PIE session does not test weak-reference invalidation upon actor destruction, unbinding, or level streaming. | Execute explicit `Actor->Destroy()` and witness clean context unbinding. | Step 2b GC Lifecycle |
| **83** | `check(mode + " teardown world gone", world() is None)` | `editor_request_end_play()` called; world torn down. | Editor subsystem reports game world is None. | **Teardown Leak Blindness:** World pointer being cleared does not prove background tasks, unmanaged memory, or static delegates were freed. | Witness allocation tracking / transaction ledger cleanup. | Step 2a Teardown Contract |

---

## 3. Deep-Dive Material False-Confidence Analysis

### 3.1 The Vacuous Invalid-Mode Pass Defect
In [`pie_encounter_binding.py:66-68`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_encounter_binding.py#L66-L68):
```python
if invalid:
    check("strict invalid publishes no ready stack", ctx.get_ready_count() == 0)
    check("strict invalid no participant fallback", not any(c.is_ready() for c in participants))
```

#### Counterexample Proof:
Consider executing this driver iteration when no participant components exist in the level (or if an authoring failure prevented actor spawning):
1. `actors = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)`
2. `participants = [c for a in actors for c in a.get_components_by_class(unreal.RPGCombatParticipant)]` $\rightarrow$ Evaluates to `[]` (empty list).
3. `ctx.get_ready_count() == 0` $\rightarrow$ Evaluates to `0 == 0` $\rightarrow$ **`True` (PASS)**.
4. `not any(c.is_ready() for c in participants)` $\rightarrow$ Evaluates to `not any([])` $\rightarrow$ `not False` $\rightarrow$ **`True` (PASS)**.

> [!NOTE]
> **Scope of Vacuity:** While earlier valid iterations (`legacy`, `auto`, `data` with `invalid=0`) fail at line 70 (`get_bound_count() >= 4`) if the fixture map is blank, this specific `invalid=1` branch passes vacuously when components are absent. It provides zero proof that the invalid input was detected and rejected by the subsystem.

#### Proposed Remedy:
Bad configuration rejection may legitimately result in **zero** participant components being spawned on candidate actors. Therefore, requiring non-zero ready participants in invalid mode is the wrong fix. The correct witness sequence requires:
1. Independently witnessing that the fixture binding actor and candidate actors exist in the level.
2. Independently witnessing that the invalid input was ingested by the subsystem and produced an explicit rejection diagnostic state.
3. Then verifying zero published ready stack and no fallback:
```python
if invalid:
    # 1. Witness fixture actor presence
    binding_actors = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGEncounterBinding)
    check("invalid mode fixture binding actor present", len(binding_actors) > 0)
    # 2. Witness explicit rejection diagnostic state
    check("strict invalid logs rejection diagnostic", ctx.get_rejection_count() > 0)
    # 3. Verify zero published ready stack
    check("strict invalid publishes no ready stack", ctx.get_ready_count() == 0)
    check("strict invalid no participant fallback", not any(c.is_ready() for c in participants))
```

---

### 3.2 Key Uniqueness vs Encounter Association
In [`pie_encounter_binding.py:73-74`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_encounter_binding.py#L73-L74):
```python
keys = [str(c.get_key_diagnostic()) for c in participants]
check(mode + " keys unique", len(keys) >= 4 and len(keys) == len(set(keys)))
```

#### Topological Failure Mode:
`FRPGParticipantKey` is composed of `(WorldSession, EncounterInstance, Slot, Generation)` (`RPGEncounterBinding.h:72-82`).
Suppose an encounter authoring defect causes all 4 participants to be assigned to a **single encounter** with slots `Boss`, `Minion1`, `Minion2`, `Minion3`:
- All 4 keys have identical `EncounterInstance` GUIDs.
- All 4 keys have identical `WorldSession` GUIDs.
- But their slot strings differ $\rightarrow$ String diagnostics are mutually unique!
- `len(keys) == 4` and `len(set(keys)) == 4` $\rightarrow$ **`True` (PASS)**!

The test announces `"explicit two-encounter fixture present"` and passes, even though:
1. Only **one** encounter exists in the level.
2. The second encounter was never spawned or bound.
3. Cross-encounter isolation is completely unverified.

#### Proposed Remedy (Pseudocode Diagnostic Seams):
Verify the actual encounter topology using proposed read-only diagnostic seams (marked as pseudocode; not current exposed runtime APIs):
```python
# Proposed diagnostic pseudocode:
encounter_ids = {c.get_encounter_instance_id() for c in participants}
check("exactly two distinct encounter instances bound", len(encounter_ids) == 2)
for enc_id in encounter_ids:
    enc_participants = [c for c in participants if c.get_encounter_instance_id() == enc_id]
    check(f"encounter {enc_id} has exactly 2 participants", len(enc_participants) == 2)
    slots = {c.get_slot_name() for c in enc_participants}
    check(f"encounter {enc_id} has Boss and Player slots", slots == {"Boss", "Player"})
```

---

## 4. Startup CVar State Isolation Defect

### 4.1 The Unisolated CVars
In [`pie_encounter_binding.py:17-18`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_encounter_binding.py#L17-L18):
```python
ORIGINAL = {name: unreal.SystemLibrary.get_console_variable_string_value(name)
            for name in ("rpg.CatalogSource", "rpg.CatalogTestInvalid")}
```

In [`Source/OneBossFight/Player/RPGCombatCatalog.cpp:17-20`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L17-L20), there are **four** interacting startup CVars:
1. `rpg.CatalogSource` (Startup only: `auto`, `legacy`, `data`)
2. `rpg.CatalogTestFourth` (Startup only: integer flag for fourth build fixture)
3. `rpg.CatalogPath` (Startup only: string path to isolated test catalog)
4. `rpg.CatalogTestInvalid` (Startup only: integer flag for invalid fixture)

`pie_encounter_binding.py` completely ignores `rpg.CatalogPath` and `rpg.CatalogTestFourth`!

### 4.2 Cross-Test Contamination Scenarios (Hypothetical Preconditions)
If an uncleaned external session, aborted test, or process crash leaves startup CVars in non-default states:

#### Scenario A: Residual `rpg.CatalogPath`
If an uncleaned session leaves `rpg.CatalogPath` set to a test catalog (e.g. under `/Game/OneBossFight/Data/TypedABIFixtures/...`):
1. `pie_encounter_binding.py` runs its first iteration: `command("rpg.CatalogSource legacy")`.
2. In `RPGCombatCatalog.cpp:307`:
   ```cpp
   if (LatchedSource != TEXT("data"))
       PathError = TEXT("CatalogPath: a test catalog needs rpg.CatalogSource data (no legacy/auto fallback)");
   ```
3. **Failure:** `URPGCombatCatalog` enters an error state because a test catalog path was supplied while `CatalogSource` was set to `legacy`. The driver fails unexpectedly due to uncleaned external state.

#### Scenario B: Residual `rpg.CatalogTestFourth`
If an uncleaned session leaves `rpg.CatalogTestFourth = 1`:
1. `pie_encounter_binding.py` runs its third iteration: `command("rpg.CatalogSource data")`.
2. In `RPGCombatCatalog.cpp:308`:
   ```cpp
   else if (CVarCatalogFourth.GetValueOnGameThread() != 0)
       PathError = TEXT("CatalogPath: conflicts with rpg.CatalogTestFourth (one startup fixture at a time)");
   ```
3. If `CatalogPath` was also set, a hard conflict error is triggered.
4. Furthermore, `pie_encounter_binding.py` does not clear `CatalogTestFourth` upon exit, leaving the fourth build injected for subsequent tests.

#### Proposed Remedy:
All 4 startup CVars must be captured, isolated, and restored:
```python
MONITORED_CVARS = (
    "rpg.CatalogSource",
    "rpg.CatalogTestFourth",
    "rpg.CatalogPath",
    "rpg.CatalogTestInvalid"
)
ORIGINAL = {name: unreal.SystemLibrary.get_console_variable_string_value(name)
            for name in MONITORED_CVARS}
```
At start of each test iteration, explicitly reset unneeded CVars:
```python
command("rpg.CatalogPath \"\"")
command("rpg.CatalogTestFourth 0")
```

---

## 5. Distinguishing Missing Approved Fixtures from False Passes

It is essential to distinguish between two completely different classes of test outcomes:

1. **Class 1: Legitimate Missing-Fixture Failure (Expected & Correct):**
   - When `pie_encounter_binding.py` is run on a normal map without the unpromoted two-encounter fixture, it should fail loudly at Line 70 (`ctx.get_bound_count() >= 4`).
   - This failure is **expected and desirable**: it confirms that the prototype requires its approved two-encounter map and does not silently manufacture fake data.
2. **Class 2: Silent False Pass (Latent Danger):**
   - When run with `invalid = 1` on an empty map, lines 67-68 pass vacuously without verifying that invalid inputs were actually rejected.
   - When run on a broken map with 4 participants under 1 encounter, line 74 passes and reports `"explicit two-encounter fixture present"`.
   - These are **false passes**: they report green checkmarks while exercising none of the intended safety invariants.

---

## 6. Conclusion & Recommendations for Work Order 07

1. **Do not treat `pie_encounter_binding.py` as an acceptance gate in its current form:** Its invalid-mode and topological assertions permit false passes under trivial map conditions.
2. **Harden driver preconditions:** In valid binding mode, require explicit four-participant counts with two distinct encounter instances before confirming binding; in invalid rejection mode, verify an explicit rejection witness and logged catalog diagnostic rather than vacuously accepting empty maps.
3. **Expand CVar isolation:** Include `rpg.CatalogPath` and `rpg.CatalogTestFourth` in `ORIGINAL` save/restore routines.
4. **Enforce topology verification:** Dissect participant keys to confirm exactly two distinct encounter instances with paired `(Boss, Player)` slots.
