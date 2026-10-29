# Staged Custom Build Authoring Helper (`AG-CONTENT03 REV2`)

**Author:** Antigravity (Party Code `A`) - Senior C++ Implementer & Unreal Engine Specialist  
**Work Order:** `[X-278]` / `[X-280]` / `Docs/BossCombatReview/Execution/Codex/A176_STAGED_HELPER_SOURCE_REVIEW.md`  
**Review Status:** REV2 source delivery submitted for Technical Lead Codex (`X`) independent review. Original `A-176` files preserved byte-for-byte under `original_A176/`.  
**Execution Boundary:** **STRICTLY OFFLINE IMPLEMENTATION**. Zero Unreal Engine processes launched; zero assets created, mutated, or deleted; zero pack edits; zero git commits or pushes.

---

## 1. Overview & Purpose

`author_custom_build.py` is a staged Unreal Editor Python authoring helper designed to automate the authoring of an additive custom build Data Asset and generate a cloned Combat Catalog with the new build registered.

Key operational characteristics:
1. **Three-Tier Staged Execution Architecture:**
   * **Dry-Run Mode (DEFAULT):** Read-only inspection of source catalog, builds, and weapon inputs. Checks whole-input source dirty flags, validates namespace keys, verifies output paths, and outputs a formatted **Proposed Output Plan**. Zero writes, zero saves.
   * **Apply Mode (`--apply`):** Executes staged in-memory creation and duplication of assets using explicit UE5.5 property setters (`set_editor_property`). Read-back verification is performed before proceeding. **Does not save by default.**
   * **Save Opt-in (`--apply --save`):** Explicit separate opt-in to save output packages to disk. Must be explicitly requested alongside `--apply`.
2. **Additive Strength Weapon Reuse:** Reuses the existing `Strength` weapon (`WeaponId = Strength`). It adds **zero new weapons** and introduces **zero duplicate combat styles**, strictly adhering to the style conflict constraint (`RPGCombatCatalog.cpp:130-141`).
3. **Preserves Pinned Legacy Contract:** Enforces the pinned 3-build compatibility contract (`Starter` [0], `Strength` [1], `Dex` [2]). The custom build is assigned `LegacySlot = -1` (`INDEX_NONE`).
4. **Isolated Output Directory:** Outputs are targeted strictly under `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/`. The shipped default catalog (`/Game/OneBossFight/Data/Catalog/DA_CombatCatalog`) is never modified.

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

## 3. Strict Safeguards & Failure Modes (REV2 Enhancements)

1. **Editor State & Non-PIE Guard:**
   * Verifies `unreal.SystemLibrary.is_editor() == True` and confirms the editor is not in Play-in-Editor (PIE) or simulation mode.
2. **Fail-Closed Native Class Verification:**
   * Explicitly loads and verifies native classes from `/Script/OneBossFight`:
     * `CLASS_CATALOG_PATH = "/Script/OneBossFight.RPGCombatCatalog"`
     * `CLASS_BUILD_DEF_PATH = "/Script/OneBossFight.RPGBuildDefinition"`
     * `CLASS_WEAPON_DEF_PATH = "/Script/OneBossFight.RPGWeaponDefinition"`
   * Verifies loaded source catalog class matches `CLASS_CATALOG_PATH`.
   * Verifies all referenced builds match `CLASS_BUILD_DEF_PATH`.
   * Verifies all referenced weapons match `CLASS_WEAPON_DEF_PATH`.
3. **Whole-Input Package Dirty Inspection:**
   * Gathers all packages involved: the catalog package, all referenced build packages, and all referenced weapon packages.
   * Loads each package (`unreal.load_package(None, path)`). If any package cannot be loaded or is dirty in memory, **fails closed immediately** in both dry-run and apply modes.
4. **Canonical Path & Anti-Traversal Enforcement:**
   * Output paths must strictly match regex `^/Game/OneBossFight/Data/[A-Za-z0-9_/]+$`.
   * Rejects path traversal (`..`), double slashes (`//`), backslashes (`\`), and sub-object colons (`:`).
5. **Anti-Overwrite / Anti-Delete Protection:**
   * Uses `unreal.EditorAssetLibrary.does_asset_exist()`.
   * If either target output asset already exists on disk, execution halts with a fatal refusal. The helper **never overwrites, deletes, or repairs** existing assets.
6. **Exact Native Normalization Parity:**
   * Matches Unreal Engine 5.5 `String.cpp.inl:971-974 TrimQuotesInline` and `RPGCombatRegistry::Normalize`:
     * Trims whitespace, trims double quotes (`"`) ONLY (single quotes are preserved), trims whitespace, and converts to lowercase.
   * Case-insensitive `FName` equality is enforced for `BuildId` and `WeaponId`.
7. **Explicit Property Access & Read-Back Verification:**
   * Uses explicit `get_editor_property` and `set_editor_property` on copies of `FRPGCatalogBuild` struct and `TArray<TSoftObjectPtr>` arrays.
   * Performs explicit read-back assertions before proceeding.
8. **Source Preservation & Drift Abort:**
   * Re-verifies all source packages remain clean after in-memory asset generation. If any source package is dirtied, execution aborts and saves are blocked.
9. **Fail-Closed Partial Failure Reporting:**
   * If an exception occurs at any point, the script catches the error, outputs the exact list of newly created packages, and **halts immediately**.
   * It **does not attempt auto-deletion**, does not auto-clean, and makes no claim of transactional rollback.

---

## 4. Native Compilation Gap & Testing Seams

> [!IMPORTANT]
> **Python Structural Check vs. Native C++ Compilation:**  
> Python reflection checks validate asset presence, property definitions, and namespace strings inside the Unreal Editor environment. They **do NOT** execute native C++ `RPGCombatRegistry::Compile` or validate `FEpoch` binary ABI layout.  
> 
> Furthermore, existing automated test suites (such as `OneBossFight.Catalog.Validation` and `OneBossFight.Catalog.TestPathSeam` in `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp`) validate the shipped catalog and the test fixture root (`/Game/OneBossFight/Data/TypedABIFixtures/DA_ABITest_Catalog`), but **do not automatically discover or compile newly authored preview outputs**.  
> 
> True native compilation and ABI validation requires the sole engine operator to test the cloned catalog through the native C++ testing seam (`RPGCombatCatalog::Compile`), with `CVarCatalogPath` pointing to `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_CombatCatalog_VanguardCloned`.

---

## 5. Invocations & CLI Matrix (For Future Sole-Operator Execution)

These commands are documented for the future engine operator. **They have not been run inside Unreal during this offline stage.**

### A. Dry-Run Inspection (Default)
Inside Unreal Editor Python console or command line:
```bash
py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py"
```
Or with JSON output format:
```bash
py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py" --json
```

### B. In-Memory Staged Apply (No Saves)
```bash
py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py" --apply
```

### C. Staged Apply with Explicit Save Opt-in
```bash
py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py" --apply --save
```

---

## 6. Offline Verification Evidence & Artifact Hashes

### Offline Python Syntax & CLI Validation
```bash
# 1. Syntax Compilation Check
python -m py_compile Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py

# 2. CLI Matrix Tests (Offline)
python Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py          # Dry-run: Exit 0
python Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py --save   # Guard: Exit 1 (Requires --apply)
python Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py --apply  # Guard: Exit 2 (Requires Unreal Editor)
```
* **Result:** All offline CLI matrix tests pass with expected exit codes and guard messages. Clean syntax compilation with zero warnings or errors.

### Delivered Artifacts
| Path | Description |
| :--- | :--- |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py` | Staged Unreal Editor Python authoring helper (REV2) |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/README.md` | Architecture, specifications, safeguards, and verification |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/evidence_sha256.txt` | Cryptographic SHA-256 evidence receipt |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A176/` | Preserved byte-exact historical A-176 deliverables |
