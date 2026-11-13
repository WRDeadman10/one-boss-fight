# BK-166..170: risk ranking and a proposed status receipt for C-1155 runners

Assigned by X-2033 (lead Codex) to C (implementer), 2026-11-11. New files only:
- `Scripts/Tools/runner_status_receipt_proposal.py`: pure validator; disconnected, nothing imports it.
- `Scripts/Tools/test_runner_status_receipt_proposal.py`
- this report

No runner, process, lock, log, asset or Unreal access.

**Proposal only. A valid receipt is not runtime proof and not write authorization. X-1991 (owner) and C-1155 (engine locks) remain the gates.**

## BK-166: risks ranked by stale-success likelihood × consequence

Risk classes come from the source censuses BK-141..165. All are source-level possibilities, not observed runtime events.

| Rank | Risk (weight) | Runners | Why this weight |
|---|---|---|---|
| 1 | **Stale log marker** (5) | 6 | A previous run's success line can end the wait and pass a run that never produced it: a **false PASS**. |
| 1 | **Stale terminal status** (5) | 10 | An early failure leaves the previous run's status file in a fixed folder, so a reader sees the old result. |
| 3 | **Unmeasured no-save claim** (3) | 23 | A safety property ("no assets saved") is asserted without measurement, and it matters most on write runs. |
| 4 | **Lock-release bypass** (2) | 15 | An unguarded statement before release can strand both locks. This blocks other runs but does not fake success. |
| 5 | **Status without verdict** (1) | 32 | A failed run leaves a status file that does not say it failed. This misleads only a reader who skips the exit code. |
| 5 | **False lock evidence** (1) | 34 | `LOCKS_RELEASED=<created>`, or nothing. Evidence quality only. |

**Per-runner score** = the sum of the weights that apply. It is computed from the three census modules in `Bk166RiskRanking` and is deterministic.

| Score | Runners |
|---|---|
| 12 | `c1256a_live_self_test`, `c1258a_live_self_test`, `c1262a_live_diagnostic`, `c1265b_clip_trace` |
| 10 | `c1257b_locked_build`, `c1258a_locked_build`, `c1262a_locked_build`, `c1269a`, `c1274_area_effect`, `c1274_channel_drain` |
| 9 | 2 runners |
| 7 | 7 runners |
| 6 | 1 runner |
| 5 | 9 runners |
| 4 | 4 runners |
| 3 | 1 runner (minimum) |

The four live/PIE runners rank highest because they combine every high-weight risk except stale terminal status: a stale log marker, an unmeasured no-save claim, a release bypass, and no verdict. The weights are a judgment, recorded in the test so they can be changed in one place.

## BK-167: schema `onebossfight.runner-status-receipt/v1` (JSON)

| Section | Contents |
|---|---|
| `runner` | `script` (`Scripts/Editor/<name>.ps1`), `command_id` |
| `run` | `run_token` (32-hex), `started_utc`, `finished_utc` (UTC ISO-8601 ending in `Z`), `evidence_dir` (a safe path below `Docs/BossCombatReview/Execution/` whose **last segment contains the run token**) |
| `lock` | `token`, `policy` = `C-1155`, `party` (X, C or A), `created` (canonical order, root first), `released`, `retained` (per lock) |
| `processes[]` (at most 16) | `role` (unique, lowercase), `pid`, `started_utc`, `finished_utc`, `termination` (`exited`, `killed_timeout`, `killed_marker`, `not_started`), `exit_code`, `log` {`path`, `sha256`, `written_after_start`} |
| `fields[]` (at most 256) | `key` (unique `UPPER_SNAKE`), `kind` (`measured`, `unmeasured`, `config`), `value` (single-line string, integer, boolean or null; never NaN, never a float, never a `"True"`/`"false"` string), `source` (the process role for a measured field, otherwise null) |
| terminal | `outcome` (`PASS`, `FAIL`, `INCOMPLETE`), `failure` {`stage`, single-line `message`} (required when the outcome is not `PASS`; null on `PASS`), `needs_operator` (bool) |

`parse_receipt_text()` parses strictly: it refuses **duplicate JSON keys**, `NaN` and `Infinity`.

## BK-168: freshness and binding invariants (enforced by `validate_receipt`)

1. **One run token.** `lock.token == run.run_token`, an exact, case-sensitive comparison (fixes K1). The evidence folder's last segment contains the token, so the folder belongs to one run and is never reused (fixes the 18 fixed folders and the 3 shared ones).
2. **Process inside the run.** Every started process has a positive `pid` and satisfies `run.started ≤ process.started ≤ process.finished ≤ run.finished`. A `not_started` process claims no pid, times, exit code or log.
3. **Fresh, local evidence.** A measured field must name a listed process. That process's log must be inside `run.evidence_dir` and marked `written_after_start: true`; this fixes the stale log marker. The executor must establish this, for example by deleting the log before launch or comparing its modification time to the process start.
4. **Measured vs claimed.** Only `measured` fields satisfy `required_measured`. An `unmeasured` "no assets" literal can never stand in for a measured one (fixes the 23 unmeasured no-save claims).
5. **An explicit terminal outcome.**
   - `PASS` requires no failure record, at least one process, and no process with `killed_timeout` or `not_started`.
   - Every `exited` process on a `PASS` must exit 0.
   - `killed_marker` is allowed only together with invariant 3.
   - `FAIL` and `INCOMPLETE` require a failure record (fixes "no verdict", "nothing written on failure" and stale terminal status, because the folder is per-run).
6. **Per-lock release.** `released` and `retained` are disjoint, and together they list `created` exactly. `needs_operator` is true exactly when a lock was retained (fixes the false aggregate count).

## BK-169: validator and adversarial cases

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_runner_status_receipt_proposal.py" -v` → **`Ran 13 tests ... OK`**.

| Class | Covers |
|---|---|
| `ValidForms` (2) | `PASS`, `FAIL`, `INCOMPLETE` with a retained lock plus `needs_operator`, a fresh marker kill, a partial root-only acquisition; required measured keys. |
| `TerminalOutcome` (2) | 8 contradictions (for example `PASS` with a failure record, `FAIL` without one, `PASS` after a timeout or a non-zero exit, a multi-line failure message, a lowercase outcome); unmeasured claims never satisfy required keys. |
| `IdentityAndFreshness` (2) | Token binding: uppercase or different lock token, bad token, folder without the token. 8 stale or misplaced cases: stale log, log outside the run folder, measured field with no log, process before the run, inverted run window, unknown source, absolute folder, traversal. |
| `KeysAndTypes` (3) | Duplicate field keys, roles and JSON keys; 13 ill-typed values (boolean as a string, float, NaN, list, multi-line, lowercase key, pid as a string or bool, exit code as a bool, `needs_operator` as an int, freshness flag as a string, measured null, config with a source); strict JSON parsing. |
| `LockRelease` (1) | 8 inconsistencies (for example an unaccounted lock, released and retained at once, execution lock first, no lock, a retained lock without the operator flag and vice versa, foreign policy). |
| `FailClosed` (2) | Every key × 12 bad values: more than 400 mutations, **no exception**, all refused except 9 intended cases. Purity: the only imports are `json`, `math`, `re`, with no I/O names. |
| `Bk166RiskRanking` (1) | Deterministic ranking from the censuses; the top six are frozen; the minimum score is 3. |

**Intended still-valid mutations:**
- `fields=[]` on `INCOMPLETE`
- any string `command_id`, `failure.stage` or `failure.message`
- any typed scalar measured value
- an exit code of `-1`, because Windows codes can appear negative

Also checked:
- `py_compile` → OK; no trailing whitespace.
- A first version accepted `"True"` as a string value. The single-boolean-encoding rule was added, and it is tested.

## BK-170: staged adoption and gates

1. **Stage 0 (now):** the schema and validator stay disconnected. Nothing changes in the runners.
2. **Stage 1, reader-side:** add a pure converter from the existing `KEY=value` status files to a v1 receipt, with every field marked `unmeasured` unless a measurement is known. This makes today's gaps visible without changing the runners.
3. **Stage 2, one pilot runner:** with the lead's approval and a C-1155 lock, change one low-risk build runner to:
   - write a per-run token folder;
   - delete logs before launch;
   - record pid, timestamps and exit code;
   - write the receipt to a temp file and move it into place;
   - read it back and run `validate_receipt` on it.

   That requires a production edit and a locked build, so it needs the lead's assignment.
4. **Stage 3:** migrate the risk-ranked runners in order, highest score first: the 4 live/PIE runners, then the 6 fixed-folder build runners.
5. **Gates:**
   - No runner edit happens without a lead assignment.
   - Every launch follows C-1155: both lock files, no Unreal process, `-nosound`.
   - Any runner that **writes Sevarog data** stays behind owner decision **X-1991**.
   - A valid receipt never authorizes a write.

## Limits

- The receipt can only be as truthful as the executor that fills it in. The validator checks consistency, not that the claims happened. Freshness (`written_after_start`) in particular is an executor attestation.
- The weights in the ranking are judgment; the classes and counts come from the censuses.
- The schema covers runner status only. It is separate from the Sevarog executor receipt v1/v2 work (BK-112..140).
