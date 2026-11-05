# Queue V C091–C095 handover and evidence review

Date: 2026-11-06. Scope: offline documentation, source/validator review, ledger evidence paths, and offline suite timing. No Unreal, Editor, build, package, commit, or push was run by Codex.

## C091 — Codex handover

- Queue V is the active 200-task plan; Codex works in batches of five, posts one concise mailbox update per batch, then proceeds without waiting for review. Review rejections are hotfixes to take at the next cycle.
- C086–C090 is closed as reported in X-1309. Round 6 evidence remains absent and owner approval gates any settings change. Queue W was subsequently posted by Claude in C-930; after V-C091–V-C100, begin W-C001.
- BUILD-232 is Claude-reported GREEN 478/478 and committed reviewed state `440cf09` (C-929/C-930). Codex verified the two reported native-test hotfixes against source; no test/build was rerun for that check.
- Do not commit/push. Claude owns Editor/build/PIE and native-suite runs. Keep claims tied to retained logs and preserve uncertainty.
- Active C091–C095 review findings are below. C096 (bench-kit dry-run) is lead-run; do not claim a local GPU or runtime result.

## C092 — consistency pass

The C-929 BUILD-232 verdict agrees across the current TEST_PLAN index/receipt, DECISIONS C-929 entry, mailbox C-929, and PROJECT_STATE build note. TEST_PLAN contains both the indexed C086–C090 section and a detailed BUILD-232 row; the two agree on GREEN 478/478 and attribution to Claude. Queue W was missing at the time of X-1309 but exists now and is created by Claude per C-930. PROJECT_STATE has historical Queue V snapshots and duplicated batch-6 summaries; they are dated/status-labeled historical notes, not competing current batch status. No substantive cross-file contradiction found in the checked current build/queue status.

## C093 — offline suite timing

Measured `python -m unittest discover -s Scripts/Tools`: 345 tests, 1 skipped, 0 failures. Wall time was 4.27 seconds in the test runner; PowerShell `Measure-Command` measured 4.57 seconds, below the 10-second target. This is an offline host measurement, not an Unreal performance measurement.

## C094 — second review of Antigravity tool/source output

Reviewed V-A054's coverage-matrix report and validator. The artifact presents 82/82 requirements as mapped to native automation test suites, but `test_requirements_coverage_matrix.py` only validates row count/IDs, nonempty fields, allowed enums, and existence of `SourceFile`. It never checks that `PrimaryAutomationTest` corresponds to a registered automation test in that source file. Thus the validator does not enforce the claimed mapping; the report needs a scope qualification or a stronger validator plus evidence. This is a validator coverage gap, not proof that any particular mapping is false. No AG-owned file changed.

## C095 — Antigravity ledger evidence cross-check

- Ledger parses as v3.37, 82 canonical entries, census 80 WITNESSED / 2 PARTIAL / 0 NOT YET. Its four newest integration witnesses (F1-PARRY-SLOWMO, H8-REBIND-RETRY, U-C05-MEMORY-SOAK, W1-H10-TIER1-NIAGARA) have WITNESSED status and each referenced evidence directory exists; their declared builds are BUILD-227/228, consistent with the row summaries and TEST_PLAN references.
- The ledger's own `test_witness_status_v3.py` is stale: it hard-codes census 75/7/0 while JSON and markdown now state 80/2/0. Direct run fails at `Expected 40 WITNESSED, got 80` (the assertion is 75; its error text is stale too).
- A separately invoked citation-verbatim check also finds a stale line citation at `BOSS-AWR-005`, `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:211`: the quoted `same floor is eligible` assertion is no longer at that line. The requirements-integrity check passes (82 IDs, 61 delta rows); full citation and formatting checks were not established because the citation check stops at this failure. Ledger contents were not edited.

## C094/C095 disposition

These are review findings for Antigravity/Claude to disposition. The report does not modify the AG matrix, validator, ledger, or their evidence. Next: C096–C100, then Claude's Queue W at W-C001.

## C096 — bench-kit dry-run evidence

The Round 6 bench-kit folder exists at `C:/BenchTransfer/R6/OneBossFight_BenchKit`, but the current repository checker reports FAIL: it lacks `Scripts/PackagedRunLog.psm1`, `Scripts/Tools/check_bench_kit.py`, and `BUILD_INFO.txt` with generated package ID/executable SHA-256. The folder is a 7,540,732,206-byte Development-only kit. This is a static kit validation, not a game dry-run; no GPU or runtime claim is made. A Lead/owner rebuild is needed before its kit can pass the repository's current checks.

## C097 — owner engineering summary

BUILD-232 gives the team a fresh 478/478 native automation baseline, and Claude reports all five default-off gameplay/presentation parity pairs pass. The measured offline tool suite completes in under five seconds. These are strong engineering checks, while release readiness is still open: the returned Round 6 performance bundle is absent, the current Round 6 kit fails the repository's kit-integrity checker, selected-route packaged/visual recovery evidence still needs owner runs, and Tier 2 art still needs owner review. Keep defaults and the delayed legacy-retirement policy unchanged until those gates have real evidence and the owner approves the image quality.

## C098 — current residual risks

| Risk | Current evidence | Remaining gate |
|---|---|---|
| Performance target | R5 DLSS Performance reached 38.1 average / 31.9 ms p99 on RTX 3060; still below 60 FPS and above 16.67 ms. | Round 6 return, owner image-quality approval, valid kit, then apply only approved settings and rerun confirmation/parity. |
| Kit provenance | R6 kit folder exists but current checker fails required support files/build stamp. | Lead rebuild/repair and validate current package provenance before physical run. |
| Selected-route release | 31 A5 parity drivers accepted; Build 232 green. | Packaged first-caller/selector proof, cook manifest, and refusal visuals remain separate release gates. |
| Presentation/art | Tier 1 wiring is reviewed; Tier 2 hooks and owner review package exist. | Owner reviews look-changing Tier 2 option; performance and visual cost are unmeasured on accepted hardware. |
| Ledger / coverage assurance | AG census says 80/2/0; requirements integrity passes. | Fix stale census assertions/citation line and strengthen V-A054 test-name verification; keep these as review findings until AG disposition. |

This register is a snapshot and does not close any release gate.

## C099/C100 — lane close-out and continuation

Queue V C091–C100 is closed as a work cycle with C096 marked FAIL/pending Lead kit repair and no GPU claim. C097/C098 summaries are above. C-930 posted Queue W; W-C001–W-C005 are now complete, and the next batch is W-C006–W-C010, with one mailbox post per batch, hotfixes first, and no wait between batches.

## Queue W W-C001–W-C005 — Round 6 intake prep

- W-C001 assembled a temporary ZIP from the retained Round 5 return layout (102 entries) plus a synthetic 13-row Phase 1 receipt carrying all three new telemetry fields. Intake emitted three mode rows with zero exceptions. The ZIP was temporary and removed; synthetic values are not evidence.
- W-C002 found and fixed a real missing-witness crash in `round6_benchmark_report.validate`: it now records the missing active-mode witness as a validation error rather than indexing a missing key. Added missing-upscaler and missing-mode-witness regressions. Focused tests: 9/9.
- W-C003 filled V-A021 predicted ranges for L1–L3, leaving measured savings blank.
- W-C004 prepared the three-choice owner decision sheet with historical R5 context and explicit Round 6 evidence gates; no choice is made.
- W-C005 batch report is posted as X-1311. Continue W-C006–W-C010 without waiting for review.

## Queue W W-C006–W-C010 — A7-B startup preparation

- W-C006: removed the explicit `bUseLegacyStartup=True` line from DefaultGame.ini; the UPROPERTY initializer remains true, so absence of the key preserves today's fallback. Existing automation now explicitly names and asserts that absent-key default. No default-route flip or data caller was introduced.
- W-C007: startup now logs why the data route or legacy no-selection route was chosen. Automation snapshot assertions cover legacy, disabled, and selected routes. W-C008 adds the paired future replacement test matrix while retaining current legacy controls; Claude build/native run remains pending.
- W-C009 records all 31 exact registered A5 parity drivers, fresh-process arm expectations, acceptance rules, and owner/Lead gates in `W_C009_A7B_31_PAIR_PARITY_PLAN.md`.
- W-C010 batch update is posted as X-1312 with SOURCE CHANGED. Next is W-C011–W-C015, without waiting for the build review.

## Queue W W-C011–W-C015 — dead-code and warning review

Removed only the two private no-caller helpers; retained the two public APIs because external callers are not ruled out. The build log has only the Visual Studio toolchain warning, with no project deprecation warning. V-A039's 14 assets remain untouched pending explicit owner authorization. Added a source/API shape regression test (2/2). Report: `W_C011_C014_DEAD_CODE_AND_WARNING_REVIEW.md`; W-C011 remains partial pending Lead build/API disposition. X-1313 posted; next W-C016–W-C020.
