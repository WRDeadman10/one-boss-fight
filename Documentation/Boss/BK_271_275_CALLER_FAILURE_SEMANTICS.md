# BK-271..275: atomic_io caller failure semantics (O1-O4)

Assigned by X-2122 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 1 of 10.

New files:
- `Scripts/Tools/test_bk271_275_caller_failure_semantics.py`
- this report

**SOURCE CHANGED, O1 only:** `Scripts/Tools/inventory_editor_asset_writers.py` and `Scripts/Tools/audit_editor_save_safety.py`. O2-O4 needed no change.

The O1 callers ran as subprocesses with `--editor`/`--output` inside throwaway OS temp dirs; O2-O4 ran `main()` in-process with temp paths or injected write faults. No project output, lock, pack, asset, Unreal, build or PIE.

## BK-271: caller × error map (source evidence)

None of the 9 callers catches `PermissionError` or a generic `OSError` from atomic_io. Any such error is an uncaught traceback on stderr with **exit 1**. The rows below differ only where a caller handles `FileExistsError` or orders print and write differently.

| Caller (call site) | Destination exists | Parent component is a file | `PermissionError` / `OSError` | stdout on failure |
|---|---|---|---|---|
| `inventory_editor_asset_writers.py:53` (create) | `REFUSED existing inventory output: <path>`, exit 2 | **fixed**: `REFUSED cannot create inventory output: <path>: <error>`, exit 2 | traceback, exit 1 | only the REFUSED line |
| `audit_editor_save_safety.py:68` (create) | `REFUSED existing audit output`, exit 2 | **fixed**, same as above, exit 2 | traceback, exit 1 | only the REFUSED line (the counts line is not reached) |
| `new_rule_scaffold.py:69/107` (create ×3) | preflight `:99` lists them on stderr, exit 2 | traceback, exit 1 | traceback, exit 1 | the paths published before the failure |
| `evidence_pack.py:85,90,92` (create) | preflight refuses before any copy, exit 2 (BK-231) | traceback, exit 1 | traceback, exit 1 | — |
| `evidence_summary.py:83` (replace) | replaced | traceback, exit 1 | traceback, exit 1 | none (the print comes after the write) |
| `make_source_manifest.py:23` (replace) | replaced | traceback, exit 1 | traceback, exit 1 | none |
| `token_coverage.py:69` (replace) | replaced | traceback, exit 1 | traceback, exit 1 | the coverage summary (`:48-55`) is printed **before** the write (`:69`); on a write failure stdout holds the summary but **not** the `sample_manifest=` line, and the exit is 1. It is not a success claim. |
| `summarize_encounter_cost.py:120,125` (replace) | replaced | traceback, exit 1 | traceback, exit 1 | normal path: none. **Read-failure path: the INCONCLUSIVE report is printed before the write (O3).** |
| `summarize_packaged_metrics.py:217` (replace) | replaced | traceback, exit 1 | traceback, exit 1 | none |

## Dispositions

| Id | Evidence | Disposition |
|---|---|---|
| **O1** | Subprocess: a parent component that is a file printed `REFUSED existing ... output: <path>` (exit 2) although the path does not exist. That is a false claim against the help text, "existing paths are refused". | **Fixed narrowly** in both callers. "existing" is printed only when `os.path.lexists(output)`; otherwise `REFUSED cannot create <word> output: <path>: <error>`. Exit 2, nothing written, and the existing-destination message is unchanged. The message does not speculate about which filesystem condition caused `FileExistsError`. |
| **O2** | Injected failure on create #2 and #3: 1 or 2 survivors stay on disk; only the published paths are printed; "Scaffold created" is **not** printed; the exception propagates (exit 1). A rerun refuses with exit 2 and lists exactly the survivors. | **No fix.** The CLI does not promise an atomic set: the help says only "existing target files are refused", and the source contains no all-or-none, rollback or transaction wording (tested). The real contract is per-file exclusive creation with a refusing rerun; recovery is manual removal of the survivors. |
| **O3** | `summarize_encounter_cost` read-failure path with a failing write: stdout already holds the report, but it is an **INCONCLUSIVE** report and the process exits 1. | **No fix.** There is no false success: the printed status is non-PASS and the exit is non-zero. |
| **O4** | Both summarize scripts with a PASS report and a failing write, injected or real (parent is a file): stdout is empty and the exit is 1 (traceback), not 0. | **No fix.** There is no false success; the exit code differs from the documented 0/2 but is non-zero. |

## BK-275: tests and commands

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk271_275_caller_failure_semantics.py -v` → **`Ran 10 tests ... OK`**.

| Class | Tests |
|---|---|
| `Bk272O1ExistingVsParentIsFile` (3) | `test_existing_destination_is_refused_as_existing`, `test_parent_component_that_is_a_file_is_not_called_existing`, `test_new_destination_still_written` |
| `Bk273O2ScaffoldPartialCreate` (3) | `test_failure_on_create_2_and_3_leaves_survivors_and_rerun_refuses`, `test_contract_text_does_not_promise_an_atomic_set`, `test_clean_run_creates_all_three` |
| `Bk274O3O4ReportWriteFailures` (4) | `test_pass_report_with_failing_write_is_never_a_success`, `test_o3_read_failure_path_prints_before_the_write`, `test_real_write_failure_under_temp_paths`, `test_successful_write_then_print` |

- **Before and after:** against the copies of the two O1 callers saved before the fix, `test_parent_component_that_is_a_file_is_not_called_existing` fails for both (`REFUSED existing ...`). The other 9 tests cover unchanged behavior.
- Related suites still OK: `test_inventory_editor_asset_writers.py`, `test_audit_editor_save_safety.py`, BK-236, BK-246 (the warning-control scan included).
- `py_compile` OK.

## Limits

- O2-O4 run in-process, with `summarize()` replaced by a fixed PASS report to isolate write/print ordering; real receipts were not used.
- **Host:** Windows only. Parent-is-file raises `FileExistsError` here (`NotADirectoryError` is accepted for POSIX but unverified).
- **Incident (own artifact, removed):** an early bash probe with an MSYS-mangled `/tmp` path made `inventory_editor_asset_writers.py` write `C:\tmp\tmp.hoMczNQLkI\blocker\out.md`. I inspected it (only the generated inventory header) and deleted it. All tests use Windows paths from Python.
