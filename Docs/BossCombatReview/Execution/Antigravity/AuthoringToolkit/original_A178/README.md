# OneBossFight Authoring Toolkit (`AG-CONTENT04`)

**Author:** Antigravity (Party Code `A`) - Senior C++ Implementer & Unreal Engine Specialist  
**Work Order:** `[X-282]` / `Docs/BossCombatReview/Execution/Codex/AG_CONTENT04_AUTHORING_TOOLKIT_IMPLEMENTATION.md`  
**Review Status:** Source delivery submitted for Technical Lead Codex (`X`) independent review.  
**Execution Boundary:** **STRICTLY OFFLINE IMPLEMENTATION**. Zero Unreal Engine processes launched; zero assets created, mutated, or deleted; zero pack edits; zero git commits or pushes.

---

## 1. Architecture Overview & Components

The **OneBossFight Authoring Toolkit** provides a pure, defensive, staged Python infrastructure for inspecting, validating, authoring, and exporting gameplay Data Assets for Unreal Engine 5.5.

The toolkit connects four cohesive deliverables:

```
AuthoringToolkit/
├── authoring_core.py                 <-- Pure Python shared validation core (standard library only)
├── draft_boss_profiles.py            <-- Staged DRAFT creator for boss & player participant URPGBossDefinition assets
├── inspect_authored_assets.py        <-- Read-only asset inspector & JSON exporter (zero mutations)
├── test_authoring_core.py            <-- Standard library unittest test suite (33 adversarial tests)
├── test_run_output.txt               <-- Raw test suite execution output (exit code 0)
├── examples/
│   └── boss_draft_profiles.json      <-- Explicit two-boss + one-player draft profile specifications
├── README.md                         <-- This integrated architecture and usage specification
└── evidence_sha256.txt               <-- Cryptographic SHA-256 evidence receipt

BuildAuthoringHelper/
├── author_custom_build.py            <-- Staged custom build & cloned catalog authoring helper (imports authoring_core)
├── original_A176/                    <-- Byte-exact preserved A-176 historical delivery
└── original_A177/                    <-- Byte-exact preserved A-177 historical delivery
```

---

## 2. Core Validation Invariants (`authoring_core.py`)

1. **Exact Native Normalization (`exact_native_normalize`):**
   * Mirrors Unreal Engine 5.5 `String.cpp.inl:971-974 TrimQuotesInline` and `RPGCombatRegistry::Normalize`:
     ```cpp
     FString Normalize(const FString& Text) {
         return Text.TrimStartAndEnd().TrimQuotes().TrimStartAndEnd().ToLower();
     }
     ```
   * Trims leading/trailing whitespace, trims leading/trailing double quotes (`"`) independently, trims remaining whitespace, and converts to lowercase.
   * **Single quotes (`'`) are preserved characters** in native UE5 strings and are never stripped.
2. **Strict FName Semantics (`exact_fname_equal`):**
   * Case-insensitive ASCII comparison.
   * **Whitespace is significant**: in Unreal Engine, `FName(" Strength ") != FName("Strength")`.
3. **Canonical Path & Anti-Traversal Enforcement:**
   * Enforces authorized project roots (`/Game/OneBossFight/Data/Catalog/`, `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/`).
   * Rejects path traversal (`..`), empty segments (`//`), backslashes (`\`), sub-object colons (`:`), and non-canonical characters.
4. **Finite Numeric Domain Verification:**
   * Validates strict finite integers and floats.
   * Rejects booleans (which are subclasses of `int` in Python), `NaN`, positive infinity, and negative infinity.
5. **Immutable Source Snapshotting & Drift Prevention:**
   * Deep snapshot comparison (`SourceInventorySnapshot`) comparing weapon arrays, build arrays, ordering, field values, and package dirty flags.
   * Guarantees zero source mutation during asset creation or duplication.
6. **Cloned Catalog Read-Back Verification:**
   * Verifies that the cloned catalog contains all original builds in the exact same order, plus exactly one new reference pointing to the custom build.

---

## 3. Staged Authoring Workflow & Anti-Overwrite Policy

All authoring tools implement a defensive three-phase lifecycle:

1. **Dry-Run Mode (Default):**
   * Validates input parameters, checks namespace collisions, inspects source packages, verifies destination paths, and outputs a formatted Proposed Plan.
   * Zero writes, zero saves, zero engine mutations.
2. **In-Memory Apply Mode (`--apply`):**
   * Creates Data Assets in memory only using explicit `set_editor_property` and soft object paths.
   * Performs complete read-back assertions before proceeding.
   * **Does not save to disk by default.**
3. **Explicit Save Opt-in (`--apply --save`):**
   * Saves newly created output packages to disk only when explicitly requested.
   * Verifies source packages remain clean. Any source drift blocks saving.
4. **Anti-Overwrite Protection:**
   * If target output packages already exist on disk or in memory before creation, execution halts with a fatal refusal.
   * **Existing outputs block retry.** Re-running the command after an apply will not silently overwrite, delete, or recreate assets.

---

## 4. Draft Boss & Player Profiles (`draft_boss_profiles.py`)

Authors `URPGBossDefinition` assets from JSON specifications:

* **Two Distinct Boss Profiles:**
  * `DA_Boss_EmberWarden_Draft` (`DefinitionId = Boss_EmberWarden`)
  * `DA_Boss_AbyssalRevenant_Draft` (`DefinitionId = Boss_AbyssalRevenant`)
  * Both feature exactly 1 transition phase record (`PhaseTwo` / `PhaseTwo_Abyssal`), strictly adhering to the native backend constraint (`RPGBossPhaseAdapters.cpp:107` requiring `NativeTransitionRecords == 1`).
* **One Player Participant Profile:**
  * `DA_Player_Hero_Draft` (`DefinitionId = Player_Hero`)
  * Validates `TargetOnly` / player participant configuration (zero boss phases).
* **Truthful Draft Status:**
  * `Fields` arrays are intentionally left empty because no 51-row parity manifest is fabricated.
  * A truthful manifest with real source paths and SHA256 hashes is required before production compilation.
  * These definitions are **NOT playable duels**.

---

## 5. Read-Only Authored Asset Inspector (`inspect_authored_assets.py`)

* **Strictly Read-Only:** Zero setters, zero asset creation/duplication, zero deletions, zero saves.
* **Authorized Inputs:** Inspects project-owned paths under `/Game/OneBossFight/Data/Catalog/` and `TypedABIFixtures/`.
* **Typed Asset Diagnostics:** Identifies `URPGCombatCatalog`, `URPGBuildDefinition`, `URPGWeaponDefinition`, and `URPGBossDefinition`.
* **Dependency Inspection:** Optional `--inspect-dependencies` reports disk existence and memory status without resolving the entire pack or making capability claims.
* **Bounded Export:** `--export-file` output is strictly confined to the `AuthoringToolkit/` directory.

---

## 6. Native Compilation Gap & Testing Seams

> [!IMPORTANT]
> **Python Reflection vs. Native C++ Compilation:**  
> Python reflection checks validate asset presence, property definitions, and namespace strings inside the Unreal Editor environment. They **do NOT** execute native C++ `RPGCombatRegistry::Compile` or validate `FEpoch` binary ABI layout.  
> 
> Furthermore, existing automated test suites (such as `OneBossFight.Catalog.Validation` and `OneBossFight.Catalog.TestPathSeam` in `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp`) validate the shipped catalog and the test fixture root (`/Game/OneBossFight/Data/TypedABIFixtures/DA_ABITest_Catalog`), but **do not automatically discover or compile newly authored preview outputs**.  
> 
> True native compilation and ABI validation requires the sole engine operator to test the cloned catalog through the native C++ testing seam (`RPGCombatCatalog::Compile`), with `CVarCatalogPath` pointing to `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/DA_CombatCatalog_VanguardCloned`.

---

## 7. Offline Unit Test Suite Results (`test_run_output.txt`)

Executed with Python standard library `unittest`:
```bash
python Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_authoring_core.py -v
```

* **Results:** **33/33 tests PASS** (0 failures, 0 errors, exit code `0`).
* **Coverage:**
  * Double-quote and single-quote normalization parity (TrimQuotesInline).
  * FName case-insensitivity without whitespace stripping.
  * Path traversal, sub-object colon, and unauthorized root rejections.
  * Finite integer and float boundary checks (anti-NaN, anti-Infinity, anti-bool).
  * Build namespace collision and reserved keyword rejections.
  * Pinned 3-build and 3-weapon contract validation.
  * Deep source inventory snapshot comparison and drift detection.
  * Cloned catalog readback ordering and parity verification.
  * Draft boss profile and player participant validation.
  * Partial operation report records.

---

## 8. Delivered Artifacts
| Path | Description |
| :--- | :--- |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/authoring_core.py` | Pure Python shared validation core (standard library only) |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py` | Staged DRAFT creator for URPGBossDefinition assets |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/inspect_authored_assets.py` | Read-only asset inspector & JSON exporter |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_authoring_core.py` | Comprehensive standard-library unittest suite (33 tests) |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_run_output.txt` | Raw test suite execution output (33/33 PASS, exit 0) |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json` | Sample draft boss and player profile definitions |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/README.md` | Integrated architecture, safeguards, and verification guide |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/evidence_sha256.txt` | Cryptographic SHA-256 evidence receipt |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py` | Updated build authoring helper integrating authoring_core |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A176/` | Preserved byte-exact A-176 deliverables |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A177/` | Preserved byte-exact A-177 deliverables |
