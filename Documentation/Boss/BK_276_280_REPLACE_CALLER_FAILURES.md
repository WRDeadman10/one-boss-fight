# BK-276..280: atomic_write_text (replace) callers: prior destination, output ordering, injected replace failure

Assigned by X-2124 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 2 of 10. New files only:
- `Scripts/Tools/test_bk276_280_replace_caller_failures.py`
- this report

**No source change.** No false success was found.

**Method:**
- Each caller runs as a **real subprocess** on synthetic fixtures in a throwaway OS temp dir.
- The fixtures are: a stub validator with only `SCHEMAS` and `validate_log_file`, one `editor_raw.log`, a `Source/a.cpp`, and a `{}` receipt.
- A small `runpy` wrapper replaces `os.replace` with `PermissionError(13)` **before** the script runs. So the real atomic_io path executes (temp written and fsynced, publication refused, temp cleaned), not a mocked `atomic_write_text`.
- No production data, lock, asset, Unreal, build or PIE.

## BK-276: prior-destination and ordering contract (source)

| Caller | Prior destination | Output order | Publication claim line |
|---|---|---|---|
| `evidence_summary.py` | replaced (`os.replace`) | build CSV in memory → write → print | `logs=N output=…` after the write |
| `make_source_manifest.py` | replaced | hash rows → write → print | `files=N manifest=…` after the write |
| `token_coverage.py` | replaced | **summary printed first** → write → print | `sample_manifest=…` after the write |
| `summarize_encounter_cost.py` | replaced | normal path: write → print. Read-failure path: print (INCONCLUSIVE) → write (O3, BK-271) | JSON report after the write |
| `summarize_packaged_metrics.py` | replaced | write → print | JSON report after the write |

None of the five promises to preserve the destination's metadata (see BK-264) or to keep a backup.

## BK-277 / BK-278: injected replace failure, all 5 callers runnable

| Caller | Exit | stdout | stderr | Destination | Temp |
|---|---|---|---|---|---|
| `evidence_summary.py` | 1 | empty | traceback, `PermissionError: [Errno 13] synthetic replace failure` | **old bytes intact** | none |
| `make_source_manifest.py` | 1 | empty | same | intact | none |
| `token_coverage.py` | 1 | the pre-write summary (`logs_scanned=1 schemas=1 observed=1`, ...) with **no** `sample_manifest=` line | same | intact | none |
| `summarize_encounter_cost.py` | 1 | empty | same | intact | none |
| `summarize_packaged_metrics.py` | 1 | empty | same | intact | none |

All five callers could be run on synthetic fixtures, so there were **no non-runnable callers**. The success path was also checked: the destination is replaced, the claim line is present and no temp is left. The summarize scripts exit 2 there, because a `{}` receipt is INCONCLUSIVE by design.

## BK-279: false-success check

**No concrete false success; no fix.**
- The publication claim lines are printed only after `atomic_write_text` returns. This is checked statically and at runtime.
- `token_coverage.py` prints its coverage summary before the write. That summary describes the scan, not the manifest, and the manifest claim line is absent on failure.
- **Note:** `token_coverage.py` exit 1 is overloaded: it means "observed without schema" and also an uncaught write failure. Only stderr (traceback) and the missing `sample_manifest=` line tell them apart. This is non-blocking.

## BK-280: tests

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk276_280_replace_caller_failures.py -v` → **`Ran 4 tests ... OK`**; repeated 5 times, 5/5.

| Class | Test |
|---|---|
| `Bk276OrderingContracts` | `test_print_after_write` (static) |
| `Bk277InjectedReplaceFailure` | `test_old_bytes_intact_exit_1_traceback_no_temp` (5 subtests) |
| `Bk279NoFalseSuccessOnStdout` | `test_publication_lines_absent_after_failure` and `test_success_path_publishes_and_claims` (5 subtests each) |

## Limits

- Windows host only. The injected fault is a `PermissionError` at `os.replace`; other fault points are covered by the BK-238 and BK-241 atomic_io suites.
- The fixtures are minimal stubs. Validator semantics and real receipts were not exercised. Only failure semantics are in scope.
