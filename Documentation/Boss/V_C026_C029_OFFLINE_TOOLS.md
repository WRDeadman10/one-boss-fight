# V-C026–V-C029 — A5, determinism, and memory-soak offline tools

## V-C026 — A5 nightly pair run

`Scripts/RunA5ParityNightly.ps1` already schedules the 31 registered A5 pairs and writes an updating `summary.md`. `Scripts/Tools/test_a5_nightly_runner.py` now guards its 31 unique drivers, dry-run-by-default behavior, and no-overwrite evidence rule. The actual no-Editor dry-run prints 31 commands and leaves the specified output directory absent. This extends the existing S23 tool; it does not create a competing runner. Live pairs remain Lead-run.

## V-C027 — nightly report comparison

`Scripts/Tools/diff_a5_nightly_reports.py` compares two 31-row summary reports. It rejects a missing header, partial run (not all rows), duplicate drivers, malformed check counts, and PASS rows without both arm counts. It reports new failures, fixed failures, and per-arm count changes. A matching report is not proof of matching gameplay values; the summary contains per-arm check counts and verdicts, not full receipts.

## V-C028 — determinism comparator edges

`compare_determinism_runs.py` already requires six complete route/repeat arms, equal seed/schedule, per-run metadata consistency, and matching input/event traces. It now rejects a non-object row without throwing an exception; the regression fixture confirms a malformed arm is both reported and treated as missing. The evidence boundary in `U_C07_DETERMINISM_LEAD_RUN.md` remains: this only compares observed tracker/input signals, not every game subsystem or bitwise determinism.

## V-C029 — memory-soak interpretation

`Scripts/Tools/summarize_memory_soak.py` reads the two retained Editor logs without importing Unreal. It requires each arm's `PASS 50/50`, all 101 samples, one baseline and exactly 50 pre/post-reset rows, route consistency, pre-sample GC markers, cycle identities 1–50, actor census, and private-memory measurements. It reports actor min/max and first-to-last post-GC private-memory delta. An incomplete arm exits 2. A positive or monotonic delta is a leak candidate, not a leak conclusion; allocator/cache retention and observation noise still require engineering diagnosis. The current C-915 20-reset figures remain a watch item until the Lead supplies both 50-reset logs.

Tests use synthetic fixtures only; no memory soak, PIE, Editor, or live parity pair was run by Codex.
