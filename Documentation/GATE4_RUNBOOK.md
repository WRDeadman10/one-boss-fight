# Gate 4 Runbook

This runbook executes G4-1 through G4-3. The final gate is a packaged 1920x1080 result on an RTX 2060 Super: average FPS >= 60 and p99 frame time <= 16.67 ms. An RTX 3060 result is a **proxy**, not a target-hardware pass. 120 FPS / 8.33 ms is stretch telemetry only.

## Preconditions

1. Use an active, unlocked Windows session. Do not start Unreal while `query user` reports the interactive session as disconnected (KI-093).
2. Close the Unreal Editor before packaging. Close browsers, capture tools, launchers, and other GPU-heavy applications before every benchmark set.
3. Record the GPU model, driver version, CPU, RAM, OS, UE version, monitor mode, and whether VSync is enabled in the results table.
4. Use the same 1920x1080 windowed launch mode for all compared runs. Record every launch cvar exactly as passed to `-ExtraArgs`.
5. Do not compare results from different build configurations or driver versions. Re-package after a code, content, or config change.

## G4-1: Packaged Performance Profile

1. Produce a Development package:

   ```powershell
   .\Scripts\Package.ps1 -Configuration Development
   ```

2. Run one disposable warm-up fight. It primes the staged build and is not entered in `PERFORMANCE_LOG.md`:

   ```powershell
   .\Scripts\RunBenchmark.ps1 -Label g4_warmup
   ```

3. Run the baseline fight three times. The benchmark itself discards its first five seconds and records the following 60 seconds. Keep all three recorded `frames.csv` and `summary.json` directories:

   ```powershell
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_a
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_b
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_c
   ```

   Results are printed from `Saved\StagedBuilds\Windows\OneBossFight\Saved\Benchmark\<label>_<timestamp>\summary.json`; the matching raw `frames.csv` is in the same directory.

4. For every recorded run, retain and record: build configuration; hardware and driver line; complete cvar string; `avg_fps`; `p95_ms`; `p99_ms`; `max_ms`; and the number of frame rows above 16.67 ms in `frames.csv`. Also preserve the raw `frames.csv` and `summary.json`.

5. A target-hardware run passes only when the RTX 2060 Super result has average FPS >= 60 **and** p99 <= 16.67 ms. On this RTX 3060 machine, label every result `proxy`; it informs bottleneck work but cannot close the target-hardware gate.

6. If a baseline fails, identify the limiting thread from the summary and make one change only per follow-up variant. Re-run that variant three times against the same baseline. Do not combine cvar changes while diagnosing a failure. The predefined variant batch is:

   ```powershell
   .\Scripts\RunVariants.ps1 -Map /Game/OneBossFight/Levels/L_SevarogArena
   ```

   `RunVariants.ps1` currently copies summaries to `Documentation\PerfCaptures`; preserve those copies with the raw staged results. Its default map is stale (`L_Greybox`), so always pass the arena map above.

## G4-2: Package, Cooked-Asset Check, and Smoke

1. Create a fresh Development package with the G4-1 command above.
2. Inspect the generated UAT cook log and newest staged runtime log without modifying them:

   ```powershell
   .\Scripts\CheckPackagedLog.ps1
   ```

   A non-zero exit is a G4-2 failure: resolve each named asset load, cook/shader error, or fatal marker before proceeding. The checker reports KI-084 candidates by the asset/path line that failed.
3. Start the staged executable outside the editor and conduct this manual smoke checklist in one fresh encounter:
   - wake the boss;
   - observe the phase-two transition;
   - cause a stance break;
   - execute a riposte;
   - trigger bleed;
   - die and confirm reset;
   - win and confirm victory and retry.
4. Record each smoke result, the precise staged build configuration, and any missing animation, sound, effect, weapon data, or `CheckPackagedLog.ps1` evidence in `PERFORMANCE_LOG.md` and `KNOWN_ISSUES.md` as appropriate.

## G4-3: Shipping Debug-Off Verification

1. Produce a fresh Shipping package:

   ```powershell
   .\Scripts\Package.ps1 -Configuration Shipping
   ```

2. Run the staged Shipping executable outside the editor through the full G4-2 smoke checklist. Do not enable `rpg.Debug`.
3. Run the checker against the exact package logs. Supply paths explicitly if the newest logs are not the Shipping run:

   ```powershell
   .\Scripts\CheckPackagedLog.ps1 -CookLog '<UAT cook log or folder>' -RuntimeLog '<staged runtime log or folder>'
   ```

4. Shipping passes this row only when the checker has no asset, error/cook/shader, or fatal findings and no `LogRPGDebug`, `rpg.Debug`, or `DrawDebugCircle` text. `RPGCombatDebug` and the shockwave debug circle are compiled behind `!UE_BUILD_SHIPPING`; the runtime check is a regression guard, not proof of source compilation by itself.

## Results Template

Paste one table like this into `Documentation/PERFORMANCE_LOG.md` for each baseline or single-variable set:

| Date | Hardware / driver | Build | Label | Map / mode | Cvars | Warm-up discarded | Avg FPS | p95 ms | p99 ms | Max ms | Frames >16.67 ms | Result | Notes |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| YYYY-MM-DD | RTX model / driver | Development or Shipping | label | `L_SevarogArena` / fight | exact string | `g4_warmup` | | | | | | Target pass / proxy / fail | raw paths and bottleneck |

For a failed set, add the selected bottleneck and exactly one follow-up cvar or content change. For a target pass, attach or retain all three recorded `frames.csv` and `summary.json` pairs.
