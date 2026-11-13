# BK-131..135: receipt-to-stage map and a proposed v2 evidence schema

Assigned by X-2017 (lead Codex) to C (implementer), 2026-11-11. Reworked for X-2019 (review guidance) and X-2020/X-2021 (findings R1-R3); see "Rework" below. New files only:
- `Scripts/Tools/sevarog_receipt_v2_proposal.py`: a pure proposal module. Nothing imports it.
- `Scripts/Tools/test_sevarog_receipt_v2_proposal.py`
- this report

The v1 validator, adapter, executor contract, runner and receipts are unchanged.

**This is a proposal. A valid v2 receipt is not runtime proof and not write authorization. X-1991 is still open, and no real operation is allowed.**

Anchors:
- `C` = `Scripts/Tools/sevarog_executor_contract.py`
- `V1` = `Scripts/Tools/validate_sevarog_executor_receipt.py`
- `R` = `Scripts/Editor/run_bk56_60_deferred_selection.ps1`

## BK-131: current receipt fields vs execution stages

| Stage (contract) | Contract anchor | v1 receipt evidence | Ambiguity |
|---|---|---|---|
| start / bind | `C:81-91` (refusal → `REFUSED`) | none | **A1:** A lock-free refusal (state `REFUSED`) has no v1 outcome. `V1:10-11` has no such outcome, and `REFUSED_AFTER_LOCKS` needs at least one created lock (`V1:133-134`). Refusals at start, at dry plan, and acquisition with zero locks created (`R:24` aborts on an existing lock) cannot be receipted. |
| dry run | `C:93-107`, snapshot kept `:99` | `DRY_STEPS` `V1:18`; `before_sha256` must be null `V1:180-181` | **A2:** The dry snapshot hash that `C:148` later compares against is never recorded, so a dry-run receipt cannot show which asset state was reviewed. |
| lock acquisition | `C:109-139`; locks recorded `:118` before the refusals at `:119-136` | `REFUSED_STEPS[0]` (`locks_acquisition_partial`, 1 created) or `[1]` (`locks_verified`, 2 created), `V1:29-34`, `:173-178` | **A3:** A run that created both locks but was then refused (`:121-124` explicit write or approval, `:125` token, `:129-133` readback, `:134-136` identity) can only claim `locks_verified`, which is false. The reason is lost. |
| lock order | `C:118` keeps the given order | either lock may be the single created one (`V1:94-98`, `:174-176`) | **A4:** The runner creates root then execution and stops at the first throw (`R:74-79`), so a lone execution lock is impossible, yet v1 accepts it. Release iterates creation order (`R:206-209`). |
| backup | `C:141-156`: missing before-hash `:147`, asset changed `:149`, backup mismatch `:152` | all three map to `backup_refused` (`V1:32`), and no backup data may be claimed (`V1:189-190`) | **A5:** The three refusal reasons cannot be told apart. A rejected backup copy that is still on disk cannot be recorded. `before_sha256` (`V1:183`) can be either the dry hash or the locked hash. A missing dry `file_sha256` (`C:99`, not checked) surfaces at `:148` as "asset changed". |
| write plan | `C:158-171`: refused `:165`, diverged `:168` | `write_plan_refused` (`V1:33`) | Refused and diverged cannot be told apart (part of A5). |
| save | `C:173-182`: a failed save goes to `RESTORE_REQUIRED` without `SAVED` | `RESTORED_STEPS` / `RESTORE_FAILED_STEPS` always contain `save` and need a 64-hex `after_sha256` (`V1:21-28`, `:201`) | **A7:** A failed save cannot be receipted truthfully, because it must claim a save step and an after hash. |
| readback / restore | `C:184-203` | `restored_sha256` rules `V1:205-215` | Covered (BK-126..130). |
| release | `C:205-225`, allowed from any lock-holding state `:207` | retained forms only after `readback_verified` or `restore_failed` (`V1:23-26`) | **A6:** Releasing early from `WRITE_PLANNED`, `SAVED` or `RESTORE_REQUIRED` gives `REFUSED_AFTER_LOCKS` (`:222-223`) although the asset may already be written (confirmed by test). **A8:** A lock retained after `RESTORED` or after a refusal has no v1 step form. |

## BK-132: v2 schema (`onebossfight.sevarog-executor-receipt/v2`)

Top-level keys: `schema, outcome, source, plan_sha256, history, refusal, asset, backup_attempt, locks, artifacts`.

- **`history`:**
  - Holds the contract's own state list (`ExecutorContract.history`). Every adjacent pair must be a contract transition (`TRANSITIONS` mirrors each `_move`, `_refuse` and the `:207` release). It must start at `INIT`, end in `DRY_RUN_PLANNED`, `RELEASED` or `REFUSED`, and have at most 12 states.
  - This fixes A3, A5, A7 and A8: a failed save shows `WRITE_PLANNED → RESTORE_REQUIRED`, a retained lock after a restore shows `RESTORED → RELEASED`, and so on.
- **`outcome`:**
  - Derived from history and lock release by `derive_outcome`, a mirror of `C:205-223`, and must match the claim.
  - Two new outcomes:
    - `REFUSED_BEFORE_LOCKS` (A1).
    - `ABANDONED_NEEDS_OPERATOR`: a release from `WRITE_PLANNED`, `SAVED` or `RESTORE_REQUIRED` (A6). This is a deliberate divergence from the contract and is pinned by a test.
  - v2 outcomes are a strict superset of v1.
- **`refusal`:**
  - Shape is `{stage, reason}` and it is required exactly when the history shows a refusal or an abort.
  - `stage` is derived from history. `reason` comes from a closed code set per stage (`REASONS`) that mirrors each contract refusal site. `EXECUTOR_ABORTED` covers a release with no refusal.
- **Three hash meanings, kept apart (X-2019):**
  - `source.sha256`: the Owner mailbox body.
  - `asset.dry_run_sha256`: the asset snapshot reviewed in the dry run.
  - `asset.locked_before_sha256`: the asset snapshot under the locks.

  Equality of the last two is a concurrency check (`C:148`), not interchangeable provenance.
- **`asset`:**
  - **`dry_run_sha256`:** required once `DRY_RUN_PLANNED` is reached (A2).
  - **`locked_before_sha256`:** set only once the locked snapshot was compared (`BACKED_UP`, `ASSET_CHANGED`, `BACKUP_MISMATCH`). It must equal the dry hash, except under `ASSET_CHANGED`, where it must differ (A5).
  - **`after_sha256`:** 64-hex exactly when `SAVED` is in the history (A7).
  - **`restored_sha256`:**
    - After `RESTORED`, it must equal the before-hash.
    - After `RESTORE_FAILED`, it may be null (no readback; the contract records `RESTORE_FAILED` for any non-match, including `None`, `C:195-203`) or a 64-hex hash other than the before-hash.
    - Otherwise it must be null.

## BK-133: backup lifecycle and leftover evidence

`backup_attempt` records each observation separately (X-2019, X-2020):

| Field | Values | Meaning |
|---|---|---|
| `attempted` | bool | the executor tried to make a copy |
| `copy_result` | `created` / `failed` / `unknown`, or null when not attempted | the copy operation's result |
| `path` | safe path below `Docs/BossCombatReview/Execution/`, or null | the copy's target |
| `observed_sha256` | 64-hex, or null when not read | hash read from the copy (only a created copy may have one) |
| `verified` | bool, must equal "`BACKED_UP` in history" | the contract accepted the copy |
| `cleanup_attempted` | bool | the run tried to remove the copy |
| `cleanup_readback` | `absent` / `present` / `not_observed` | what a later check of the path showed |
| `final_state` | derived, must match the claim | see below |

Rules:
- **When required:** once `LOCKED` is reached. `attempted: false` is allowed only for `BEFORE_HASH_MISSING` or an abort before `BACKED_UP`, and then it may claim no copy, cleanup or readback.
- **A verified backup** is a created copy whose observed hash equals the locked before-hash. It cannot be cleaned up by the run, because it is the restore source.
- **`BACKUP_MISMATCH`:** the observed hash differs from the before-hash, or is null.
- **`final_state`** is derived by `backup_final_state`. Removal is claimed only with an observed-absent readback:
  - `none`: not attempted, or a failed copy observed absent.
  - `kept_evidence`: created and not cleaned up.
  - `removed`: cleanup attempted and readback `absent`.
  - `retained`: cleanup attempted and readback `present`.
  - `unknown`: cleanup attempted but not observed, or a failed or unknown copy without an absent readback.

  "No copy" (`none`) and "copy removed" (`removed`) are distinct.

`artifacts`: at most 4 entries, order does not matter. They must equal the derived set exactly:
- one `lock` entry per retained lock
- one `backup` entry when `final_state` is `retained` (with the observed hash) or `unknown` (null hash)
- one `asset_needs_operator` entry after `RESTORE_FAILED` or an abandoned release. Its hash is the post-restore readback when one exists; otherwise null (unknown). The pre-restore `after_sha256` is never used as current-state evidence (X-2021).

## BK-134: lock ordering

- **Acquisition order is explicit, not inferred from the array index (X-2019).** The `locks` array stays in canonical `LOCK_PATHS` order for lookup. Each record carries `create_order` (1 or 2; null when not created), and the created locks must be numbered 1..n with no gaps or repeats.
- **Root must be first.** The contract itself accepts `created_paths` in caller order (`C:113-118`), so this rule is a proposed executor requirement. It matches the runner, which creates root first and throws on the first failed move (`R:74-79`).
- **Partial refusal.** The only legal partial receipt is root created with order 1. A run that reached `LOCKED` created both. Refusals during acquisition may show a missing or foreign readback token, party or policy (`C:129-136`).
- **Release order stays unordered by design.** Every created lock must show `release_attempted` (the executor's finally block), and `released` must equal `release_token_match`. The order is not recorded, because each release is token-guarded and independent. The runner attempts every created lock regardless of the others (`R:206-209`), and no state depends on which lock is deleted first.

## BK-135: tests (25, synthetic): `python -I -m unittest discover -s . -p "test_sevarog_receipt_v2_proposal.py"` → `Ran 25 tests ... OK`

| Class | Covers |
|---|---|
| `ValidForms` | All 18 scenarios are valid with their expected outcome; every v2 outcome is reachable. |
| `Bk131HistoryAndOutcome` | 9 illegal histories; wrong or unhashable claimed outcomes; refusal record vs history (8 cases). |
| `Bk132AssetHashes` | Staging of the dry and locked hashes; locked-vs-dry relation; after and restored hashes follow history. Includes the R3 regression: `RESTORE_FAILED` with an unknown readback is valid, its artifact hash is null, and substituting the after-hash is refused. The real contract is driven with `record_restore(None)`. |
| `Bk133BackupAndArtifacts` | Backup presence by stage. R1 regression: 8 backup fields and `create_order` × malformed values (lists, dicts, floats, bools, wrong strings) are invalid, not exceptions. R2 regression: 8 observation combinations, each with its derived `final_state`; every other claimed state is refused; an unobserved "removed" claim is refused; none vs removed. 11 record rules; exact artifact sets. |
| `Bk134LockOrder` | Explicit `create_order` (root first, numbered 1..n, null when not created); locked runs need matching readback; refusals may show a foreign readback; release attempted for every created lock; shared token and party. |
| `Bk135ContractCompatibility` | Drives the **real** `ExecutorContract` with a stub binder over 8 runs. Contract histories pass `check_history`, and `derive_outcome` equals `contract.outcome`. Pins the A6 divergence. Constants match the contract and v1. v1 and v2 refuse each other's receipts. |
| `Purity` | Malformed top-level values (each key × 5 values) are invalid, not exceptions; input is not mutated; AST shows the only import is `re`. |

Validation:
- `python -I -m py_compile` on both files → OK; no trailing whitespace.
- Existing suites are unchanged and not affected (new files only).

## Rework (X-2019..X-2021)

- **R1** (`disposition` raised `TypeError` on a list): every enum field now goes through `_enum`, a type-guarded membership check. Flags are type-checked before use.
- **R2** (the backup state mixed up "no copy" with "deleted" and accepted a deletion claim with no evidence): the backup is now recorded as separate observations, and its final state is derived from them. Removal is claimed only with an observed-absent readback.
- **R3** (`RESTORE_FAILED` needed a hash; the artifact reused the pre-restore hash): a null restored hash is now accepted, and the artifact hash is the post-restore readback or null.
- **X-2019:** the three hash meanings are documented; lock order comes from an explicit `create_order`.

## Limitations

- The v2 reason codes are assigned by the executor. The receipt cannot prove that the code matches the contract's actual refusal message. A future adapter could map `contract.errors[-1]` to a code.
- Observations (`copy_result`, `cleanup_readback`, `observed_sha256`) are the executor's claims; the schema can only check that they are consistent with each other.
- `TOKEN_INVALID` with created locks is representable only with a 32-hex token. A real executor generates the token itself, so this combination should not occur.
- Proposal and contract can drift: the cross-check covers 8 driven runs and the `HOLDS_LOCKS` set, not every refusal site.
- **Rollout** is a lead decision. Rolling out v2 would need: a v2-aware adapter, executor emission of `history`, and a decision on A6, either changing the contract's outcome or accepting the divergence. v1 receipts are never upgraded in place, because the dry hash and refusal reason cannot be recovered.
