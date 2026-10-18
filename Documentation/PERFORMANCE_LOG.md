# Performance Log

Target: packaged build, 1920x1080, average >= 120 FPS and 99th-percentile frame time <= 8.33 ms, full encounter including phase 2.

## Hardware record

| Field | Value |
|---|---|
| GPU / driver | NVIDIA GeForce RTX 3060 / 610.88 (internal 32.0.16.1088) |
| CPU | AMD Ryzen 5 5500 |
| RAM | 32 GB |
| OS | Windows 11 25H2 (10.0.26200.8457) |
| UE version | 5.5.4 |
| Build type | Development (packaged), windowed 1920x1080, uncapped, VSync off |

**Target-hardware warning:** the plan targets an RTX 2060 Super (8 GB). This PC has an RTX 3060, which is usually faster. Numbers below are not 2060 Super results. Treat 120 FPS here as a necessary, not sufficient, check.

## Method

Packaged build, map `L_Benchmark` (greybox arena, no boss, no VFX yet), `ARPGBenchmarkRunner` orbits a camera 30 s per revolution; 5 s warmup discarded, 60 s recorded. Raw wall-clock frame times. Run with `Scripts/RunBenchmark.ps1 -Label <name>`. Raw summaries are in `Documentation/PerfCaptures/` (run 1 of baseline_defaults is missing: it was wiped when the build was re-staged; its numbers were copied from the console).

Variants are applied with `-ExecCmds` at launch, not yet in project config.

## Captures (M1)

| Date | Label | Settings | Avg FPS | p95 ms | p99 ms | Max ms | Over 8.33 ms | Game ms (avg/p99) | Render ms (avg/p99) | GPU ms (avg/p99) | Meets 120 gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-18 | baseline_defaults (run 1, before thread timing) | Project defaults: Lumen GI + Lumen reflections + virtual shadow maps, DX12 SM6 | 96.5 | 12.0 | 13.0 | 27.9 | 5683 / 5793 | n/a | n/a | n/a | No |
| 2026-10-18 | baseline_defaults (run 2) | same | 94.4 | 18.9 | 23.1 | 29.2 | 5550 | 2.2 / 4.0 | 10.3 / 22.8 | 9.2 / 20.9 | No |
| 2026-10-18 | gi_off | `r.DynamicGlobalIlluminationMethod 0`, `r.ReflectionMethod 2` (SSR) | 137.5 | 7.9 | 8.26 | 10.2 | 59 | 1.8 / 2.7 | 7.2 / 8.2 | 6.6 / 7.0 | Yes (p99 margin 0.07 ms) |
| 2026-10-18 | gi_vsm_off | gi_off + `r.Shadow.Virtual.Enable 0` | 142.0 | 7.6 | 7.95 | 14.2 | 15 | 1.8 / 2.8 | 6.9 / 8.1 | 6.3 / 6.6 | Yes |

## Findings

- The empty arena is **GPU/render bound** (game thread about 2 ms). Optimization targets the renderer, not gameplay code.
- Project defaults (Lumen, VSM) cost about 3-4 ms of GPU per frame versus GI off, and p99 is unstable (13 ms vs 23 ms between two identical runs; run 2 may include background load).
- Removing Lumen GI and Lumen reflections alone reaches the gate on this PC. Virtual shadow maps add a smaller gain (about 0.3 ms GPU).
- Headroom is thin before any boss, VFX, lightning, fog or post-processing exist. Expect the real fight to cost more.
- `r.AllowStaticLighting=False` currently prevents baked lighting. Decide in M6 whether to enable static lighting for the arena.

## Open

- Repeat on the actual target GPU (RTX 2060 Super) if available.
- Re-run with background apps closed and 3+ repeats per variant to measure run-to-run variance.
- Move chosen settings into `DefaultEngine.ini`/scalability once the lighting decision is made.
