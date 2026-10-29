# Staged Custom Build Authoring Helper (`AG-CONTENT03`)

**Author:** Antigravity (Party Code `A`) - Senior C++ Implementer & Unreal Engine Specialist  
**Work Order:** `[X-278]` / `Docs/BossCombatReview/Execution/Codex/AG_CONTENT03_STAGED_BUILD_AUTHORING_HELPER.md`  
**Review Status:** Source delivery submitted for Technical Lead Codex (`X`) independent review.  
**Execution Boundary:** **STRICTLY OFFLINE IMPLEMENTATION**. No Unreal Engine process launched; no live assets created, mutated, or deleted; no pack edits; no git commit or push.

---

## 1. Overview & Purpose

`author_custom_build.py` is an Unreal Editor Python authoring helper designed to automate the staged creation of a new additive custom build Data Asset and a cloned Combat Catalog with the custom build registered.

Key operational characteristics:
1. **Staged Execution Architecture:** The default action is a strictly read-only dry-run (`--dry-run` or no flag). It inspects source catalog, builds, and weapon inputs, checks namespace collisions, verifies destination paths, and outputs a formatted **Proposed Output Plan**.
2. **Explicit Apply Gate:** Creation and saving logic is contained within the `--apply` branch, but is **strictly unexecuted** during this offline phase. It requires a separate sole-operator release from Technical Lead Codex or the Owner before running inside the Unreal Editor.
3. **Additive Strength Weapon Reuse:** Reuses the existing `Strength` weapon (`WeaponId = Strength`). It adds **zero new weapons** and introduces **zero duplicate combat styles**, adhering to the duplicate style constraint (`RPGCombatCatalog.cpp:130-141`).
4. **Preserves Pinned Legacy Contract:** Preserves the pinned 3-build compatibility contract (`Starter` [0], `Strength` [1], `Dex` [2]). The custom build is assigned `LegacySlot = -1` (`INDEX_NONE`).
5. **Isolated Output Directory:** Outputs are targeted strictly under `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/`, ensuring the shipped default catalog (`/Game/OneBossFight/Data/Catalog/DA_CombatCatalog`) is never modified.

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

The script implements comprehensive defensive programming guards modeled directly on the C++ catalog compiler (`Source/OneBossFight/Player/RPGCombatCatalog.cpp`):

1. **Output Root Boundary Guard:**
   * Output paths must strictly begin with `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/`. Any attempt to author into `/Game/OneBossFight/Data/Catalog/` or any other directory is immediately rejected.
2. **Refuse Existing Outputs (Anti-Overwrite / Anti-Delete):**
   * Uses `unreal.EditorAssetLibrary.does_asset_exist()`. If either output package already exists on disk, execution halts with a fatal error. The helper **never overwrites, deletes, or repairs** existing assets.
3. **Case-Insensitive Namespace Collision Validation:**
   * Mirrors `RPGCombatRegistry::Normalize` (`Text.TrimStartAndEnd().TrimQuotes().TrimStartAndEnd().ToLower()`).
   * Evaluates `Aliases + [ConsoleName, BuildId]` for every build.
   * Rejects empty tokens, reserved words (`"none"`, `"off"`), and duplicate keys across distinct builds.
4. **Source Package Dirty Guard:**
   * Inspects `unreal.load_package(None, source_catalog_path).is_dirty()`. If the source catalog is modified in memory, apply is blocked to prevent accidental cross-saving.
5. **Partial-Failure Reporting & Halting Policy:**
   * If an exception or failure occurs during asset creation or save, the script catches the error, dumps the exact list of newly created objects to stdout, and **stops immediately**.
   * It **does not attempt auto-deletion**, does not attempt auto-cleanup, and makes no claim of transactional rollback. Partial assets remain on disk for inspection.
6. **Save Boundary:**
   * Only the two newly created output assets are saved (`EditorAssetLibrary.save_loaded_asset(only_if_dirty=True)`). No other assets or configuration files are touched.

---

## 4. Native Compilation Gap & Testing Seam

> [!IMPORTANT]
> **Python Structural Check vs. Native C++ ABI Validation:**  
> Python reflection checks validate asset presence, property definitions, and namespace strings inside the Unreal Editor environment. They **do NOT** execute native C++ `RPGCombatRegistry::Compile` or validate `FEpoch` binary ABI layout.  
> 
> True validation is performed by the designated sole engine operator via the native C++ testing seam:
> * **Test Class:** `OneBossFight.Binding.CatalogTests` (`Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp`)
> * **Verification Seam:** Invoking `RPGCombatCatalog::Compile` with `CVarCatalogPath` pointing to `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_CombatCatalog_VanguardCloned`.

---

## 5. Invocations (For Future Sole-Operator Execution)

These commands are documented for the future engine operator. **They have not been run during this offline stage.**

### A. Dry-Run Inspection (Default)
Inside Unreal Editor Python console or command line:
```bash
py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py"
```
Or with JSON output format:
```bash
py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py" --json
```

### B. Apply Execution (Creation & Save)
Inside Unreal Editor Python console or command line:
```bash
py "Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py" --apply
```

---

## 6. Offline Verification Evidence & Artifact Hashes

### Offline Python Syntax Check
```bash
python -m py_compile Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py
```
* **Result:** Exit code `0`, clean compilation, zero syntax errors.
* **Offline Execution Test:** Run in pure Python mode (`HAS_UNREAL = False`); successfully verified static specification, namespace checks, and output plan generation.

### Exact Source Dependency Hashes
| Path | SHA-256 | Description |
| :--- | :--- | :--- |
| `Source/OneBossFight/Player/RPGCombatCatalog.h` | `e7d5296833cfa5bec4101e608a98ab336a5b8c7a5c476e0d3b17eae57279dbb5` | C++ Catalog & Build Struct Definitions |
| `Source/OneBossFight/Player/RPGCombatCatalog.cpp` | `f6f71036804f60f0e4c8b3cf455f2a04a7bc4cf379760334903a2d9d613de59d` | C++ Compile Invariants & Normalize |
| `Content/OneBossFight/Data/Catalog/DA_CombatCatalog.uasset` | `be49c7f4f3551fa8a45eb33d067711bb5bed526f90fd2cf7f4aa39cfd232b315` | Shipped Default Combat Catalog |
| `Content/OneBossFight/Data/Catalog/DA_Build_Starter.uasset` | `e3c0d6c86aca343fac8307d1b95209a0ce3a693920493ee5211e6fa6bce80682` | Pinned Legacy Build: Starter (Slot 0) |
| `Content/OneBossFight/Data/Catalog/DA_Build_Strength.uasset` | `24b6ad77dbaf8db5f64db5edad035471d2e8ea05487d02864c51e8e27da02033` | Pinned Legacy Build: Strength (Slot 1) |
| `Content/OneBossFight/Data/Catalog/DA_Build_Dex.uasset` | `8ec63be096a1f43de82baceb30cb36a373bf018f59812db06184220c0c4d520b` | Pinned Legacy Build: Dex (Slot 2) |
| `Content/OneBossFight/Data/Catalog/DA_Weapon_Sword.uasset` | `b7702e2af28db57442dbe9ca20195ac23c02bc57941e760d57280e2bcb68d3c2` | Pinned Legacy Weapon: Sword |
| `Content/OneBossFight/Data/Catalog/DA_Weapon_Claymore.uasset` | `d203bb0555b1e6239218fd180611a6fc14017544c7ac55ace0086b308f35da8c` | Pinned Legacy Weapon: Claymore (Strength) |
| `Content/OneBossFight/Data/Catalog/DA_Weapon_DualSwords.uasset` | `31680000e80764945d9483a3286f0075fd839244797ce7f2277b9f34b3770128` | Pinned Legacy Weapon: DualSwords |

### Delivered Artifacts
| Path | Description |
| :--- | :--- |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py` | Staged Unreal Editor Python authoring helper |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/README.md` | Architecture, specifications, safeguards, and verification |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/evidence_sha256.txt` | Cryptographic SHA-256 evidence receipt |
