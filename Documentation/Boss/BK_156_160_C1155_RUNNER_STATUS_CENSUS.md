# BK-156..160: status fields, success markers, terminal status and run binding in C-1155 runners

Assigned by X-2031 (lead Codex) to C (implementer), 2026-11-11. New files only: `Scripts/Tools/test_bk156_160_c1155_runner_status_census.py` and this report.

**Source-only.** The 34 `.ps1` files under `Scripts/` that contain `owner_token` are read as text. Nothing is executed, and no lock, log, temp file or asset is touched.

`classify_status()` is checked on a synthetic runner. Its results are compared with tables frozen on 2026-11-11, and it reuses the BK-151..155 census read-only for fixed vs per-run folders.

**Counts describe the source, not runtime behavior. Audit only, with no production edit. X-1991 is still open.**

## BK-156: status / receipt fields and what they claim

- **Formats:**
  - 33 runners write a `KEY=value` status text file built from a string, array or list.
  - `run_bk7_shipping_pipeline` writes a JSON receipt with artifact hashes, check exit codes, `source_head` and `verdict`.
- **Measured fields:** fields such as `BUILD_EXIT`, `SUITE_EXIT`, `STARTED`, `PASSED`, `FAILED` and `COMPLETE` carry the process exit codes and the marker counts from the logs.
- **Literal fields:** 29 runners write at least one field whose value is a **literal**, not a measured variable. A separate 25 echo the constant `DD27J=<manifest hash>`; that is an input pin, not a result.
- **No-save claims:**
  - **28** runners write a literal no-save or no-asset claim: `NO_ASSETS=1` (18 runners), `MAP_SAVED=0`, `NO_ASSET_SAVES=1`, `NO_PACKAGES_SAVED=1`, `SAVED_ASSET_COUNT=0`, `SAVED_ASSETS=0`, `NO_MAP_OR_OTHER_CONTENT_SAVES=1`.
  - Only **5** of them contain a related check: a content-state hash, a saved-package counter, or a `saves=0` marker. They are `be_x26_x30`, `bk56_60`, `c1257a_dry_run`, `c1275a` and `c1280_x26`.
  - **23** assert the claim with nothing in the script that measures it.
- **Other literals** describe configuration rather than outcome: for example `LOCKED=1`, `NO_PIE`, `PIE_SCOPE`, `REQUESTED_RANGE_CM=140`, `ASSET_ALLOWLIST`, and `bk56`'s `*=PASS` fields. `bk56` reaches those only after its preceding checks pass.

## BK-157: success markers, freshness and current-run correlation

- **165** marker checks (`-Pattern '…'` or `.Contains('…')`) across **33** runners; `bk7` uses exit codes only.
- **None** includes the run token or a run id. A marker therefore cannot tell this run's output from an earlier run's.
- **18** marker-checking runners read logs in a **fixed** evidence folder. If the child process fails before rewriting its log, the earlier log can remain and be read. For the polling subset this is the BK-154 stale-log risk.

## BK-158: catch / finally / early-exit terminal status

| Class | Count | Note |
|---|---|---|
| Overall verdict field present | **1** | `bk7` (`verdict` PASS/FAIL); `c1252a` and `c1253a` `SUCCESS=` fields count passed tests |
| Terminal record written on failure | **2** | `bk56` (`failure_status.txt` in `catch`), `bk7` (the receipt records FAIL before the throw) |
| Status written, then a later check may throw | **32** | All **32** lack an overall verdict, so a failed run can leave a status file that does not say it failed. |
| Can throw after taking locks but before writing any status | **25** | That run gets no terminal record. |
| …and the evidence folder is **fixed** | **10** | `c1252a`, `c1253a`, `c1255`, `c1256a_spawn_bridge_build_suite`, `c1257b`, `c1258a_locked_build`, `c1262a_locked_build`, `c1269a`, `c1274_area_effect`, `c1274_channel_drain`. The **previous run's status file stays in place and reads as this run's result** (stale terminal status). |

## BK-159: run binding (task, token, process, evidence path)

- **Lock record:**
  - Carries `command_id` in all **34** runners.
  - Carries the **runner's own** `pid` in 30; `c1252a`, `c1253a`, `c1254a` and `c1255` omit it.
  - No lock record carries the child process id.
- **Status files:** **none** carries the run token, the command id, or a child process id.
- **Evidence path:** a per-run folder in 16 runners (BK-153); a fixed folder in 18.
- **Result:** in all 34 runners, status, lock and launched process are **not bound**. The only binding is folder placement, and only in the per-run runners.

## BK-160: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk156_160_c1155_runner_status_census.py" -v` → **`Ran 10 tests ... OK`**. All 10 are ordinary census tests.

| Class | Tests |
|---|---|
| `ClassifierSelfCheck` (1) | A synthetic runner checks measured vs literal keys, verdict, status-then-throw, throw-before-status, no-save claim vs measurement, the manifest echo, token/child-pid binding, failure status, and a run-id marker. |
| `Census` (1) | 34 runners, deterministic, every one with a status file or receipt. |
| `Bk156StatusFields` (2) | Literal claims 29, manifest echo 25, `NO_ASSETS` 18; no-save claims 28 / measured 5 / unmeasured 23. |
| `Bk157Markers` (2) | 165 checks, 0 run-correlated; 18 read from fixed folders. |
| `Bk158TerminalStatus` (3) | Verdict 1, failure record 2; status-then-throw 32 / without verdict 32; early throw 25 / stale in fixed folder 10. |
| `Bk159RunBinding` (1) | `command_id` 34, `pid` 30 (4 named without it); 0 status files bind token, command or child pid. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- The BK-146..150 and BK-151..155 census suites still pass.

Corrections made while writing this batch:
- A first key regex rejected keys that follow PowerShell's `` `n `` escape, so it missed most literals. It was fixed and is now covered by the synthetic check.
- The stale-terminal-status table was set from the classifier's result: 10, not my first estimate of 9.

## Limits

- Regex classification of source text, with no runtime claims. "Measured" means the value is a script variable; it does not prove the variable measures what its name says.
- The no-save measurement check is a broad pattern match. A related check that is phrased differently would be missed, and the frozen table would then need a review.
- Stale-status and stale-marker risks are possibilities read from the source. They depend on a failure happening at the specific point and on an earlier run's files existing.
