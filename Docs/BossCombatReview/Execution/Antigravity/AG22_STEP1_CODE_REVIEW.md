# AG-22: Adversarial Code & Architecture Review of DD-1 Step 1

**Document ID:** `AG22_STEP1_CODE_REVIEW`  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Directive:** Claude `[C-122]`  
**Specifications Audited:**  
- [`Docs/BossCombatReview/Execution/Claude/DD1/STEP1_SPEC_v2.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/DD1/STEP1_SPEC_v2.md)  
- [`Docs/BossCombatReview/Execution/Claude/DD1/STEP1_SPEC_v3_AMENDMENTS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/DD1/STEP1_SPEC_v3_AMENDMENTS.md)  
**Implementation Files Audited:**  
- [`Source/OneBossFight/Player/RPGCombatCatalog.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.h) & [`.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp)  
- [`Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp)  
- [`Source/OneBossFight/Player/RPGBuildRules.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildRules.h)  
- [`Source/OneBossFight/UI/RPGBuildSelectRules.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBuildSelectRules.h)  
- [`Source/OneBossFight/UI/RPGBuildSelect.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBuildSelect.h) & [`.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBuildSelect.cpp)  
- [`Source/OneBossFight/Player/RPGBuildLoadout.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.h) & [`.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.cpp)  
- [`Scripts/Editor/make_combat_catalog.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/make_combat_catalog.py)  
- [`Scripts/Editor/pie_combat_catalog.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_combat_catalog.py)  
**Status:** DELIVERED  

---

## 1. Executive Summary & Review Scope

In accordance with Claude's directive `[C-122]`, Antigravity conducted an independent, adversarial line-by-line review of the built and passing DD-1 Step 1 implementation against `STEP1_SPEC_v2.md` and `STEP1_SPEC_v3_AMENDMENTS.md`.

The implementation represents a substantial architectural leap:
- Eliminates process-global mutable epoch state in favor of game-instance subsystem ownership (`URPGCombatCatalogSubsystem`).
- Strictly enforces startup-only console latching (`rpg.CatalogSource`).
- Implements single-publication context isolation (`RPGCombatRegistry::FContext`).
- Unifies visible-row geometry across paint, hit-testing, and keys.

However, static analysis revealed **8 concrete adversarial defects and edge-case vulnerabilities**, including a direct violation of the v3 Section C.4 reverse-mapping contract, silent uninitialized property hazards in the legacy compiler, stale legacy enum state retention, and a 100% blindspot in automation testing regarding asset resolution.

---

## 2. Specification Compliance Matrix (v3 Sections A to D)

| Spec Requirement | Target Contract | Implementing File & Line | Status |
| :--- | :--- | :--- | :--- |
| **A.1 Shipping CVar Stripping** | `rpg.CatalogSource` & test fixtures compiled out of Shipping | `RPGCombatCatalog.cpp:14-18, 241-243, 261-272` | **IMPLEMENTED** |
| **A.1 Startup Latching** | Late CVar change does not alter live epoch; logs "next session only" | `RPGCombatCatalog.cpp:278-283` | **IMPLEMENTED** |
| **A.1 Auto Fallback Provenance** | `auto` logs complete legacy fallback with reason | `RPGCombatCatalog.cpp:214` | **IMPLEMENTED** |
| **A.2 Subsystem Lifetime** | Epoch owned by `UGameInstanceSubsystem`, fresh per PIE | `RPGCombatCatalog.h:125`, `RPGCombatCatalog.cpp:236-275` | **IMPLEMENTED** |
| **A.2 Context Isolation** | Pure automation uses isolated `FContext`; no global LIFO | `RPGCombatCatalog.h:108-117`, `Tests/RPGCombatCatalogTests.cpp:16-24` | **IMPLEMENTED** |
| **A.3 Soft Icon Degradation** | Broken/uncooked optional icon falls back to text; logs warning | `RPGCombatCatalog.cpp:198-202`, `RPGBuildSelect.cpp:118, 132` | **IMPLEMENTED** |
| **B Strict Modes** | `auto`, `legacy`, `data` (strict init failure on invalid data) | `RPGCombatCatalog.cpp:207-225` | **IMPLEMENTED** |
| **C.1 Attack-Table Routes** | Records `exact`, `any`, or `fallback` route per `(style, kind)` | `RPGCombatCatalog.cpp:188-196` | **IMPLEMENTED** |
| **C.2 Coverage Manifest** | Epoch carries per-weapon, per-action coverage manifest | `RPGCombatCatalog.h:92`, `RPGCombatCatalog.cpp:195` | **IMPLEMENTED** |
| **C.3 Whole-Reference Closure** | Type checks, cook policy, item/actor/ability wiring text | `RPGCombatCatalog.cpp:164-187` | **IMPLEMENTED** (See Finding 6) |
| **C.4 Non-Injective Reverse** | Unbound reverse query returns `Ambiguous`/`Unknown`, never `Starter` | `RPGCombatCatalog.cpp:43-54` | **PARTIAL / DEFECT** (See Finding 1) |
| **D.2 Visible-Row Geometry** | Single computed list for paint, hit test, number keys, and focus | `RPGCombatCatalog.cpp:232-233`, `RPGBuildSelect.cpp:130, 162, 184` | **IMPLEMENTED** (See Finding 7) |

---

## 3. Eight Concrete Adversarial Findings

### FINDING 1: `FEpoch::Describe` Falls Back to `Starter`, Violating Spec v3 Section C.4
- **Citation:** [`Source/OneBossFight/Player/RPGCombatCatalog.cpp:59`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L59) vs [`Source/OneBossFight/Player/RPGBuildRules.h:281-284`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildRules.h#L281-L284)
- **Input:** Unbound reverse query for `SwordCombatStyle` when multiple builds share the weapon (e.g. `Starter` and `CatalogFourth` are both registered; `VerifiedBuild = NAME_None`).
- **Expected Behavior:** Per `STEP1_SPEC_v3_AMENDMENTS.md` Section C.4: *"an unbound reverse query returns Ambiguous or Unknown, never the first row or Starter."*
- **Actual Behavior:** In `RPGCombatCatalog.cpp:59`:
  ```cpp
  if (!Matches(Style, IdToDescribe) && StyleToBuild(Style, IdToDescribe) != EResolve::Found)
      return RPGBuildRules::DescribeStyle(Style);
  ```
  Because `StyleToBuild` returns `EResolve::Ambiguous`, line 59 falls back to `RPGBuildRules::DescribeStyle(Style)`. In `RPGBuildRules.h:281`, `DescribeStyle` executes:
  ```cpp
  if (BuildOfStyle(Style, Build)) // Maps SwordCombatStyle -> ERPGBuild::Starter
      return FString::Printf(TEXT("%s (%s)"), Entry(Build).Name, Entry(Build).Weapon);
  ```
  It unconditionally returns **`"Starter (Sword)"`**, recovering `Starter` on an ambiguous query in direct contradiction of the v3 contract.

---

### FINDING 2: Unverified Catalog Weapon Incorrectly Classified as `"OffBuild"`
- **Citation:** [`Source/OneBossFight/Player/RPGBuildLoadout.cpp:280-282`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.cpp#L280-L282)
- **Input:** Player holds a valid catalog weapon (`SwordCombatStyle`) shared by multiple builds, but `VerifiedBuildId` is `NAME_None` (e.g. initial spawn or before equip verification callback).
- **Expected Behavior:** `GetBuildName()` should report `Unknown` or `Ambiguous`.
- **Actual Behavior:**
  ```cpp
  if (Epoch && (Epoch->Matches(ActualStyle, Build) || Epoch->StyleToBuild(ActualStyle, Build) == RPGCombatRegistry::EResolve::Found))
      if (const auto* B = Epoch->Find(Build)) return B->DisplayName;
  return ActualStyle.IsNone() ? FString(TEXT("Unknown")) : FString(TEXT("OffBuild"));
  ```
  Because `Build` is `NAME_None`, `Matches` is false. Because two builds share the style, `StyleToBuild` returns `Ambiguous` (not `Found`). Execution falls through to line 282, returning **`"OffBuild"`**. The primary catalog weapon is falsely branded as an off-build weapon.

---

### FINDING 3: Stale Legacy Enum Slot Retained on Non-Legacy Build Selection
- **Citation:** [`Source/OneBossFight/Player/RPGBuildLoadout.cpp:545`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.cpp#L545) & [`Source/OneBossFight/Player/RPGBuildRules.h:66-71`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildRules.h#L66-L71)
- **Input:** Player previously chose `Strength` (`Chosen == ERPGBuild::Strength`), then selects a fourth data build (`CatalogFourth`, where `LegacySlot == INDEX_NONE`).
- **Expected Behavior:** The legacy view `Chosen` should reflect an unmapped/unknown state or reset to `Starter`.
- **Actual Behavior:** Line 545 executes:
  ```cpp
  ChosenId = Build;
  Rules::LegacySlotOf(*Epoch, ChosenId, Chosen);
  ```
  `LegacySlotOf` returns `false` when `LegacySlot == INDEX_NONE` and leaves `Chosen` unmodified. Consequently, `Chosen` **retains its previous value (`Strength`)**. Any legacy code or test polling `Chosen` believes the player is on `Strength` while holding a fourth-build weapon.

---

### FINDING 4: `RPGCombatRegistry::Legacy()` Omits `ItemBaseClass`, Breaking Compilation with Asset Resolution
- **Citation:** [`Source/OneBossFight/Player/RPGCombatCatalog.cpp:71-90`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L71-L90) vs [`RPGCombatCatalog.cpp:176-178`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L176-L178)
- **Input:** Invoking `Compile(Legacy()->Builds, Legacy()->Weapons, Error, true)` with `bResolveAssets = true`.
- **Expected Behavior:** The built-in legacy epoch definition should be self-validating and pass full asset compilation.
- **Actual Behavior:** `RPGCombatRegistry::Legacy()` never populates `W.ItemBaseClass` (it remains an empty `FSoftObjectPath`). In `Compile()`, line 176 attempts `ItemBaseClass.TryLoad()`, which returns `nullptr`. Line 178 evaluates `if (!ItemBase)` and unconditionally **aborts compilation with failure**: `Starter.References: unresolved/wrong type/cook policy`.

---

### FINDING 5: Same-Choice Detection in `URPGBuildSelect::Pick` Broken by Raw Aliases
- **Citation:** [`Source/OneBossFight/UI/RPGBuildSelect.cpp:428`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBuildSelect.cpp#L428)
- **Input:** Player equipped with `Starter` calls `Pick(FName("sword"))` or `Pick(FName("SWORD"))`.
- **Expected Behavior:** Since `"sword"` resolves to `Starter`, `Pick` should recognize it as the current build and return `"Same"`.
- **Actual Behavior:**
  ```cpp
  if (Loadout->HasChoice() && Loadout->GetChosenBuildName().Equals(Build.ToString(), ESearchCase::IgnoreCase))
  ```
  `GetChosenBuildName()` returns `"Starter"`. `Build.ToString()` is `"sword"`. `"Starter".Equals("sword")` is **`false`**. `Pick` fails to detect the same choice and issues a redundant call to `SetBuild()`, re-triggering an equip cycle. The check must compare `ChosenId == Parsed` rather than raw alias strings against `ConsoleName`.

---

### FINDING 6: Unchecked Concatenation in Dependency Wiring Validation
- **Citation:** [`Source/OneBossFight/Player/RPGCombatCatalog.cpp:180-186`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L180-L186)
- **Input:** A malformed weapon data asset where `Item` references `ActorClass`, but `AbilityClass` is missing from `Item` and only appears in `ActorClass->GetDefaultObject()`.
- **Expected Behavior:** Validation should strictly assert that `Item` references all three dependencies (`ActorClass`, `AbilityClass`, `StyleAsset`).
- **Actual Behavior:**
  ```cpp
  FString Wiring;
  for (UObject* Owner : {Item, ActorClass->GetDefaultObject(), Style})
      for (TFieldIterator<FProperty> It(Owner->GetClass()); It; ++It)
      {
          FString Value; It->ExportText_InContainer(0, Value, Owner, nullptr, Owner, PPF_None); Wiring += Value;
      }
  if (!Wiring.Contains(...) || !Wiring.Contains(...) || !Wiring.Contains(...)) return Fail(...);
  ```
  All exported text from `Item`, `ActorClass` CDO, and `Style` is concatenated into a single shared string `Wiring`. If `ActorClass` references `AbilityClass`, `Wiring.Contains(AbilityClass)` succeeds, masking the fact that `Item` itself is missing the wiring reference.

---

### FINDING 7: Programmatic `Pick()` Bypasses Viewport Row Visibility Check for Legacy Rows
- **Citation:** [`Source/OneBossFight/UI/RPGBuildSelect.cpp:418`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBuildSelect.cpp#L418) vs [`RPGBuildSelect.cpp:162, 184`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBuildSelect.cpp#L162)
- **Input:** Severely constrained viewport (e.g. `Height = 60.f`) where `RowVisible(0, 3, 60.f)` returns `false`.
- **Expected Behavior:** Spec Section D.2 mandates: *"Paint, hit testing, number keys and focus use a single computed list of visible rows... Rows that do not fit are not drawn, not hit-testable and not selectable by key or focus"*. Direct programmatic picking should enforce identical geometry constraints.
- **Actual Behavior:** In `Pick()`:
  ```cpp
  const int32 ParsedRow = Epoch->Builds.IndexOfByPredicate([Parsed](const FRPGCatalogBuild& B) { return B.BuildId == Parsed; });
  if (ParsedRow >= 3 && !IsRowVisible(ParsedRow, LayoutHeight()))
  {
      LastPickResult = TEXT("row not visible"); return LastPickResult;
  }
  ```
  Mouse click (`NativeOnMouseButtonDown:162`) and keys (`NativeOnKeyDown:184`) strictly check `IsRowVisible(I)` and block selection of Row 0. But programmatic `Pick("Starter")` bypasses the check because `ParsedRow < 3`, creating an asymmetry where invisible legacy rows remain selectable via `Pick()`.

---

### FINDING 8: Zero Coverage of Asset Resolution and Cook Checks in Automation Tests
- **Citation:** [`Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp:13, 53`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp#L13)
- **Input:** Running automation tests `OneBossFight.Catalog.Context` and `OneBossFight.Catalog.Validation`.
- **Expected Behavior:** Automation suite should validate production asset loading, `CookedDependency` rules, class ancestry, and attack table coverage.
- **Actual Behavior:** Both tests explicitly invoke `Compile(..., false)` with `bResolveAssets = false`:
  - `FRPGCatalogContextTest:13`: `Compile(Base->Builds, Base->Weapons, Error, false)`
  - `FRPGCatalogValidationTest:53`: `Compile(Builds, Weapons, Error, false)`
  Lines 164-203 of `RPGCombatCatalog.cpp` (the entire asset loading, packaging directory validation, wiring export, and attack table route matching engine) have **zero automation test coverage**.

---

## 4. Summary Table of Checks

| Area Checked | Clean Aspects | Flagged Adversarial Concerns |
| :--- | :--- | :--- |
| **Legacy String & Order Parity** | `BuildName`, `StyleOfBuild`, `DescribeStyle`, and HUD suffixes match legacy verbatim. | Ambiguous reverse mapping defaults to `Starter` (Finding 1). |
| **Strict Data Mode** | Strict `data` mode properly returns `nullptr` on error and disables consumers without falling back. | `Legacy()` cannot compile with asset resolution enabled (Finding 4). |
| **Epoch Lifetime & Ownership** | `FEpoch` owns its data via value copies; leases held via `TStrongObjectPtr`. | Legacy `Entry()` returns static table, not active epoch data. |
| **Reverse Mapping** | `StyleToBuild` correctly returns `Ambiguous` for multi-build styles. | `GetBuildName()` misclassifies catalog styles as `OffBuild` (Finding 2). |
| **Visible-Row Geometry** | Mathematical formula `Height * .25f + 52.f + Row * 42.f + 42.f <= Height` is unified. | Asymmetry in `Pick()` for rows $< 3$ on ultra-small viewports (Finding 7). |
| **Automation Suite** | Pure context isolation and structural malformation rejection thoroughly tested. | Asset resolution, cook checks, and UI interaction completely untested in automation (Finding 8). |
