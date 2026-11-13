# BK-116..120: adversarial audit of the Sevarog executor receipt validator

Assigned by X-2009 (lead Codex) to C (implementer), 2026-11-11. New file only (`Scripts/Tools/test_validate_sevarog_executor_receipt_adversarial.py`); `validate_sevarog_executor_receipt.py` is unchanged. Synthetic receipts only; no files, Unreal, assets or locks.

**Receipt validity is not runtime proof and not write authorization. X-1991 is still unanswered.**

## Held (6 test groups, all refused correctly)

- **Top-level malformed values** (BK-116): unhashable `outcome` (`[]`, `{}`; the X-2010/X-2011 case is kept), `schema=[]`, `steps` as a dict or None, `source` as a string, `locks` as a string, `asset` as a list.
- **Nested records:**
  - Lock record malformed: a lock record given as a string, an unhashable lock path, reversed lock order, a single lock, an extra lock key.
  - Hash and keys: a missing asset key, an uppercase source hash.
- **Type edges:** `created=1`, `released=1`, `release_attempted="yes"`, `token=True`, a non-hex token.
- **Per outcome** (BK-117):
  - Hashes: after equals before, a different backup hash, a restore claim on a success, a missing or wrong `restored_sha256`, a missing plan hash.
  - Locks: a retained outcome where every lock was released, a success with a retained lock, a readback token mismatch, a matched-but-not-released lock.
  - Source: a write without a source, an agent source id.
- **Steps and dry run** (BK-118): duplicated, reordered, cross-outcome, missing and non-string steps are refused. A dry run claiming an after hash, a backup, a created lock, a lock token, or write steps is refused.

## Confirmed gaps (6; pinned as `expectedFailure`, each with a docstring gap report)

| Id | Gap (all in `validate_sevarog_executor_receipt.py`) | Suggested fix |
|---|---|---|
| G1 | The two lock records may carry **different tokens**; `_locks` checks each token's shape and create/readback match, but never that both share the one C-1155 run token | Require `locks[0].token == locks[1].token` for every lock-taking outcome |
| G2 | The two locks may belong to **different parties** (X + C passes); each is checked against {X, C, A} independently | Require one party for both records |
| G3 | Under `LOCK_RETAINED_NEEDS_OPERATOR`, a lock can be `released=True`, `release_token_match=True`, `release_attempted=False`: released without an attempt | `released=True` implies `release_attempted=True` for every outcome |
| G4 | `asset.backup_path` only has to be a non-empty string; `C:/…`, `../../…`, `/tmp/…` and UNC paths pass | Require a repo-relative path without traversal (ideally under the run's evidence folder) |
| G5 | The executor contract also ends runs as `REFUSED_AFTER_LOCKS` and `FAILED_RESTORE_NEEDS_OPERATOR`, but the receipt has no form for them, so the runs that most need operator evidence cannot produce a valid receipt | Add both outcomes, each with its own ordered step list and per-outcome evidence rules |
| G6 | `DRY_STEPS` begins with `mailbox_read`, and the executor binds the owner message before the dry run (BK-104), yet a dry-run receipt with an all-null source is accepted: the step claims evidence the receipt omits | Require a bound source for dry runs too, or drop `mailbox_read` from `DRY_STEPS` if source-free dry runs are intended (a lead decision) |

## Validation (exact)

- From `Scripts/Tools`:
  - `python -I -m unittest discover -s . -p "test_validate_sevarog_executor_receipt_adversarial.py" -v` → `Ran 12 tests ... OK (expected failures=6)`.
  - Existing `test_validate_sevarog_executor_receipt.py` → `Ran 10 tests ... OK`.
- `python -I -m py_compile Scripts/Tools/test_validate_sevarog_executor_receipt_adversarial.py` → OK.
- `git diff --check` → clean.

## Limits

- A coincidentally equal `plan_sha256` and asset hash is not treated as an error (no rule can tell that apart from a real collision).
- The receipt binds identities (plan hash, owner message hash), not their contents; checking the plan contents against a stored dry-run plan is a separate step.
- G6 depends on intent; the test encodes "dry runs are bound", per BK-104.

## Lead review and hotfix disposition (2026-11-11)

Accepted with fixes. G1/G2 are enforced across every created-lock subset; G3 is enforced globally; G4 rejects rooted, traversal, backslash, drive, colon, and control-character paths and requires the execution evidence subtree; G5 adds refusal-after-locks and restore-failed operator outcomes with distinct step sequences and hashes; G6 binds dry-run receipts to the Owner message. Expected-failure markers were removed and each finding is now a passing regression. Refusal receipts allow only stage-appropriate before/backup evidence. Receipt suite 12/12 and adversarial suite 12/12 pass; executor contract 16/16 and adversarial contract 12/12 pass; compilation passed. No runtime proof or authorization is implied; X-1991 remains open.
