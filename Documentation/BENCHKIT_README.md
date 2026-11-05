# One Boss Fight: benchmark kit (read this first)

This folder (`OneBossFight_BenchKit`) holds a packaged **Shipping** build of One Boss Fight (an Unreal Engine 5.5 game, Windows 64) and the scripts that measure its frame rate. You run it on the physical PC that has the NVIDIA card to test, then send one results zip back to the development PC.

Target: 1920 x 1080, average FPS at least 60, p99 frame time at most 16.67 ms. The owner accepted an RTX 3060 as a stand-in for the RTX 2060 Super, so any RTX 2060 Super or RTX 3060 (or better) result counts; say which card it was.

## Round 1 result (2026-10-24, RTX 3060, console session, valid)

Average 28.4 to 29.4 fps, p99 39.6 to 41.5 ms, every frame over the 16.67 ms budget; GPU frame time about 34 ms average, game and render threads only 3 to 4 ms: the GPU is the limit (the empty arena also runs at 33 fps). Round 2 below finds out where the GPU time goes.

## Round 2 result (2026-10-25, same PC)

The fire lights of the arena are the main GPU cost: the 12 shadow casting brazier lights (radius 32 m) cost about 8 ms of GPU; with their shadows off the game ran at 71.6 fps, with all fire lights off at 77.7 fps. The GPU profile shows, besides the virtual shadow maps (8 ms) and the lights (2 ms), volumetric clouds 5.3 ms and TSR 3.5 ms. Unexplained: the first ten experiments ran at 22 to 35 fps and the later ones at 44 to 49 fps (including no-op experiments), so round 2's early comparisons are not reliable. Round 3 repeats a baseline every few runs and logs the GPU clocks to find out.

## Round 4 (2026-11-05): legacy route vs data-driven route (A7 gate) + owner play test

This kit holds BOTH builds of BUILD-222 (2026-11-05): `Saved\StagedBuilds\Windows` = **Shipping** (play test, final look and feel) and `Saved\StagedBuilds_Development\Windows` = **Development** (benchmark; only the Development build accepts the data-route selector, by design). Round 4 measures the same fight twice: the legacy startup route and the data-driven route (`DA_Sevarog_G044_Encounter`), and checks that the data route is not slower.

## Prompt for Claude on the benchmark PC, ROUND 4 (copy everything between the lines)

----------------------------------------------------------------------
You are helping me measure the frame rate of a game on this PC (round 4). Do exactly this and report faithfully: never say a step passed unless you saw it pass, never replace a failed run silently, never edit, delete or move anything inside the kit's `Saved` folders, do not change drivers or Windows settings, do not install software. The kit folder is `OneBossFight_BenchKit` (called KIT); work in a PowerShell prompt opened in KIT. Close the browser, chat apps, launchers and recorders first (keep yourself open). I must not touch the keyboard or mouse while a run is going (a bot plays the game; each run takes about 1.5 minutes).

1. **Session check (mandatory).** Run `query user`: my line must show SESSIONNAME `console`. If it shows `rdp-tcp#...`, STOP and tell me (remote desktop numbers are invalid). Run `nvidia-smi`: tell me the GPU name, driver version and current GPU utilisation (should be under 10 percent).
2. **Set the stage variable** (the Development build): `$dev = (Resolve-Path 'Saved\StagedBuilds_Development\Windows').Path` and confirm `Test-Path "$dev\OneBossFight.exe"` is True.
3. **Legacy route, 4 runs** (first is a warm-up):
   `Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue`
   then one after another: `.\Scripts\RunBenchmark.ps1 -StageDir $dev -Label r4_legacy_warmup`, `... -Label r4_legacy_a`, `... -Label r4_legacy_b`, `... -Label r4_legacy_c` (same command, only the label changes).
4. **Data route, 4 runs:**
   `$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'`
   then `.\Scripts\RunBenchmark.ps1 -StageDir $dev -Label r4_selected_warmup`, `... -Label r4_selected_a`, `... -Label r4_selected_b`, `... -Label r4_selected_c`.
   Afterwards: `Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue`.
   If a run fails or times out: copy the exact error, keep its folder, and run that label once more with the suffix `_retry`; report both.
5. **Summarise.** `python -I .\Scripts\SummarizeBenchmark.py --root "$dev\OneBossFight\Saved\Benchmark"` and show me the table exactly as printed.
6. **Collect.** `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\BenchKit_Collect.ps1` writes `bench_results_<computer>_<time>.zip` next to KIT. Tell me its full path and size.
7. **Report to me:** (a) GPU, driver, session type, utilisation before start; (b) the summary table verbatim; (c) for each route the average of the three measured runs (a, b, c): average FPS and p99 frame time in ms; (d) PASS or FAIL for: data route average FPS >= 60, data route p99 <= 16.67 ms, data route p99 at most 0.5 ms worse than legacy p99; (e) whether `fight_started` was true and the `gpu` field named this NVIDIA card in every run; (f) anything that looked wrong (crash, error, visible stutter, a run much slower than the others).
----------------------------------------------------------------------

## Owner play test (no Claude needed)

- **Final look and feel:** run `KIT\Saved\StagedBuilds\Windows\OneBossFight.exe` (Shipping). This build starts the legacy route (no Blueprint selects the data route yet, by the J049-A decision); the parity runs show the two routes play the same.
- **Data-driven boss by hand:** run `KIT\Saved\StagedBuilds_Development\Windows\OneBossFight.exe`, press the console key (` or ~), type `rpg.EncounterDefinition /Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter`, Enter, then `open L_SevarogArena`, Enter. The arena reloads with the data-driven boss. To go back: `rpg.EncounterDefinition ""` then `open L_SevarogArena`.
- Worth writing down: input delay on attack/dodge/parry, whether hits feel connected (hit stop, sound, camera), boss telegraph readability, phase two at 60 % health, death and restart, and any frame hitch you can feel. Compare the two builds if you like.

## Prompt for Claude on the benchmark PC, ROUND 3 (historical)

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

## Prompt for Claude on the benchmark PC, ROUND 5 (experiment plan; owner review required)

The plan is an experiment only. Do not change project settings, assets, or the shipped look. The result is an RTX 3060 proxy; the RTX 2060 Super remains the release target. Do not claim a release pass from this run.

----------------------------------------------------------------------
You are helping me test graphics CVars in One Boss Fight (round 5). Report only what you observed. Never edit, delete, move, or clean anything inside KIT\Saved. Do not change drivers, Windows settings, or install software. Do not alter project settings or assets. Run only the Development build so the Development-only `rpg.Perf.*` experiment controls are available. The route must be the selected data route. If any step fails, retain its output and report the exact error; do not silently replace a failed run.

1. **Session and GPU check.** Run `query user`; the benchmark user's session must be `console`, not `rdp-tcp#...`. Run `nvidia-smi`; record GPU, driver, and utilization before start. Stop if this is not the owner's RTX 3060 proxy machine or if another heavy application is using the GPU.
2. **Select the Development build and data route.** In KIT, set `$dev = (Resolve-Path 'Saved\StagedBuilds_Development\Windows').Path`, confirm `Test-Path "$dev\OneBossFight.exe"` is True, then set `$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'`.
3. **Check the run list before launching.** Run `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1 -Round5 -DryRun`. Confirm that it lists exactly 20 rows: four baseline rows and 16 one-CVar treatments. This is a dry-run; it must not launch the game or touch Saved output.
4. **Run Round 5.** Only after step 3 is correct, run `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1 -Round5 -StageDir $dev`. It makes one discarded warm-up then runs the 20 listed rows in order. Baseline repeat rows follow each block of four treatments. Allow the script to finish; do not touch input during each bot fight. If a row fails, copy the exact error and preserve the folder. Do not restart the complete plan without asking me.
5. **Report actual measurements.** Show the final printed table verbatim. Include GPU/driver/session/utilization, each baseline and treatment's avg FPS, p99, GPU average, `fight_started`, and actual CVar summary. State that `r.LightMaxDrawDistanceScale` affects global light draw distance, and that the new `rpg.Perf.FireRadiusScale` is Development-only. Do not attribute treatment deltas if any repeated baseline metric differs from baseline group 0 by more than 5%; mark those comparisons unusable.
6. **Collect and return.** Run `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\BenchKit_Collect.ps1`. Return the zip path, size, and written report. Do not edit a copy of the experiment plan. Keep the selected-route environment variable set only for these runs, then clear it with `Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue`.
----------------------------------------------------------------------

The Round 5 plan and one-variable controls are documented in `Documentation/Boss/U-C01_GPU_COST_MODEL.md` and `Scripts/round5_experiments.json`. Round 5 report intake uses `Scripts/Tools/round4_benchmark_report.py experiments <receipt.json>` with `Scripts/Tools/round5_benchmark.schema.json`. Any visual or performance-default change still needs owner approval.

## Notes

- The build in this kit was packaged on the development PC; `BUILD_INFO.txt` has its time. A newer build may follow; the frame time should not change much.
- The runs write to `%LOCALAPPDATA%\OneBossFight\Saved\Benchmark\` (Shipping builds write there). `BenchKit_Collect.ps1` copies those folders.
- Nothing in the kit sends data anywhere. The zip contains frame times, system facts (GPU, CPU, RAM, Windows version, computer name) and the game log; the computer name is the only personal item: remove it from the zip's file name if you prefer.
