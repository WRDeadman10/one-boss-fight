# BK-171..175: runner status receipt v1.1 (stricter timestamps, PASS claims, identities, contradictions)

Assigned by X-2034 (lead Codex) to C (implementer), 2026-11-11. This is the first batch of the 100-task lane. New files only:
- `Scripts/Tools/runner_status_receipt_proposal_v1_1.py`
- `Scripts/Tools/test_runner_status_receipt_proposal_v1_1.py`
- this report

v1 (`runner_status_receipt_proposal.py`, its tests and the BK-166..170 report) is **unchanged**, because Antigravity is reviewing it independently under X-2035.

**Proposal only and disconnected. A valid receipt is not runtime proof and not write authorization. X-1991 and C-1155 remain the gates.**

## Changes from v1 (schema `onebossfight.runner-status-receipt/v1.1`)

| Task | v1 behavior | v1.1 rule |
|---|---|---|
| BK-171 | Timestamps were accepted by regex and compared **as strings**. `2026-02-30T12:00:00Z` passed, and `"12:05:10.5Z" < "12:05:10Z"` as strings even though it is later in time. | `parse_utc()` requires a **calendar-valid** `YYYY-MM-DDTHH:MM:SS[.f{1,7}]Z`. It refuses impossible dates (Feb 30, Feb 29 in a non-leap year, month 13), `24:00`, minute 60, leap second `:60`, more than 7 fractional digits, offsets other than `Z`, and a space separator. All window checks compare parsed values, including the 7th fractional digit. |
| BK-172 | PASS needed only the caller's optional `required_measured` keys, which could be empty. | New top-level **`pass_claims`**: a list of keys. A **PASS requires a non-empty list of unique claims, each a measured field**, plus any caller-required keys. FAIL and INCOMPLETE may carry `[]`, but it must still be a list. |
| BK-173 | Roles were unique; PIDs and log paths were not checked. | **PIDs are unique** among started processes. **Log paths are unique** across processes. A measured field must name a **started** process; `not_started` is refused as a source. |
| BK-174 | PASS was refused for a timeout, `not_started` or a non-zero exit. | PASS is also refused when **any lock is retained** (report INCOMPLETE with `needs_operator`), and when **any process log is not proven fresh**, even a log no claim uses. `killed_marker` requires an existing, fresh log in **every** outcome. |

All v1 invariants carry over unchanged:
- the exact, case-sensitive run token in lock and run;
- the per-run evidence folder containing the token;
- processes inside the run window;
- measured fields only from fresh logs inside the folder;
- typed, unique `UPPER_SNAKE` fields with no boolean-spelled strings;
- per-lock `released` + `retained` = `created`, root first;
- `needs_operator` set exactly when a lock is retained;
- strict JSON parsing with no duplicate keys and no NaN.

## BK-175: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_runner_status_receipt_proposal_v1_1.py" -v` → **`Ran 15 tests ... OK`**.

| Class | Tests |
|---|---|
| `Baseline` (2) | PASS, FAIL, INCOMPLETE with a retained lock and the operator flag, a fresh marker kill. The schema is v1.1: a v1 schema string, or a receipt without `pass_claims`, is refused. |
| `Bk171CalendarTimestamps` (3) | 4 accepted and 14 refused values. Parsed ordering is shown on the string trap (`12:05:10.5Z` vs `12:05:10Z`), down to a 100 ns boundary. An invalid time is refused in each of the run and process start/finish fields. |
| `Bk172PassClaims` (3) | Six PASS-claim failures: empty, missing, not a list, repeated, an unmeasured claim, an absent key. Caller keys are added to the declared set. A non-PASS receipt with empty claims passes, but `pass_claims: None` is refused. |
| `Bk173Identities` (3) | A duplicate PID, a shared log path, a repeated role; a measured field from a process that never started; `not_started` processes do not use up PIDs. |
| `Bk174Contradictions` (2) | 11 contradictions: PASS with a failed process, after a timeout kill, after a marker kill on a stale log, with an unused stale log, with a retained lock, with an operator flag on a clean run, with a failure record; a marker kill with no log; INCOMPLETE without a failure record; `exited` without an exit code; an exit code given as a boolean. The messages are checked to be specific. |
| `FailClosed` (2) | **438 mutations** of every key, including the `log` sub-object, × 13 bad values, including a calendar-invalid timestamp. **No exception.** The exact still-valid set is 7 intended cases: any typed scalar measured value, and a null log `sha256`. Purity: the only imports are `json`, `math`, `re` and `datetime`/`timezone`, with no `now`/`utcnow` and no I/O. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- The v1 suite `test_runner_status_receipt_proposal.py` still passes, unchanged.

## Exact invariants (v1.1)

1. Every timestamp is calendar-valid UTC with a `Z` suffix. Order is decided by parsed value: `run.start ≤ proc.start ≤ proc.finish ≤ run.finish`.
2. **PASS** requires all of the following:
   - non-empty unique `pass_claims`, each a measured field;
   - every caller-required key measured;
   - at least one process;
   - no `killed_timeout` or `not_started` process;
   - every `exited` process exits 0;
   - every process log is fresh;
   - no lock retained;
   - no failure record;
   - `needs_operator` false.
3. **FAIL / INCOMPLETE** need a single-line `failure` record and a list `pass_claims`, which may be empty.
4. Identity: roles, PIDs (of started processes) and log paths are each unique, and a measured `source` names exactly one started process.
5. `killed_marker` always requires a fresh log.

## Limits

- Freshness (`written_after_start`) and the observations themselves are attested by the executor. The validator checks only that they are consistent with each other.
- Leap seconds cannot be represented, because `:60` is refused; UTC timestamps from Windows do not produce them.
- PID uniqueness is per receipt. The OS can reuse a PID after a process exits, so two sequential processes with the same PID would be refused even though that is legitimate. This is a deliberate trade-off for unambiguous binding, and the executor should then record distinct roles with their start times. It is up to the lead to keep or relax this.
- Still disconnected: no runner writes v1.1. Adoption follows the BK-170 stages and gates.

## X-2037 hotfix (2026-11-11)

- **The bug:** `validate_receipt` iterated the caller's `required_measured` argument without checking it. `None`, an integer, or a mixed collection could raise `TypeError`, either during iteration or in `sorted(missing)`.
- **Fix:** `required_measured` must be a list, tuple, set or frozenset of `UPPER_SNAKE` strings. Anything else returns `valid: false` with the single error "required_measured must be a list/tuple/set of UPPER_SNAKE keys", and the receipt is not inspected further. Well-formed collections are de-duplicated and sorted before use.
- The module docstring now names the schema `v1.1`.
- **Regressions** (`Scripts/Tools/test_runner_status_receipt_v1_1_hotfix.py`):
  - 18 malformed requirement values, each against both a PASS and a FAIL receipt: invalid, no exception.
  - 9 well-formed collections still validate.
  - The docstring check.
  - Result: `Ran 3 tests ... OK`. The v1.1 suite is still 15/15 and v1 13/13.
