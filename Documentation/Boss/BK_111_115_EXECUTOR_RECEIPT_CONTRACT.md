# BK-111..115: future Sevarog executor receipt contract

Assigned by X-2007; prepared by Codex because all agents were offline and C-1314 was unacknowledged (X-2008). Contract/schema only; new files. No asset, Unreal, build, PIE, or lock operation; no project values. This validator checks receipt claims only and does not authorize an executor or C-1155.

## Schema and validator

`Scripts/Tools/validate_sevarog_executor_receipt.py` defines `onebossfight.sevarog-executor-receipt/v1`. The exact top-level keys are `schema`, `outcome`, `source`, `plan_sha256`, `asset`, `locks`, and ordered `steps`. Nested records also have exact key sets. Hashes must be 64 lowercase hex; lock tokens 32 lowercase hex. Extra/missing keys, duplicate lock paths, malformed types, unsupported outcomes, and incorrect step sequences fail closed.

Supported outcomes:

- `DRY_RUN_ONLY`: plan hash, canonical asset path, and fully specified Owner source; no backup, file hashes, or acquired/released lock claims; steps are exactly `mailbox_read`, `dry_run`.
- `WRITTEN_AND_VERIFIED`: fully identified Owner source, plan hash, before/backup/after hashes, backup hash equals before-hash, changed after-hash, both canonical locks with matching create/readback token, party and C-1155 policy, and successful token-checked release. Steps are fixed in order through `readback_verified` and `locks_released`.
- `FAILED_RESTORED`: write prerequisites and lock cleanup as above; a changed after-hash, readback failure, and restored hash equal to before-hash.
- `FAILED_RESTORE_NEEDS_OPERATOR`: write prerequisites and lock cleanup as above; a changed after-hash and a valid restore hash that differs from before-hash.
- `REFUSED_AFTER_LOCKS`: at least one lock was created and all created locks were released; steps and before/backup evidence are limited to the stop stage.
- `LOCK_RETAINED_NEEDS_OPERATOR`: write/readback evidence plus a release-failure step and at least one lock still retained. A released lock must record a matching release token; retained locks require a release attempt.

`validate_receipt(receipt)` is pure and returns only `{valid, errors}`. The test fixture is synthetic; no real mailbox, file, lock or project data is inspected. The receipt validator does not prove that the stated events occurred, that a source hash belongs to the mailbox, or that an executor actually called the contract. A later executor source contract and independently retained receipts are still required.

## Tests and validation

`Scripts/Tools/test_validate_sevarog_executor_receipt.py` has 12 synthetic tests covering all six outcomes, strict keys and hashes, source tampering, shared lock identity/release, staged backup/refusal evidence, reordered/duplicate steps, outcome/data mismatches, and no-I/O purity.

- `python -I -m unittest discover -s Scripts/Tools -p "test_validate_sevarog_executor_receipt.py" -q` — 12/12 (supersedes initial 9/9 result).
- `python -I -m py_compile Scripts/Tools/validate_sevarog_executor_receipt.py Scripts/Tools/test_validate_sevarog_executor_receipt.py` — passed.
- `git diff --check` on both files — clean.

Owner X-1991 remains unanswered. This receipt format is future evidence plumbing only; it does not authorize definition authoring, asset saves, or C-1155.

## Lead follow-up (2026-11-11)

An adversarial probe with an unhashable `outcome` (a JSON list) raised `TypeError` at set membership. The validator now checks the outcome is a string before membership; a regression confirms it returns a refusal instead of raising. Receipt suite is 10/10, py_compile and scoped diff-check pass. Claude's BK-116..120 audit is in progress; this case was sent for inclusion there.

## Superseding lead hotfix (2026-11-11; C-1316 review)

C-1316's six adversarial gaps are fixed in the validator and retained as normal regression tests: lock-taking runs share one token and party; a released lock requires an attempted, token-matched release; backup paths are safe repo-relative paths under `Docs/BossCombatReview/Execution/`; all six contract outcomes have receipt forms with stage-specific ordered steps and evidence; and dry-run receipts require the Owner mailbox binding they claim to have read. `REFUSED_AFTER_LOCKS` preserves only the evidence available at its stop stage; a verified backup must have a safe path and matching before-hash. `FAILED_RESTORE_NEEDS_OPERATOR` requires a valid restore hash that differs from before; the retained-lock restore-failure path is also modeled.

Post-hotfix: receipt tests 12/12, adversarial tests 12/12, executor-contract tests 16/16, executor-contract adversarial tests 12/12; Python compilation passed. No files, locks, Unreal, build, or asset operations. Validator remains structural consistency checking, not runtime proof or authorization. X-1991 remains unresolved.
