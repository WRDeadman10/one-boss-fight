# BK-191..195: closing A-848 fail-open edges in the Sevarog planner, contract and receipt validator

Assigned by X-2042 (lead Codex) to C (implementer), 2026-11-12. This is batch 5 of 20. **SOURCE CHANGED**; source-level validators only, with synthetic regressions.

**No executor was invoked. No lock, asset, Unreal, build or PIE was touched. Proposal and read-only behavior and every existing gate are preserved. X-1991 still blocks authoring.**

## Changes

| Task | File | Change |
|---|---|---|
| BK-191 | `Scripts/Tools/plan_sevarog_definition_repair.py`, `verify_readback` | The after-readback must show **`exists is True`** and a **valid 64-hex `file_sha256`** before the saved object is accepted. Previously a missing or `None` after-hash passed, because it only had to differ from the before-hash. Each failure routes to `restore_backup_then_release_locks`. |
| BK-192 | planner `plan_repair` / `verify_readback`; `Scripts/Tools/sevarog_executor_contract.py` `plan_dry_run` / `plan_write` | The plan now records **`untouched_phase_snapshot`**, a deep copy of every complete non-Phase_1 row. The readback compares the complete rows against it, not only `phase_id`, and a plan without a snapshot fails closed. The contract stores the reviewed snapshot from the dry run and refuses a write plan whose snapshot differs. The id list `untouched_phase_rows` is kept for compatibility. |
| BK-193 | planner `plan_repair` | A write-mode `owner_token` must match **`[0-9a-f]{32}`** (`OWNER_TOKEN`), the same rule as the contract's lock acquisition (`TOKEN`). Dry runs still need no token. |
| BK-194 | planner (`safe_backup_path`, `BACKUP_PREFIX`) and contract (`_safe_backup_path` in `verify_backup`) | The backup path must be **below `Docs/BossCombatReview/Execution/`**, with no backslash, colon, control character or empty, `.` or `..` segment. This is the receipt validator's rule. The planner reports an unsafe path and a hash mismatch independently. The contract keeps a local copy, so injected test binders need no planner attribute. All three copies are parity-tested. |
| BK-195 | `Scripts/Tools/validate_sevarog_executor_receipt.py` | A `REFUSED_AFTER_LOCKS` **partial-acquisition** receipt is refused when the **execution lock was created without the root lock**. Acquisition is root first (runner `:74-79`; v2 `create_order`). A root-only partial stays valid. |

**Changed lines, measured against pre-change copies:** planner 38, contract 18, receipt validator 5. While patching, a script briefly rewrote the planner and receipt validator from LF to CRLF. Both were restored to LF, so the diffs above are only the intended edits.

## Existing tests updated for intended behavior (fixtures only, no weakened assertion)

- **Planner, binder and contract fixtures:**
  - `"t0k3n"` and `"tok"` were replaced by a 32-hex token.
  - The backup path `backup/…` was replaced by `Docs/BossCombatReview/Execution/Claude/backup/…`.
  - Files: `test_plan_sevarog_definition_repair.py`, `test_bind_owner_approval.py`, `test_sevarog_executor_contract.py`, `test_sevarog_executor_contract_adversarial.py`.
- **`test_bk126_130_receipt_refusal_adversarial.py`:** the partial-lock test previously accepted either lock as the lone created one. It now accepts root-only and asserts that execution-only is refused (BK-195).
- **`test_bk136_140_v2_contract_audit.py`:** the contract now has **16** `_refuse` sites instead of 15. The new backup-path refusal maps to the existing `LOCKED` / `BACKUP_MISMATCH` reason, so the v2 reason table did not change.

## Tests and results

From `Scripts/Tools`:

| Suite | Result |
|---|---|
| **New: `test_bk191_195_validator_hotfixes.py`** | **16/16 OK** (no skips) |
| planner | 12 |
| contract | 16 |
| contract adversarial | 12 |
| receipt | 13 |
| receipt adversarial | 12 |
| BK-126 refusal | 29 |
| binder | 11 |
| receipt-source adapter | 14 |
| v2 proposal | 25 |
| BK-136 v2 contract audit | 15 |

All pass. `py_compile` OK; no trailing whitespace.

New regression coverage:
- **BK-191:** `exists` set to False, None, `"true"`, 1 or absent; after-hash None, empty, uppercase, 63 characters, an int or a list.
- **BK-192:** the snapshot is a deep copy; a changed value under the same `phase_id` is refused; a plan without a snapshot fails closed; the contract refuses a snapshot that differs from the dry run.
- **BK-193:** 7 bad tokens are refused and a valid one passes; a dry run needs no token; the planner rule matches the contract rule.
- **BK-194:** 13 paths give the same verdict in all three modules; the planner reports a bad path and a bad hash separately; the contract refuses unsafe paths.
- **BK-195:** execution-without-root is refused; root-only stays valid; lock order matches v2.

**Full `Scripts/Tools` sweep:** 24 test modules fail or cannot be imported in unrelated areas: encounter-manifest, tier-2 hooks, retarget docs, and several modules whose imports fail. **None of their files references the planner, the contract or the receipt validator**, so these failures are independent of this batch. Whether they pass on HEAD was not checked here. They were not caused by, or changed by, this batch.

## Limits

- These remain synthetic contract checks. No executor exists, and nothing here authorizes a write; X-1991 is still open.
- The three backup-path rule copies are kept identical by a parity test, not by sharing one import. This was a deliberate choice to keep the contract independent of the binder's planner attribute.
