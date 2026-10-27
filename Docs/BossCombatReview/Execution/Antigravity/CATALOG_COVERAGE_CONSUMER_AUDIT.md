# AG14: Catalog Coverage Snapshot vs Combat Consumer Audit (Rev 02)

**Document Date:** 2026-10-27  
**Author:** Antigravity (Pair Programming AI Assistant)  
**Task Classification:** Work Order 14 (AG14) — Audit Catalog Coverage Snapshots vs Actual Combat Consumers (Revision 02)  
**Governing Inputs:**
- Acceptance & Task Directive: [`Docs/BossCombatReview/Execution/Codex/AG13_A138_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG13_A138_ACCEPTANCE.md) (`SHA256: e241098fd415393d6a3719ce6b79416c638f127e238e5b9c7b2c0a78ed105aff`)
- Review Feedback: [`Docs/BossCombatReview/Execution/Codex/AG14_A139_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG14_A139_REVIEW.md) (`SHA256: 1a7f0efd5ea15b648b0e0ea20656fd59a2d12d500c9423bdf013a1be883cee15`)
- Mailbox Directives: `[X-211]`, `[X-212]`, and `[X-213]` (2026-10-27 06:13:54 +05:30)

---

## 1. Executive Summary & Audit Scope (Rev 02)

Per Codex directives `[X-211]`, `[X-213]`, and [`AG14_A139_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG14_A139_REVIEW.md), this revised audit traces the dataflow and consumption pathways between the Catalog compilation snapshot (`RPGCombatRegistry::FEpoch::Coverage`) and the actual combat gameplay consumers:
- [`URPGHitIntake`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.h) (boss hit intake, posture damage, bleed buildup, health scaling)
- [`URPGSwingTracker`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.h) (player swing tracking, stamina costs, hyperarmor windows)
- [`URPGBuildLoadout`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.h) (console build selection, weapon equipping, HUD coverage reporting)
- [`URPGWeaponAttackTable`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGWeaponAttackTable.h) (per-weapon attack data table asset)

### Primary Architectural Findings & Corrections (Rev 02):
1. **Runtime Combat Decoupling from Catalog Coverage:**
   The `FEpoch::Coverage` array compiled in `RPGCombatCatalog.cpp:193-201` is **completely decoupled from actual combat damage and rule evaluation**. The combat components ([`URPGHitIntake`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L166) and [`URPGSwingTracker`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.cpp#L59)) **never read `FEpoch` or `FEpoch::Coverage`**. Instead, each independently caches a pointer to `URPGWeaponAttackTable::LoadOrDefault()` at `BeginPlay()` and executes live queries directly against that table instance on each hit or swing.
2. **Coverage Lines Are Pure Diagnostic Telemetry:**
   The only consumers of `FEpoch::Coverage` in the inspected source are `URPGBuildLoadout::GetCatalogCoverageLines()` (`RPGBuildLoadout.cpp:321-326`) and `URPGCombatCatalogSubsystem::GetCoverageLines()` (`RPGCombatCatalog.cpp:378-380`). Both iterate `Epoch->Coverage` solely to format debug strings for UI/HUD inspection. A diagnostic line displaying values is **not proof** that runtime combat executed those values.
3. **Hyperarmor Is Copied into Coverage, Omitted Only from Formatted Lines:**
   `FCoverage::Effective` is a full `FRPGWeaponAttackRow` struct (`RPGCombatCatalog.h:82`), which contains `HyperArmorStart` and `HyperArmorEnd` (`RPGWeaponAttackTable.h:44-47`). `Table->Find` copies the complete row into `Effective`. The diagnostic formatters omit hyperarmor from their generated text strings (`posture=... stamina=... bleed=... health=...`), but the numeric window values **remain present in the in-memory `FCoverage` object**. A formatter text omission is not a schema absence.
4. **Cached UObject Pointers vs Package Reload Outcomes:**
   `BeginPlay()` table pointer caching and the absence of explicit consumer reload code are verified source facts. However, this does **not prove** that engine package reloaders cannot replace/fix up reflected `TObjectPtr` references or mutate objects in-place. The guaranteed unchanged-address claim has been retracted; witness 3 is specified as a conditional, unrun observational experiment.
5. **Exact API & Override Grounding:**
   - In `RPGHitIntake.h:175`, `BleedOverride` is a plain private `float`, not a `UPROPERTY`.
   - In `RPGHitIntake.h:185`, `Scaler` is a persistent private member (`FRPGDamageScaler`), not a stack object; health scaling operates through asynchronous `OnHit` and `OnLoss` pairing across frames.
   - In `RPGSwingTracker.h/cpp`, the test restoration method is `ClearCostOverrides()` (cpp:63-70). Stamina cost evaluation respects `CostOverrides` precedence before falling back to `Swing.Row.StaminaCost` and checking `bApplyStaminaCosts`.
   - In-place table mutations affect **subsequent lookups on that object**, not in-flight or already captured row structs.
6. **AG13 Receipt Disclosed & Closed:**
   As instructed in `[X-211]`, the AG13 receipt table in [`IMMUTABILITY_LEASE_DEPENDENCY_AUDIT.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/IMMUTABILITY_LEASE_DEPENDENCY_AUDIT.md) was updated to **3,137 bytes**, SHA256 `5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e` for `RPGTimelineCompiler.h`, formally closing the receipt exception.

---

## 2. Inspected Input Receipts & Scope Boundary

The audit scope is strictly bounded to the catalog, attack table, and direct combat consumer headers and implementations:

| File Path | SHA256 Hash | Bytes | Role in Combat Dataflow |
|:---|:---|:---:|:---|
| [`Source/OneBossFight/Player/RPGCombatCatalog.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.h) | `e7d5296833cfa5bec4101e608a98ab336a5b8c7a5c476e0d3b17eae57279dbb5` | 7,427 | `FCoverage`, `FEpoch`, `FContext`, `FDiagnosticLedger` |
| [`Source/OneBossFight/Player/RPGCombatCatalog.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp) | `f6f71036804f60f0e4c8b3cf455f2a04a7bc4cf379760334903a2d9d613de59d` | 23,675 | `Compile` asset resolution, `Table->Find` snapshotting, coverage formatters |
| [`Source/OneBossFight/Player/RPGWeaponAttackTable.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGWeaponAttackTable.h) | `3140b087c97f888ce5e1aa262fcbeeb7a16f57e646aa86dfedacf162b8eddfa1` | 4,079 | `FRPGWeaponAttackRow` struct, table class declaration |
| [`Source/OneBossFight/Player/RPGWeaponAttackTable.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGWeaponAttackTable.cpp) | `f6cdd38ff4957b2831b16c74814bfd28e3499ae2ece50ad06c07be3b88d93ce7` | 5,503 | `Find` route lookup logic, default values, `LoadOrDefault` |
| [`Source/OneBossFight/Player/RPGHitIntake.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.h) | `9cc7604a0cda61f3c8e5e94c84526019eccb28ea0e04852307d027206340121c` | 9,431 | `FRPGHitRecord`, hit intake component declaration, private `BleedOverride`, `Scaler` |
| [`Source/OneBossFight/Player/RPGHitIntake.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp) | `f2d0bd281924c4d29509214c1344234e1a8b2f476a77e51e00a045e73ae4a3db` | 20,867 | `BeginPlay` table caching, hit dispatch, posture/bleed/health scaling |
| [`Source/OneBossFight/Player/RPGBuildLoadout.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.h) | `095c385d2403c1b22d7ca00eafe99e9b4202902d826a47ca5422a91fe10c64af` | 13,126 | Build loadout declaration, `GetCatalogCoverageLines` |
| [`Source/OneBossFight/Player/RPGBuildLoadout.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.cpp) | `7d1f5e70fe19dd8eeb05844e5514c1c3f1dd4c6c97d29819a415820d696e93e2` | 37,628 | Epoch query for weapon equipping, coverage lines stringify |
| [`Source/OneBossFight/Player/RPGDamageScale.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageScale.h) | `d8c8f882225d5a4ecfdddf9ff7d010f12e09314932daf2cad4c3c72e86fb36e6` | 2,947 | `FRPGDamageScaler` health difference adjustment logic (`Window = 0.35s`) |
| [`Source/OneBossFight/Player/RPGSwingTracker.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.h) | `98efb272ddcdc6c7cc76840ead6e70e1030132071e9dd931e86c5118d5f0ae79` | 9,165 | Swing tracker declaration, stamina and hyperarmor overrides |
| [`Source/OneBossFight/Player/RPGSwingTracker.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.cpp) | `ae1f6e0727cfd3c6ad7c9890ececd8880938247e504de179ace799e960088e51` | 12,848 | `BeginPlay` table caching, stamina deduction, `ClearCostOverrides`, hyperarmor |
| [`Source/OneBossFight/Player/RPGAttackKind.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackKind.h) | `8f1b1adcf77d1f19010fe2124aeb3158f63ca313d01527867c7eed56838bb224` | 2,024 | `ERPGAttackKind` enum and string conversion helpers |
| [`Source/OneBossFight/Player/RPGBuildRules.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildRules.h) | `cd6b2a8006a33b90fdc19e8a55d3112b0f60692aac0dbe8988a1b87e7ed84fc6` | 13,229 | Legacy fallback build rules and slots |
| [`Docs/BossCombatReview/Execution/Codex/AG13_A138_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG13_A138_ACCEPTANCE.md) | `e241098fd415393d6a3719ce6b79416c638f127e238e5b9c7b2c0a78ed105aff` | 4,957 | Codex AG13 acceptance & AG14 assignment terms |
| [`Docs/BossCombatReview/Execution/Codex/AG14_A139_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG14_A139_REVIEW.md) | `1a7f0efd5ea15b648b0e0ea20656fd59a2d12d500c9423bdf013a1be883cee15` | 6,959 | Codex A139 review and AG14 Rev 2 correction instructions |
| [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md) | `486b07b40625b99ecdc81883e9daecd842347063c9183715a28a904128e69ed7` | 6,245 | Codex observer content association contract specification |

---

## 3. Dataflow Trace: Compilation Snapshot vs Combat Consumers

### 3.1. Compilation Snapshot Creation (`RPGCombatCatalog.cpp:173-202`)
During catalog compilation (`RPGCombatRegistry::Compile`), when `bResolveAssets == true`:
1. The table asset is loaded: `Table = URPGWeaponAttackTable::LoadOrDefault();`
2. A strong lease is recorded: `E->Leases.Emplace(Table);` (pins the valid UObject under normal GC while `FEpoch` is alive).
3. For each weapon in `Weapons`, for each action `Kind` in `W.Actions`:
   ```cpp
   FCoverage C;
   C.WeaponId = W.WeaponId;
   C.Kind = Kind;
   Table->Find(W.StyleName, Kind, C.Effective);
   C.Route = TEXT("fallback");
   for (const auto& R : Table->Rows) if (R.Kind == Kind && R.Weapon.IsNone()) C.Route = TEXT("any");
   for (const auto& R : Table->Rows) if (R.Kind == Kind && R.Weapon == W.StyleName) C.Route = TEXT("exact");
   ...
   E->Coverage.Add(MoveTemp(C));
   ```
4. **Nature of `FEpoch::Coverage`:**
   - It is a value-copied `TArray<FCoverage>`, where each `FCoverage` contains a deep copy of `FRPGWeaponAttackRow` (`C.Effective`).
   - `C.Effective` **contains all row properties**, including `PostureDamage`, `StaminaCost`, `BleedBuildup`, `HealthDamageMultiplier`, `HyperArmorStart`, and `HyperArmorEnd`.
   - If `bResolveAssets == false`, the loop does not run and `Coverage` remains empty.

---

### 3.2. Combat Domain Consumption Matrix

The table below traces how each combat domain is populated at compile time versus how it is actually resolved and consumed during live gameplay:

| Combat Domain | Captured in `FEpoch::Coverage`? | Live Consumer Component | Actual Consumption Path & Method | Source Location | Value Lifetime & Storage Mode |
|:---|:---:|:---|:---|:---|:---|
| **Posture Damage** | Yes (`C.Effective.PostureDamage`) | `URPGHitIntake` | Invokes `Table->Find(Record.Weapon, Record.Kind, Record.Row)`. Calls `Posture->ApplyPostureDamage(Record.Row.PostureDamage, ...)`. | `RPGHitIntake.cpp:482, 516` | Cached `Table` member query; copied per-hit into `FRPGHitRecord::Row`. |
| **Stamina Cost** | Yes (`C.Effective.StaminaCost`) | `URPGSwingTracker` | Invokes `Table->Find(Swing.Weapon, Swing.Kind, Swing.Row)`. Checks `CostOverrides` precedence, then calculates `RPGSwingRules::StaminaExtra(Wanted, PackCost, Now)` if `Wanted >= 0` and `bApplyStaminaCosts`. | `RPGSwingTracker.cpp:237, 251-260` | Cached `Table` member query; copied per-swing into `FRPGSwingRecord::Row`. |
| **Bleed Buildup** | Yes (`C.Effective.BleedBuildup`) | `URPGHitIntake` | Invokes `Table->Find(Record.Weapon, Record.Kind, Record.Row)`. Checks private `BleedOverride >= 0.f`, else applies `Record.Row.BleedBuildup` via `Bleed->AddBuildup`. | `RPGHitIntake.cpp:482, 524` | Cached `Table` member query; copied per-hit into `FRPGHitRecord::Row`. |
| **Health Damage Multiplier** | Yes (`C.Effective.HealthDamageMultiplier`) | `URPGHitIntake` | Invokes `Table->Find(Record.Weapon, Record.Kind, Record.Row)`. Records `Record.HealthMultiplier`; passes to persistent member `Scaler.OnHit(Time, Multiplier)`. Asynchronously pairs with `Scaler.OnLoss`. | `RPGHitIntake.cpp:482, 493, 502` | Cached `Table` member query; evaluated across frames by member `FRPGDamageScaler`. |
| **Hyperarmor Windows** | **Yes in struct, Omitted in Text** (`C.Effective.HyperArmorStart / End`) | `URPGSwingTracker` | Invokes `Table->Find(Swing.Weapon, Swing.Kind, Swing.Row)`. Evaluates `HyperArmorOverrides` then `Swing.Row.HyperArmorStart / End` via `RPGSwingRules::ResolveWindow`. Applies via `UpdateHyperArmor` / `SetHyperArmor`. | `RPGSwingTracker.cpp:237, 249, 277-375` | Copied per-swing; window open/close evaluated per animation frame. Omitted only from formatted diagnostic text. |
| **Weapon Equipping** | No (Build metadata only) | `URPGBuildLoadout` | Reads `Epoch->Find(Build)` and `Epoch->Weapon(WeaponId)` to get item asset path; calls pack `Update Equip Slot Item`. | `RPGBuildLoadout.cpp:679-680` | Read-only access to `FEpoch` build definitions. |
| **Diagnostic Coverage Lines** | Yes (`Epoch->Coverage`) | `URPGBuildLoadout` / Subsystem | Formats debug text in `GetCatalogCoverageLines()` (`RPGBuildLoadout.cpp:324` and `RPGCombatCatalog.cpp:378-380`). Formats posture, stamina, bleed, health only. | `RPGBuildLoadout.cpp:324`, `RPGCombatCatalog.cpp:378-380` | Pure string formatting for diagnostics; zero gameplay effects. |

---

## 4. Lookup Keys, Route Precedence, Overrides & Refresh Triggers

### 4.1. Table Lookup Key & Route Precedence
Both `Compile()` and runtime consumers (`URPGHitIntake`, `URPGSwingTracker`) query the table via `URPGWeaponAttackTable::Find(FName Weapon, ERPGAttackKind Kind, FRPGWeaponAttackRow& OutRow)`:

1. **Exact Match (Precedence 1):**
   - Matches both `Row.Weapon == Weapon && !Weapon.IsNone()` AND `Row.Kind == Kind`.
   - Returns immediately with `true`.
2. **Any-Weapon Match (Precedence 2):**
   - If no exact match is found, falls back to the first row where `Row.Weapon.IsNone()` AND `Row.Kind == Kind`.
   - Returns with `true`.
3. **Fallback Match (Precedence 3):**
   - If neither matches, assigns `OutRow = this->Fallback`.
   - Populates `OutRow.Weapon = Weapon; OutRow.Kind = Kind;`.
   - Returns `false`.

### 4.2. Overrides & CVar Influences
- **Build Selection (`rpg.Build` CVar):**
  - Read by `URPGBuildLoadout` to select the player's weapon.
  - Equipping a different weapon changes the pawn's `CurrentCombatStyle` (e.g. `SwordCombatStyle` -> `ClaymoreCombatStyle`).
  - This shifts the `Weapon` style key supplied to `Table->Find()` on subsequent hits/swings.
  - It does **not** modify or override any row values within the table.
- **Hit Intake Bleed Override:**
  - `URPGHitIntake::BleedOverride` (`float`, private member, default `-1.f`).
  - In `RPGHitIntake.cpp:524`: if `BleedOverride >= 0.f`, it overrides `Record.Row.BleedBuildup`.
- **Swing Tracker Cost & Hyperarmor Overrides:**
  - `URPGSwingTracker::CostOverrides` (`TMap<ERPGAttackKind, float>`): If a test cost override exists for `Swing.Kind`, `Wanted` uses that value instead of `Swing.Row.StaminaCost` (`RPGSwingTracker.cpp:252-255`).
  - `URPGSwingTracker::HyperArmorOverrides` (`TMap<ERPGAttackKind, FVector2D>`): Test hook overrides table hyperarmor windows (`RPGSwingTracker.cpp:249`).
  - `URPGSwingTracker::bApplyStaminaCosts` (`bool`, default `true`): If `false`, the tracker's extra stamina correction is bypassed entirely (`RPGSwingRules::StaminaExtra` is not evaluated or deducted); this does not alter or refund the pack's own base cost (15) previously paid at swing initiation (`RPGSwingTracker.cpp:256`).
  - `ClearCostOverrides()` (`RPGSwingTracker.cpp:63-70`): Test helper that clears `CostOverrides`, `HyperArmorOverrides`, and restores `Table = OriginalTable`.

### 4.3. Cache Lifetimes & Timing of Mutations
- **Catalog Epoch Lifetime (`URPGCombatCatalogSubsystem`):**
  - Latched **once per game instance** via `FContext::Publish`.
  - Owned by `URPGCombatCatalogSubsystem` (`UGameInstanceSubsystem`), whose lifetime is bounded by the game instance session, not the operating system process.
  - The published-context path has **zero runtime recompile or dynamic refresh mechanism** (though `Compile` remains callable independently for tests or non-published contexts).
- **Hit Intake & Swing Tracker Table Caching:**
  - Both components call `Table = URPGWeaponAttackTable::LoadOrDefault();` once in `BeginPlay()`.
  - `LoadOrDefault()` attempts `LoadObject` on the authored asset path; if not found, it falls back to a rooted transient default instance.
  - **Absence of Consumer Reload Hooks:** Neither component contains code to re-query `LoadOrDefault()` during combat.
  - **Scope Limit on Reload Claims:** The absence of consumer reload code confirms the component does not initiate reloads. However, it does **not prove** that engine package reloaders cannot update reflected `TObjectPtr` references or mutate resident objects in-place.
  - **Mutation Timing:** When an in-memory table is modified in-place, the change affects **subsequent lookups on that specific object**. It does not alter rows already copied into in-flight `FRPGHitRecord` or `FRPGSwingRecord` structs.

---

## 5. Epoch Availability vs Actual Combat Consumption

### 5.1. The "Decoupled Epoch" Reality
An essential assurance distinction must be maintained between **epoch availability** and **actual combat consumption**:

```
[ Catalog Compiler ]
       |
       +---> Generates FEpoch::Coverage (Value-copied snapshot at compile time)
       |            |
       |            +---> Read by URPGBuildLoadout::GetCatalogCoverageLines()
       |            +---> Read by URPGCombatCatalogSubsystem::GetCoverageLines()
       |                  (Both format strings for UI/HUD/debug inspection only)
       |
[ Asset / Memory Table: URPGWeaponAttackTable ]
       |
       +---> Cached by URPGHitIntake::BeginPlay() ------> Live hit query (Posture, Bleed, Health)
       |
       +---> Cached by URPGSwingTracker::BeginPlay() ---> Live swing query (Stamina, Hyperarmor)
```

1. **`URPGBuildLoadout`:**
   - Consumes `FEpoch` for build definitions, weapon definitions, and style name matching.
   - It **does not consume `Coverage.Effective` for equipping**.
   - It reads `Coverage` strictly to build diagnostic text arrays.
2. **`URPGHitIntake` & `URPGSwingTracker`:**
   - **Zero catalog consumption.** They never call `RPGCombatRegistry::ForWorld()`, never inspect `FEpoch`, and never read `FEpoch::Coverage`.
   - They consume numbers directly from `URPGWeaponAttackTable`.
3. **Diagnostic Formatting Limitation:**
   - `GetCoverageLines()` prints strings keyed by `WeaponId` (the catalog weapon identifier), not necessarily `StyleName`.
   - A diagnostic line displaying `posture=18 stamina=35` confirms only what the catalog compile queried at startup. It does **not** prove that runtime hits or swings applied those numbers.

---

## 6. Concrete Unrun Witnesses & Test Proposals

To empirically demonstrate the operational boundary between the catalog coverage snapshot and live combat execution without executing intrusive or unauthorized mutations, the following concrete unrun witnesses are specified:

### Witness 1: In-Place Table Mutation vs Epoch Divergence
- **Objective:** Demonstrate that `URPGHitIntake` reads live in-memory table rows on subsequent hits, while `FEpoch::Coverage` retains its startup snapshot.
- **Procedure (Unrun Proposal):**
  1. Boot game instance; record `FEpoch::Coverage` for the selected test weapon and attack kind via `URPGCombatCatalogSubsystem::GetCoverageLines()`.
  2. Pinpoint the exact `FRPGWeaponAttackRow` inside the active `URPGWeaponAttackTable` instance that matches the test weapon's style name and attack kind (do not assume `Rows[0]`, which in default tables corresponds to claymore-light).
  3. Via a future approved test fixture (not ad hoc reflection in PIE), modify that specific row's `PostureDamage` to a distinct test value `P_test`.
  4. Trigger a player attack hit matching the test style and kind against the boss.
  5. Inspect the newly copied `FRPGHitRecord::Row.PostureDamage`:
     - If hit intake reads the live table, `Row.PostureDamage == P_test`.
     - If hit intake read `FEpoch::Coverage`, `Row.PostureDamage` matches the original startup value.
  6. Re-read `GetCoverageLines()`: verify it continues displaying the original compile value, proving the epoch snapshot does not track in-memory table edits.
  7. Confounders to control: ensure boss posture pool is not at min/max clamps, posture hold state is inactive, and no hit merge or swing kind override intercepted the event.

### Witness 2: Route Precedence & Fallback Verification
- **Objective:** Verify route branching across exact match, any-weapon match, and table fallback.
- **Procedure (Unrun Proposal):**
  1. Specify a test weapon style with no exact row in the table, in an environment where an any-weapon row (`Weapon.IsNone()`) exists for that attack kind.
  2. Execute a hit; verify `Table->Find` returns `true` and populates `Row` from the any-weapon entry, disproving that an unlisted style unconditionally drops to `Fallback`.
  3. In a second isolated test fixture where both exact and any-weapon rows are absent for that kind, execute a hit.
  4. Verify `Table->Find` returns `false` and assigns `OutRow = Fallback`.
  5. Inspect hit intake log: verify it logs fallback usage.
  6. Catalog compile check: Note that if `W.bRequireExactRows == true`, catalog compilation will intentionally reject a weapon that routes to fallback, confirming compile validation guards distinct from runtime fallback tolerance.

### Witness 3: Table Asset Reload Observation (Conditional Experiment)
- **Objective:** Observe whether an engine package reload alters or preserves the cached `Table` pointer in `URPGHitIntake`.
- **Procedure (Unrun Proposal):**
  1. Prior to any reload operation, capture a non-owning `TWeakObjectPtr<URPGWeaponAttackTable>` and record serial object identity metadata from `URPGHitIntake::Table`.
  2. If an approved, non-destructive package reload or replacement is executed in the future, inspect `URPGHitIntake::Table` without calling `BeginPlay()`.
  3. Observe whether the pointer remains valid, points to the original serial identity, or was updated by engine serialization fixups.
  4. Compare a newly executed hit's `FRPGHitRecord::Row` against the reloaded asset data.
  5. Do not infer reload behavior without executing the controlled experiment; record actual outcomes objectively.

### Witness 4: Hyperarmor Struct Presence vs Text Omission & Application
- **Objective:** Prove that hyperarmor window values exist in `FEpoch::Coverage` structs despite omission from diagnostic text, and verify runtime application dependencies.
- **Procedure (Unrun Proposal):**
  1. Direct memory inspection: Read `FEpoch::Coverage[I].Effective.HyperArmorStart` and `HyperArmorEnd` for a strength weapon entry (e.g. claymore jump heavy); confirm non-negative window numbers exist in memory (e.g. `0.352` and `0.618`).
  2. Formatter inspection: Call `GetCatalogCoverageLines()`; verify the formatted string for that entry contains posture, stamina, bleed, and health, but omits hyperarmor numbers.
  3. Runtime swing execution: Initiate the corresponding montage (`Ability_E_Anim_Montage`).
  4. At position `0.400s`, inspect `URPGSwingTracker::bHyperArmor`.
  5. Note that successful hyperarmor activation requires:
     - Active montage matching the swing record
     - Animation position falling within the inclusive interval `Position >= HyperArmorStart && Position <= HyperArmorEnd` per `RPGSwingRules.h:32-35` (including boundary endpoints)
     - Successful execution of `SetHyperArmor(true)` without suppression by state blocks.
  6. Confirm that table window metadata defines the candidate timing window, but does not guarantee runtime immunity without matching playback state.

---

## 7. Architectural Options & Trade-Offs (Proposals Only)

Without mandating schema rewrites or modifying working pack flows, two architectural alternatives exist for future alignment:

1. **Option A: Explicit Decoupling Preserved (Current Architecture)**
   - **Characteristics:** Catalog `FEpoch::Coverage` remains a startup structural and diagnostic integrity check; combat components continue querying `URPGWeaponAttackTable` directly.
   - **Pros:** Zero disruption to existing combat code; allows hot-reloading/tuning of data assets during development without rebuilding catalog epochs.
   - **Cons:** A passing catalog coverage check does not mathematically guarantee live combat parity if runtime table instances diverge.
2. **Option B: Unified Epoch Consumption (Candidate Proposal)**
   - **Characteristics:** Pass `TSharedPtr<const FEpoch>` into `URPGHitIntake` and `URPGSwingTracker` at `BeginPlay()`. Have combat components query `Epoch->Coverage` directly rather than caching `URPGWeaponAttackTable`.
   - **Pros:** Aligns combat input numbers directly with the compiled catalog epoch.
   - **Cons & Limits:** Does **not** guarantee complete parity or strict immutability (combat overrides, lookup timing, damage scalers, and attribute caps still govern final effects); requires refactoring component initialization; prevents live in-place table tuning without publishing new epochs.

---

## 8. Conclusion & Scope Verification

- **Offline Audit Complete:** Conducted entirely through static source inspection, header analysis, and receipt verification.
- **Zero Forbidden Edits:** No edits to `Source/`, `Config/`, `Scripts/`, Unreal assets, or Codex drafts.
- **Zero Prohibited Executions:** No Unreal Editor, PIE, build, packaging, or `UnrealPak` commands were executed.
- **Git Authority Preserved:** In strict accordance with `RULE[c:\UnrealProject\OneBossFight\AGENTS.md]`, no git commits or pushes were performed.
