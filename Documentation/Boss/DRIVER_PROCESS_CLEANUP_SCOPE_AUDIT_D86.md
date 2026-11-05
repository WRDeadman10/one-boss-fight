# Driver process cleanup scope audit (D86)

Date: 2026-11-03. Static review of the maintained driver/build/packaged process wrappers and process-stop callsites. No process was started or stopped.

## Ownership and cleanup map

| Wrapper | Spawn/selection | Cleanup scope | Finding |
|---|---|---|---|
| `Scripts/PackagedSmoke.ps1` | Starts the resolved staged launcher and retains its `Process` object (line 60). | In `finally`, snapshots descendant PIDs, stops the launcher by `taskkill /PID <root> /T /F`, then rechecks each surviving snapshotted descendant's creation time and parent PID before a PID-tree stop (lines 71–99). | Explicit PID-tree ownership; no image-name sweep. If CIM enumeration fails it warns and still attempts the root tree. Child `taskkill` exit status is not checked. |
| `Scripts/Rebuild.ps1` | Enumerates `UnrealEditor.exe`, but selects only command lines containing this checkout's full `.uproject` path (lines 10–16). | Requests normal close, waits 120 seconds, rechecks the same project filter, then kills each remaining selected PID tree (lines 21–45). | Process-name enumeration is narrowed by project identity before termination. CIM failure aborts before close/build. No broad image-name termination. |
| `Scripts/RunEditorScript.ps1` | Starts and retains the editor process it launched (line 19). | On stop-pattern or timeout, calls `.Kill()` on that process object (lines 29–35). | Root PID is owned, but descendants are not enumerated or explicitly cleaned. Direct `Kill()` does not itself establish descendant cleanup. |
| `Scripts/RunBenchmark.ps1` | Starts staged launcher with `-PassThru -Wait` (line 48). | No timeout or `finally` cleanup path; it checks the returned process exit code after it exits. | A hung launcher can wait indefinitely; interruption/failure before return has no explicit owned-tree cleanup here. |
| `Scripts/RunPerfExperiments.ps1` | Starts an owned `nvidia-smi` sampler and retains its process object (line 57). | Stops that PID on the benchmark nonzero branch and the normal post-run path (lines 64, 69). | Local PID is scoped, but cleanup is not in `finally`; terminating errors or interruption between launch and either stop can leave the sampler running. |
| `Scripts/RunDrivers.ps1` + `Scripts/run_in_editor.py` | Invokes Python synchronously to submit editor scripts and poll bridge results (RunDrivers line 84; Python HTTP call at line 12). | Driver-marker timeout requests editor PIE stop through `pie_stop.py` (RunDrivers line 137); that script only calls `editor_request_end_play()`. | No image-name process kill. The Python call is not given a tracked-process cleanup path here; the separate bridge/request budget gap is documented in D85. A timed-out PIE can leave a tick callback, and the wrapper explicitly requires editor restart. |
| `Scripts/PlayDevBuild.ps1` | Starts the staged game without `-PassThru` (line 20). | No process handle or cleanup path. | Intentional hand-test launcher; ownership transfers to the user, so automatic cleanup is not claimed. |

## Scope scan and limits

Searches for `taskkill`, `Stop-Process`, `.Kill()`, `CloseMainWindow`, and `Start-Process` across maintained PowerShell scripts found no `taskkill /IM`, `Stop-Process -Name`, or wildcard image-name termination. Rebuild's image-name query is only an inventory filter; termination requires the exact project path in the command line. The known broad packaged-smoke sweep was already removed and replaced by PID-tree ownership in S186.

Acceptance is met for the no-broad-termination requirement, and explicit descendant cleanup exists for PackagedSmoke and Rebuild. It is not uniform: RunEditorScript lacks descendant handling, RunBenchmark has no bounded cleanup, and RunPerfExperiments lacks a `finally` for its sampler. This is a static ownership audit, not evidence that Windows process trees were exercised or that `taskkill` succeeded. No scripts were changed for D86.
