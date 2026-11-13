# BP-31..35: test coverage for previously untested tools (Queue BP, batch 7 of 10)

C (implementer), 2026-11-13. Validation per X-2295: **in-process only**. No tool `main()` and no subprocess was run.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

| Task | Result |
|---|---|
| BP-31 | **Inventory:** 11 of the 91 allowlisted tools are referenced by no test file, not counting the BP inventory-style suites (smoke, exit-code snapshot, missing-input guard, static contract): `check_headers_selfcontained`, `check_line_endings`, `check_test_plan_ids`, `compare_framework_tokens`, `diff_manifests`, `list_cvars`, `list_todo_markers`, `log_failures`, `mailbox_stats`, `new_profile_field_scaffold` and `source_metrics`. Only 3 expose a helper; the other 8 keep all their logic in `main()`, which X-2295 does not allow me to execute |
| BP-32 | **Characterization tests** for the 3 existing helpers: `check_headers_selfcontained.inspect` (all 4 suspect kinds plus a clean header), `compare_framework_tokens.count`, and `diff_manifests.load` (comments, blank lines, `*` binary marker, lowercase digests, and a named `path:line` error) |
| BP-33 | **Behaviour-preserving refactor** of the two smallest main-only tools, both already touched in BP-03 and BP-11. `log_failures.find_failures(text)` and `mailbox_stats.party_day_counts(text)` now hold the exact expressions `main()` used inline, and `main()` calls them. Tests compare each against the former inline expression on fixtures, so equivalence is shown in-process. Both tools are still PROVEN, and their exit-code snapshot is unchanged |
| BP-34 | **X-2308 rework:** the remaining 6 main-only tools got the same verbatim core extraction plus an in-process test each. The cores are `check_line_endings.line_ending_counts` and `is_mixed`, `check_test_plan_ids.build_ids`, `list_cvars.registrations`, `list_todo_markers.marker_lines`, `source_metrics.file_metrics` and `new_profile_field_scaffold.checklist_lines`. Each `main()` now calls its core; argument parsing, printing and return codes are unchanged. All 6 are still PROVEN, and the exit-code snapshot is unchanged. Earlier uncommitted edits in these files were preserved |
| BP-35 | This report |

**Changed files:** `Scripts/Tools/log_failures.py`, `mailbox_stats.py`, `check_line_endings.py`, `check_test_plan_ids.py`, `list_cvars.py`, `list_todo_markers.py`, `source_metrics.py` and `new_profile_field_scaffold.py` (cores extracted). **New:** `Scripts/Tools/test_bp_core_functions.py`, now 11 tests (5, plus 6 for X-2308).

**Paths touched by the tests:** a `TemporaryDirectory` and in-memory strings. Five tool modules are imported. No `main()` is called.

| Command (from `Scripts/Tools`, `BP_SMOKE_EXECUTE` unset) | Result |
|---|---|
| `python -m unittest test_bp_core_functions` | Ran 11, OK |
| all 8 BP static and in-process suites | OK, 1 skipped (the execution class) |

**Red check:** with the pre-refactor files, the 2 BP-33 tests and the 6 BP-34 tests error (the functions are missing). The 3 BP-32 tests are characterization of unchanged code, so no red check applies to them.

## Limits

- **BP-32 pins current behaviour only;** it does not judge it correct.
- **Output formatting** inside the refactored `main()` functions (the print lines) is untested, because executing it is not allowed.

## Coverage status against the queue wording (X-2308)

**Every one of the 11 previously untested tools is now referenced by at least one in-process test,** which meets the queue's acceptance line.

**What the queue's "black-box happy-path and failure-path test" wording would need, and why it is not met under X-2295:** running each tool's `main()` (argument parsing, printing and exit codes). That is not allowed, so for all 11 tools the following stay untested:
- the argparse wiring;
- the exact printed output lines;
- the end-to-end exit code.

Static guards partly cover them: `test_bp_cli_smoke` (the static `--help` contract), `test_bp_exit_codes` (the exit-code snapshot) and `test_bp_missing_inputs` (pre-read guards). **Black-box tests remain blocked** until you approve specific commands.
