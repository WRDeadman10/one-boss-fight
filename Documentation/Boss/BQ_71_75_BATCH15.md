# BQ-71..75: Queue BQ batch 15, Shipping pipeline, packaged smoke, stage-provenance inputs

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Static and in-process only.** No package, cook, smoke run or binary read. No new native C++ test was added in this batch while the "no-test instruction" question (C-1592) is open; only in-process Python tests ran.

| Task | Result | Files |
|---|---|---|
| **BQ-71** (D5) Shipping pipeline command sheet | **reconciled, already exists.** `Documentation/GATE4_RUNBOOK.md` is the command sheet: preconditions and C-1155 locks (§Preconditions, §Editor and staging locks); G4-1 `Package.ps1 -Configuration Development` plus benchmark; G4-2 package, cooked-asset check and smoke (`CheckPackagedLog.ps1`); G4-3 Shipping debug-off (`Package.ps1 -Configuration Shipping`, `CheckPackagedLog.ps1 -CookLog -RuntimeLog`); and the owner sections (console-session benchmark, other-PC benchmark, hand tests). A second sheet would duplicate it, so none was written | none |
| **BQ-72** (D6) packaged smoke checklist | **reconciled, already exists.** It is runbook §"Packaged smoke and Shipping debug-off check": `PackagedSmoke.ps1 -Seconds 20` detects the Shipping child binary, runs `CheckShippingBinary.py`, and stops the whole launcher process tree. The receipt checker `check_packaged_smoke_receipt.py` was rerun in-process: **7/7**. The audit found the binary checker only inspected `rpg.Debug` and `LogRPGDebug`; BQ-74 below now supplies the full source-derived forbidden CVar list. | none |
| **BQ-73** (D7) stage-provenance checker inputs | **new, source/planning accepted A-978.** `Scripts/Tools/shipping_cvar_expectations.py` classifies each `rpg.*` registration by its preprocessor region: `#if !UE_BUILD_SHIPPING`, the `#else` of `#if UE_BUILD_SHIPPING`, and `#if UE_BUILD_DEVELOPMENT/DEBUG` count as excluded. For `RPG_PERF_SWITCH` it uses the guarded `#define` line. Anything it cannot classify is reported as **unknown**, never assumed guarded. Lead review fixed `#ifndef` polarity for Shipping/Development/Debug macros and added synthetic coverage. `violations(found, exp)` fails closed for guarded/unclassified names found in a binary. **Real-tree result: 43 expected absent, 7 expected present, 0 unknown.** The 7 present are exactly the KI-168 / BQ-23 set (`BossOverlay`, `CameraDebug`, `Legend`, `LegendShakeScale`, `Build`, `CloseTelegraph`, `Boss.ProjectHitReaction`). The focused in-process suite passes **7/7**, including binary-check integration. | `Scripts/Tools/shipping_cvar_expectations.py`, `Scripts/Tools/test_shipping_cvar_expectations.py` |
| **BQ-74** existing stage-identity checks and binary checker wiring | **reconciled and wired.** Existing suites: `test_check_stage_identity` 5/5 (distinct Shipping and Development roots, required files, `OBF-<CONFIG>-<stamp>-<hash>` build stamp), `test_package_stage_roots` 9/9, `test_aq_package_gates` 5/5, `test_packaged_smoke_receipt` 7/7. `Scripts/CheckShippingBinary.py` now obtains expected-absent and unknown CVar names from the source expectation library, scans ASCII and UTF-16 strings along with the legacy debug names, and fails on any forbidden match. The new synthetic integration case covers an excluded CVar and the legacy debug name. Package/Shipping binary execution remains ENG-gated and was not run. |
| **BQ-75** | this report | |

## Gates

- **ENG:** package Shipping under C-1155 and run the smoke. Then run the binary string check with the expanded list. That is KI-168's packaged-binary evidence, still open.
- **Lead:**
  - wiring approved and applied; remaining acceptance is the source-only review plus C-1155/ENG packaged-binary run;
  - the three Shipping guards accepted in X-2343 are still unimplemented. Once added, `rpg.BossOverlay`, `rpg.CameraDebug` and `rpg.Boss.ProjectHitReaction` move to expected-absent automatically, and the real-tree test must then be updated from 7 names to 4.

## Limits

- The preprocessor model is deliberately simple. Compound conditions such as `UE_BUILD_SHIPPING || WITH_EDITOR` are reported as unknown, and the real tree has none today. Direct `#ifdef`/`#ifndef` of Shipping/Development/Debug build macros are covered; unrecognized `UE_BUILD_*` macro-name guards remain unknown rather than being assumed safe.
- Registrations in headers are scanned too. Names spread across files are merged: if any unguarded site exists, the name counts as present.
