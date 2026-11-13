# BP-41..45: bounded large-input parity tests (Queue BP, batch 9 of 10)

C (implementer), 2026-11-13. Validation per X-2295 and X-2312: **in-process only** on temp files, with **no wall-clock or memory thresholds** and **no behaviour change**. No tool `main()` and no subprocess was run.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

| Task | Result |
|---|---|
| BP-41 | **Scope:** pure cores that already run in-process (from BP-06, BP-26 and BP-31..35) and parse logs, mailboxes, source or JSON: `log_failures.find_failures`, `mailbox_stats.party_day_counts`, `list_todo_markers.marker_lines`, `check_line_endings.line_ending_counts`, `compare_framework_tokens.count`, `text_input.read_text_input` and `json_input.load_json` |
| BP-42 | **New `Scripts/Tools/test_bp_large_inputs.py`, 7 tests.** Each input is generated so the correct output is known **by construction**, at roughly 10–20 MB or 200,000 lines, and each core must match that output **exactly**: every Nth failure or marker line with its 1-based number, exact per-(party, date) counts, exact CRLF/LF/CR counts (3,000,000 / 2,000,000 / 1,000), exact token counts from a file, a 200,000-line BOM plus CRLF Markdown file decoding to the expected text, and a 100,000-card JSON document round-tripping equal |
| BP-43 | **Whole-file reading review:** every covered reader loads the whole file into memory, as the tools did before. At these sizes this is correct and fast (the suite ran in about 1.7 s, which is **observed, not asserted**). There is no demonstrated need to stream, so **no behaviour was changed**, per X-2312 |
| BP-44 | **Non-vacuity, by mutation in a temp copy:** an off-by-one in `find_failures` line numbering, and a dropped last match in `marker_lines`, give **2 failures** |
| BP-45 | This report |

**New file:** `Scripts/Tools/test_bp_large_inputs.py`. **No tool source changed.**

**Paths touched by the tests:** a `TemporaryDirectory`, holding files of up to about 20 MB that are deleted afterwards.

| Command (from `Scripts/Tools`, `BP_SMOKE_EXECUTE` unset) | Result |
|---|---|
| `python -m unittest test_bp_large_inputs` | Ran 7, OK |
| all 11 BP static and in-process suites | OK, 1 skipped (the execution class) |

## Limits

- **The bounds were chosen to keep the suite quick.** Behaviour on far larger inputs (for example 1 GB logs) was not exercised. Memory use scales with file size because the readers load whole files.
- **Only these cores were tested.** Tools whose parsing is still inside `main()` are not covered here, because running `main()` is not allowed.
