# BK-101..105: state-machine contract for a future Sevarog definition executor

Assigned by X-2004 (lead Codex) to C (implementer), 2026-11-11. Contract work, not an authoring executor. New files only; no existing author, runner, driver, helper or validator edited; no Unreal, build, PIE, assets or locks; no project values.

**No data authoring and no C-1155 run is authorized. X-1991 is unanswered.**

## BK-101: conventions this contract encodes

- **C-1155 locks** (`run_bk56_60_deferred_selection.ps1:17-58`):
  - Two lock files, repo-root `ENGINE_LOCK.json` and `Docs/BossCombatReview/Execution/ENGINE_LOCK.json`, held under one GUID token (32 lowercase hex). The record carries agent, party, task, command_id, owner_token, pid, start_utc, policy=C-1155 and scope.
  - Creation is atomic (temp file then move). The run aborts if a lock already exists or the editor appears during acquisition.
  - Release happens in `finally`, and only for a lock whose `owner_token` matches. `lock_result.txt` records the count.
- **Backup:** copy the draft `.uasset` into the evidence folder before any write (the runner's `DA_Boss_Sevarog_Draft.before.uasset`).
- **Readback:** a separate locked readback (as the encounter author's `--readback` does).
- **Sevarog entry points:**
  - The binder (`bind_owner_approval.py`, with the lead's issued-capability hotfix X-2004: forged `bound=True` dictionaries are refused by `plan_from_bound`).
  - The planner (`plan_repair`, `verify_readback`).
  - The existing append-only helper and the encounter author, which stay untouched.

## BK-102: contract (`Scripts/Tools/sevarog_executor_contract.py`)

`ExecutorContract(binder, party)` is pure: its only import is `re`, it performs no I/O, and it executes nothing. The executor does every real action and reports each observation; the contract allows or refuses the next transition.

Allowed transitions:
- `INIT` → `start(binding, explicit_write)` → `STARTED`. Refused without an issued binding that is `bound`.
- `STARTED` → `plan_dry_run(snapshot)` → `DRY_RUN_PLANNED`. Planning goes through `binder.plan_from_bound`, so forged or incomplete approvals are refused here.
- **Dry run (the default):** the run stops at `DRY_RUN_PLANNED` with outcome `DRY_RUN_ONLY`, and no lock is ever taken.
- **Write:** `acquire_locks(token, observed)` → `LOCKED`. This needs explicit write opt-in, `approval_complete`, a 32-hex run token, and both lock records carrying that token with this party and `policy=C-1155`.
- `verify_backup(locked_snapshot, backup)` → `BACKED_UP`. The before-hash must equal the dry-run snapshot's (the asset must not change in between), and the backup SHA-256 must equal the before-hash.
- `plan_write()` → `WRITE_PLANNED`, via `plan_from_bound(..., allow_write=True)` with this run's token and backup.
- `record_save(ok)` → `SAVED`; a failed save goes to `RESTORE_REQUIRED`.
- `readback(after)` → `VERIFIED` on a match, or `RESTORE_REQUIRED` on a mismatch (via the planner's `verify_readback`).
- `record_restore(sha)` → `RESTORED` if the before-hash came back, otherwise `RESTORE_FAILED`.

Locks and release:
- Any refusal after a lock exists moves to `RELEASE_REQUIRED`. `release_locks(released)` is the only exit from every lock-holding state and always ends in `RELEASED`.
- `locks_to_release` lists exactly the locks this run created. A lock held by another owner, or a failed create, is never released.
- Outcomes:
  - `WRITTEN_AND_VERIFIED`
  - `FAILED_RESTORED`
  - `FAILED_RESTORE_NEEDS_OPERATOR`
  - `REFUSED_AFTER_LOCKS`
  - `LOCK_RETAINED_NEEDS_OPERATOR` (a lock could not be removed)
- Out-of-order calls are refused without changing state.

## BK-103: synthetic tests (`Scripts/Tools/test_sevarog_executor_contract.py`, 13 tests)

These use the real binder and planner with synthetic mailbox text, envelopes and snapshots; lock records, hashes, save and readback results are in-memory values.
- **Dry run:** no locks, and a write is refused.
- **Source:**
  - None, a string or an int is refused.
  - An unbound binding is refused, for example envelope quotes that no longer match the reply.
  - A forged `bound=True` dictionary is refused at planning.
- **Incomplete approval:** refused at planning; no locks are taken.
- **Lock failures:**
  - A failed second create, or another owner holding one lock: only this run's lock is listed for release.
  - Wrong party or policy: both of this run's locks are released.
  - Nothing created: no release and the run ends `REFUSED`.
  - A bad run token is refused before any lock is claimed.
- **Backup:** a hash mismatch, a missing backup, or an asset changed since the dry run all require release (outcome `REFUSED_AFTER_LOCKS`).
- **Success:** save, readback, release, with the exact state history.
- **Failure paths:**
  - A readback mismatch leads to restore, release and `FAILED_RESTORED`.
  - A failed save leads to restore.
  - A wrong restore hash leads to `FAILED_RESTORE_NEEDS_OPERATOR`.
  - A partial release reports `LOCK_RETAINED_NEEDS_OPERATOR`.
- **Ordering:** six out-of-order steps from `INIT`, and a double `start`, are refused without moving.
- **Purity (AST):** the only import is `re`, and there are no file, process or eval calls.

## BK-104: executor integration (for a later, separately authorized batch)

1. Read `Documentation/TEAM_MAILBOX.md` in full, call `bind_owner_approval(text, owner_id, envelope)`, then `contract.start(binding, explicit_write=<operator flag>)`.
2. Take a readback snapshot (no locks are needed for a dry run) and call `contract.plan_dry_run(snapshot)`. Show the diffs. Without explicit write, or with an incomplete approval, stop here.
3. Generate the token and create both locks atomically, then read them back. Call `contract.acquire_locks(token, {path: record_or_None})`. From this point the executor wraps everything in `try/finally`, and the `finally` block calls `contract.release_locks(...)` after deleting each path in `contract.locks_to_release` only on a token match.
4. Take the locked snapshot, copy the backup, hash it, and call `contract.verify_backup(snapshot, {"path", "sha256"})`.
5. Call `contract.plan_write()`, apply exactly `contract.plan["writes"]` and `["field_records"]` in place, save, and call `contract.record_save(ok)`.
6. Take the after snapshot and call `contract.readback(after)`. On `RESTORE_REQUIRED`, copy the backup back, hash it, and call `contract.record_restore(sha)`.
7. Report `contract.outcome`. Anything other than `WRITTEN_AND_VERIFIED` stops the pipeline. On success: the encounter readback, the pinned suite, then the BK-59 deferred PIE, each separately gated.

The executor needs its own source contract (BK-82 style) proving it calls exactly these transitions in this order, plus a locked dry run, before any real write.

## BK-105: validation (exact)

- From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_sevarog_executor_contract.py"` → `Ran 13 tests ... OK`.
- Neighbor suites, unchanged: `test_bind_owner_approval.py` → OK; `test_plan_sevarog_definition_repair.py` → OK; `test_validate_owner_approval_envelope.py` → OK (skipped=1).
- `python -I -m py_compile Scripts/Tools/sevarog_executor_contract.py Scripts/Tools/test_sevarog_executor_contract.py` → OK.
- `git diff --check` on both files → clean.

## Limits

- The contract trusts the observations the executor reports (lock records, hashes, save and readback results); a dishonest executor could lie. The executor's own source contract and its receipts are the control for that.
- `start()` accepts any object with `get`; issued-capability enforcement happens at `plan_dry_run` via the binder, so a forged binding cannot get past the dry run.
- One run, one asset (`DA_Boss_Sevarog_Draft`); multi-asset edits are out of scope.

## Lead review / hotfix (2026-11-11)

Review found `acquire_locks()` inferred that a lock belonged to this invocation solely because its record carried the supplied run token. If a create failed while a stale/pre-existing lock happened to carry that same token, `locks_to_release` could incorrectly include it. The contract now requires explicit per-path receipts that this invocation's atomic creates succeeded, in addition to the read-back token/party/policy checks. Added regressions for a same-token pre-existing lock without a creation receipt and malformed receipt paths. Updated focused executor-contract suite passes 15/15; binder 11/11 and planner 12/12 remain green; py_compile and scoped diff-check pass. No actual locks or project files were touched. The `acquire_locks` API is now `acquire_locks(token, observed, created_paths)`; this section supersedes the earlier two-argument call examples above.

## Follow-up hardening (Lead, 2026-11-11)

Additional review found a cleanup edge: if `created_paths` contained one valid receipt plus a malformed extra path, the contract refused before recording the valid receipt, which could strand a lock created by this run. It now records valid known-path receipts first, then refuses malformed/duplicate extras; `locks_to_release` retains only the token-matching lock proven created by this run. Added a mixed valid+unknown receipt regression. Executor-contract suite: 16/16; py_compile and scoped diff-check pass.
