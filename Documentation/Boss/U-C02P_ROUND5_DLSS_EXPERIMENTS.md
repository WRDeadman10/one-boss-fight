# U-C02p — Round 5 DLSS experiment schedule

## Phase 1: fixed 16-run schedule

`Scripts/round5_experiments.json` is the source for the dry run. It contains 4 TSR anchors and 12 DLSS treatments. Each of DLAA, Quality, Balanced, and Performance appears three times, interleaved once per block. A fresh TSR anchor follows each four-treatment block. Each treatment sets only the selected upscaler mode as one logical condition using the plugin enable CVar plus `r.ScreenPercentage`; `r.NGX.DLSS.Enable` and `r.ScreenPercentage` are the only DLSS CVars. Their names are sourced from the installed plugin guide pp. 3 and 7. Mode percentages are starting inputs, and every run must pass the plugin feature-log mode check in the Round 5 preflight.

The runner passes each plan `cvar` string through `RunBenchmark.ps1 -ExtraArgs '-RPGBenchmarkCvars="..."'`; `RPGBenchmarkRunner.cpp:90-93` applies those values through the console manager. No runner or game code change is required. Dry run (16 printed rows; no game launch):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1 -Round5 -DryRun
```

When Lead's Development kit is ready and the selected encounter is configured, the Phase 1 command is:

```powershell
$dev = (Resolve-Path 'Saved\StagedBuilds_Development\Windows').Path
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1 -Round5 -StageDir $dev
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
```

This runs one discarded warm-up and the 16 rows; it does not launch until explicitly run by the owner/Lead.

## Phase 2: conditional shadow experiment

Round 2 E18 tested fire-light shadows off and reported 71.6 FPS; the current Dev-only CVar for that treatment is `rpg.Perf.FireShadows=0` (`RPGPerfSwitches.cpp`), not a global scene-light change. The cvar-only treatment is available without editing assets.

Do not guess the best DLSS mode before Phase 1 results. Choose the mode with the highest median avg_fps only among modes that have three accepted active-mode log witnesses, no baseline drift beyond 5%, no p99 regression above 5% vs TSR, and owner image-quality notes that accept the appearance. If no mode qualifies, omit Phase 2. Otherwise run three repeats of that mode plus `rpg.Perf.FireShadows=0`, with a TSR anchor before and after. The three treatment Cvars are `r.NGX.DLSS.Enable=1`, the selected mode's screen percentage, and `rpg.Perf.FireShadows=0`. Use the same selected Development build and route. Record the exact percentage and mode from the active-feature log; never execute a placeholder. Phase 2 is separate because its mode depends on Phase 1 observations.

Both phases are experiments on the RTX 3060 proxy. RTX 2060 Super remains the release target. No visual asset or shipped default is changed by this plan.
