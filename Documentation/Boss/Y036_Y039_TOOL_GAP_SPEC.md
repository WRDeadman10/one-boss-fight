# Queue Y Y036–Y039 — comparator, runner, and matrix gap specification

Date: 2026-11-06. Read-only review of current tool and test source plus prior audit counterexamples. This document specifies changes/fixtures; it does not apply them or run tests.

## Y036 — bind G044 legacy values to cited source tokens

`compare_manifest_to_legacy_defaults.py` checks that the cited source line still equals the table's saved `excerpt`, then compares manifest value to table `legacy_value`. It does not extract/validate the numeric literal in that excerpt. The existing test file covers ordinary match/mismatch and tuning approvals but not this binding gap.

**Fixture specification:** create a temporary source line `float MaxHealth = 2000.f;`, a comparable default rule citing that exact line but supplying `legacy_value: 1800.0`, and a manifest field `1800.0`. The checker must reject the stale/inconsistent table/source binding (clear validation error or MISMATCH), never MATCH. Positive control uses 2000.0 in source/table/manifest and matches. Preserve legitimate expression/array/cited-token formats via explicit parsing or an explicit reviewed nonnumeric disposition; do not silently regex the first number in arbitrary prose. Keep owner-approved intentional tuning separate from the baseline source value. Existing synthetic counterexample details: `X_C016_C019_G044_PARITY_AUDIT.md`.

## Y037 — compare health as a structured observable

`compare_encounter_parity.py` can compare check-message numbers when the observable has no typed `comparison`; when a typed timing comparator is present, the messages are not compared. Current `test_typed_observable_precedes_check_message_tokens` documents equal PASS statuses and timing 0.400/0.427 while check messages say health 2000/1500 and accepts no issue. The existing health-text checks cover a different message-only branch.

**Fixture specification:** add a structured health metric (for example, `boss_health_before`/`boss_health_after`, with units or explicit integer semantics) to the observation schema. Construct two receipts whose typed timing values remain within tolerance and statuses remain PASS but whose health metric differs (2000 vs 1500); comparator must report the health mismatch independently of timing. Equal metric positive control passes. Keep prose comparison for explicitly enumerated state tokens only; avoid comparing unrelated log text. See the X-C019 counterexample in `X_C016_C019_G044_PARITY_AUDIT.md`.

## Y038 — retain failed benchmark logs per run

`Scripts/RunBenchmark.ps1` waits for the process and throws on timeout/nonzero exit before it locates benchmark output and copies the shared, rotating `OneBossFight.log` to a per-run folder. Success-only copy occurs later. A timeout, crash, or nonzero return can therefore leave no immutable run-local log; a later launch can rotate the shared source.

**Fixture specification:** create a unique run directory before launch; use an isolated per-run log destination where supported, or snapshot/copy the process log from a `finally` path before any subsequent launch can rotate it. Fake-process tests cover (1) timeout/owned PID-tree termination with partial log preserved, (2) nonzero exit with log preserved and failure status, and (3) success with log/result association. Each asserts distinct per-run log path/hash, no overwrite of prior evidence, and correct return/fail verdict. Preserve outputs when result JSON is missing. Existing source review: `X_C021_C024_R6_KIT_AUDIT.md`; no PowerShell/source fixture was added.

## Y039 — matrix registration and source-path mapping

`requirements_automation_coverage_matrix.csv` has 82 IDs matching the witness ledger; its validator checks row count/ID set, nonempty cells, source path existence, and enum membership. It does not assert that `PrimaryAutomationTest` is actually registered in `SourceFile`, nor that an existing but unrelated source file is correct. The prior static scan found 5/82 exact name/source matches and 77 declared registration names absent from the scanned native registration literals; absence from the scan does not establish conceptual requirement coverage is missing.

**Disposition:** treat 77 mappings as UNKNOWN/UNVERIFIED until their owners either map to real exact automation registrations and the containing source files, or deliberately change the CSV contract to documented suite-level mapping with an explicit evidence field. Validator fixture requirements: (a) known exact macro registration in declared source passes; (b) fabricated identifier fails; (c) identifier registered only in a different source fails; (d) registration comments/string literals do not count; (e) a declared suite-level mapping is accepted only with the separate schema/evidence contract. Do not rewrite owner matrix rows in this audit. See `X_C011_C014_REQUIREMENTS_MATRIX_REVIEW.md`.

## Y040 — batch disposition

All four gaps remain unfixed and untested in this pass. These are concrete implementation/fixture specifications for their owning tool lanes, not proof that the live/package acceptance cases pass. No source, test, package, or runtime changes. Continue Queue Y Y041–Y045.
