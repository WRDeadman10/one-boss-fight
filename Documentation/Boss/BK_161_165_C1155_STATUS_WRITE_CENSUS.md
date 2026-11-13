# BK-161..165: how C-1155 runners write, encode, read back and parse status and evidence files

Assigned by X-2032 (lead Codex) to C (implementer), 2026-11-11. New files only: `Scripts/Tools/test_bk161_165_c1155_status_write_census.py` and this report.

**Source-only.** The 34 `.ps1` files under `Scripts/` that contain `owner_token` are read as text. Nothing is executed, and no file, lock, log or asset is touched.

`classify_writes()` is checked on synthetic runner text, then compared with tables frozen on 2026-11-11.

**Counts describe the source, not runtime behavior. Audit only, with no production edit. X-1991 is still open.**

## Correction applied to BK-156..160

The earlier BK-158 table counted **3** runners with an overall verdict field: `bk7`, `c1252a` and `c1253a`. That was wrong. In `c1252a` and `c1253a`, `SUCCESS=$success` is the **number of passed tests**, `(Select-String … 'Result={Success}').Count`, not a verdict. The lead corrected the BK-156..160 test and report as part of the BK-161..165 review.

- **Correct count:** **1** runner has a verdict field: `bk7` (`verdict` PASS/FAIL).
- **Knock-on:** "status written then may throw, with no verdict" becomes **32 of 32**, not 30.

`test_success_key_is_a_test_count_not_a_verdict` pins this correction.

## BK-161: atomic vs direct writes

| Method | Runners |
|---|---|
| `Set-Content` (overwrite) | 32 |
| `Set-Content`, then per-stage `Add-Content` appends | 1 (`bk2_x26`; it writes build/suite status first and then appends each PIE stage, so nothing is overwritten) |
| `[IO.File]::WriteAllText` (JSON receipt) | 1 (`bk7`) |
| Temp file + move into place (atomic) | **0** |

Every status or receipt write is direct. An interrupted write can leave a **truncated** file. In `bk2` it can leave a **partially appended** file, holding build/suite results plus only the stages completed so far, with no verdict.

## BK-162: encoding and key ambiguities

- **Encoding:** **33** runners write status without `-Encoding`, so the byte encoding depends on the PowerShell host and version. Only `bk7` writes UTF-8 explicitly, without a BOM.
- **Several pairs per line, and duplicate keys:** `c1265b_clip_trace` writes `"<move>_TRACE_START=…; FRAMES=…; MAX_LOCAL_SECONDS=…; FULL_CLIP=…"` once per move. So `FRAMES`, `MAX_LOCAL_SECONDS` and `FULL_CLIP` **repeat for every move**, and a `KEY=value` parser keeps only one of them.
- **Keys derived from marker text:** both `c1257a` runners build keys with `$item -replace '[^A-Za-z0-9]+','_'`. These keys are long and unstable: two markers that differ only in punctuation would collide.
- **Free-text value:** `bk56`'s `failure_status.txt` writes `ERROR=$($failure.Exception.Message)`. The message can contain newlines or `=`, which breaks line-based parsing.
- **Mixed boolean encodings:** **21** runners mix `True`/`False` (from `[bool]`, `.Contains()`, `HasExited`, `.Success`) with literal `1`/`0` in the same status.
- **Missing keys:** a key whose variable was never set, for example `PIE_EXIT` before PIE ran, is written as `KEY=` with an empty value. A reader cannot tell "not run" from "empty".

## BK-163: readback

**0 of 34** runners re-read or parse the status or receipt they wrote. Nothing verifies that the file on disk matches what was intended.

## BK-164: evidence parseability and missing or malformed files

- **27** runners call `Select-String … -ErrorAction SilentlyContinue`. A missing or unreadable log produces **zero matches**, not an error.
- **34 of 34** runners have a throw that fires when expected evidence is **absent**: `count -eq 0`, `!$flag`, `-not …`. Some are on one line and some in multi-line `if` blocks. **So a missing log fails the run instead of passing it.** This holds. The stale-log risk from BK-154 and BK-157 is different: there an old log is present, not missing.
- **9** runners guard log reads with `Test-Path`. `bk7`, which uses exit codes only, has neither silencing nor guards.
- **Malformed evidence:**
  - Status files are never parsed back (BK-163).
  - Lock JSON is parsed only at release, inside `try/catch` (BK-144).
  - `bk7`'s receipt is generated with `ConvertTo-Json -Depth 8`, so it is well-formed by construction, but nothing checks it.

## BK-165: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk161_165_c1155_status_write_census.py" -v` → **`Ran 9 tests ... OK`**.

| Class | Tests |
|---|---|
| `ClassifierSelfCheck` (1) | Synthetic runners check each detection: write method, an atomic temp+Move write with encoding and readback, a multi-line positive-evidence throw vs an exit-code-only throw, loop-repeated keys, free-text `ERROR`, mixed booleans. |
| `Census` (1) | 34 runners, deterministic. |
| `Bk161WriteAtomicity` (1) | Method counts 32 / 1 / 1; 0 atomic; `bk2` has 2 status writes. |
| `Bk162EncodingAndKeys` (3) | Explicit encoding only in `bk7`; multi-pair / repeated keys in `c1265b`; marker-derived keys in the two `c1257a` runners; free text in `bk56`; mixed booleans 21. The BK-158 correction (`SUCCESS` is a test count). |
| `Bk163Readback` (1) | 0 readbacks. |
| `Bk164EvidenceParsing` (2) | Silent `Select-String` 27, positive-evidence throws 34/34, no silent runner without one; `Test-Path`-guarded 9; `bk7` is the only runner with neither. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- A first single-line pattern missed multi-line `if` blocks and reported 3 runners with no positive-evidence throw. Those 3 do have one; the classifier now looks 5 lines ahead, and the synthetic check covers that case.

## Limits

- Regex classification of source text. "Fails closed on a missing log" means a matching throw condition exists. It does not prove every evidence variable is guarded.
- Encoding effects depend on the host: Windows PowerShell 5.1 and PowerShell 7 use different defaults. Which host runs each runner is not specified in the source.
- Truncated and partial writes are possibilities. They need an interruption at the exact write moment.
