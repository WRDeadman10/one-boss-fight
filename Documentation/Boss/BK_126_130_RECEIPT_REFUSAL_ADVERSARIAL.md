# BK-126..130: adversarial tests for refusal and restore receipts and the receipt-source adapter

Assigned by X-2014 (lead Codex) to C (implementer), 2026-11-11. New file only: `Scripts/Tools/test_bk126_130_receipt_refusal_adversarial.py`. The validator, adapter, binder, executor contract, author and runner are unchanged. All inputs are synthetic; there is no file, Unreal, asset, lock or process access beyond test discovery.

**Receipt validity is not runtime proof and not write authorization. X-1991 is still open.**

## Held (24 tests, all pass)

**BK-126, partial-lock refusal (`Bk126PartialLockStep`, 6 tests)**
- `test_partial_step_accepts_exactly_one_created_released_lock`: either lock may be the single created lock.
- `test_partial_step_refuses_two_or_zero_created_locks`
- `test_post_acquisition_steps_refuse_a_single_created_lock`: the `locks_verified` and `backup_refused` stages need both locks.
- `test_created_lock_release_claim_mutations_are_refused`: these 8 changes are each refused:
  - release not attempted
  - token mismatch
  - lock kept
  - released without a token match
  - readback token differs
  - foreign policy
  - unknown party
  - non-boolean flag
- `test_uncreated_lock_cannot_claim_lock_or_release_data`: token, readback, party, policy, release flags, `created=None`.
- `test_two_created_refusal_locks_share_token_and_party`

**BK-127, refusal-stage asset evidence (`Bk127RefusalStageAsset`, 6 tests)**
- `test_before_backup_stages_accept_null_or_hex_before_and_no_backup`
- `test_before_backup_stages_refuse_backup_claims`: a path only, a hash only, or both, before `backup_verified`.
- `test_malformed_before_hash_is_refused_at_every_stage`: uppercase, 63 characters, an int or a list, at all 4 stages.
- `test_write_plan_refusal_requires_the_verified_backup`: each of these is refused:
  - missing before hash, path or backup hash
  - backup hash differs from before hash
  - absolute path
  - path traversal
  - path outside `Docs/BossCombatReview/Execution/`
- `test_no_refusal_stage_may_claim_save_readback_or_restore`
- `test_refusal_steps_cannot_be_mixed_or_extended`

**BK-128, restore failure (`Bk128RestoreFailure`, 6 tests)**
- `test_valid_forms`: `FAILED_RESTORE_NEEDS_OPERATOR`, the retained-lock restore failure, and a restore hash equal to the bad save.
- `test_restore_hash_matching_before_missing_or_malformed_is_refused`: covers both restore-failed forms.
- `test_retained_without_restore_steps_cannot_claim_a_restore_hash`
- `test_restore_failed_outcome_requires_both_locks_released`
- `test_retained_restore_lock_mutations`: each of these is refused:
  - every lock released
  - no release attempt
  - token match but not released
  - released without an attempt
  - after hash equal to before hash
- `test_restore_steps_cannot_cross_outcomes`

**BK-129, injected adapter dependencies (`Bk129InjectedReturnTypes`, 6 tests)**
- `test_real_dependencies_bind`
- `test_non_object_or_non_true_validator_results_fail_closed`: 11 results, including truthy non-`True` values, and `errors` that is not a list.
- `test_extractor_bad_returns_fail_closed`: None, bytes, int, list or dict.
- `test_extractor_that_reports_an_error_but_returns_a_body_fails_closed`
- `test_extractor_returning_a_different_body_fails_on_hash`
- `test_valid_result_for_a_receipt_without_a_source_object_fails_closed`

## Gaps found (4) and fixed by the lead (X-2016); now regressions in `Bk126To129HotfixRegressions`

| Id | Where | Failure | Suggested rule |
|---|---|---|---|
| R1 | `validate_sevarog_executor_receipt.py:174` | A `REFUSED_AFTER_LOCKS` receipt with `locks=None` or `locks=3` raises `TypeError` (the `"locks"` key always exists, so `.get("locks", [])` returns None). | Count created locks only when `locks` is a list, so `_locks` reports the error. |
| R2 | `bind_receipt_source.py:56` | Once the injected validator says valid, `claimed["message_id"]` raises `KeyError` for a source object without that key. | Require all `SOURCE_KEYS` in the claimed source before extraction; refuse otherwise. |
| R3 | `bind_receipt_source.py:35`, `:50` | An exception from the injected validator or extractor propagates, so the caller gets no `{bound: False}` record. | Lead decision: catch `Exception` and refuse, naming the exception type, or document propagation as intended. |
| R4 | `bind_receipt_source.py:57` | A body containing a lone surrogate (`\udc80`) raises `UnicodeEncodeError` while it is hashed. | Refuse a body that is not valid UTF-8 text. |

R1-R4 were confirmed with the exact exceptions shown before the fix. X-2016 fixed them in production only, and the `expectedFailure` markers were then removed. R5 was added for the closed edge: `test_r5_valid_flag_with_reported_errors_does_not_bind`. A `valid: True` result now binds only with an empty `errors` list. A non-empty, missing, None, tuple or string `errors` value is refused before the extractor runs.

## Still open (lead notes, not tests)

- **Partial-lock order:** the receipt accepts either lock as the single created one. If the executor always creates the repo-root lock first, a partial refusal could require `locks[0]` to be the created one. That needs the order fixed in the executor contract first.
- **Rejected backup:** at the `backup_refused` stage the receipt cannot record a backup copy that was made and then rejected, for example on a hash mismatch. A stray file an operator may need to clean up is then invisible.
- **Before-hash timing:** a dry-run receipt must keep `before_sha256` null, yet the contract's dry snapshot has `file_sha256` (`sevarog_executor_contract.py:148`). Refusals before backup may claim a before hash, and the receipt cannot say whether it came from the dry snapshot or the locked one.
- The adapter still trusts that the injected functions are the real validator and binder; wiring them is the executor's job.

## BK-130: validation (exact)

- From `Scripts/Tools`:
  - `python -I -m unittest discover -s . -p "test_bk126_130_receipt_refusal_adversarial.py" -v` → `Ran 29 tests ... OK` after X-2016 (before the fix: `Ran 28 tests ... OK (expected failures=4)`).
  - Neighbor suites pass unchanged:

    | Suite | Result |
    |---|---|
    | receipt | 13/13 |
    | receipt adversarial | 12/12 |
    | adapter | 14/14 |
    | binder | 11/11 |
    | executor contract | 16/16 |
    | contract adversarial | 12/12 |
- `python -I -m py_compile Scripts/Tools/test_bk126_130_receipt_refusal_adversarial.py` → OK; no trailing whitespace.
- This batch modified no production files; the X-2016 fixes are the lead's.
