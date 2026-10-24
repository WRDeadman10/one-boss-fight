# One Boss Fight: benchmark kit (read this first)

This folder (`OneBossFight_BenchKit`) holds a packaged **Shipping** build of One Boss Fight (an Unreal Engine 5.5 game, Windows 64) and the scripts that measure its frame rate. You run it on the physical PC that has the NVIDIA card to test, then send one results zip back to the development PC.

Target: 1920 x 1080, average FPS at least 60, p99 frame time at most 16.67 ms. The owner accepted an RTX 3060 as a stand-in for the RTX 2060 Super, so any RTX 2060 Super or RTX 3060 (or better) result counts; say which card it was.

## Round 1 result (2026-10-24, RTX 3060, console session, valid)

Average 28.4 to 29.4 fps, p99 39.6 to 41.5 ms, every frame over the 16.67 ms budget; GPU frame time about 34 ms average, game and render threads only 3 to 4 ms: the GPU is the limit (the empty arena also runs at 33 fps). Round 2 below finds out where the GPU time goes.

## Prompt for Claude on the benchmark PC, ROUND 2 (copy everything between the lines)

----------------------------------------------------------------------
You are helping me find out why a packaged game is slow on this PC (it ran at 29 fps, GPU limited). Do exactly this and report faithfully (never say a step passed unless you saw it pass). Do not edit, delete or move anything inside the kit's `Saved\StagedBuilds` and `Saved\StagedBuilds_Development` folders, do not change drivers or Windows settings, do not install software. The kit folder is `OneBossFight_BenchKit` (called KIT); work from a PowerShell prompt opened in KIT. Close the browser, games, launchers and recorders first; I must not touch the keyboard or mouse during runs (a bot plays the game).

1. **Session check (mandatory).** `query user`: my line must show SESSIONNAME `console` (physical PC). If it shows `rdp-tcp#...` STOP and tell me. Run `nvidia-smi`, tell me the GPU and driver.
2. **Experiments (about 40 minutes).** Run `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1`. It runs 16 one-minute fights, each with different graphics settings (the game applies them itself), after a thrown-away warm-up, prints a table and saves `Saved\perf_experiments_<time>.txt`. If it stops with an error, copy the exact error, then continue with `-Only E05,E06,...` for the rest (names are in the script). Show me the final table exactly as printed.
3. **GPU profile (about 6 minutes).** With the Development build, which prints a per-pass GPU table into its log:
   - `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -Label prof_a -StageDir "$PWD\Saved\StagedBuilds_Development\Windows" -ExtraArgs '-RPGBenchmarkProfileGPUAt=25'`
   - the same with `-Label prof_b` and `-RPGBenchmarkProfileGPUAt=45`.
   Afterwards find the game log under `Saved\StagedBuilds_Development\Windows\OneBossFight\Saved\Logs\OneBossFight.log` and tell me whether it contains the words `ProfileGPU` and `Lumen` (do not paste the whole log).
4. **Collect.** `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\BenchKit_Collect.ps1` writes `bench_results_<computer>_<time>.zip` next to the KIT folder. Tell me its full path and size.
5. **Report to me:** (a) GPU, driver, session type; (b) the experiment table verbatim; (c) which single change reduced the average GPU time the most, and which combination (if any) reached an average of 60 fps or more with p99 at or below 16.67 ms; (d) whether `fight_started` was true in every row; (e) anything that looked wrong (crashes, an experiment whose `cvars` field says UNKNOWN variable, stutter you saw).
----------------------------------------------------------------------

## What to bring back to the development PC

Only the file `bench_results_<computer>_<timestamp>.zip` (one file, a few MB) and the written report from the prompt above (round 2 includes the Development game log with the GPU profile tables, a few MB more). On the development PC: copy the zip into `OneBossFight\Saved\bench_return\`, unzip it there, and the development Claude reads it (`python -I Scripts\SummarizeBenchmark.py --root Saved\bench_return\<unzipped>\runs`).

## Notes

- The build in this kit was packaged on the development PC; `BUILD_INFO.txt` has its time. A newer build may follow; the frame time should not change much.
- The runs write to `%LOCALAPPDATA%\OneBossFight\Saved\Benchmark\` (Shipping builds write there). `BenchKit_Collect.ps1` copies those folders.
- Nothing in the kit sends data anywhere. The zip contains frame times, system facts (GPU, CPU, RAM, Windows version, computer name) and the game log; the computer name is the only personal item: remove it from the zip's file name if you prefer.
