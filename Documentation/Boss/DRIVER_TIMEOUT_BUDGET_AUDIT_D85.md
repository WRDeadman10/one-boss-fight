# Driver timeout budget audit (Queue D85)

Source-only comparison of per-step driver budgets and wrapper/process watchdogs. No driver or Unreal process was run.

## PIE automation driver chain

`Scripts/RunDrivers.ps1` has a default 420-second wall-clock final-marker wait per driver, with fixed table overrides from 300 to 1500 seconds. `-Full` uses a 1500-second wait for the 180-trial dodge driver. It polls every 4 seconds, then invokes `pie_stop.py` on timeout and stops the batch because the driver's tick callback may remain registered. Drivers' local `until`/`wait_until` helpers generally count `S["now"]` (PIE/game time), with representative action windows of 2–10 seconds; these are not real-time watchdogs and can stop progressing if PIE/editor ticking stalls.

The wrapper also has a bounded bridge-readiness loop of 240 seconds, 30 seconds after readiness, and a 40-second warmup. There is no total batch deadline; time accumulates across warmup, every driver, and the 6-second inter-driver gaps. Each fixed per-driver limit is positive and below the 1500-second full-run limit, but these configured limits cover only final log-marker waiting.

## Material outer-watchdog gap

`RunDrivers.ps1` calls `Invoke-Editor` synchronously before it creates the per-driver `$deadline`. `Invoke-Editor` runs `Scripts/run_in_editor.py`. That Python wrapper gives each bridge HTTP request a 600-second socket timeout and performs up to 1200 `task_result` polls with one-second sleeps. It has no monotonic overall deadline and sends no cancellation when polling ends. Therefore the 420–1500-second RunDrivers watchdog does not bound editor task submission or result polling; it starts only after `run_in_editor.py` returns. A delayed or stuck bridge call can outlast the driver's nominal limit, and repeated per-request timeouts can make total polling time much longer than the nominal 20-minute sleep budget.

## Other process wrappers reviewed

- `RunEditorScript.ps1` has an absolute wall-clock timeout (default 600 seconds), polls every 2 seconds, and kills the launched editor on expiry; stopping on a matched `StopPattern` is an intentional separate exit path with a 3-second grace.
- `PackagedSmoke.ps1` bounds its intentional alive interval with `Seconds` in 1–3600 and cleans up the launcher process tree in `finally`; it does not impose a separate startup/readiness timeout, so a blocked `Start-Process`/startup call is outside that duration check.
- `RunBenchmark.ps1` uses `Start-Process -Wait` and checks exit status, but has no process timeout; a packaged benchmark that never exits can wait indefinitely. `RunPerfExperiments.ps1` inherits this behavior for warmup and each experiment.

## Disposition

Configured PIE final-marker limits are ordered and positive, but they do not form a hard end-to-end budget because of the synchronous unbounded bridge-poll stage. Benchmark process waits also lack a hard timeout; smoke startup is outside its alive-duration budget. A complete fix would need a wall-clock deadline spanning bridge calls and process launch/wait, plus a bounded cancellation/cleanup path. No code changed for D85.
