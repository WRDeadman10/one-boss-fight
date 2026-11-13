# BK-66..70: read-only verifier for the BK-56..60 runner receipt bundle

Assigned by X-1993 (lead Codex) to C (implementer), 2026-11-11. New files only; no edits to the BK-56..60 runner or driver; no Unreal, build, PIE, assets or locks.

## Files

- `Scripts/Tools/verify_bk56_60_receipts.py`: verifier (CLI and `verify_bundle(folder)`).
- `Scripts/Tools/test_verify_bk56_60_receipts.py`: 17 synthetic-fixture tests in temp folders.

## Rules (BK-66..68)

The verifier reads only `status.txt`, `failure_status.txt`, `pie_exit.txt` and `lock_result.txt` from one `Run_<timestamp>` folder, plus `deferred_pie.log` if present, for one contradiction check. Field sets match what `run_bk56_60_deferred_selection.ps1` writes (success status at its "success status" stage; `failure_status.txt` in its `catch`; `pie_exit.txt` after the PIE process exits; `lock_result.txt` in `finally`).

| Outcome (exit code) | Meaning |
|---|---|
| `SUCCESS` (0) | Complete, consistent success receipt; `live_route=PASS`. |
| `FAILURE` (1) | Well-formed failure at a named stage; `live_route=NOT_PROVEN`. |
| `INVALID` (2) | Missing, malformed or contradictory receipts; `live_route=NOT_PROVEN`. |

Success requires all of the following:
- Exactly the 17 fields the runner writes.
- `BUILD_EXIT`, `SUITE_EXIT`, `FOCUSED_CONTRACTS_EXIT`, `PY_COMPILE_EXIT` and `PIE_EXIT` all `0`.
- `SUITE_STARTED > 0`, `SUITE_PASSED == SUITE_STARTED` and `SUITE_FAILED == 0`.
- `DD27J` a 64-hex hash.
- `PHASE_PREREQUISITE`, `ASSET_READBACK` and `DEFERRED_PIE` set to `PASS`.
- The four check flags set to `True`, and `NO_MAP_OR_OTHER_CONTENT_SAVES=1`.
- `pie_exit.txt` present and equal to the status `PIE_EXIT`.
- `LOCKS_RELEASED=2`.
- No `failure_status.txt`.
- No refusal marker (`outcome=ActivationRefused`, "activation refused", `[FrameworkEncounterAuthor] REFUSED`) in `deferred_pie.log`.

A refusal marker never yields success.

Failure requires all of the following:
- `STAGE` is one of the runner's nine stage names.
- `ERROR` is non-empty; multi-line exception text is accepted as a continuation of `ERROR`.
- `PIE_EXIT` is empty or an integer, and equals `pie_exit.txt` when both exist.
- A pre-PIE stage has no `pie_exit.txt`.
- No other fields, so a failure cannot claim `DEFERRED_PIE=PASS`.
- `lock_result.txt` is present with `LOCKS_RELEASED` in 0..2 (a lock-acquisition failure may release 0).

The following are always `INVALID`:
- Both receipts present.
- Neither receipt present.
- Duplicate keys.
- Lines without `=`.

## Fixtures (BK-69)

The positive cases cover:
- A complete success.
- A refusal with crash exit (`PIE_EXIT=1` plus a refusal marker), which is a `FAILURE`, never a pass.
- A pre-PIE exception (Development build failure, empty `PIE_EXIT`, no `pie_exit.txt`).
- A lock-acquisition failure with 0 locks.
- A multi-line `ERROR`.

The negative cases cover:
- A success with crash exit.
- A missing success field, or a nonzero `BUILD_EXIT`.
- A suite mismatch, a bad hash, or a `False` flag.
- A success with 1 lock, no lock record, no `pie_exit.txt`, or a mismatched `pie_exit.txt`.
- Success and failure receipts together.
- A success next to a refusal marker.
- A failure claiming `DEFERRED_PIE=PASS`.
- No receipt at all.
- In the failure-rule table: unknown stage, empty error, non-integer or mismatched `PIE_EXIT`, a pre-PIE stage with `pie_exit.txt`, missing or out-of-range lock record, duplicate key, missing `STAGE`, and a malformed success line.

There is also a CLI exit-code check (0, 1, 2), and a static read-only check: the verifier contains no write, open, subprocess, unreal, unlink, remove or rename call.

## Validation (BK-70, exact)

- `python -I -m unittest discover -s . -p "test_verify_bk56_60_receipts.py" -v` (from `Scripts/Tools`) → `Ran 17 tests ... OK`.
- `python -I -m py_compile verify_bk56_60_receipts.py test_verify_bk56_60_receipts.py` → OK.
- `test_bk61_65_refusal_shutdown_contract.py` (with the lead's F1/F2 decorators removed) → OK.
- `test_verify_*` group, from `Scripts/Tools` with `discover`: 51 run, 1 error, `test_verify_evidence_manifest`, which fails to import `Scripts.Tools` (pre-existing; it needs the repo-root package import). The baseline without my file has the same single error. Run by dotted module name from the repo root, three other pre-existing modules fail to import instead. The group mixes the two import styles, so neither invocation loads every module. The new module loads in both because it uses path-based import.
- `git diff --check` on both new files: clean.
- Real-folder sanity run: all 16 retained `Docs/BossCombatReview/Execution/Codex/BK_56_60/Run_*` folders → `INVALID live_route=NOT_PROVEN` ("neither status.txt nor failure_status.txt"). They predate the F1/F2 runner fix; none is read as a success.

## Limits

- `LOCKS_RELEASED` is the count of locks the runner created and attempted to remove (`$created.Count`), not proof that each file is gone. The verifier does not inspect lock files, by design (no lock access).
- The success rule requires `PIE_EXIT=0` as X-1993 specifies. Because the shutdown crash (BK-61) has so far appeared only after refusals, a future successful activation that still crashes at exit would be `INVALID`, not `SUCCESS`. That needs a lead decision if it happens.
- The verifier checks the receipts for internal consistency; it does not re-derive the runner's log-order checks. It only cross-checks `deferred_pie.log` for refusal markers.
- The first real post-fix bundle comes from the lead's next authorized C-1155 run; the verifier should be run on it then.
