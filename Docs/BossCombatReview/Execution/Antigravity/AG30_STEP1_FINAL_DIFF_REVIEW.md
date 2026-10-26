# AG-30: Adversarial Audit of the Final DD-1 Step 1 Diff

**Document ID:** `AG30_STEP1_FINAL_DIFF_REVIEW`  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Directive:** Claude `[C-131]`  
**Target Codebase:** Final WP-15 implementation of DD-1 Step 1 (`Source/OneBossFight/`)  
**Audited Git Diff:** `Source/OneBossFight/Player/RPGCombatCatalog.cpp`, `Source/OneBossFight/Player/RPGBuildLoadout.h/.cpp`, `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp`  
**Status:** DELIVERED  

---

## 1. Executive Summary

In response to Claude's invitation in `[C-131]`, Antigravity re-audited the final Step 1 diff produced by Claude under WP-15 against the 8 adversarial findings originally documented in `AG22_STEP1_CODE_REVIEW.md`.

### Summary Scorecard
- **FIXED:** 4 findings (`F1`, `F2`, `F3`, `F8`) — verified with exact code diffs and passing automation tests.
- **NOT A DEFECT (As Designed / Specified):** 3 findings (`F4`, `F6`, `F7`) — confirmed as intentional architectural boundaries (ACF pack topology, headless automation support, static built-in table scope).
- **OPEN (Benign UX Residual):** 1 finding (`F5`) — loadout prevents gameplay desync, minor console log discrepancy remains.

---

## 2. Granular Line-by-Line Disposition Matrix

| Finding ID | Original Defect / Hazard | Status | Exact File & Line in Final Code | Technical Proof / Resolution |
| :--- | :--- | :--- | :--- | :--- |
| **F1** | `FEpoch::Describe` fell back to `Starter` on ambiguous style query | **FIXED** | [`Source/OneBossFight/Player/RPGCombatCatalog.cpp:62`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L62)<br>[`Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp:60`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp#L60) | Line 62 explicitly intercepts `EResolve::Ambiguous` and returns `FString::Printf(TEXT("Ambiguous (%s)"), *Style.ToString())`. Strictly conforms to Spec v3 Section C.4. Test assertion at line 60 confirms `"Ambiguous"` prefix. |
| **F2** | `URPGBuildLoadout::GetBuildName` misclassified unverified catalog weapon as `"OffBuild"` | **FIXED** | [`Source/OneBossFight/Player/RPGBuildLoadout.cpp:287-290`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.cpp#L287-L290) | Line 287 explicitly evaluates `Reverse == EResolve::Ambiguous` and returns `TEXT("Ambiguous")`. Line 291 reserves `"OffBuild"` strictly for styles present on no epoch build. |
| **F3** | Stale legacy enum slot retained in write-only derived `Chosen` | **FIXED** | [`Source/OneBossFight/Player/RPGBuildLoadout.h:205`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.h#L205)<br>[`Source/OneBossFight/Player/RPGBuildLoadout.cpp:552`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.cpp#L552) | The derived write-only variable `ERPGBuild Chosen` was completely deleted from header and cpp. Line 552 removed `Rules::LegacySlotOf`. `ChosenId` is the sole authoritative state; stale enum retention eliminated. |
| **F4** | `RPGCombatRegistry::Legacy()` lacked `ItemBaseClass`, aborting resolving compile | **NOT A DEFECT (AS SPECIFIED)** | [`Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp:128-132`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp#L128-L132) | Built-in fallback table is intended for non-resolving offline execution (`bResolveAssets = false`) to avoid hardcoded asset paths. In test `FRPGCatalogResolutionTest`, ancestry is populated via pack item query, and production data catalog sets `ItemBaseClass` properly on disk. |
| **F5** | `URPGBuildSelect::Pick` same-choice check broken by raw aliases | **OPEN (BENIGN RESIDUAL)** | [`Source/OneBossFight/UI/RPGBuildSelect.cpp:428`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBuildSelect.cpp#L428)<br>[`Source/OneBossFight/Player/RPGBuildLoadout.cpp:549-551`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.cpp#L549-L551) | `Pick()` still logs `"requested"` instead of `"Same"` when given an alias (e.g. `"sword"` while on `Starter`). However, `URPGBuildLoadout::ReadChoice()` catches the alias at lines 549-551 (`if (bExplicit && ChosenId == Build) break;`), preventing redundant re-equipping. Gameplay is safe; minor UI log residual. |
| **F6** | Unchecked concatenation in dependency wiring validation | **NOT A DEFECT (AS DESIGNED)** | [`Source/OneBossFight/Player/RPGCombatCatalog.cpp:186-193`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp#L186-L193) | Concatenation is required by ACF pack architecture: `Item` references `ActorClass`, while `Style` references `AbilityClass`. Validating all three objects jointly tests the closed dependency loop of the ACF weapon bundle. |
| **F7** | Programmatic `Pick()` bypasses viewport row visibility check | **NOT A DEFECT (AS DESIGNED)** | [`Source/OneBossFight/UI/RPGBuildSelect.cpp:418`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/UI/RPGBuildSelect.cpp#L418) | Necessary for headless test automation where viewport height is 0. Guarding rows 0..2 in programmatic API would cause all headless CI tests to fail. Number keys and mouse clicks are strictly guarded by UI layout. |
| **F8** | Zero asset resolution & cook checks in automation tests | **FIXED** | [`Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp:116-143`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp#L116-L143) | Added `OneBossFight.Catalog.Resolution` automation test: compiles all 3 shipped weapons with `bResolveAssets = true`, verifies asset loading, leases, ancestry, cook policy, and proves rejection on mismatched style assets. |

---

## 3. Conclusion & Recommendation

The final Step 1 implementation under WP-15 cleanly resolves all core specification and safety hazards identified in `AG-22`:
- Spec v3 Section C.4 reverse mapping is mathematically sound and verified by automation.
- Unverified catalog styles correctly report `"Ambiguous"` rather than falling through to `"OffBuild"`.
- Legacy enum drift is eliminated by deleting the write-only enum variable.
- Resolving compile coverage is verified by automated test `OneBossFight.Catalog.Resolution`.

Antigravity recommends **ACCEPTANCE of Step 1 from an animation and technical systems perspective**, subject to Codex's formal acceptance review and owner sign-off.
