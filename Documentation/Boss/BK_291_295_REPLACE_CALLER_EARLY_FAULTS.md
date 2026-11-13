# BK-291..295: replace callers under early temp-stage faults (fsync, fdopen)

Assigned by X-2132 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 5 of 10. New files only:
- `Scripts/Tools/test_bk291_295_replace_caller_early_faults.py`
- this report

**No source change.** No behavioral divergence was found.

**Method:**
- The five `atomic_write_text` callers run as **real subprocesses** on the BK-276 synthetic fixtures: a stub validator, one log, `Source/a.cpp`, a `{}` receipt.
- A `runpy` wrapper installs the fault before the script runs:
  - `os.fsync` raises `PermissionError(13)`;
  - or `os.fdopen` raises `OSError` after `_temporary_path` has created the temp descriptor.
- In fdopen mode the wrapper records every descriptor it was handed. At interpreter exit (`atexit`, which runs after an uncaught traceback) it prints `FDCHECK fd=N OPEN|closed`, using `os.fstat`.
- No production data, lock, pack, asset, Unreal, build or PIE.

## BK-291 / BK-292 results: identical for all five callers

| Fault | Exit | stderr | stdout | Prior destination | Temp | Descriptor |
|---|---|---|---|---|---|---|
| `os.fsync` → `PermissionError` | 1 | traceback, `PermissionError: [Errno 13] synthetic fsync failure` | empty (`token_coverage`: scan summary only) | **intact** (old bytes) | removed | n/a: the stream's `with` block closed it |
| `os.fdopen` → `OSError` | 1 | traceback, `OSError: synthetic fdopen failure` | same | **intact** | removed | **exactly 1 fd handed, `closed`** at exit (T4 `_open_owned`) |

The callers covered are `evidence_summary.py`, `make_source_manifest.py`, `token_coverage.py`, `summarize_encounter_cost.py` and `summarize_packaged_metrics.py`.

## BK-293: success claims

- **No publication claim** appears after any fault. `logs=`, `files=` and `sample_manifest=` are absent, and the summarize scripts print nothing.
- Statically, every claim line comes after the `atomic_write_text` call.
- `token_coverage.py` prints its scan summary (`logs_scanned=… schemas=… observed=…`, never-observed/unknown lists) **before** the write. That summary describes the log scan, not the manifest. The only publication marker is `sample_manifest=…`, which is printed after the write. Both properties are pinned by tests.

## BK-294: atomic_io contract vs observed behavior

| Contract statement (`atomic_io.py` docstring) | Observed for the callers |
|---|---|
| fsync/replace failure → the ORIGINAL exception propagates | yes: the injected `PermissionError` or `OSError` is what the traceback shows |
| old content kept for `atomic_write_*` | yes: `OLD` bytes intact in all 10 runs |
| temp sibling removed | yes: 0 `.tmp` files |
| fdopen failure → the descriptor is closed before cleanup (T4) | yes: `FDCHECK ... closed` |

**No divergence.** One **documentation gap only, non-blocking**: the module docstring does not yet mention the later J1 behavior (bounded temp creation with the realpath fallback, BK-251) or the M1 behavior (read-only source mode kept writable and restored after publication, BK-261). Both are documented in their batch reports; the docstring was not edited.

## BK-295: tests

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk291_295_replace_caller_early_faults.py -v` → **`Ran 5 tests ... OK`**; repeated 3 times, 3/3.

| Class | Test |
|---|---|
| `Bk291FsyncFailure` | `test_fsync_permission_error_all_five` (5 subtests) |
| `Bk292FdopenFailure` | `test_fdopen_failure_closes_descriptor_and_cleans_all_five` (5 subtests) |
| `Bk293ClaimMarkers` | `test_claim_lines_are_printed_after_the_write_in_source`, `test_token_coverage_summary_precedes_write_and_is_not_a_publication_marker` |
| `Bk294ContractParity` | `test_contract_text_covers_the_observed_guarantees` |

## Limits

- Windows host only.
- The fd check uses `os.fstat` at exit; a recycled fd number could in theory mask a leak, but no other files are opened after the failure.
- The fixtures are stubs.
