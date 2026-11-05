# Run the suite and preserve reviewable evidence

This guide distinguishes the headless Unreal automation suite from the PIE regression drivers. It describes the checked-in commands; it does not claim that a run happened.

## Full build plus Unreal automation suite

1. Confirm the intended checkout and binary. The rebuild script requests a normal close only for editor processes whose command line identifies this checkout, waits for teardown, and stops only a confirmed matching PID tree if it remains hung. See the [editor/staging lock runbook](../GATE4_RUNBOOK.md#editor-and-staging-locks). Run it from the project root in PowerShell:

   ```powershell
   powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1 -Tests -NoRelaunch
   ```

2. `Scripts\Rebuild.ps1` builds `OneBossFightEditor Win64 Development`, then invokes `UnrealEditor-Cmd.exe` with `Automation RunTests OneBossFight; Quit`, `-unattended -nullrhi -nosound -nosplash`. `-NoRelaunch` leaves the editor closed. It prints process-specific build/test log paths and returns nonzero for compiler errors or nonzero child status, missing test completions, or failed/incomplete test counts. Its actual command and result parsing are in `Scripts/Rebuild.ps1`.

3. **Confirm the run is real and complete.** The log must be newly written for this run, contain test start/completion records, and show the expected `Test Completed` rows. Compare `finished` against `passed`; zero completed tests is a no-run (for example, a disconnected Windows session can stop startup; KI-093). Inspect `Expected`/failure records and build output for compile errors. The wrapper's nonzero status is a failure signal; it does not replace review of the retained logs.

## PIE regression drivers

The editor-driven gate is separate. Open the editor with `-nosound`, ensure the project bridge is available, then run `Scripts/RunDrivers.ps1`. It executes the named PIE drivers serially, reports per-driver counts, and expects `RESULT passed/total passed` or `SUMMARY total checks, 0 failed`. The complete table takes about 100 minutes; use `-Only` to run a selected comma-separated set, and `-SkipWarmup` only for later chunks after the first warm-up. A timed-out driver leaves a tick callback registered; restart the editor before running another driver. These details and exact options are in `Scripts/RunDrivers.ps1:1–15,101–145`.

## Preserve evidence

- Create a unique run folder under `Docs/BossCombatReview/Execution/Claude/<RUN_ID>/` (or the assigned evidence location) before copying logs. Keep the raw build output, raw automation log, exact command/arguments, date/time, reported `finished/passed` counts, relevant driver results, and a short run report together.
- Save failed attempts too, with `FAIL` in the filename. Do not replace an earlier failure with a later pass; record what changed between attempts. BUILD-168 keeps both failed and successful suite logs in `B_CODEX_R1_85`, with an `evidence_sha256.txt` manifest.
- Hash the copied evidence files after the run and record the hashes, for example:

  ```powershell
  Get-FileHash Docs\BossCombatReview\Execution\Claude\<RUN_ID>\tests_raw.log -Algorithm SHA256
  ```

- Keep the report literal: distinguish source review, build success, automation test success, PIE proof, and packaged proof. Record exact counts; list tests that failed or did not finish. Do not describe a skipped, stale, or zero-completion log as a pass.

## Recorded examples

- Full automation example: `BUILD-168`, 321 of 321 passed after two boundary-test fixes; evidence is `Docs/BossCombatReview/Execution/Claude/B_CODEX_R1_85/` and its failed first-run log is retained (`Documentation/TEST_PLAN.md:594`).
- Earlier pure-rule suite example: `BUILD-163`, 301 of 301 passed (`Documentation/TEST_PLAN.md:589`).
- Driver-table behavior and per-driver result formats: `Scripts/RunDrivers.ps1:3,132–145`.

Source references: [`Rebuild.ps1`](../../Scripts/Rebuild.ps1:1), [`RunDrivers.ps1`](../../Scripts/RunDrivers.ps1:1), [`PROJECT_STATE.md`](../PROJECT_STATE.md), and [`TEST_PLAN.md`](../TEST_PLAN.md:589).
