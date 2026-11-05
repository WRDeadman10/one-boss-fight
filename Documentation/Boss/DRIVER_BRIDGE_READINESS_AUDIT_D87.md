# Driver bridge readiness audit (D87)

Date: 2026-11-03. Static review of `Scripts/RunDrivers.ps1` and `Scripts/run_in_editor.py`; no editor, bridge request, or driver was run.

## Startup handshake

`RunDrivers.ps1` probes `http://127.0.0.1:3000/mcp/status` with a 3-second request timeout and retries every 5 seconds for up to 240 seconds (lines 88–97). If all probes fail, it emits a specific “not reachable after 4 minutes” message and exits 2. When a probe succeeds after retries, it sleeps another 30 seconds for map loading. However, the probe discards the response body and treats any successful HTTP response as ready; it does not validate the bridge's payload, editor project, loaded map, or tool availability. HTTP/protocol errors and connection failures are caught identically as `false`, so an HTTP error response can be misreported as “not reachable.”

## Task submission and result polling

`Invoke-Editor` runs `python -I run_in_editor.py ... | Out-Null` but does not inspect or propagate `$LASTEXITCODE` (line 84–86). It is used for warmup and driver launches (lines 99–124), before the final-marker deadline is created (125–126). A submission failure can therefore be swallowed at the wrapper level and later surface as a missing marker/driver timeout, or warmup can continue after a failed command.

The Python runner calls `execute_script`, assumes `r["data"]["task_id"]`, then polls `task_result` up to 1200 times. It prints a failed/error/cancelled or missing terminal status and exits 1; exhaustion without completion also exits 1 (lines 12–39). A returned `HTTPError` body is parsed as JSON, while URL/timeouts, malformed JSON, and missing response fields are uncaught exceptions. There is no request retry or cancellation. Per-call socket timeout is 600 seconds, so the number of polls does not establish a 20-minute wall-clock upper bound (see D85).

## Acceptance and limits

There is a distinct exit 2 for exhausting the startup probe loop and exit 1 for most returned editor-task failures, but readiness errors are not classified by transport versus HTTP/protocol response, and the PowerShell caller does not preserve the Python failure as an immediate distinct outcome. D87 acceptance is not fully met: diagnostics/exit behavior are partly distinct, but the readiness handshake is shallow and task-launch failures can be delayed or obscured by later marker waits. No implementation change was made. No network/bridge or editor behavior was verified live.
