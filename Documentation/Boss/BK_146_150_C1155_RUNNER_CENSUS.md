# BK-146..150: static census of C-1155 lock code across all runners

Assigned by X-2029 (lead Codex) to C (implementer), 2026-11-11. New files only: `Scripts/Tools/test_bk146_150_c1155_runner_census.py` and this report. The earlier audits and all runners are unchanged.

**Source-only.** The 34 `.ps1` files under `Scripts/` that contain `owner_token` are read as text. Nothing is executed, and no lock or temp file is created, read or deleted.

`classify()` derives each class from the source. A test then compares it with an explicit expected table frozen on 2026-11-11, so any runner edit fails a test and gets re-reviewed. The classifier is also checked on synthetic runner text (strings only, nothing written).

**Counts describe the source, not runtime behavior. Audit only, with no production edit. X-1991 is still open.**

## Common facts (all 34)

- `$ErrorActionPreference = 'Stop'` is set.
- The created-lock list is `$created` or `$createdLocks`.
- Release happens in a `finally` loop over that list.
- Each lock has its own `try { read; if owner_token -eq $token { Remove-Item } } catch { Write-Warning }`.

## BK-146: `finally` ordering (statements before the lock-release loop)

| Class | Count | Runners |
|---|---|---|
| **Unguarded `$proc.Kill(); $proc.WaitForExit()` before release**: if either throws, `finally` exits and every created lock is retained | **12** | `run_be_x26_x30_locked_validation`, `run_bk2_x26_locked_validation`, `run_bk56_60_deferred_selection`, `run_c1256a_live_self_test`, `run_c1257a_author`, `run_c1257a_dry_run`, `run_c1258a_live_self_test`, `run_c1262a_live_diagnostic`, `run_c1265b_clip_trace`, `run_c1274_s6_locked_dryrun`, `run_c1275a_locked_validation`, `run_c1280_x26_locked_validation` |
| **Unguarded temp `Remove-Item -Force` before release**: with `ErrorActionPreference` set to `Stop`, a failed delete (file in use, access denied) skips release | **3** | `run_bf_x11_x15_locked_build`, `run_bf_x16_x20_locked_build`, `run_bk7_shipping_pipeline` |
| **Release first**: no statement before the lock loop | **19** | all others, for example the `run_be_x01..x25`, `x31`, `x36`, `bf_x01` builds, `c1252a`, `c1253a`, `c1254a`, `c1255`, `c1256a_spawn`, `c1257b`, `c1258a_locked`, `c1262a_locked`, `c1269a`, `c1274_area`, `c1274_channel` |

Guarded env-var restores appear in 8 runners, all inside the Kill class: `Remove-Item Env:\… -ErrorAction SilentlyContinue`, `$env:X = …`, `SetEnvironmentVariable`. They are not counted as bypass risks.

**Risk boundary:** release-bypass is possible in **15 of 34** runners if a pre-release statement throws. Whether `Kill` or `WaitForExit` actually throws in the exited-process race depends on the .NET runtime and was not run.

## BK-147: post-create readback

**0 of 34** runners read a created lock back (`Get-Content $lock`) between the first `CreateNew` and `finally`. The only lock reads are the release-time ownership checks. So the v2 receipt fields `readback_token`, `party` and `policy`, and the contract's `acquire_locks` `observed` records, have no runner source anywhere.

## BK-148: temp-file cleanup (temp + `File.Move` promotion)

- **4** runners promote locks from temp files: `bf_x11_x15`, `bf_x16_x20`, `bk7_shipping_pipeline`, `bk56_60_deferred_selection`.
- **3** of them record the temp path before `CreateNew` (`$temps.Add($temp)`) and delete leftovers in `finally`. That delete is unguarded and runs before lock release (BK-146).
- **`run_bk56_60` tracks no temp path**, so a failed `Move` leaves `<lock>.<token>.tmp` behind (BK-142 L1).
- The other **30** create the lock directly with `CreateNew`, so no temp file exists.

## BK-149: release evidence

| Evidence | Count | Accuracy |
|---|---|---|
| `LOCKS_RELEASED=<created count>`: 28 written as `'…' + $created.Count`, 1 as `"…$($created.Count)"` (`c1256a_spawn_bridge_build_suite`) | **29** | **False aggregate.** It counts locks created, so a lock kept on a token mismatch or a delete failure is reported as released. |
| No lock evidence written | **5** | `bk7_shipping_pipeline`, `c1252a`, `c1253a`, `c1254a_transient_profile_check`, `c1255_live_bridge_validation` |
| Per-lock evidence (attempted / matched / deleted / retained) | **0** | — |

Warnings: **34/34** warn when the ownership read or delete throws (`catch`), and **0/34** warn on a plain token mismatch, which is silent. **0/34** compare case-sensitively (K1, X-2027). No runner's evidence can distinguish deleted from retained per lock.

## BK-150: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk146_150_c1155_runner_census.py" -v` → **`Ran 11 tests ... OK`**. All 11 are ordinary tests; there are no expected failures, because this is a census of current state, not a fix list.

| Class | Tests |
|---|---|
| `ClassifierSelfCheck` (1) | Synthetic runners check each detection: unguarded vs `try`-guarded `Kill`, guarded env restore, temp tracking and cleanup, both created-count evidence forms, per-lock evidence, `-ceq`, mismatch warning, readback after create. |
| `Census` (1) | 34 runners; deterministic; two list-variable names; the `finally` opens before the lock loop. |
| `Bk146FinallyOrdering` (4) | The Kill table (12), the temp-remove table (3), release-first (19, disjoint, covering all), `ErrorActionPreference` set to `Stop` in all 34. |
| `Bk147Readback` (1) | 0 runners read back after create. |
| `Bk148TempCleanup` (2) | 4 temp+Move runners; 3 track and clean; `bk56_60` is the exception. |
| `Bk149ReleaseEvidence` (2) | Evidence classes 29 / 5 / 0; warnings 34 catch / 0 mismatch / 0 case-sensitive. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- The previous audit, `test_bk141_145_c1155_preflight_audit.py`, still gives `OK (expected failures=7)`.

## Limits

- Classification uses regexes on source text, checked against synthetic samples and frozen tables. An unusual coding style could be misclassified; a frozen-table failure flags it for manual review.
- **Risk is stated as possible, not observed.** No runner was executed, and exception behavior of `Kill`, `WaitForExit` and `Remove-Item` is runtime-dependent.
- Only `finally` statements before the lock loop are classified. Statements after it (evidence writes) cannot block release.
