# BK-106..110: adversarial audit of the executor state contract

Assigned by X-2005 (lead Codex) to C (implementer), 2026-11-11. New file only (`Scripts/Tools/test_sevarog_executor_contract_adversarial.py`); `sevarog_executor_contract.py` and every other existing file are unchanged. No filesystem writes, Unreal, assets or real locks; synthetic inputs only.

**Contract audit only. No authoring and no C-1155 run is authorized; X-1991 is still unanswered.**

## Probes and results

### BK-106: lock observations and receipts

These held:
- Receipt containers that are not lists are refused: a string, `None`, an int or a dict.
- Unknown paths (`Saved/ENGINE_LOCK.json`), duplicate paths and non-string entries in the receipts are refused.
- An uppercase record token, a foreign party or a missing policy is refused.
- A same-token record without a create receipt is never listed for release (the lead's X-2005 fix holds).

**Gap A (lock leak):** if the executor created both locks and then `acquire_locks` refuses early (no explicit write, incomplete approval, or a malformed run token), the run ends `REFUSED` with an empty `locks_to_release`. The early checks run before the receipts are read, so `created_locks` stays empty.
- Fix: compute `created_locks` from valid receipts first, then refuse into `RELEASE_REQUIRED`.

**Gap B (lock leak):** a lock with a create receipt whose readback is garbled or missing is dropped from `locks_to_release`; only the readable lock is listed.
- Fix: list every receipted path. The executor's delete-on-token-match stays the final guard.

### BK-107: snapshots and backup across the dry-run and locked phases

These held, each refused into `RELEASE_REQUIRED` with both locks listed:
- A changed before-hash between the dry run and the locked phase.
- An uppercase hash.
- A snapshot that is not a dict.
- A backup hash mismatch, an empty backup path, or a backup that is not a dict.

**Gap C (aliasing):** `verify_backup` stores the caller's snapshot by reference. Mutating that dict afterwards changes `locked_snapshot` (its hash and its phase rows), which `plan_write` and `record_restore` then trust.
- Fix: store deep copies of the dry-run snapshot, the locked snapshot and the backup.

**Gap D (diff the reviewer saw vs. writes executed):** with the same file hash, a locked snapshot that reports different current values (for example a different `max_health`) yields an accepted write plan whose from-values differ from the reviewed dry-run diff.
- Fix: `plan_write` should refuse unless each write plan entry (`field_path`, `from`, `to`) equals the dry-run plan's.

**Gap E:** a non-string backup path (a list) is accepted.
- Fix: require a non-empty string.

### BK-108: repeated, out-of-order and terminal transitions

These held:
- A repeated `acquire_locks` does not move the state.
- After `RELEASED`, `release_locks`, `plan_write`, `record_restore` and `start` are all refused without moving, and `locks_to_release` is empty.
- A lock-free refusal lists nothing to release, and `release_locks` is refused there.

Only locks with a receipt and a matching token reach the release list, apart from the two leak gaps above, which list too few, never too many.

Known by design, not a gap: `start()` accepts any object with `get`. The issued-binding capability is enforced at `plan_dry_run` through `bind_owner_approval.plan_from_bound`, so a forged dictionary cannot pass the dry run.

## BK-109: regression cases

`Scripts/Tools/test_sevarog_executor_contract_adversarial.py` has 11 tests: 6 held defenses as ordinary tests, and 5 `expectedFailure` cases (gaps A–E), each asserting the safe behavior. Remove the decorators when the contract is fixed.

## BK-110: validation (exact)

- From `Scripts/Tools`:
  - `python -I -m unittest discover -s . -p "test_sevarog_executor_contract_adversarial.py" -v` → `Ran 11 tests ... OK (expected failures=5)`.
  - Neighbor suites, unchanged: `test_sevarog_executor_contract.py` → 16 run, OK; `test_bind_owner_approval.py` → OK; `test_plan_sevarog_definition_repair.py` → OK.
- `python -I -m py_compile Scripts/Tools/test_sevarog_executor_contract_adversarial.py` → OK.
- `git diff --check` → clean.

## Limits and gates

- The contract still trusts executor-reported observations. Gaps A–D concern what it does with them: leaking locks, aliasing, and divergence from the reviewed diff. The executor's own source contract and receipts remain the outer control.
- No-write gates are unchanged: dry run by default; write needs a bound, complete owner approval (X-1991), explicit opt-in, both receipted C-1155 locks, a matching backup, and readback before release.
- Owner decisions still required (X-1991): MaxHealth/MaxPosture (and the poise mapping), regen delay/rate, threshold, and the three multipliers.

## Lead review / hotfix (2026-11-11)

The five confirmed gaps are fixed: (A) receipts are recorded before write/approval/token refusals so any receipted locks enter release; (B) every known receipted path is retained for cleanup even when readback is missing/garbled, while the executor still must delete only after token match; (C) dry-run and locked snapshots plus backup metadata are deep-copied; (D) proposed write `(field_path, from, to)` tuples and untouched rows must match the reviewed dry-run; (E) backup path must be a non-empty string. Added an early-refusal regression with an invalid token and already-created receipts. The 12 adversarial tests now pass without expected failures; base contract 16/16, binder 11/11, planner 12/12; compilation and scoped diff-check pass. State contract now imports only `copy` and `re`; no I/O was added.
