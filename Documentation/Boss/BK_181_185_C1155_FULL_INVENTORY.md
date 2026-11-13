# BK-181..185: repository-wide C-1155 lock inventory and the scripts outside the earlier censuses

Assigned by X-2039 (lead Codex) to C (implementer), 2026-11-11. This is batch 3 of 20. New files only:
- `Scripts/Tools/test_bk181_185_c1155_full_inventory.py`
- this report

**Source-only.** Every `.ps1` under `Scripts/` is read as text. Nothing is executed, and no lock, log, temp file or asset is touched. **All classes describe code, not observed runtime.** Audit only; X-1991 is still open.

## Scope note on the earlier censuses

BK-146..165 (and BK-141..145) selected the **34 scripts that contain `owner_token`**. That is a defined **subset**, not a complete inventory. Their historical counts stay as published, and those files are not edited. This batch adds the full inventory and audits the remainder.

## BK-181: inventory query

`inventory()` returns every `Scripts/**/*.ps1` (recursive) whose text matches the regex **`ENGINE_LOCK|C-1155`** (case-sensitive), as sorted repo-relative POSIX paths. The result is deterministic and a test checks it.

**Result: 63 scripts.**

## BK-182: subset and remainder

- **Subset:** 34 scripts contain `owner_token`. Every one also matches the query, and no other `.ps1` contains `owner_token`.
- **Remainder:** 29 scripts match the query but have no `owner_token`. **28** of them write a lock. The 29th, `Scripts/Tests/TestRunLeadPieDryRun.ps1`, only checks that a dry run leaves the lock state unchanged.
- **63 = 34 + 29.**

A-845 counted 28 additional scripts. This query counts 29; the difference is most likely the test script, which references `ENGINE_LOCK` but never writes one. The query and its criteria are stated exactly above, so anyone can re-run them.

## BK-183: lock handling in the 28 lock-writing remainder scripts

Classified by `classify_lock()`. Each of the 29 scripts was also reviewed independently by its own read-only agent, using written definitions, and **the agents agreed with the classifier on all 145 checks** (29 scripts × 5 fields), once "pre-check" was defined only for scripts that write a lock.

| Dimension | Result |
|---|---|
| Lock paths | **Both locks: 12**; **Execution lock only: 13**; **root lock only: 3**. Scripts that take one lock do not coordinate with runs holding only the other. |
| Create | **Exclusive: 16** (`New-Item -ItemType File` without `-Force` plus `-ErrorAction Stop`, or `CreateNew`; a later `Set-Content` into the file just created does not change this). **Overwrite: 12** (`Set-Content` or `WriteAllText`, which replace an existing lock). |
| Pre-check for an existing lock | Present in 9 of the 12 overwrite scripts and in most exclusive ones. **Absent in 3 overwrite scripts.** |
| Release | **Ownership-checked: 4** (they read the JSON and compare a token or command id). **Acquired-gate: 11** (they delete only the paths or flags this run recorded, without reading the content). **Unconditional: 13** (`Test-Path` then `Remove-Item` on whatever is at the path). |
| Release placement | Every releasing script releases inside `finally`. |
| Unique run token | 10 scripts: the 4 ownership-checked scripts and the `c123x` group. |

## BK-184: high-risk patterns (code risk, not observed events)

1. **Overwrite with no pre-check, plus unconditional release (3):** `Scripts/Editor/run_apply_notifies.ps1`, `run_inspect_props.ps1` and `run_verify_notifies.ps1`, at **`:8` `Set-Content -Path $lockFile`** and **`:11-12` `Test-Path` then `Remove-Item -Force`**.
   - **Effect:** the script can replace another holder's live lock, and its `finally` then deletes it, leaving the other run unprotected.
   - **Lock coverage:** the Execution lock only.
2. **Overwrite after a pre-check (a TOCTOU race), plus unconditional release (9):**
   - Write and release lines:
     - `run_author_aura_boostlite_production` `:30-31` / `:47-51`
     - `run_export_sfx_batch3` `:30-31` / `:48-51`
     - `run_verify_aura_boostlite_roundtrip` `:30-31` / `:47-51`
     - `run_author_boss01_heavyswordsocket` `:30` / `:46-47`
     - `run_restore_pack_heavyswordsocket` `:30` / `:46-47`
     - `run_pie_ember_sword_probe_ag` `:29` / `:43-44`
     - `run_reauthor_guard_counter_c1046` `:24` / `:34-35`
     - `run_rebuild_ppm` `:24` / `:34-35`
     - `Scripts/Tools/run_c1249_editor_validation` `:11` (`WriteAllText`) / `:30`
   - **Effect:** a lock created between the check and the write is overwritten and later deleted.
   - **Writes outside the `try`:** in the `boostlite`, `export_sfx_batch3`, `restore_pack` and `verify_roundtrip` scripts, the lock writes sit before the `try`. If the second write fails, the first lock is left behind.
3. **Release loops that abort on error (4 ownership-checked scripts):** `run_aura_graph_authoring` `:40,44`, `run_aura_graph_commandlet` `:58`, `run_c1210_build_suite` `:35`, `run_c1210_ember_aura_definition` `:29`.
   - **Cause:** `Get-Content | ConvertFrom-Json` (and `Write-Error` on an owner mismatch) run unguarded under `ErrorActionPreference` `Stop`.
   - **Effect:** a malformed or foreign first lock ends the loop, so this run's second lock is never released. The ownership check itself is good.
4. **Acquired-gate release with hidden failures (`c1230b`, `c1231b`, `c1232a`, `c1233a`, `c1237a`):**
   - **Hidden failures:** `Remove-Item … -ErrorAction SilentlyContinue` (for example `run_c1230b_ember_timing_audit` `:66`) hides a failed delete.
   - **False count:** `LOCKS_RELEASED=$created.Count` still claims success, the same false aggregate as E1 in BK-149.
5. **`Scripts/RunLeadPie.ps1`:** an exclusive `CreateNew` (`:59`), but an unconditional `Remove-Item -Force` at `:157` with no owner or token check. It takes the Execution lock only.

This batch confirms no runtime incident. These are the code paths that would cause one if two runs overlapped.

## BK-185: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk181_185_c1155_full_inventory.py" -v` → **`Ran 12 tests ... OK`**.

| Class | Tests |
|---|---|
| `Bk181Inventory` (2) | Deterministic inventory of 63 `Scripts/*.ps1` paths; the query string is fixed and case-sensitive. |
| `Bk182SubsetAndRemainder` (2) | 34 + 29 = 63; `owner_token` appears only in the subset; the test script is the one non-writer. |
| `Bk183LockHandling` (4) | Create classes 16 / 12, with the overwrite list frozen; release classes: ownership-checked 4, acquired-gate 11, unconditional 13, all in `finally`; lock paths 12 / 13 / 3; unique tokens 10. |
| `Bk184HighRisk` (3) | The 3 "overwrite, no pre-check, unconditional release" scripts; the 9 TOCTOU overwrite scripts, all with unconditional release; `file:line` anchors for 6 example scripts. |
| `ClassifierSelfCheck` (1) | Synthetic overwrite, exclusive-with-ownership, and `New-Item -Force` cases. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- The BK-146, 151, 156 and 161 census suites still pass, unchanged.
- A first expected lock-path table had the "both" and "execution only" counts swapped; it was corrected to the classifier's result, 12 / 13.

## Limits

- Regex classification of source, confirmed by an independent per-script agent review. Neither runs the scripts.
- `Scripts/**/*.ps1` only. Python or batch files that might touch locks are out of this query's scope.
- No runtime claims: whether any overlap ever happened is not knowable from source.

## Corrections (append-only, X-2041 / A-847, 2026-11-11)

The original text and tests above are preserved as first published. The corrections live in `BK_186_190_C1155_LOCK_SCOPE.md`, and `Scripts/Tools/test_bk186_190_c1155_lock_scope.py` (class `Bk181Corrections`) tests them.
1. **"Unique run token: 10" is 9 lock writers.** The 10th `NewGuid` is `TestRunLeadPieDryRun.ps1`'s temp-folder name, not a lock token.
2. **`Scripts/RunLeadPie.ps1` acquires before its cleanup try.**
   - **Where:** `CreateNew` at `:59` with its payload write inside an inner `try` (`:61-66`); the release `try` opens at `:69`.
   - **Effect:** a write failure in between leaves the lock behind.
   - **Status:** documented only; not edited, not run, not assigned.
3. **New-Item exclusivity now also requires a hard failure** (`-ErrorAction Stop` or an earlier global Stop). All 15 current lock `New-Item` writers meet it.
