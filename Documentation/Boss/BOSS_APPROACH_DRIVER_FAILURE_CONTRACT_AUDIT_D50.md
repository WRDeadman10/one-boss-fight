# Boss approach-driver failure contract audit (Queue D D50)

## Inspected route and driver

The maintained PIE encounter driver is `Scripts/Editor/pie_boss_encounter.py`; it includes a player-walk `approach` stage and `approach2` after respawn, with a global 160 s timeout, a 30 s first-wake timeout, and a 4 s second-wake stage that currently has no timeout branch (`:61-67, 112-124, 156-173`). The first approach failure records a failed check and calls `finish("no wake")`; the global timeout calls `finish("timeout")`. Neither emits the `RunDrivers.ps1` `RESULT passed/total` or `SUMMARY` marker. `pie_boss_encounter` is not registered in `Scripts/RunDrivers.ps1` (the wrapper's registered driver list is a separate set).

The approach sends `pawn.add_movement_input(flat.normal(), 1.0, False)` each tick and declares success when the encounter is no longer dormant and the player is within 1300 cm. It does not compare player position against the stage-start position or assert displacement. Thus wake-within-range is the behavioral result; actual player movement is not separately diagnosed. Missing boss or pawn causes callback polling to continue until the global timeout, without identifying which dependency stayed absent.

## Failure propagation and log retention

| Failure | Source behavior | Process/result behavior | Gap |
|---|---|---|---|
| No wake during first approach | Failed check, `finish("no wake")`, ends PIE. | `finish` only logs `finished`; it does not raise/return a failing bridge task status. | A caller that checks only bridge task completion can misclassify this as successful script execution. |
| Global timeout / stalled progress | `finish("timeout")` ends PIE; no stage-specific missing-state diagnosis. | No `RESULT`/`SUMMARY` status row for this driver. `RunDrivers.ps1` only detects timeout for registered scripts and exits 1 for collected failures; it does not list this script. | No standalone nonzero failure contract or machine-readable timeout result. |
| No movement / no pawn or boss | Input is continually requested; missing pawn/boss keeps returning until timeout. No displacement threshold or initial-setup timeout. | Same logged completion path as above. | The log cannot distinguish movement input acceptance from actual displacement; absent actor vs no wake is ambiguous. |
| Bridge/HTTP error | `Scripts/run_in_editor.py` uses `urllib.request`; it catches `HTTPError` only, then assumes response fields `data.task_id`, polls for up to 1200 seconds, and prints status/output. | It does not translate `failed`, missing result, malformed response, timeout, or uncaught URL/connection exceptions into explicit `sys.exit(nonzero)` branches. | Wrapper status may be zero on a reported task failure or absent; transport errors can terminate with traceback. |
| Headless Editor timeout/exit | `run_editor_script.ps1` waits for the engine, kills it on timeout, then snapshots state, hashes `editor_raw.log`, and writes `result.json`. | Result records `timed_out` and `exit_code`, but the shown script does not exit nonzero based on either value. Early engine/lock guards write `STOP.txt` and exit 2. | Evidence files are retained on normal timeout path, but automation must inspect result.json; process status alone does not encode timeout. |

## Bounded contract for a future driver

Keep the observed run's raw log and command/result identity. A future runner should return nonzero for: explicit failed assertions, stage deadline/no wake, no displacement when displacement is required, missing required actor/component, bridge connection/HTTP/task failure, and outer process timeout. Each should log a stable failure code and stage before ending PIE where possible; outer timeout should retain the partial editor log and wrapper result. A normal bridge task completion is not the same as passing the gameplay checks. This is a source-only contract audit; no driver or bridge was run or changed.
