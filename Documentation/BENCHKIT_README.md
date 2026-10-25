# One Boss Fight: benchmark kit (read this first)

This folder (`OneBossFight_BenchKit`) holds a packaged **Shipping** build of One Boss Fight (an Unreal Engine 5.5 game, Windows 64) and the scripts that measure its frame rate. You run it on the physical PC that has the NVIDIA card to test, then send one results zip back to the development PC.

Target: 1920 x 1080, average FPS at least 60, p99 frame time at most 16.67 ms. The owner accepted an RTX 3060 as a stand-in for the RTX 2060 Super, so any RTX 2060 Super or RTX 3060 (or better) result counts; say which card it was.

## Round 1 result (2026-10-24, RTX 3060, console session, valid)

Average 28.4 to 29.4 fps, p99 39.6 to 41.5 ms, every frame over the 16.67 ms budget; GPU frame time about 34 ms average, game and render threads only 3 to 4 ms: the GPU is the limit (the empty arena also runs at 33 fps). Round 2 below finds out where the GPU time goes.

## Round 2 result (2026-10-25, same PC)

The fire lights of the arena are the main GPU cost: the 12 shadow casting brazier lights (radius 32 m) cost about 8 ms of GPU; with their shadows off the game ran at 71.6 fps, with all fire lights off at 77.7 fps. The GPU profile shows, besides the virtual shadow maps (8 ms) and the lights (2 ms), volumetric clouds 5.3 ms and TSR 3.5 ms. Unexplained: the first ten experiments ran at 22 to 35 fps and the later ones at 44 to 49 fps (including no-op experiments), so round 2's early comparisons are not reliable. Round 3 repeats a baseline every few runs and logs the GPU clocks to find out.

## Prompt for Claude on the benchmark PC, ROUND 3 (copy everything between the lines)

----------------------------------------------------------------------
You are helping me measure the frame rate of a game on this PC again (round 3 of a performance investigation). Do exactly this and report faithfully (never say a step passed unless you saw it pass). Do not edit, delete or move anything inside the kit's `Saved\StagedBuilds_Development` folder, do not change drivers or Windows settings, do not install software. The kit folder is `OneBossFight_BenchKit` (called KIT); work from a PowerShell prompt opened in KIT. Close the browser, chat apps, launchers and recorders first (Edge, WhatsApp, Comet and the like; keep yourself open); I must not touch the keyboard or mouse during runs (a bot plays the game).

1. **Session check (mandatory).** `query user`: my line must show SESSIONNAME `console`. If it shows `rdp-tcp#...` STOP and tell me. Run `nvidia-smi` and tell me the GPU, driver and the current GPU utilisation (it should be under 10 percent before you start).
2. **Experiments (about 40 minutes).** Run `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1`. It runs a thrown-away warm-up and 16 one-minute fights with different settings (the game applies them itself), logs the GPU clock, power, temperature and throttle reasons once per second per run into `Saved\smi_<name>.csv`, prints a table and saves `Saved\perf_experiments_<time>.txt`. If it stops with an error, copy the exact error and continue with `-Only R3_05,R3_06,...` for the rest. Show me the final table exactly as printed.
3. **GPU state check (about 3 minutes of your time, no game runs).** From the `Saved\smi_*.csv` files compute for each run: the average `clocks.gr` in MHz, the maximum of `clocks.max.gr`, the average power draw, the maximum temperature, and whether the throttle reasons column was ever other than `0x0000000000000000`/`Not Active`. Give me one small table (run name, average GPU clock, average power, max temperature, throttled yes or no). I want to know whether the GPU clock differs between the slow and the fast runs.
4. **Collect.** `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\BenchKit_Collect.ps1` writes `bench_results_<computer>_<time>.zip` next to the KIT folder. Tell me its full path and size.
5. **Report to me:** (a) GPU, driver, session type, GPU utilisation before you started; (b) the experiment table verbatim; (c) the GPU state table; (d) a sentence on whether the four baseline rows (R3_00, R3_04, R3_09, R3_13 and R3_15) agree with each other within 5 percent; if they do not, say how they trend; (e) which of R3_10, R3_11 and R3_12 reached an average of 60 fps or more with p99 at or below 16.67 ms; (f) whether `fight_started` was true in every row and whether any `cvars` field says UNKNOWN variable (then which one); (g) anything that looked wrong (crashes, stutter you saw, errors).
----------------------------------------------------------------------

## What to bring back to the development PC

Only the file `bench_results_<computer>_<timestamp>.zip` (one file, a few MB) and the written report from the prompt above (round 2 includes the Development game log with the GPU profile tables, a few MB more). On the development PC: copy the zip into `OneBossFight\Saved\bench_return\`, unzip it there, and the development Claude reads it (`python -I Scripts\SummarizeBenchmark.py --root Saved\bench_return\<unzipped>\runs`).

## Notes

- The build in this kit was packaged on the development PC; `BUILD_INFO.txt` has its time. A newer build may follow; the frame time should not change much.
- The runs write to `%LOCALAPPDATA%\OneBossFight\Saved\Benchmark\` (Shipping builds write there). `BenchKit_Collect.ps1` copies those folders.
- Nothing in the kit sends data anywhere. The zip contains frame times, system facts (GPU, CPU, RAM, Windows version, computer name) and the game log; the computer name is the only personal item: remove it from the zip's file name if you prefer.
