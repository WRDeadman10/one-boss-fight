# D146 — packaged 1080p settings audit

Date: 2026-11-03  
Scope: distinguish project configuration defaults, packaging inputs, and settings imposed by the benchmark launch/runtime. Static inspection only; no build, Editor, or benchmark run.

## Settings and where they come from

| Layer | Evidence | What it establishes | What it does not establish |
|---|---|---|---|
| Project config defaults | `Config/DefaultEngine.ini:3-31` | Default/startup map is `/Game/OneBossFight/Levels/L_SevarogArena`; project renderer config selects Lumen GI/reflections (`1`), VSM (`1`), static lighting disabled, and Windows DX12. | The actual values used by an already packaged process after user config, launch args, runtime CVars, driver, or per-map content are considered. This is source config, not a runtime readback. |
| Package input | `Scripts/Package.ps1:28-41` | UAT cooks/stages only `/Game/OneBossFight/Levels/L_SevarogArena`, with `Development` or `Shipping` selected by the script parameter. | A unique binary/content build identity or exact runtime settings. The script does not pass renderer overrides or resolution flags. |
| Benchmark launch | `Scripts/RunBenchmark.ps1:14-16,35-44` | Defaults to that arena map and requests a windowed 1920x1080 viewport with `-ForceRes`; launches benchmark/fight mode, `-NoSound`, and optional caller-provided `ExtraArgs`. | Display mode, refresh rate, actual VSync after startup, or every cvar passed/changed elsewhere. `-KeepConfig` also permits existing user settings to remain. |
| Benchmark runtime changes | `Source/OneBossFight/Benchmark/RPGBenchmarkRunner.cpp:88-146,357-379,416-460` | Benchmark removes frame cap/smoothing and disables `r.VSync` during sampling, applies recognized `-RPGBenchmarkCvars`, records the observed viewport resolution, map, engine version, build configuration, hardware, and applied benchmark cvar string, then restores frame-cap/VSync state on finish. | A comprehensive readback of effective scalability/renderer settings, actual window/display mode, effective external `ExtraArgs` cvars, or a unique package/source hash. The summary's `cvars` field contains the runner's applied pairs, not the full process command line. |
| Gate procedure | `Documentation/GATE4_RUNBOOK.md:7-10,32-44` | Requires a console session, matching GPU and `fight_started`, 1920x1080 windowed comparisons, same launch cvar string, and three comparable baseline runs; asks the operator to record monitor mode and VSync from the run. | Machine-verifiable evidence of mode/VSync when the operator's separate record is missing. |

The source defaults and the packaged runtime are therefore separate evidence layers. The performance target's 1920x1080 requirement is enforced by the benchmark script's launch arguments and observed viewport-size fields, while renderer defaults originate in `DefaultEngine.ini`. A benchmark run may intentionally differ through `ExtraArgs` or `-RPGBenchmarkCvars`; recorded source defaults alone cannot certify what was active in the process.

## Current limits

- `RunBenchmark.ps1` removes matching `GameUserSettings.ini` files under the stage and local Shipping data roots unless `-KeepConfig` is selected. This reduces one source of persistent variation, but is not a full reset or readback of all engine settings.
- Summary JSON records actual viewport width/height and the runner-applied cvar list, but not a complete effective-settings snapshot, monitor mode, VSync state, complete command line, or unique build identity. Treat these absent runtime fields as **UNKNOWN** unless retained operator/collection evidence supplies them.
- `PERFORMANCE_LOG.md` notes round-2 variation and suspected persisted settings as unproven; this audit does not attribute the measured change to a specific setting.

Acceptance: project defaults, packaging configuration, and benchmark launch/runtime overrides are identified separately. No source default is presented as proof of packaged runtime state. Static inspection only.
