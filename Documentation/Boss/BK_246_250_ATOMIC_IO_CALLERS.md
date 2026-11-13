# BK-246..250: atomic_io.py callers after the hotfix, and exclusive-create concurrency

Assigned by X-2100 (lead Codex) to C (implementer), 2026-11-12. This is batch 16 of 20. New files only:
- `Scripts/Tools/test_bk246_250_atomic_io_callers.py`
- this report

No source was changed. No production caller was run; each caller was inspected from source, and the nine-caller inventory was cross-checked with the synthetic AST test. Tests run in throwaway OS temp directories only.

## BK-246: caller inventory and warning filters

| Semantics | Caller : call site |
|---|---|
| Replace (`atomic_write_text`) | `evidence_summary.py:83`, `make_source_manifest.py:23`, `summarize_encounter_cost.py:120,125`, `summarize_packaged_metrics.py:217`, `token_coverage.py:69` |
| Create (`atomic_create_text` / `_copy`) | `audit_editor_save_safety.py:68`, `evidence_pack.py:85,90,92`, `inventory_editor_asset_writers.py:53`, `new_rule_scaffold.py:69` (called from `:107`) |

**Warning filters:**
- No non-test `.py`, `.ps1`, `.bat` or `.cmd` under `Scripts/` uses `simplefilter`, `filterwarnings`, `catch_warnings`, `PYTHONWARNINGS` or `-W error`.
- The repo has no `pytest.ini`, `setup.cfg`, `tox.ini`, `pyproject.toml` or `sitecustomize.py`.
- So callers run with Python's default filters: an orphan-temp `RuntimeWarning` prints once to stderr, and the exit code is unaffected.
- The replace callers can never get the warning, because `os.replace` consumes the temp.

## BK-247: each caller against the contract

All 9 are **compatible**. None catches a broad exception that could hide the original error. An unexpected I/O error propagates as a traceback with exit 1. After a successful publish, each caller prints its normal success line and exits with its normal code.

Non-blocking observations, re-checked by hand:

| Id | Where | Observation |
|---|---|---|
| O1 | `inventory_editor_asset_writers.py:52-56`, `audit_editor_save_safety.py:66-70` | `except FileExistsError` also catches the `FileExistsError` that `atomic_io._temporary_path`'s `mkdir(parents=True, exist_ok=True)` raises when a parent component is an existing **file**. That case is misreported as "REFUSED existing ... output" (exit 2). It still fails closed and nothing is written. |
| O2 | `new_rule_scaffold.py:99-108` | The three files are not created as one atomic set. If file 2 or 3 fails (a race after the `:99` existence check, or an I/O error), the earlier files stay and the run exits 1. A re-run then refuses at `:99`. The per-file guarantee still holds. |
| O3 | `summarize_encounter_cost.py:118-120` | On the receipt-read-failure path, the report is printed before it is written, so a write failure leaves stdout output with no file and exit 1. |
| O4 | `summarize_*`: write failure | A write error escapes `atomic_write_text` to the top-level `raise SystemExit(main())`, producing a traceback/non-zero exit; normal report outcomes return 0 or 2. |
| — | `evidence_pack.py` | An orphan `.tmp` left by T1 is an unlisted member, so strict `verify()` refuses the pack (fail-closed; also seen in A-861). |

## BK-248 / BK-249: tests

From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk246_250_atomic_io_callers.py -v` → **`Ran 7 tests ... OK`**. Repeated 20 times: **20/20 OK**.

| Class | Tests |
|---|---|
| `Bk246CallerInventoryAndFilters` (3) | Exactly 9 direct callers; no warning control in any non-test source or launcher; no repo-level warning config. |
| `Bk248FilterModes` (2) | Create text and copy with an orphan temp under the `default`, `ignore` and `error` filters: no exception, published bytes correct, 1 orphan, warning recorded only under `default`. A genuine `FileExistsError` still raises under every filter, the target is kept and no temp remains. |
| `Bk249ConcurrentCreate` (2) | 8 threads race on one target, for create text and for create copy. A barrier just before `os.link` makes every link attempt contend on purpose, not by timing luck. Result: exactly 1 winner, 7 `FileExistsError`, the target holds the winner's bytes, and no temp is left after normal cleanup. |

## BK-250: limits

- The concurrency test uses threads in one process on NTFS. Multiple processes, network filesystems and filesystems without hard links were not exercised.
- Caller behavior was reviewed statically. The O1-O4 paths were not executed.
- Orphan temps are produced by patching `Path.unlink`, not by a real Windows sharing violation.
