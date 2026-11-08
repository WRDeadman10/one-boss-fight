# Queue AD-C21–C25 — test inventory, authoring coverage, and native rerun

Date: 2026-11-07. Codex source and documentation audit; no Unreal Editor, build, cook, package, or PIE run.

## AD-C21 — focused player discovery

Ran `python Scripts/Tools/discover_focused_player_tests.py` against the current source. It reports **19 methods in 5 groups**: air_attack 3, default_route 5, dlss_player_settings 4, guard_counter 3, and optional_presentation 4. The discovery script parses only the five listed Python contract files with `ast`; it neither imports nor executes those tests and does not enumerate C++ automation.

## AD-C22 — montage segment helper test coverage

`Source/OneBossFight/Tests/RPGMontageUtilsTests.cpp` has one editor automation, `OneBossFight.Authoring.MontageSegmentRange`. It covers null montage, the constructor-created `DefaultSlot` with an empty segment array, a real source sequence, negative start, empty range, end beyond source length, rejected-call segment/package preservation, successful range update, recomputed montage length, montage dirty state, and unchanged source package dirty state. It does not directly exercise a montage with zero slot tracks, a null segment animation, non-finite inputs, multiple slots/segments, or selection of a named/non-default slot. `SetMontageSegmentRange` uses slot 0 / segment 0; these absent cases are coverage limits, not demonstrated runtime defects. The source already rejects non-finite times and missing slot/segment/source animation.

## AD-C23 — offline suite timing wrapper

`run_offline_suite_timed.py` passes the configured limit to `subprocess.run`, returns 2 on `TimeoutExpired`, preserves a nonzero child return code, prints timing and PASS only after a successful child exit under budget, and inherits child stdout/stderr. `KeyboardInterrupt` is intentionally allowed to propagate, so the wrapper does not translate Ctrl+C into success. Added focused fixtures for interrupt propagation and inherited child output; together with the existing timeout and nonzero fixtures, `python -m unittest Scripts.Tools.test_offline_suite_timing_runner -v` passed **5/5**. The interrupt fixture verifies wrapper behavior, not OS-level child termination/reaping after Ctrl+C; only subprocess timeout/cleanup has a real-child fixture elsewhere (`test_process_test_support.py`).

## AD-C24 — native automation count chronology

The mailbox receipts record distinct successive Lead builds: BUILD-241 through BUILD-246 each **482/482**; BUILD-247 **483/483**; BUILD-248 **484/484**, with Shipping compile. BUILD-246 separately records CookCoverage Success and Lead importer 7/7. The build receipts are not one cumulative suite run, and CookCoverage/importer/offline counts are different scopes. The one-count increases are visible between receipts, but the mailbox summaries do not identify the exact newly counted native test for each increment; no attribution is inferred. Sources: C-963, C-966, C-969, C-970, C-972, C-973, C-975, C-978 in `Documentation/TEAM_MAILBOX.md`.

## AD-C25 — Lead rerun checklist for next source revision

1. Confirm the editor is closed and no `ENGINE_LOCK.json`/active editor session conflicts with the build; record the exact branch/commit and source-tree identity before building.
2. Build the intended Development Editor target and record the new BUILD ID, toolchain/target, source identity, build log path, and exit status. Keep Shipping compile as a separate result.
3. Run the native suite on that build. Capture the exact automation filter/command, raw output, executed/passed/failed/skipped counts, and final process status. Include `OneBossFight.Authoring.MontageSegmentRange` explicitly so its one-test presence is distinguishable from the overall suite count.
4. Report CookCoverage, importer, offline Python suite, and native automation as separate checks with their own commands and raw evidence. Do not reuse BUILD-246/247/248 results as proof for the new revision.
5. If a failure occurs, preserve the first failing test/log and source identity; do not label a partially executed suite GREEN.

No claim is made here that the current source revision has been built or that Lead has run the new helper test after BUILD-248.
