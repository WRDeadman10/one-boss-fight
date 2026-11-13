# BK-141..145: static audit of the C-1155 lock code in the runner

Assigned by X-2024 (lead Codex) to C (implementer), 2026-11-11. Extended for X-2027 (K1, case-sensitive token compare). New files only: `Scripts/Tools/test_bk141_145_c1155_preflight_audit.py` and this report.

The primary target is `Scripts/Editor/run_bk56_60_deferred_selection.ps1` (`R`), the runner the executor contract cites. It is **read as text only**: it is never executed, and no lock file is created, read or deleted. A survey covers all 34 `.ps1` files under `Scripts/` that contain C-1155 lock code (`owner_token`). Line anchors are computed by the tests from the source, so they move if the runner changes.

**Audit only. There is no production edit and no authorization. X-1991 is still open.**

## BK-141: token

- **Held.** `R:27` sets `$token = [guid]::NewGuid().ToString('N')`: 32 hex digits, lowercase on .NET.
  - The token is generated before `$record` (`R:28`, `owner_token=$token`) and before the first create (`R:76`).
  - It is assigned exactly once.
- **T1 (gap).** Validity rests only on the GUID format; nothing asserts it, for example `$token -cmatch '^[0-9a-f]{32}$'`, before the first create. X-2023 (F1 = b) requires the executor to validate the token before any filesystem create, so this assertion belongs between `R:27` and `R:76`.

## BK-142: paths, order, create semantics

- **Paths and order (held).** `R:17` lists exactly two canonical locks, the repo-root `ENGINE_LOCK.json` and then `Docs\BossCombatReview\Execution\ENGINE_LOCK.json`. The acquisition loop (`R:74-80`) takes them in that order: **root then execution**.
- **Pre-checks (held).** An active `UnrealEditor` process (`R:23`) or an existing lock (`R:24`) aborts before any create. After acquisition, an editor that started during it aborts the run (`R:81`).
- **Create semantics (held), in this order, all inside `try` and with no `catch` in the loop:**
  1. A temp file `<lock>.<token>.tmp` is opened with `FileMode CreateNew` + `FileShare None` (exclusive; fails if it exists).
  2. The record is written and flushed with `Flush($true)`.
  3. `[System.IO.File]::Move($temp,$lock)` (the 2-argument form, which never overwrites an existing lock) moves it into place.
  4. `$created.Add($lock)` records the path.

  With `$ErrorActionPreference='Stop'` the first failure ends the loop, so the execution lock is never created after a failed root create. This matches v2's root-first `create_order`.
- **L1 (gap).** If `Move` throws, for example because the lock appeared after the `R:24` pre-check, the `.tmp` file is left behind. `$created` never lists it, and `finally` visits only `$created`.

## BK-143: record fields → v2 receipt

| v2 lock field | Runner source |
|---|---|
| `path` | `$locks` (`R:17`) |
| `created`, `create_order` | membership and position in `$created` (`R:79`); root first by loop order |
| `token` | `$token` (`R:27`) |
| `party`, `policy` | record literals `party='X'`, `policy='C-1155'` (`R:28`) |
| `readback_token` | **no source:** **R1 (gap)**, nothing reads the lock back after `Move`. The contract's `acquire_locks` `observed` records (`C:127-136`) need this readback. |
| `release_attempted`, `release_token_match`, `released` | **no per-lock evidence:** **R2 (gap)** |

The record also carries `agent`, `task`, `command_id`, `pid`, `start_utc` and `scope`. These are extra context, and v2 does not need them.

## BK-144: `finally` cleanup

- **Held:**
  - The cleanup loop visits **only `$created`** (`R:206`), never `$locks`.
  - **The token is compared before delete:** `if ($current.owner_token -eq $token) { Remove-Item ... }` (`R:208`).
  - **Each lock has its own `try/catch`** (`R:208-209`), so garbled JSON or a delete error on one lock does not stop the next.
- **C1 (gap).** `finally` first restores env vars (`R:204`), then runs `if (!$proc.HasExited) { $proc.Kill(); ... }` with no guard (`R:205`). If `Kill` throws, for example because the process exits between the check and the call, or access is denied, the exception leaves `finally` before the lock loop and **both locks are retained**. Whether .NET throws in that race depends on the runtime version. Not verified here: static audit only.
- **K1 (gap, X-2027).** `$current.owner_token -eq $token` (`R:208`) uses PowerShell's **case-insensitive** string equality. A lock whose token differs from this run's lowercase token only by letter case passes the ownership check and is **deleted as if owned**.
  - Rule: exact ordinal comparison, either `-ceq` or `[string]::Equals($current.owner_token, $token, [StringComparison]::Ordinal)`.
  - **All 34** C-1155 runners use the same case-insensitive `-eq`, one comparison each; none uses `-ceq` or an ordinal `Equals`.
- **E1 (gap).** `lock_result.txt` reports `'LOCKS_RELEASED=' + $created.Count` (`R:212`), which is the number **created**, not released. A lock kept on a token mismatch is still counted as released, and so is one kept after a delete error. A token mismatch is also **silent**: only the `catch` path warns.
  - The same counting line appears in **28 of the 34** C-1155 runners.

## BK-145: tests and results

- `python -I -m unittest discover -s . -p "test_bk141_145_c1155_preflight_audit.py" -v` (from `Scripts/Tools`) → `Ran 24 tests ... OK (expected failures=7)`: **17 held, 7 expected failures**. Earlier runs: 21 tests with 6 expected failures (first version), then 23 with 7 after X-2027. My C-1333 message wrongly said 22.
- **Held (17 tests):**
  - **Token:** generated before the record and the first create, never reassigned.
  - **Acquisition:** canonical paths root first; pre-checks before create; the exclusive create → flush → no-overwrite move → record order, inside `try`; the first failure stops acquisition.
  - **Record and mapping:** the record identity fields; the v2 mapping sources.
  - **Cleanup:** visits only created paths; compares the token before delete; isolates each lock with its own `try/catch`; a mismatch is silent (documents E1); the K1 rule is checked on synthetic strings.
  - **Survey of all 34 runners:** each uses `CreateNew`, a GUID `'N'` token, and a token compare before `Remove-Item` (`-eq` or `-ceq`, so a K1 fix does not break this check); the K1 `-eq` compare is shared by all 34 and the E1 counting line by 28.
- **Gaps (7, `expectedFailure`, each confirmed to fail on its assertion):** T1, L1, R1, R2, C1, K1, E1. The K1 rule is shown on synthetic strings by `test_k1_rule_accepts_exact_patterns_and_rejects_case_insensitive_on_synthetic_strings`. It accepts `-ceq` and `[string]::Equals(..., [StringComparison]::Ordinal)`, and rejects `-eq`, `-ieq` and `OrdinalIgnoreCase`. Each docstring states the fix rule. A fix that follows the rule turns its test into an "unexpected success", which is the signal to remove the marker.
- `py_compile` → OK; no trailing whitespace.

## Limits

- The tests are text and regex checks on the runner source, not execution. They prove what the source says, not runtime behavior. C1's exception behavior in particular is version-dependent and was not run.
- The fix-detection regexes are deliberately narrow. A correct fix written differently may need its test adjusted.
- Only `R` was audited line by line. The other 33 runners were checked only for the shared invariants and for the E1 pattern, so they may have other differences, for example the 30 that create the lock directly with `CreateNew` and do not use a temp file and `Move`.
