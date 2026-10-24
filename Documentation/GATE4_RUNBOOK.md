# Gate 4 Runbook

This runbook executes G4-1 through G4-3. The final gate is a packaged 1920x1080 result on an RTX 2060 Super: average FPS >= 60 and p99 frame time <= 16.67 ms. An RTX 3060 result is a **proxy**, not a target-hardware pass. 120 FPS / 8.33 ms is stretch telemetry only.

## Preconditions

1. Use an active, unlocked **console** Windows session. Before every benchmark set, run `query user`; the benchmark user's `SESSIONNAME` must be `console`, never `rdp-tcp#...`. Remote Desktop can select `Microsoft Remote Display Adapter` rather than the NVIDIA GPU, invalidating the run (C-8; KI-093).
2. Close the Unreal Editor before packaging. Close browsers, capture tools, launchers, and other GPU-heavy applications before every benchmark set.
3. After **every** warm-up or recorded run, read that run's `summary.json`. Discard the run unless its `gpu` field names the expected NVIDIA card; `Remote Display` or `Virtual` means the result is invalid. For a fight-mode run, also discard it unless `fight_started` is `true`. Record the hardware line from this same `summary.json`, not a previously copied log table, with the driver version, CPU, RAM, OS, UE version, monitor mode, and VSync state.
4. Use the same 1920x1080 windowed launch mode for all compared runs. Record every launch cvar exactly as passed to `-ExtraArgs`.
5. Do not compare results from different build configurations or driver versions. Re-package after a code, content, or config change.

## G4-1: Packaged Performance Profile

1. Produce a Development package:

   ```powershell
   .\Scripts\Package.ps1 -Configuration Development
   ```

2. Run one disposable warm-up fight, then verify its `summary.json` GPU field before proceeding. It primes the staged build and is not entered in `PERFORMANCE_LOG.md`:

   ```powershell
   .\Scripts\RunBenchmark.ps1 -Label g4_warmup
   ```

3. Run the baseline fight three times with the **same driver, hardware, map, launch mode, and cvar string**. Verify each run's `summary.json` GPU field and `fight_started: true` before retaining it. The benchmark itself discards its first five seconds and records the following 60 seconds. Keep all three recorded `frames.csv` and `summary.json` directories:

   ```powershell
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_a
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_b
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_c
   ```

    A Development stage writes under `Saved\StagedBuilds\Windows\OneBossFight\Saved\Benchmark\<label>_<timestamp>\`; Shipping writes under `%LOCALAPPDATA%\OneBossFight\Saved\Benchmark\<label>_<timestamp>\`. `RunBenchmark.ps1` and `SummarizeBenchmark.py` search both roots; the matching raw `frames.csv` sits beside `summary.json`.

4. For every recorded run, retain and record: build configuration; the hardware line and `gpu` from that run's `summary.json`; `fight_started`; complete cvar string; `avg_fps`; `p95_ms`; `p99_ms`; `max_ms`; `game_thread_p99_ms`; `render_thread_p99_ms`; `gpu_p99_ms`; and the number of frame rows above 16.67 ms in `frames.csv`. Also preserve the raw `frames.csv` and `summary.json`. Use `python -I .\Scripts\SummarizeBenchmark.py` as the immediate GPU and percentile table check.

5. A target-hardware run passes only when the RTX 2060 Super result has average FPS >= 60 **and** p99 <= 16.67 ms. On this RTX 3060 machine, label every result `proxy`; it informs bottleneck work but cannot close the target-hardware gate.

6. Interpret a retained result in this order: validate `gpu` and (for fight mode) `fight_started` first; then assess `avg_fps` and `p99_ms` against the gate; then compare `game_thread_p99_ms`, `render_thread_p99_ms`, and `gpu_p99_ms`. The largest thread p99 is the diagnostic bottleneck, not a separate pass criterion. If a baseline fails, report that largest field and make one change only per follow-up variant. Re-run that variant three times against the same baseline. Do not combine cvar changes while diagnosing a failure. The predefined variant batch is:

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

## Owner checklist

### Console-session benchmark

1. Use the physical PC, **or** transfer your active session to its console before
   disconnecting Remote Desktop. First run `query user`, note the active session
   ID, then from that session run `tscon <session-id> /dest:console`. This
   disconnects RDP immediately; do not use it unless you can return to the
   physical PC. A valid `query user` result shows that benchmark user's
   `SESSIONNAME` as `console`, not `rdp-tcp#...`.
2. Close the editor and GPU-heavy applications. The current final stage is
   Shipping at `Saved\StagedBuilds` (its executable is under `Windows`); the
   retained Development stage is `Saved\StagedBuilds_Development`.
   `Scripts\RunBenchmark.ps1` searches both the staged Development output and
   `%LOCALAPPDATA%\OneBossFight\Saved\Benchmark`, so benchmark Shipping first.
   To benchmark the retained Development stage, first preserve the current
   Shipping stage and restore Development with these two commands:
   `Rename-Item Saved\StagedBuilds Saved\StagedBuilds_Shipping` then
   `Rename-Item Saved\StagedBuilds_Development Saved\StagedBuilds`. Reverse
   those names to restore Shipping afterwards. The Shipping benchmark was
   **verified to run by Claude 2026-10-24 (invalid GPU under RDP)**: it accepts
   `-RPGBenchmark` and writes `summary.json`, but that RDP result is not valid
   performance evidence.
3. From the project root, run one disposable warm-up and then three identical
   recorded runs:

   ```powershell
   .\Scripts\RunBenchmark.ps1 -Label g4_warmup
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_a
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_b
   .\Scripts\RunBenchmark.ps1 -Label g4_baseline_c
   python -I .\Scripts\SummarizeBenchmark.py
   ```

4. After every run, open its emitted `summary.json`: Development can place it
   under `Saved\StagedBuilds\Windows\OneBossFight\Saved\Benchmark\<label>_<timestamp>\`,
   while Shipping places it under
   `%LOCALAPPDATA%\OneBossFight\Saved\Benchmark\<label>_<timestamp>\`.
   Keep a run only when its `gpu` names the installed NVIDIA card and, for a
   fight-mode run, `fight_started` is `true`. Discard `Remote Display` or
   `Virtual` GPU results. The summary table is the quick check; retain every
   run's `summary.json` and `frames.csv`.
5. Send back: the four output directories, the `SummarizeBenchmark.py` table,
   the exact `gpu`, hardware, and `fight_started` fields from each summary; GPU
   driver version; monitor mode; VSync state; full launch cvar string;
   `avg_fps`, `p95_ms`, `p99_ms`, `max_ms`, and game/render/GPU p99 values; and
   the largest of the three thread p99 values as the diagnostic bottleneck.
   State whether the RTX 2060 Super meets average FPS >= 60 and p99 <= 16.67
   ms. A non-2060 result is a proxy only.

### Benchmark on another PC (owner decision 2026-10-24)

The owner runs the benchmark on another PC that has its own Claude. On the development PC: `.\Scripts\Package.ps1 -Configuration Shipping`, then `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MakeBenchKit.ps1 -OutDir C:/BenchTransfer -Zip` (forward slashes: the Git Bash shell eats backslashes) builds `C:\BenchTransfer\OneBossFight_BenchKit` (about 3.1 GB, no .pdb files) and the same as a zip (tar.exe writes it, Compress-Archive of Windows PowerShell 5.1 fails above 2 GB). Kit of 2026-10-24 20:10 (before B10b and the Shiva shrine). `Documentation/BENCHKIT_README.md` (inside the kit) holds the prompt for the Claude on that PC; its `Scripts\BenchKit_Collect.ps1` writes `bench_results_<computer>_<time>.zip` (run folders with frames.csv and summary.json, system_info.txt with the session type and GPU, the summary table, the game log). Bring that zip back, put it under `Savedench_return\`, and read it with `python -I Scripts\SummarizeBenchmark.py --root Savedench_return\<unzipped>uns`. A result counts only when the session was `console`, the `gpu` names the NVIDIA card and `fight_started` is true. The owner accepted the RTX 3060 as a stand-in for the 2060 Super (`DECISIONS.md`).

### Manual hand tests

These are owner observations, not automated claims. Record `pass`, `fail`, or
`unclear`, what build/cvar was used, and a short video or screenshot when a
result is surprising.

| ID | What to do | Pass looks like | Question to answer |
|---|---|---|---|
| G1-10 | Let the A2 stand-in begin. Roll early once, then roll through its damaging moment; on another attempt walk away after commitment and let it whiff. | Early roll is caught; correctly timed roll passes; walking away works; a whiff leaves about 1.2 s to punish. | Is the cue and punish window readable and fair? |
| G2-17 | Play complete encounters through phase two, stance breaks, ripostes, player death/reset, victory, and retry; repeat at least once. | No stuck boss/player state, missing attack, broken reset, or victory/retry failure. | Does the full duel feel coherent from wake to retry? |
| KI-085 | Hold sprint, start a frontal riposte, release sprint during its clips, then move after control returns. Repeat with guard held/released. | Player neither keeps sprinting nor guarding; speed and stamina behave normally. | Did either held action remain latched? |
| LEG-02 / KI-078 | Play with sound enabled: reach the roar, a slam, a riposte, phase two, and a kill. | Shake is readable but not nauseating; hit stop and slow motion have weight; music swaps/crossfades cleanly with no objectionable loop dip or quiet-intro mismatch. | Which effect, timing, or music transition needs tuning? |
| KI-079 | Inspect the packaged size and playback of both boss music tracks. | Audio plays correctly; the 19.2 MB / 36.7 MB asset sizes are acceptable to the owner. | Is re-importing Phase 1 from OGG worth the size risk? |
| B-key selector | Before wake, press B; select rows 1, 2, and 3 in separate attempts, including one mouse click. Press Escape and B to close. Wake the boss and try B again. | Panel opens only while dormant; each selection equips its intended build; Escape/B close it; it cannot reopen while boss is awake. | Is the selector readable, responsive, and appropriately placed? |
| Build feel | For Starter, Strength, and Dex, play the same short encounter twice: current default `rpg.CloseTelegraph 0.4`, then raw pack pacing `rpg.CloseTelegraph 0`. Restore the chosen default afterwards. | All builds remain usable; the close attacks are readable with 0.4 and the comparison is perceptible. | Should 0.4 remain the default until authored clips arrive, or should the raw timing return? |

Console commands for the final row, entered in the game console, are:

```
rpg.CloseTelegraph 0.4
rpg.CloseTelegraph 0
```

The owner decision recorded on 2026-10-24 is **0.4 by default** pending the
authored clips. The current rebuild/full-gate result for that default was not
verified by this documentation edit.

### README capture list

The README currently has four placeholders. Capture from the staged game where
possible so presentation matches the package; exact framing is owner judgement
and is **unverified** by this runbook.

| README placeholder | Suggested subject | Existing capture help |
|---|---|---|
| `the player facing the Ember Warden in the arena` | Clean pre-fight arena composition with both combatants visible. | In PIE, `HighResShot 1280x720`; `Scripts\Editor\pie_look.py` and `Scripts\shot.sh` are existing arena-shot helpers. |
| `phase-two roar or leap attack` | The phase-two roar or airborne leap at its strongest readable frame. | In PIE, `Shot ShowUI` keeps HUD, while `HighResShot 1280x720` favours clean action; `Scripts\Editor\pie_legend.py` and `pie_boss_clips.py` are related existing drivers. |
| `the three-build selection screen` | Open B-key panel with the three rows, preferably before the boss wakes. | In PIE, `Shot ShowUI`; `Scripts\Editor\pie_build_select.py` and `pie_build_hud.py` are existing references. |
| `benchmark or performance capture` | Benchmark summary/table plus a representative staged-game frame. | `python -I .\Scripts\SummarizeBenchmark.py`; for a window image use `Scripts\CaptureWindow.ps1 -Process OneBossFight-Win64-Shipping -Out Saved\benchmark.png` if that process name is present. The exact packaged window capture is unverified. |

`Shot ShowUI` is documented by `Documentation/PROJECT_STATE.md` as saving a
PIE screenshot with the HUD. `HighResShot 1280x720` is used by the existing
PIE capture drivers. `Scripts\CaptureWindow.ps1` is an existing PrintWindow
helper; it writes the requested path relative to the project root.

### Packaged smoke and Shipping debug-off check

For the current Shipping stage, use the helper instead of looking for a
runtime log (Shipping logging is compiled out):

```powershell
.\Scripts\PackagedSmoke.ps1 -Seconds 20
```

It detects the Shipping child binary and runs `Scripts\CheckShippingBinary.py`
for `rpg.Debug` and `LogRPGDebug`. The staged `OneBossFight.exe` is a launcher;
the smoke helper stops its whole process tree. Do not stop only the launcher,
or its child can keep the staging directory locked.
