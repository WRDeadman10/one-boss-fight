# Performance Log

Target (2026-10-20 decision, DECISIONS.md: the owner accepts 60 FPS, look first): packaged build, 1920x1080, average >= 60 FPS and 99th-percentile frame time <= 16.67 ms, full encounter including phase 2. 120 FPS and 8.33 ms are stretch telemetry only.

## Hardware record

| Field | Value |
|---|---|
| GPU / driver | NVIDIA GeForce RTX 3060 / 610.88 (internal 32.0.16.1088) |
| CPU | AMD Ryzen 5 5500 |
| RAM | 32 GB |
| OS | Windows 11 25H2 (10.0.26200.8457) |
| UE version | 5.5.4 |
| Build type | Development (packaged), windowed 1920x1080, uncapped, VSync off |

**Target-hardware warning:** the plan targets an RTX 2060 Super (8 GB). This PC has an RTX 3060, which is usually faster. Numbers below are not 2060 Super results. The final target is 60 FPS average and p99 <= 16.67 ms (owner, 2026-10-22); numbers from this PC are labelled "proxy" and 120 FPS is stretch telemetry only.

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

## Fight captures (M6 start, 2026-10-18) - PARKED, no settings applied

Packaged Development build, `L_Greybox`, `-RPGBenchmark -RPGBenchmarkFight` (bot fights Sevarog, phase 2 forced at 30 s, Cascade effects, hit-stop, HUD), RTX 3060, 1920x1080 native, 60 s recorded. Raw summaries in `Documentation/PerfCaptures/` (`fight_*`, `v_*`, `w_*`). Run `Scripts/RunVariants.ps1` to repeat. Run-to-run noise is about 5 % (v_gi_off_a vs v_gi_off_b).

| Label | Settings | Avg FPS | p99 ms | GPU avg ms | Render thread avg / p99 ms |
|---|---|---|---|---|---|
| fight_defaults | Lumen GI, Lumen reflections, VSM, TSR | 84.2 | 14.28 | 10.5 | 11.6 / 13.9 |
| v_gi_off_a / b | GI off, SSR | 132.7 / 125.8 | 8.98 / 9.28 | 6.8 / 7.2 | 7.4 / 7.8 |
| v_no_ao, v_no_motionblur_bloom, v_no_ssr, v_vsm_off_a/b | one change vs gi_off | 125 to 133 | 8.9 to 9.6 | 6.8 to 7.2 | about 7.5 | 
| v_sp85 | gi_off + 85 % screen percentage | 109.3 | 10.33 | 8.4 | slower (upscaling cost outweighed the saving) |
| w_taa | gi_off + TAA | 163.2 | 10.33 | 3.5 | 6.0 / 10.2 |
| w_fxaa | gi_off + FXAA | 165.8 | 10.02 | 3.2 | 5.9 / 9.9 |
| w_fxaa_noshadow | FXAA + shadows off (diagnostic only) | 188.1 | 8.64 | 2.4 | 5.2 / 8.8 |

What the data says (nothing is applied; the project still has its default render settings):
- With the boss fight running the game thread is cheap (2 ms); the cost is rendering.
- Lumen GI plus Lumen reflections cost about 4 ms of GPU; TSR costs about 3.3 ms more. AO, bloom, motion blur, SSR and virtual shadow maps are each within noise.
- Once GPU time drops below about 4 ms the **render thread** limits the frame (p99 about 10 ms, GPU p99 only 3.4 ms). Shadows are the largest part of it. Particles are not.
- The 120 FPS p99 gate (8.33 ms) is not met by any variant yet on this PC; the nearest are about 8.6 to 9 ms p99.

Decision (user, 2026-10-18): performance work waits until mechanics, engineering and environment integration are done. M6 continues from these numbers then.

## Open

- Repeat on the actual target GPU (RTX 2060 Super) if available.
- Re-run with background apps closed and 3+ repeats per variant to measure run-to-run variance.
- Move chosen settings into `DefaultEngine.ini`/scalability once the lighting decision is made.

## 2026-10-20: baseline on the pack (unpackaged)

`ARPGBenchmarkRunner` fight mode in `L_SevarogArena`, editor binary in game mode, 1920x1080 windowed, 5 s warm-up and 60 s recorded: 4754 frames, average 79.2 FPS (12.6 ms), median 11.9 ms, p95 14.9 ms, p99 27.1 ms, max 504 ms (shader compile at the start), 99.3 % of frames over 8.33 ms. Not comparable to the earlier C++ numbers (different content, unpackaged). The performance milestone is still ahead; see KI-051.
