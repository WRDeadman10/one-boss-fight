# BK-211..215: strict stage/evidence diagnostics for PIE_EXIT in the BK-56..60 receipt verifier

Assigned by X-2060 (lead Codex) to C (implementer), 2026-11-12. This is batch 9 of 20.
- **SOURCE CHANGED:** `Scripts/Tools/verify_bk56_60_receipts.py` (8 changed lines, in `verify_failure`).
- **New:** `Scripts/Tools/test_bk211_215_verifier_stage_evidence.py`.

**These are strict evidence diagnostics, not false-success fixes.** A-854 showed that both asymmetries already ended as FAILURE / NOT_PROVEN. No real log, lock, asset, Unreal, build or PIE was involved. X-1991 is still open.

## BK-211: stage/evidence matrix, from the runner source

In `Scripts/Editor/run_bk56_60_deferred_selection.ps1`:
- `$pieExit` starts as `$null` (`:34`).
- In the `deferred PIE` stage (`:145`), after the PIE process exits, the runner sets `$pieExit` **and** writes `pie_exit.txt` together (`:161-162`).
- The failure record writes `PIE_EXIT=$pieExit` (`:198`).

So:

| Stage | `PIE_EXIT` field | `pie_exit.txt` | Verifier result |
|---|---|---|---|
| Pre-PIE (lock acquisition … encounter author/readback) | empty | absent | FAILURE |
| Pre-PIE | **non-empty** | any | **INVALID** (BK-213) |
| Pre-PIE | empty | present | INVALID (existing rule) |
| `deferred PIE`, before PIE exited | empty | absent | FAILURE |
| `deferred PIE`, after PIE exited | `n` | `PIE_EXIT=n` | FAILURE |
| `deferred PIE` or later | **non-empty** | **absent** | **INVALID** (BK-212) |
| `deferred PIE` or later | empty | present | INVALID (existing rule) |
| any | `n` | `PIE_EXIT=m`, m ≠ n | INVALID (existing rule) |

## BK-212 / BK-213: new checks (`verify_failure`)

- **BK-212.** A non-empty `PIE_EXIT` with no `pie_exit.txt` is refused: "failure_status.txt PIE_EXIT=<n> has no pie_exit.txt receipt (the runner writes both together)". It is not repeated when `pie_exit.txt` exists but is malformed, which is already reported.
- **BK-213.** A non-empty `PIE_EXIT` on a pre-PIE stage is refused: "pre-PIE failure stage '<stage>' must have an empty PIE_EXIT (PIE never ran)".

**Before and after**, checked against a copy of the verifier saved before the edit:

| Case | Before | After |
|---|---|---|
| A-854: `deferred PIE`, `PIE_EXIT=1`, no file | FAILURE, `errors=[]` | **INVALID** with the BK-212 message |
| A-854: `Development build`, `PIE_EXIT=0`, no file | FAILURE, `errors=[]` | **INVALID** with the BK-213 message |
| Also covered: `Content asset delta verification`, `PIE_EXIT=0`, no file | FAILURE | INVALID |

`live_route` stays `NOT_PROVEN` in every case.

## BK-214: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk211_215_verifier_stage_evidence.py" -v` → **`Ran 6 tests ... OK`**.

| Class | Tests |
|---|---|
| `Bk211StageEvidenceMatrix` (1) | All 13 rows of the matrix: outcome, `live_route`, and the exact diagnostic, or no errors for well-formed failures. |
| `Bk212Bk213Reproductions` (3) | Both A-854 cases with their exact messages; a malformed `pie_exit.txt` is not double-reported. |
| `Bk214ExistingClassificationsStayFailClosed` (2) | The original well-formed failures are still FAILURE. All 9 stages × 5 `PIE_EXIT`/file combinations yield only FAILURE or INVALID, never SUCCESS or a proven route. `EXIT_CODES` is unchanged (0 / 1 / 2). |

Neighbour suites:
- The existing `test_verify_bk56_60_receipts.py` still passes, unchanged.
- `python -m unittest discover -s Scripts/Tools -p "test_verify_*.py"` → OK (1 skip). As A-854 noted, the `-I` flag cannot resolve the `Scripts.Tools` package import in one of those modules; that is unrelated to this change.
- `py_compile` OK; the verifier keeps its CRLF endings, consistently.

## BK-215: limits

- The verifier is still a read-only checker of receipt text. It does not prove that the runner wrote the files, or when.
- These rules mirror runner lines `:34`, `:145`, `:161-162` and `:198`. A runner change would need the matrix updated; the line anchors are recorded here.
- Reclassifying FAILURE to INVALID for these cases is deliberate: contradictory or incomplete evidence is now flagged as a bad receipt, not accepted as a clean failure.
