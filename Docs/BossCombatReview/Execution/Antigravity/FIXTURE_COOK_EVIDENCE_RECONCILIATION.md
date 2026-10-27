# AG11 Delivery Report: Fixture & Cook Evidence Reconciliation (Revision 02)

**Document ID:** `Docs/BossCombatReview/Execution/Antigravity/FIXTURE_COOK_EVIDENCE_RECONCILIATION.md`  
**Revision:** Rev 02 (incorporating evidence narrowing, binary distinction, and unknown classifications from `[X-205]` and `Docs/BossCombatReview/Execution/Codex/AG11_A133_REVIEW.md`)  
**Author:** Antigravity (Assistant)  
**Assigned By:** Codex Technical Lead (`[X-203]`, `[X-205]`, `Docs/BossCombatReview/Execution/Codex/AG10_A132_ACCEPTANCE.md`)  
**Work Order:** AG11 (Fixture / Cook Evidence Reconciliation)  
**Date:** 2026-10-27  
**Execution Environment:** Windows / Pure Offline Source & Evidence Audit (No Engine, No PIE, No Packaging, No Asset Loads/Edits)

---

## 1. Pinned Source & Evidence Registry

All findings, receipt comparisons, and evidence evaluations in this audit are strictly pinned to the following raw files, verified via `Docs/BossCombatReview/Execution/Codex/Step2Preparation/review_receipt.py`:

### Packaging & Cook Coverage Tools:
| Tool / Configuration File | Repository Path | Size (Bytes) | Exact Raw SHA256 Hash |
| :--- | :--- | :--- | :--- |
| **CheckStagedContent.py** | `Scripts/CheckStagedContent.py` | 4,008 | `81625927d3b722499a1f5de70a02f079484c2114279d081ba48ecbd8a67c5683` |
| **DefaultGame.ini** | `Config/DefaultGame.ini` | 3,366 | `9827ff8e632354cb7d3013955f1c1891ca16eac037abf8cd64369e5aa8886be3` |

### C++ Source Files & Automation Tests:
| Source / Header / Test File | Repository Path | Size (Bytes) | Exact Raw SHA256 Hash |
| :--- | :--- | :--- | :--- |
| **RPGCombatCatalog.cpp** | `Source/OneBossFight/Player/RPGCombatCatalog.cpp` | 23,675 | `f6f71036804f60f0e4c8b3cf455f2a04a7bc4cf379760334903a2d9d613de59d` |
| **RPGCombatCatalog.h** | `Source/OneBossFight/Player/RPGCombatCatalog.h` | 7,427 | `e7d5296833cfa5bec4101e608a98ab336a5b8c7a5c476e0d3b17eae57279dbb5` |
| **RPGCombatCatalogTests.cpp** | `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp` | 41,486 | `fba473041e76c9f8d4bee7f1bba5111c00764e3186809376284d792ab2743639` |
| **RPGAutomationTests.cpp** | `Source/OneBossFight/Tests/RPGAutomationTests.cpp` | 79,242 | `22299a447cb207b618825981c001cced3b24d661399cf40ecc8bdc85141101f8` |

### Historical Package Evidence & Fixture Records:
| Evidence Document / Export | Repository Path | Size (Bytes) | Exact Raw SHA256 Hash |
| :--- | :--- | :--- | :--- |
| **E-012 Fixture Specification** | `Docs/BossCombatReview/Execution/Claude/Evidence/E-012_typed_abi_fixtures.md` | 5,409 | `ca1abe4bc89fef927ef8762e05182fe8e24851e475a2d25a6a3366ecaafe39ff` |
| **Historical 6-Asset Hashes** | `Docs/BossCombatReview/Execution/Claude/Evidence/exports/typed_abi_fixture_hashes.txt` | 430 | `1c8e79b5e7852ca43b01f1b8b4598ab2ec25dad88ce8a14fd06cde82648e5f9a` |
| **Seam 3-Asset Hashes** | `Docs/BossCombatReview/Execution/Claude/Evidence/exports/abitest_catalog_assets_sha256.txt` | 416 | `4c5a1ec2bb1749cf2d0354d0453e66f5f6209def86d46fe872c7ff54fe49a9de` |
| **IoStore Container List** | `Docs/BossCombatReview/Execution/Claude/Evidence/exports/utoc_list_fixtures_package.txt` | 1,300,556 | `c8279ff45b066e0b2a8c637616dc1dd3e92998cfe95cfc84b3ce4d546937afe2` |
| **Package Build UAT Log** | `Docs/BossCombatReview/Execution/Claude/Evidence/exports/package_dev_fixtures_uat.txt` | 156,903 | `5f52c67734a06bf7abdab5b2d1ed14b6dbcf826e05f43e0f9b1994527688a29c` |
| **Cold Packaged Run Log** | `Docs/BossCombatReview/Execution/Claude/Evidence/exports/packaged_dev_fixtures_run.log` | 93,564 | `2bbe28c825fc6cd765ff9764254f9904bbb6b1a5f96aa587d2ccc910460c6c26` |
| **Fourth Equip Run 3 Log** | `Docs/BossCombatReview/Execution/Claude/Evidence/exports/abi_fourth_equip_run3.log` | 203,794 | `49b9d9ed3cd9bc416a79afcc91f283effed360c30111677b636b4b850f108406` |

### Inspected Staged Manifests (Disk Reads):
| Staged Manifest File | Repository Path | Size (Bytes) | Exact Raw SHA256 Hash | Notes / Date |
| :--- | :--- | :--- | :--- | :--- |
| **Development UFS Manifest** | `Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt` | 1,117,468 | `38c5aea0d70a003c76ba25e6df9cc0e7ff94125a702150f4d4fef44e5d24c51d` | 9,191 lines, captured 2026-10-26 14:07 UTC / 19:37 IST |
| **Shipping UFS Manifest** | `Saved/StagedBuilds_Shipping/Windows/Manifest_UFSFiles_Win64.txt` | 1,109,692 | `9c74f8f942ea3aac7027e1cc7971c972c1f8419f19b11124f92fff3e8567e943` | Observational: dated 2026-10-24 22:17 (predates fixture work) |

### Actual On-Disk Fixture Asset Files (9 Total):
| Asset Name | Content Relative Path | Last Modified | Size (Bytes) | Exact Raw SHA256 Hash |
| :--- | :--- | :--- | :--- | :--- |
| **BP_ABI_FourthWeaponActor** | `Content/OneBossFight/Data/TypedABIFixtures/BP_ABI_FourthWeaponActor.uasset` | 2026-10-26 19:27 | 32,163 | `5af9499d96f8902b2e0e49fc8d8521370b01dc5b89b0fc7aaa71e0a83dd9a86b` |
| **DA_ABI_FourthCombatStyle** | `Content/OneBossFight/Data/TypedABIFixtures/DA_ABI_FourthCombatStyle.uasset` | 2026-10-26 19:27 | 5,411 | `e1446b9f6f999d8995861f4473d29c4f3ba669a8cbf565f31dd7a628bc90ea27` |
| **DA_ABI_FourthWeaponItem** | `Content/OneBossFight/Data/TypedABIFixtures/DA_ABI_FourthWeaponItem.uasset` | 2026-10-26 19:27 | 5,271 | `4c6e6b7643f01d14166b4ca03f39c6423f5988285f88368e52ea6b0f41249150` |
| **GA_ABI_FourthMelee** | `Content/OneBossFight/Data/TypedABIFixtures/GA_ABI_FourthMelee.uasset` | 2026-10-26 19:27 | 8,134 | `d673584d29345264c810ae1adc1f070f340e82190d6f4fe02eba3f3398b53fa7` |
| **BP_ToughSword (Decoy)** | `Content/OneBossFight/Data/TypedABIFixtures/DecoyPackage/BP_ToughSword.uasset` | 2026-10-26 19:27 | 34,711 | `ac3805c158cb71c2e3fe545fa1d58d145baacc3d696b2aae9b6f97832d6b5806` |
| **DA_ABITest_Build_Fourth** | `Content/OneBossFight/Data/TypedABIFixtures/DA_ABITest_Build_Fourth.uasset` | 2026-10-26 22:10 | 2,095 | `3a9d5562e0a91cf8ff4d8e4183b4b17dbcbc7318469f5ac79ed2f7ff676a8aa9` |
| **DA_ABITest_Catalog** | `Content/OneBossFight/Data/TypedABIFixtures/DA_ABITest_Catalog.uasset` | 2026-10-26 22:10 | 2,696 | `52f4222ec26767f5248a6e1922af28ef75a9fbba0c6d04e1597e7d57d8465c5b` |
| **DA_ABITest_Weapon_Fourth** | `Content/OneBossFight/Data/TypedABIFixtures/DA_ABITest_Weapon_Fourth.uasset` | 2026-10-26 22:10 | 3,463 | `cb2c53648cace1d66997d5bde45806dedde297f83fa2086e9adb1e0faa4648b0` |
| **DA_ABI_UncookedWeaponItem** | `Content/OneBossFight/ReviewFixtures/TypedABI/DA_ABI_UncookedWeaponItem.uasset` | 2026-10-26 19:33 | 5,293 | `9a5034d9552214c7fe72ae8c1b4832f07b93c55ec0a8a9fc1a3084a82d925df0` |

---

## 2. Fixture Identity, Provenance & The "Five-Entry" Limitation

### 2.1 The Two Generations of Fixtures
A detailed temporal and filesystem audit reveals that the fixture assets in tree belong to two distinct authoring epochs:

1. **Epoch 1: Original Fixture Bundle (Authored 2026-10-26 19:27 - 19:33)**
   - *Cooked Root (`/Game/OneBossFight/Data/TypedABIFixtures/`)*:
     * `BP_ABI_FourthWeaponActor` (distinct actor class)
     * `DA_ABI_FourthCombatStyle` (distinct combat style granting melee ability)
     * `DA_ABI_FourthWeaponItem` (weapon item binding actor + style)
     * `GA_ABI_FourthMelee` (distinct gameplay ability)
     * `DecoyPackage/BP_ToughSword` (actor sharing class leaf `BP_ToughSword_C` but in an isolated decoy package)
   - *Uncooked Root (`/Game/OneBossFight/ReviewFixtures/TypedABI/`)*:
     * `DA_ABI_UncookedWeaponItem` (copy of fourth weapon item with valid edges, placed outside always-cook roots)
   - *Provenance Record*: Pinned in `Claude/Evidence/exports/typed_abi_fixture_hashes.txt` (short hashes match bytes 1-16 of full raw SHA256 above).

2. **Epoch 2: Three Later Fourth-Catalog Seam Assets (Authored 2026-10-26 22:10)**
   - *Cooked Root (`/Game/OneBossFight/Data/TypedABIFixtures/`)*:
     * `DA_ABITest_Build_Fourth` (test build definition referencing fourth weapon)
     * `DA_ABITest_Catalog` (test combat catalog containing fourth build)
     * `DA_ABITest_Weapon_Fourth` (test weapon definition entry)
   - *Provenance Record*: Pinned in `Claude/Evidence/exports/abitest_catalog_assets_sha256.txt`.

### 2.2 Reconciling the Historical "Five-Entry" Package Assertion
In `Docs/BossCombatReview/Execution/Claude/Evidence/E-012_typed_abi_fixtures.md` (Revision 03), Claude asserted:
> *"UnrealPak.exe OneBossFight-Windows.utoc -List lists the PACKED IoStore container (`exports/utoc_list_fixtures_package.txt`): exactly FIVE entries under `.../Data/TypedABIFixtures/`... ZERO entries containing `ReviewFixtures` and ZERO containing `Uncooked`..."*

**Audit Finding & Qualification:**
1. The packaging run (`package_dev_fixtures_uat.txt`) and container listing (`utoc_list_fixtures_package.txt`) were executed at **19:39 on 2026-10-26**.
2. At 19:39, **only Epoch 1 fixtures existed on disk**. The container listing accurately reflected the 5 cooked assets in existence at that moment.
3. The 3 Epoch 2 seam assets (`DA_ABITest_*`) were created at **22:10 on 2026-10-26** (nearly 3 hours *after* the packaging run completed).
4. **Conclusion & Boundary**:
   - The historical "five-entry" assertion was an accurate point-in-time observation of the 19:39 container, but **it cannot and does not cover the 3 later seam assets**.
   - Under current configuration (`DirectoriesToAlwaysCook` covering `/Game/OneBossFight/Data`), the 8 current source assets in `TypedABIFixtures/` are **expected candidates** to be cooked in a future build. However, this configuration intent is not an unconditional output guarantee (it does not predict future filters, packaging overrides, or cook errors); actual verification requires an inspection of a newly produced container listing.
   - No newer covering container listing was found or identified in the inspected evidence.
   - Being outside `AlwaysCook` is not proof of non-reference or general exclusion: the historical IoStore listing proves absence in *that specific package*, but no complete binary dependency graph audit was delivered to establish zero inbound references across all assets generally.

---

## 3. Five-Tier Evidence Boundary Analysis

The relationship between source code, test fixtures, configuration, and packaging containers spans five distinct technical layers:

```mermaid
flowchart TD
    subgraph L1["Tier 1: Scanner Coverage"]
        C1["CheckStagedContent.py"]
        C2["FRPGCookCoverageTest"]
        R1["Regex: (/Game/[^\"]+)"]
        SPLIT["Split Prefix: TEXT('/Game/') + TEXT(...)"]
        C1 --> R1
        C2 --> R1
        SPLIT -.->|"Bypasses Scanner"| R1
    end

    subgraph L2["Tier 2: Metadata / Cooking Rules"]
        INI["Config/DefaultGame.ini"]
        COOK_DATA["DirectoriesToAlwaysCook: /Game/.../Data"]
        NO_COOK["ReviewFixtures NOT in AlwaysCook"]
        INI --> COOK_DATA
        INI --> NO_COOK
    end

    subgraph L3["Tier 3: Packaged Container (IoStore)"]
        UTOC["OneBossFight-Windows.utoc"]
        E1_5["5 Epoch 1 Fixtures (PRESENT in 19:39 Listing)"]
        E2_3["3 Epoch 2 Seam Assets (UNPACKED / POST-DATE)"]
        UNCOOK["DA_ABI_UncookedWeaponItem (EXCLUDED in 19:39 Listing)"]
        COOK_DATA --> E1_5
        COOK_DATA -.->|"Candidate Cook Input"| E2_3
        NO_COOK --> UNCOOK
    end

    subgraph L4["Tier 4: Shipping Executable"]
        SHIP["#if !UE_BUILD_SHIPPING"]
        CVAR["rpg.CatalogPath / rpg.CatalogSource"]
        COMPILED_OUT["Specific CVar Override Route Compiled Out"]
        SHIP --> COMPILED_OUT
        COMPILED_OUT -.->|"Cannot Load Overrides"| CVAR
    end

    subgraph L5["Tier 5: Cold Runtime Route"]
        RUN["Packaged Game Cold Start"]
        DEF["Loads Shipped Catalog Default (source=data)"]
        INERT["Fixture Memory/Execution Status UNKNOWN"]
        RUN --> DEF
        DEF --> INERT
    end
```

### 3.1 Tier 1: Literal Scanner Coverage
- **Mechanism**:
  - `Scripts/CheckStagedContent.py:12` uses `STRING_PATH = re.compile(r'["\'](/Game/[A-Za-z0-9_./]+)["\']')`.
  - `Source/OneBossFight/Tests/RPGAutomationTests.cpp:1264` uses `Pattern(TEXT("\"(/Game/[^\"]+)\""))`.
- **Implementation Reality**:
  - In `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp:257-258, 503-504` and `Source/OneBossFight/Player/RPGCombatCatalog.cpp:262`, paths are constructed via split literals:
    ```cpp
    const FString Fixtures = FString(TEXT("/Game/")) + TEXT("OneBossFight/Data/TypedABIFixtures/");
    const FString Uncooked = FString(TEXT("/Game/")) + TEXT("OneBossFight/ReviewFixtures/TypedABI/");
    ```
- **Finding**: Split string construction prevents both Python and C++ regex scanners from detecting these paths as C++ referenced assets. Running `python -B -I Scripts/CheckStagedContent.py` succeeds with exit code 0 (61/61 referenced packages present, 0 missing in `Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt` with 9,191 entries). Scanner coverage is an asset-linkage integrity check for shipped code, not a package container verification.

### 3.2 Tier 2: Metadata / Cooking Rules
- **Mechanism**:
  - `Config/DefaultGame.ini:22` specifies `+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Data")`.
- **Implementation Reality**:
  - `DirectoriesToAlwaysCook` represents cooking configuration intent. Under current settings, the Unreal Cooker traverses `/Game/OneBossFight/Data` recursively. Because `Content/OneBossFight/Data/TypedABIFixtures/` is a subdirectory, assets placed within it are expected candidate inputs for cooking.
  - `Content/OneBossFight/ReviewFixtures/` is located at `/Game/OneBossFight/ReviewFixtures`. It is NOT listed in `DirectoriesToAlwaysCook`.
- **Finding**:
  - The 8 current source assets under `TypedABIFixtures` are expected cook candidates under unchanged relevant configuration.
  - For `ReviewFixtures`, the historical IoStore listing proves absence in *that specific package*. However, general non-reference across the entire project has not been verified by an exhaustive binary dependency graph audit.

### 3.3 Tier 3: Raw Staged / UFS / IoStore Pak Listing
- **Available Evidence**:
  - `utoc_list_fixtures_package.txt` (SHA256 `c8279ff4...`, 19:39) and `Manifest_UFSFiles_Win64.txt` (SHA256 `38c5aea0...`, 14:07 UTC / 19:37 IST).
- **Distinction Between Manifest & IoStore Formats**:
  - `Manifest_UFSFiles_Win64.txt` records loose staged files: exactly 10 lines for the 5 packages (each package lists both a `.uasset` and a `.uexp` file under `Data/TypedABIFixtures/`).
  - `utoc_list_fixtures_package.txt` records IoStore container package headers: exactly 5 package-header lines. The entry counts between UFS manifests and IoStore containers must not be equated.
- **Findings**:
  - **Epoch 1 Fixtures**: Exactly 5 package headers appear in the IoStore listing (`BP_ABI_FourthWeaponActor`, `GA_ABI_FourthMelee`, `DA_ABI_FourthCombatStyle`, `DA_ABI_FourthWeaponItem`, `DecoyPackage/BP_ToughSword`). Each has a packed header footprint of ~0.8 to 1.2 KB (which is the header size, not total uncompressed asset footprint).
  - **Uncooked Exclusion**: Exactly 0 occurrences of `ReviewFixtures` or `Uncooked` exist in `utoc_list_fixtures_package.txt`.
  - **Epoch 2 Seam Assets**: Exactly 0 occurrences of `DA_ABITest_*` appear in `utoc_list_fixtures_package.txt` because the assets postdate that packaging run.
- **Finding**: Prior package container proof establishes that the uncooked negative fixture was excluded and the 5 Epoch 1 fixtures were cooked in that specific 19:39 package. No newer covering container was found in inspected evidence.

### 3.4 Tier 4: Executable Compile-Out (`#if !UE_BUILD_SHIPPING`)
- **Mechanism**:
  - In `Source/OneBossFight/Player/RPGCombatCatalog.cpp:16-21`:
    ```cpp
    #if !UE_BUILD_SHIPPING
    static TAutoConsoleVariable<FString> CVarCatalogSource(TEXT("rpg.CatalogSource"), ...);
    static TAutoConsoleVariable<int32> CVarCatalogFourth(TEXT("rpg.CatalogTestFourth"), ...);
    static TAutoConsoleVariable<FString> CVarCatalogPath(TEXT("rpg.CatalogPath"), ...);
    static TAutoConsoleVariable<int32> CVarCatalogInvalid(TEXT("rpg.CatalogTestInvalid"), ...);
    #endif
    ```
  - In `Source/OneBossFight/Player/RPGCombatCatalog.cpp:302-311` and `RPGCombatCatalog.h:130-134`, `CVarCatalogPath.GetValueOnGameThread()`, `TestCatalogRoot()`, and `ValidateTestCatalogPath()` are guarded by `#if !UE_BUILD_SHIPPING`.
- **Finding & Narrowing**:
  - `#if !UE_BUILD_SHIPPING` verifies C++ source intent: the specific `rpg.CatalogPath` / `rpg.CatalogSource` override route is compiled out when that source is built as Shipping.
  - This does not constitute an independent binary inspection of a newly built Shipping binary, nor does it prove that all possible asset loaders in the engine cannot load a test catalog.
  - *Symbol Inspection Note*: Static/internal console variables may have no exported symbols even in Development builds; the lack of a `CVarCatalogPath` export is a weak negative check, not conclusive binary proof. Proper verification requires a scoped binary string inspection and runtime verification on a freshly built Shipping binary.
- **Critical Distinction (Code vs Asset Packaging)**:
  - While test override code is compiled out in Shipping source, asset cooking is governed by `DirectoriesToAlwaysCook`.
  - Because `/Game/OneBossFight/Data` is in `DirectoriesToAlwaysCook`, `.uasset` files under `TypedABIFixtures/` would still be candidate cook inputs in a Shipping package unless explicitly relocated or excluded in packaging configuration.
  - *Artifact Age Note*: Inspected Shipping stage artifacts (`Saved/StagedBuilds_Shipping/Windows/Manifest_UFSFiles_Win64.txt`, SHA256 `9c74f8f9...`) date from 2026-10-24 22:17, predating fixture work by 2 days. The status of fixtures in a newer Shipping build remains an inspected-evidence unknown.

### 3.5 Tier 5: Actual Cold Runtime Route
- **Available Evidence**:
  - `packaged_dev_fixtures_run.log` (Development cold start, 2026-10-26 19:39) and `abi_fourth_equip_run3.log` (Automation PIE run, 2026-10-26 22:26).
- **Findings & Narrowing**:
  - In `packaged_dev_fixtures_run.log:237, 842`, normal cold start with command line `-nosound -log` initializes with `source=data` and loads the shipped default catalog (`DA_CombatCatalog`).
  - *Load / Execution Status*: The absence of fixture log strings supports that the default catalog route was selected. However, it does not prove that fixture assets were never loaded, referenced, or executed in memory; that remains **UNKNOWN** beyond the scoped path/equip observations.
  - *Error Preservation*: Cold log lines 824+ contain 19 lines with `LogMaterial: Error:` and uncooked shader warnings (KI-080; 19 lines, not 19 unique defects). Route success is an observed baseline, not a clean final package or render verdict.
  - In `abi_fourth_equip_run3.log:1693-1694`, the test seam was activated in an automation session via `rpg.CatalogPath` and `rpg.CatalogSource data`, restoring 4 CVars and ending RESULT 15/15. This confirms transient readback of fourth weapon actor, style, and item in PIE.

---

## 4. Source/Hash-Pinned Claim-Evidence-Unknown Matrix

The following matrix synthesizes all claims across the five technical tiers, pinning available evidence, identifying boundaries, and establishing the exact checks required for the replacement operator:

| Claim / Subject | Actual Available Evidence (Timestamp & Hash) | Input Boundary & Scope | Current Unknown | Future Operator Check | Governing Gate Boundary |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **1. C++ Scanner Coverage** | `Scripts/CheckStagedContent.py` (`81625927...`) exits 0; `RPGAutomationTests.cpp:1264` (`22299a44...`) | Scans only contiguous `"/Game/..."` string literals in `Source/OneBossFight/` | Lexical scanner coverage only; does not detect assets referenced via split string concatenation | Verify split string policy is maintained for test-only paths | DD-1 Step 2 / Gate 0 |
| **2. Cook Directory Configuration** | `Config/DefaultGame.ini:22` (`9827ff8e...`) lists `/Game/OneBossFight/Data` | Configures cooker directory traversal intent | Configuration intent is not an output guarantee; does not predict overrides, filters, or cook errors | Inspect actual container listing from a fresh package build | Step 2 / Gate 4 (Packaging) |
| **3. ReviewFixtures Exclusion** | `utoc_list_fixtures_package.txt` (`c8279ff4...`, 19:39) has 0 matches for `ReviewFixtures` | Validates IoStore container generated at 19:39 on 2026-10-26 | Confirms absence in that package; does not prove zero inbound references across all assets generally | Run IoStore container check (`UnrealPak -List`) on fresh packages | Step 2 / Gate 4 (Packaging) |
| **4. Historical 5-Entry Assertion** | `utoc_list_fixtures_package.txt:4083-4248` lists exactly 5 Epoch 1 fixture package headers | Point-in-time container snapshot at 19:39 on 2026-10-26 | Does NOT cover the 3 Epoch 2 seam assets (`DA_ABITest_*`, created at 22:10) | Build fresh Development package; verify container listing against then-reviewed inventory | Step 2 / Gate 4 (Packaging) |
| **5. Seam Asset Integrity** | `Claude/Evidence/exports/abitest_catalog_assets_sha256.txt` (`4c5a1ec2...`); on-disk reads match | Disk presence of `DA_ABITest_Build_Fourth`, `_Catalog`, `_Weapon_Fourth` | Byte presence does not prove packed inclusion or Shipping compile-out | Check IoStore listing on next scheduled package build | Step 2 / Gate 4 (Packaging) |
| **6. Shipping CVar Override Compile-Out** | `RPGCombatCatalog.cpp:16-21, 302-311` (`f6f71036...`) enclosed in `#if !UE_BUILD_SHIPPING` | Preprocessor source intent for specific CVar override route | Confirms source compile-out; does not inspect binary or prove all loaders cannot load test data | Scoped binary string inspection and runtime check on fresh Shipping binary | Gate 4 (Shipping) |
| **7. Shipping Container Status** | `Saved/StagedBuilds_Shipping/` manifest (`9c74f8f9...`) dated 2026-10-24 22:17 | Predates all typed ABI fixtures by 2 days | Fixture presence/exclusion in a newer Shipping package container is an inspected-evidence unknown | Execute full Shipping package build and inspect container | Gate 4 (Shipping) |
| **8. Default Packaged Runtime Route** | `packaged_dev_fixtures_run.log` (`2bbe28c8...`) shows cold start `source=data`; cold errors in line 824+ | Validates default non-override boot in Development package | Proves default catalog route chosen; fixture memory/execution status beyond path observation is UNKNOWN | Monitor packaged logs during cold boot for unexpected fixture loads; resolve material errors | DD-1 Step 2 / Gate 2 |
| **9. Live Fourth Equip in PIE** | `abi_fourth_equip_run3.log` (`49b9d9ed...`) ends 15/15, confirms readback | Exercises `rpg.CatalogPath` seam in PIE automation session | Proves transient GI readback; does not prove combat execution or weapon swing | Live combat swing and montage execution in PIE | DD-1 Step 2 / Gate 2 |

---

## 5. Architectural Synthesis & Recommendations for Replacement Operator

1. **Acknowledge Fixture Epochs & Exact Count Expectations**:
   - Historical references to "five fixture entries" must be qualified: they represent the Epoch 1 state (19:39). The tree currently holds **8 cooked fixture candidates** and **1 uncooked fixture asset** (9 total).
   - Future exact-count container expectations must derive from the then-reviewed asset inventory, configuration, and container proof, not a timeless 8-entry mandate.

2. **Preserve Scanner Bypasses**:
   - The split string concatenation (`FString(TEXT("/Game/")) + TEXT(...)`) in `RPGCombatCatalogTests.cpp` and `RPGCombatCatalog.cpp` is intentional lexical isolation. It prevents `CheckStagedContent.py` and `FRPGCookCoverageTest` from treating test-only folders as required production C++ references. Do not "clean up" these split strings into contiguous literals.

3. **Separate Code Guards from Cooking Rules**:
   - The C++ test seam is compiled out in Shipping source via `#if !UE_BUILD_SHIPPING`.
   - However, asset packaging is governed by `Config/DefaultGame.ini`. Because `/Game/OneBossFight/Data` is in `DirectoriesToAlwaysCook`, fixture assets under `TypedABIFixtures` remain candidate cook inputs in Shipping packages unless `TypedABIFixtures` is relocated outside `/Game/OneBossFight/Data` or excluded prior to final release.
   - This audit authorizes no new inclusion, exclusion, or relocation policy; that decision belongs to the replacement operator and project lead prior to final Shipping gating.

4. **Preserve Append-Only Evidence Integrity**:
   - Do not delete, re-save, or modify any existing fixture assets in `Content/OneBossFight/Data/TypedABIFixtures/` or `Content/OneBossFight/ReviewFixtures/TypedABI/`.
   - All 9 fixture assets match their historical and disk hashes exactly.
