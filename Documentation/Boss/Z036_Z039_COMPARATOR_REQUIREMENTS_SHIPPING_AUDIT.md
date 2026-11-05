# Queue Z Batch 8 — comparator, matrix and Shipping scan audit

Date: 2026-11-06. Read-only review of current source, tests, matrix and staged executable artifacts. The G044 comparator was invoked against the checked-in manifest/table; the Shipping symbol scanner was invoked against the two present Shipping executables. No tests, Unreal, Editor, PIE, build, package, source, or asset operation was run.

## Z036 — requirements matrix after review

The current CSV remains an 82-row mapping to the 82 canonical ledger IDs. A static exact-literal/source-file cross-check of its `PrimaryAutomationTest` values against `IMPLEMENT_*AUTOMATION_TEST` registrations under `Source/OneBossFight/Tests` finds **5 exact name-and-declared-source matches and 77 unmatched rows**. This reproduces the result in `X_C011_C014_REQUIREMENTS_MATRIX_REVIEW.md`; it does not establish absence of conceptual coverage. Current matching IDs: BOSS-AWR-001, BOSS-AWR-002, BOSS-EXE-007, BOSS-EXE-008, BOSS-QA-005.

`Scripts/Tools/test_requirements_coverage_matrix.py` still checks required columns, row count and ID set, nonempty cells, source-file existence, and enum membership. It does not inspect registration literals or test-to-source association. The prior review's 77 rows therefore remain **UNKNOWN/UNVERIFIED**, with any suite-level intent needing an explicit mapping contract. The matrix has not been rewritten and its tests were not run in this audit.

## Z037 — G044 source-token comparator

Ran `compare_manifest_to_legacy_defaults.py` on `Saved/G044/encounter_manifest.json` and `Scripts/Tools/legacy_defaults_g044.json`: 424 leaves, 214 MATCH, 0 MISMATCH, 210 NOT-COMPARABLE. This is a current manifest/table comparison, not a check that the table's numeric legacy values match literals in cited source.

The comparator verifies cited line/excerpt identity, then compares manifest value to `legacy_value` (`Scripts/Tools/compare_manifest_to_legacy_defaults.py`, `audit`). It does not parse the cited numeric token. The 2000-source / 1800-table / 1800-manifest counterexample remains a false-pass by direct code-path inspection. Existing tests include the source line in valid examples but no rejection fixture for the inconsistent 2000/1800 case (`test_compare_manifest_to_legacy_defaults.py`). No synthetic fixture or tests were executed here; the prior concrete counterexample in `X_C016_C019_G044_PARITY_AUDIT.md` remains unresolved.

## Z038 — structured health parity

The parity comparator still skips message rules whenever either observable has a typed `comparison` (`compare_encounter_parity.py`, `_message_warnings` and `_observable_value_matches`). The current regression test `test_typed_observable_precedes_check_message_tokens` sets typed timing values 0.400 and 0.427, both PASS, while the messages report health 2000 and 1500; it asserts that `compare()` returns no issue. The counterexample therefore remains accepted. There is no structured boss-health field in that fixture/schema path. Route identity controls remain in the comparator and are independent of this missing health comparison. No parity tests were run.

## Z039 — Shipping symbol scan scope and current binaries

`Scripts/CheckShippingFeatureSymbols.py` reads one caller-supplied executable and checks exactly three tokens (`rpg.Art.Tier2`, `BuildStamp.txt`, `DEVELOPMENT BUILD`) in ASCII and UTF-16LE. Its five existing guard tests include synthetic byte-buffer checks for both encodings (reported in `W_A016_SHIPPING_BINARY_SYMBOL_REVIEW.md`); they do not broaden the scanned token roster or scan every package binary/dependency.

Current scan results:

| Executable | Bytes | SHA-256 | Three tokens |
|---|---:|---|---|
| `Saved/StagedBuilds_Shipping/Windows/OneBossFight/Binaries/Win64/OneBossFight-Win64-Shipping.exe` | 148,816,896 | `3bb85ac273f9b2fef6ee6d730e5cdfbc4cf2b156bef3330eef096ef2e298c0c9` | all absent; PASS |
| `C:/BenchTransfer/R6/OneBossFight_BenchKit/Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/OneBossFight-Win64-Shipping.exe` | 148,816,896 | same SHA-256 | all absent; PASS |

The two present executables are byte-identical by SHA-256, and the scanner's three-token test passes for both. This establishes only the checked tokens in these exact executable bytes; it does not certify DLLs, PDBs, UFS/IoStore contents, arbitrary development symbols, or source-to-binary/package provenance. `BUILD_INFO` and the R6 kit audit still lack a package/build identity chain as recorded in `Y046_Y049_RELEASE_READINESS_RECHECK.md`. The default scanner path under `Saved/StagedBuilds` currently has no Shipping-named executable; an explicit path was needed for both successful scans.

## Z040 — batch disposition

Z036 confirms the matrix's exact mapping issue persists; Z037 and Z038 retain the prior false-pass cases; Z039 yields a narrow positive scan for two identical Shipping executable files while leaving package-wide coverage and provenance open. These are static/tool and byte-scan results, not runtime or release acceptance. No source, test, matrix, package, or asset file was changed. `git diff --check` is the only workspace validation performed after documentation edits.
