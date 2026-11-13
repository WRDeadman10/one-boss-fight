# BK-176..180: runner status receipt v1.2 (closing A-844 findings A-D)

Assigned by X-2038 (lead Codex) to C (implementer), 2026-11-11. This is batch 2 of 20 in the 100-task lane. New files only:
- `Scripts/Tools/runner_status_receipt_proposal_v1_2.py`
- `Scripts/Tools/test_runner_status_receipt_proposal_v1_2.py`
- this report

v1, v1.1 and the X-2037 hotfix test are **unchanged**, while Antigravity's read-only audit continues.

**Proposal only and disconnected. A valid receipt is not runtime proof and not write authorization. X-1991 and C-1155 remain the gates.**

## Changes from v1.1 (schema `onebossfight.runner-status-receipt/v1.2`)

| Task | A-844 finding | v1.2 rule |
|---|---|---|
| BK-176 | **A:** non-PASS `pass_claims` only had to be strings, so `['dup','dup','','bad\nkey']` was accepted. | Non-PASS `pass_claims` must be a list of **unique, valid `UPPER_SNAKE` keys**. It may be empty. |
| BK-177 | **B:** FAIL and INCOMPLETE shared one branch, so FAIL with a retained lock, and INCOMPLETE with nothing incomplete, were both accepted. | The outcome is decided by the evidence (table below). `needs_operator` is still true exactly when a lock was retained, so it implies INCOMPLETE. |
| BK-178 | **C:** a directory-shaped `log.path` (`…/dir/`) was accepted, and duplicate detection was case-sensitive (`Build.log` vs `build.log`). | `log.path` must be a **file path**: no trailing `/`, and a last segment of the form `name.ext`. It must be inside the run's evidence folder, with no traversal, backslash or colon. Duplicates are compared with **`casefold()`**, matching Windows case-insensitive paths. |
| BK-179 | **D:** `log.sha256 = null` was accepted even on PASS with measured fields relying on that log. | A log that feeds **any measured field** must carry a valid SHA-256, in every outcome. On **PASS**, every process log must carry one. An unhashed (null) log is allowed only on FAIL or INCOMPLETE when no measured field relies on it, for example a timed-out process whose log could not be read. |
| BK-180 | Fuzz scope: only the PASS fixture, `processes[1]` and `fields[1]` were mutated. | The fuzz now covers **all three outcomes** × **every** key of the top level, `runner`, `run`, `lock` (including each list element), `failure`, **every** process and its `log`, **every** field, and each `pass_claims` element. |

### Outcome rules (BK-177)

| Evidence | Required outcome |
|---|---|
| All `pass_claims` measured, every process ended cleanly, every log fresh and hashed, no lock retained | **PASS** possible (with all v1.1 PASS rules) |
| A lock was retained, **or** any process `killed_timeout` / `not_started`, **or** no process ran | **INCOMPLETE** (needs a failure record; `needs_operator` = lock retained) |
| Otherwise: every process ended (`exited` or `killed_marker`), every lock released, but not PASS | **FAIL** (needs a failure record) |

A FAIL that meets an INCOMPLETE condition is refused with "report INCOMPLETE". An INCOMPLETE without one is refused with "report FAIL".

## Tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_runner_status_receipt_proposal_v1_2.py" -v` → **`Ran 12 tests ... OK`**.

| Class | Tests |
|---|---|
| `Baseline` (1) | PASS, FAIL and INCOMPLETE fixtures are valid; the schema is v1.2 and v1.1 is refused. |
| `Bk176NonPassClaims` (1) | 9 malformed claim lists (duplicates, empty string, multi-line, lowercase, space, integer, None, a bare string) are refused for both FAIL and INCOMPLETE; a valid non-empty list is accepted. |
| `Bk177FailVsIncomplete` (4) | A retained lock forces INCOMPLETE; a timeout, an unstarted process or no process forces INCOMPLETE; INCOMPLETE without a reason must be FAIL; the operator flag tracks retained locks only. |
| `Bk178LogFilePaths` (2) | 8 non-file or misplaced paths (trailing `/`, no extension, the folder itself, `.log` alone, traversal, file-then-slash, another folder, backslash); a nested `logs/suite_stdout.v2.txt` is accepted; `BUILD.LOG` duplicates `build.log`. |
| `Bk179LogDigests` (2) | A null digest on a measured log is refused on PASS and FAIL. An unused, unhashed log is accepted on INCOMPLETE and refused on PASS. |
| `Bk180Fuzz` (2) | **2,960 mutations** (3 outcomes × every nested key, plus list elements, × 17 bad values, including a calendar-invalid time, a 64-hex string and a directory path). **No exception.** The still-valid set is frozen per outcome, and every entry was reviewed against the exact values that kept it valid; the reasons are in the test. The purity check confirms no I/O. |

**Intended still-valid mutations:**
- any typed scalar measured value
- a key renamed to another valid key that is not claimed
- another valid digest
- free-text `command_id` and failure text
- `fields: []` on non-PASS
- an exit code of `-1`, or `0` on FAIL (a marker check failed)
- on INCOMPLETE, the timed-out, unused process may have a null, stale or unhashed log and a renamed role

Also checked:
- `py_compile` → OK; no trailing whitespace.
- The v1 (13), v1.1 (15) and v1.1 hotfix (3) suites still pass, unchanged.

## Limits

- Case-insensitive duplicate detection uses `str.casefold()`. Windows NTFS uses its own upcase table, so a few exotic Unicode pairs may differ. Runner log names are ASCII.
- `name.ext` with an extension of 1-8 characters is a convention check. It does not prove the path is a regular file; that is an executor attestation, like `written_after_start` and the digest itself.
- The outcome rules are a proposal for the lead. For example, a FAIL in which every process exited 0 is allowed, for a marker check that failed.
- Still disconnected; adoption follows the BK-170 stages and gates.
