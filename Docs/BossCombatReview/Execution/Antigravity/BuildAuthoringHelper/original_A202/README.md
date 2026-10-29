# Staged Custom Build Authoring Helper (`AG-CONTENT09 REV14`)

**Author:** Antigravity (Party Code `A`) - Senior C++ Implementer & Unreal Engine Specialist  
**Work Order:** `[C-265]` / `AG-CONTENT07 Continuation`  
**Review Status:** REV11 delivery `A-189` submitted for Lead Reviewer Claude (`C`) and Implementer Codex (`X`). Work Orders `[C-267]`, `[C-269]`, `[C-270]`.  
**Preserved Archives:** `original_A176/`, `original_A177/`, `original_A178/`, `original_A179/`, `original_A180/`, `original_A181/`, `original_A182/`, `original_A183/`, `original_A184/`, `original_A186/`, and `original_A188/, original_A189/, and original_A190/` preserved byte-for-byte.  
**Execution Boundary:** **STRICTLY OFFLINE IMPLEMENTATION**. Zero Unreal Engine processes launched; zero assets created, mutated, or deleted; zero pack edits; zero git commits or pushes.

---

## Offline Float64 Qualification & IEEE 754 float32 Storage Parity

> [!IMPORTANT]
> **Offline float64 checks do NOT certify native float32 conversion or input-mode parity.**  
> Standard library CPython float arithmetic executes in 64-bit double precision. Unreal Engine native C++ properties store 32-bit single-precision floats (`float32`). The helper relies on `authoring_core.to_float32` and `normalize_native_expected_for_readback` to ensure float32 storage parity offline.

---

## 1. Overview & Purpose

`author_custom_build.py` is a staged Unreal Editor Python authoring helper designed to automate the authoring of an additive custom build Data Asset and generate a cloned Combat Catalog with the new build registered.

Key operational characteristics:
1. **Three-Tier Staged Execution Architecture:**
   * **Dry-Run Mode (DEFAULT):** Read-only inspection of source catalog, builds, and weapon inputs. Checks whole-input source dirty flags, validates namespace keys, verifies output paths, and outputs a formatted **Proposed Output Plan**. Zero writes, zero saves.
   * **Apply Mode (`--apply`):** Executes staged in-memory creation and duplication of assets using explicit UE5.5 property setters (`set_editor_property`). Read-back verification is performed before proceeding. **Does not save by default.**
   * **Save Opt-in (`--apply --save`):** Explicit separate opt-in to save output packages to disk. Must be explicitly requested alongside `--apply`.
2. **Additive Strength Weapon Reuse:** Reuses the existing `Strength` weapon (`WeaponId = Strength`). It adds **zero new weapons** and introduces **zero duplicate combat styles**, strictly adhering to the style conflict constraint (`RPGCombatCatalog.cpp:130-141`).
3. **Preserves Pinned Legacy Contract:** Enforces the pinned 3-build compatibility contract:
   * Slot 0: `Starter` (`WeaponId = Starter`, `ExpectedStyle = SwordCombatStyle`)
   * Slot 1: `Strength` (`WeaponId = Strength`, `ExpectedStyle = ClaymoreCombatStyle`)
   * Slot 2: `Dex` (`WeaponId = Dex`, `ExpectedStyle = DualSwordCombatStyle` - singular "Sword")
   * The custom build is assigned `LegacySlot = -1` (`INDEX_NONE`).
4. **Exact Native Normalization (`TrimQuotesInline`):**
   * UE5.5 `String.cpp.inl` removes at most ONE leading and ONE trailing double quote. For `""off""`, native leaves `"off"`.
   * Preserves single quotes (`'`) as literal characters.
5. **Isolated Output Directory:** Outputs are targeted strictly under `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/`. The shipped default catalog (`/Game/OneBossFight/Data/Catalog/DA_CombatCatalog`) is never modified.

---

## 2. Proposed Output Paths & Specifications

### A. Custom Build Definition Data Asset
* **Asset Path:** `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_Build_Custom_Vanguard`
* **C++ Class:** `URPGBuildDefinition` (`/Script/OneBossFight.RPGBuildDefinition`)
* **Struct Property Values (`FRPGCatalogBuild`, `Source/OneBossFight/Player/RPGCombatCatalog.h:34-45`):**
  * `BuildId`: `Build_Custom_Vanguard` (`FName`)
  * `ConsoleName`: `vanguard` (`FString`)
  * `Aliases`: `["vanguard_alt"]` (`TArray<FString>`)
  * `DisplayName`: `"Vanguard Claymore"` (`FString`)
  * `UiOrder`: `3` (`int32`, placed after legacy builds 0, 1, 2)
  * `LegacySlot`: `-1` (`INDEX_NONE`, `int32`)
  * `WeaponId`: `Strength` (`FName`, reuses existing Strength weapon)
  * `Icon`: `""` (`FSoftObjectPath`, null/empty)

### B. Cloned Combat Catalog Data Asset
* **Asset Path:** `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_CombatCatalog_VanguardCloned`
* **C++ Class:** `URPGCombatCatalog` (`/Script/OneBossFight.RPGCombatCatalog`)
* **Source Asset to Clone:** `/Game/OneBossFight/Data/Catalog/DA_CombatCatalog`
* **Catalog Property Invariants:**
  * `SchemaVersion`: `1` (`int32`)
  * `Weapons`: Retains all 3 original weapons unchanged:
    1. `/Game/OneBossFight/Data/Catalog/DA_Weapon_Sword` (`Starter`)
    2. `/Game/OneBossFight/Data/Catalog/DA_Weapon_Claymore` (`Strength`)
    3. `/Game/OneBossFight/Data/Catalog/DA_Weapon_DualSwords` (`Dex`)
  * `Builds`: Retains all 3 original builds and appends the new custom build:
    1. `/Game/OneBossFight/Data/Catalog/DA_Build_Starter` (Slot 0, Name `Starter`)
    2. `/Game/OneBossFight/Data/Catalog/DA_Build_Strength` (Slot 1, Name `Strength`)
    3. `/Game/OneBossFight/Data/Catalog/DA_Build_Dex` (Slot 2, Name `Dex`)
    4. `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_Build_Custom_Vanguard` (Slot -1, Name `Build_Custom_Vanguard`)

---

## 3. Strict Safeguards & Failure Modes

1. **Strict Fail-Closed Editor Guard (`verify_editor_environment`):**
   * Requires `unreal.SystemLibrary.is_editor()` is True, `get_editor_subsystem(UnrealEditorSubsystem)` is non-null, and `get_game_world() is None` (fails closed on any missing API, false return, None subsystem, or PIE mode).
2. **Fail-Closed Native Class Verification:**
   * Explicitly loads and verifies native classes from `/Script/OneBossFight`:
     * `CLASS_CATALOG_PATH = "/Script/OneBossFight.RPGCombatCatalog"`
     * `CLASS_BUILD_DEF_PATH = "/Script/OneBossFight.RPGBuildDefinition"`
     * `CLASS_WEAPON_DEF_PATH = "/Script/OneBossFight.RPGWeaponDefinition"`
3. **Whole-Input Package Dirty Inspection:**
   * Gathers all packages involved: the catalog package, all referenced build packages, and all referenced weapon packages.
   * Loads each package. If any package cannot be loaded or is dirty in memory, fails closed immediately in both dry-run and apply modes.
4. **Canonical Path & Anti-Traversal Enforcement:**
   * Output paths must strictly match regex `^/Game/OneBossFight/Data/[A-Za-z0-9_/]+$`.
   * Rejects path traversal (`..`), double slashes (`//`), backslashes (`\`), and sub-object colons (`:`).
5. **Anti-Overwrite / Anti-Delete Protection:**
   * Uses `unreal.EditorAssetLibrary.does_asset_exist()`.
   * If either target output asset already exists on disk, execution halts with a fatal refusal. The helper never overwrites, deletes, or repairs existing assets.
6. **Immutable Deep Source Snapshotting:**
   * Uses `copy.deepcopy` upon initialization. Any post-snapshot mutation of source objects cannot alter the baseline.
   * Compares all fields, array lengths, ordering, and package dirty flags.
7. **Explicit Property Access & Read-Back Verification:**
   * Uses explicit `get_editor_property` and `set_editor_property`.
   * Performs explicit read-back assertions before proceeding.
8. **Fail-Closed Partial Failure Reporting:**
   * If an exception occurs, records exact created packages without auto-deletion or false rollback claims.

---

## 4. Delivered Artifacts
| Path | Description |
| :--- | :--- |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py` | Staged custom build authoring helper integrating `authoring_core.py` |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/README.md` | Build helper architecture, safeguards, and verification guide |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/evidence_sha256.txt` | Cryptographic SHA-256 evidence receipt |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A176/` | Preserved byte-exact A-176 deliverables |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A177/` | Preserved byte-exact A-177 deliverables |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A178/` | Preserved byte-exact A-178 deliverables |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A179/` | Preserved byte-exact A-179 deliverables |
