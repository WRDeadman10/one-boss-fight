# RESULT generation grader review (S121)

## Current interfaces and behavior

`Scripts/Tools/framework_results.py:13–48` exposes `parse(Path) -> (rows, diagnostics)` and `counter_delta(previous, current)`. Each RESULT row contains physical log line, inferred generation (`unknown` until a `generation=` field appears), and string fields. Generation context is advanced by `encounter_reset generation=N` or any proof row with `generation=N`; RESULT rows in a segment inherit the active context. Duplicate generation RESULTs warn. `counter_delta` subtracts shared numeric lifetime fields and returns `None` for the first row or malformed values.

The authoritative parser/grader must remain unchanged for this task. Current regression coverage in `Scripts/Tools/test_queue_c_tools.py:76–94` checks 3→5 and 4→6 lifetime deltas, an unknown first generation, generation 2 after reset, missing outcome, nonnumeric values, and duplicate RESULT warning. It does not certify that each generation has exactly one terminal RESULT or that deltas are associated with explicit segment boundaries.

Retained F8 restart logs provide the relevant shape: `ki150b/restart1/editor_raw.log:1869` emits generation-one `RESULT ... acceptedHits=1 attacks=2`; `:1872` emits `encounter_reset generation=2`; `:2276` emits the second RESULT with lifetime `acceptedHits=2 attacks=2`. Thus Gen2 interval deltas are 1 accepted hit and 0 attacks. RESULT itself omits generation, so attribution relies on ordered reset context. Similar restart2/restart3 logs have the same pattern.

## Separate opt-in generation-aware checker proposal

Add a new wrapper/check function alongside, not inside or in place of, the current parser. It should consume the existing ordered rows plus lifecycle markers and return a separate per-segment report:

1. Preserve raw RESULT fields, line numbers, existing diagnostics, and lifetime totals exactly.
2. Partition segments only at explicit lifecycle generation markers. Keep any rows before the first marker as `unknown`; do not silently call them generation 1 unless a generation-1 start marker exists in the input.
3. Require exactly one terminal RESULT per requested generation only when the caller supplies the expected generation set; otherwise report counts without inventing completeness expectations.
4. Compute interval deltas only between adjacent ordered RESULT rows whose generation boundary is unambiguous. First row has `delta=null`; malformed/missing shared counters also yield null plus a diagnostic. Do not clamp negative deltas: report counter regression as an error/candidate reset, preserving source values.
5. Explicit `generation=` on RESULT, if later emitted, takes precedence but must agree with active lifecycle context; mismatch is diagnostic, never silent reassignment.
6. Keep backward compatibility: old logs lacking generation markers remain parseable with unknown attribution; legacy outcome-only RESULT lines remain valid where current rules permit them.

Suggested fixture matrix for the future wrapper: explicit gen1 start, RESULT, reset to gen2, RESULT with cumulative counters (expected delta); old log with no markers (unknown); reset before first RESULT (first segment unknown, next gen2); duplicate terminal RESULT in one generation; missing expected generation; counter decrease; malformed numeric value; explicit RESULT generation conflicting with reset marker; outcome-only legacy row. This proposal adds no new required runtime token, changes no authoritative grader verdict, and is not implemented or tested here.

Reviewed `framework_results.py`, its current tests, the F8 restart log shape, and the existing lifetime-counter decision (`DECISIONS.md:1310`). No tests/Unreal run.
