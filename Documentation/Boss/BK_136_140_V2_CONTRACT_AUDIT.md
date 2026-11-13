# BK-136..140: audit of the proposed v2 receipt schema against the real executor contract

Assigned by X-2022 (lead Codex) to C (implementer), 2026-11-11. New files only: `Scripts/Tools/test_bk136_140_v2_contract_audit.py` and this report. The v2 proposal (`sevarog_receipt_v2_proposal.py`), its tests and report, and all production code are unchanged and only imported. The real `ExecutorContract` is driven with a stub binder; there is no file, Unreal, asset or lock access beyond test discovery.

**Proposal-only. A valid v2 receipt is not runtime proof and not write authorization. X-1991 is still open.**

## Method

**Exploration (BK-136/137).** A breadth-first search starts from `INIT` and applies every action with every input variant to every reachable contract state. There are 31 variants across the 9 transition methods:
- **`start`:** explicit or dry, approved or not, missing binding, unbound binding.
- **`plan_dry_run`:** accepted or refused.
- **`acquire_locks`:** full, partial, none created, a string instead of a list, a duplicate path, a bad token, the wrong party.
- **`verify_backup`:** ok, then a write refusal, then divergence; missing hash; asset changed; backup mismatch.
- **`plan_write`**
- **`record_save`:** true or false.
- **`readback`:** ok or bad.
- **`record_restore`:** match, mismatch, or None.
- **`release_locks`:** all, root only, none.

Wrong-state calls make no transition and are skipped. Contract states are deduplicated on everything the contract keeps: history, created locks, explicit flag, outcome, binding and locked snapshot. The first version left out the last two, which merged distinct futures and hid three paths; that is fixed. Result: **52 terminal runs** (44 released, 7 refused, 1 dry run), **26 distinct edges** and **16 distinct refusals**.

## Results (`Ran 15 tests ... OK` after the X-2023 addendum)

| Task | Test | Result |
|---|---|---|
| BK-136 | `test_every_observed_contract_edge_is_in_transitions` | No contract edge is missing from `TRANSITIONS`. |
| BK-136 | `test_every_transitions_edge_is_observed_in_the_contract` | No extra edge: all 26 `TRANSITIONS` edges are taken by the real contract. |
| BK-136 | `test_every_contract_terminal_history_is_legal`, `test_exploration_is_exhaustive_and_finite` | All 52 terminal histories pass `check_history`; all are at most 12 states long. |
| BK-137 | `test_every_source_refusal_site_maps_to_a_legal_stage_reason` | AST finds exactly **15** `_refuse` sites (contract `:85`, `:87`, `:98`, `:114`, `:120`, `:122`, `:124`, `:126`, `:133`, `:136`, `:147`, `:149`, `:152`, `:165`, `:168`). Each message prefix maps to one (stage, reason) in `P.REASONS`. |
| BK-137 | `test_every_observed_refusal_maps_to_its_stage_and_a_legal_reason` | Every refusal observed while exploring maps to the state it happened in. All **14** v2 reason codes are reached. |
| BK-137 | `test_every_refused_or_released_run_maps_to_the_receipt_refusal_stage` | `refusal_stage(history)` equals the stage of the contract's refusal message. |
| BK-137 | `test_finding_f1_…`, `test_finding_f2_…` | Findings F1 and F2 below (pinned as passing tests that show the behavior). |
| BK-138 | `test_enumeration_is_bounded_and_deterministic` | Depth-first enumeration of `TRANSITIONS` gives **18** legal histories, which is deterministic, has no duplicates, and stays within the length bound. **Every legal history is reachable by the contract.** |
| BK-138 | `test_every_legal_history_has_a_valid_consistent_receipt` | Each history gets a canonical receipt with all locks released, and each lock-holding history also gets one with a lock retained: **32 receipts, all valid**. Checks that terminal and outcome agree (`REFUSED` ⇔ `REFUSED_BEFORE_LOCKS`, `DRY_RUN_PLANNED` ⇔ `DRY_RUN_ONLY`, retained ⇔ `LOCK_RETAINED_NEEDS_OPERATOR`, `VERIFIED` ⇔ written, abandon states ⇔ `ABANDONED_NEEDS_OPERATOR`), that lock artifacts appear exactly when a lock is retained, and that `asset_needs_operator` appears exactly after `RESTORE_FAILED` or an abandoned release. |
| BK-138 | `test_contract_outcomes_agree_with_v2_except_the_abandoned_divergence` | `derive_outcome` equals `contract.outcome` for every released run, except the documented A6 divergence (`REFUSED_AFTER_LOCKS` → `ABANDONED_NEEDS_OPERATOR`). |
| BK-139 | `test_no_exception_and_fail_closed_for_every_nested_key` | **5116 mutations** cover 6 scenarios × every key of every record (top level, `source`, `asset`, `backup_attempt`, `refusal`, each lock, each artifact, each history element) × 16 bad values (None, list, dict, tuple, float, negative, 0, booleans, empty or wrong string, uppercase hash, NaN, inf, nested containers). **No exception.** All are refused except 3 intended cases (below). |

**Allowed still-valid mutations (BK-139, intended).** In the `partial_lock` refusal, `locks[0].readback_token`, `.party` and `.policy` may be null. A refusal during acquisition may have no lock-file readback (contract `:129-133`).

## Findings (no code changed; lead decisions)

| Id | Finding | Evidence | Options |
|---|---|---|---|
| F1 | A `TOKEN_INVALID` refusal that has created locks cannot be receipted. `_refuse` at `:126` runs after `created_locks` is recorded (`:118`), so the run ends `RELEASE_REQUIRED → RELEASED` with locks whose token is not 32-hex. v2 requires a 32-hex token on every created lock. | `test_finding_f1_token_invalid_with_created_locks_has_no_valid_receipt` drives the contract with token `"BAD"`. | (a) Allow a null or malformed token only for `TOKEN_INVALID`. (b) Require the executor to check the token before creating any lock, so the case cannot happen. |
| F2 | The contract never sets an outcome for a lock-free refusal. It stays `None`, or stays `DRY_RUN_ONLY` when a dry-run-mode contract (`:105-106`) is later refused at `acquire_locks`. | `test_finding_f2_lock_free_refusal_outcome_is_none_or_stale_dry_run`: refused runs have outcomes {None, DRY_RUN_ONLY}. | v2 already derives `REFUSED_BEFORE_LOCKS` from the history. A future executor must not copy `contract.outcome` for `REFUSED` runs, or the contract could set it. |

## Lead decisions (X-2023, 2026-11-11)

- **F1, option (b).** v2 keeps its strict 32-hex lock-token rule. A future executor must validate its run token **before any filesystem lock create**. If the token is invalid, it calls `acquire_locks` with `created_paths=[]`. The contract then refuses with no locks held (`:126`, state `REFUSED`), and the receipt is a valid `REFUSED_BEFORE_LOCKS` with reason `TOKEN_INVALID`.
  - `test_f1_decision_b_no_lock_token_invalid_receipt_validates` drives the real contract down this path and validates the receipt.
  - `test_f1_decision_b_keeps_the_strict_lock_token_rule` checks that the created-lock invalid-token run is still rejected for the tokens `BAD`, None, uppercase, and 31 characters.
  - Receipt lock identity is not weakened.
- **F2.** v2 derives `REFUSED_BEFORE_LOCKS` from a `REFUSED` history. A future executor must use this derived outcome and **never copy `contract.outcome`**, which may be None or a stale `DRY_RUN_ONLY`, into a receipt.

## BK-140: validation (exact)

- From `Scripts/Tools`:
  - `python -I -m unittest discover -s . -p "test_bk136_140_v2_contract_audit.py" -v` → `Ran 15 tests ... OK` (13 before the X-2023 addendum).
  - Neighbor suites pass, unchanged: v2 proposal 25/25, executor contract 16/16, receipt 13/13, adapter 14/14.
- `python -I -m py_compile Scripts/Tools/test_bk136_140_v2_contract_audit.py` → OK; no trailing whitespace.

## Limits

- The exploration covers the contract's control flow through 31 chosen input variants, not every possible input value. Refusal sites are additionally covered statically (AST, all 15).
- The stub binder decides plan acceptance from snapshot markers. Rules inside the real binder's planner are out of scope; they are covered by the binder and planner suites.
- The message-to-reason map (`REFUSAL_MAP`) matches on message prefixes. If a contract message changes, the AST test fails, which is intended.
- The mapping is proposal-level only: nothing connects the contract, an executor or the v2 module at runtime.
