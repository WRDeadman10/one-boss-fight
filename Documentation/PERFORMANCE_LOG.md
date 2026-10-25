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

## Gate 4 first packaged runs, 2026-10-23: NOT VALID as a hardware measurement

Development package of the full game (`Scripts/Package.ps1`, exit 0; first attempt failed: `RerunConstructionScripts` is editor only, six call sites guarded), `Scripts/RunBenchmark.ps1`, map `L_SevarogArena`, fight mode, 1920x1080, 5 s warm-up discarded, 60 s recorded: warm-up 29.6 FPS (p99 41.1 ms); `g4_baseline_a/b/c` 36.5, 36.5 and 36.5 FPS (p99 32.7, 32.7 and 32.6 ms; game thread p99 3.9 to 4.2 ms, render thread p99 32.4 ms, GPU p99 31.5 ms), 2191 frames, all over the 16.67 ms budget. **Why it is not a result:** `summary.json` says `gpu: Microsoft Remote Display Adapter`: the owner's session is an RDP session (`rdp-tcp#0`), so the game presented through the remote display adapter, and the 23 to 33 ms frame band is the signature of the remote session, not of the RTX 3060 in the machine (`-graphicsadapter=1` gave the same 36.6 FPS and the same adapter name, `-graphicsadapter=2` 0.3 FPS). The CPU is now a Ryzen 7 5800X (the hardware table above says Ryzen 5 5500: the machine changed). A valid run needs the console session (the owner at the PC or a session on the physical console), `gpu` in `summary.json` naming the NVIDIA card, and the same driver for every compared run. The game thread (about 4 ms) is not the limit.

## Gate 4 first VALID packaged result, 2026-10-24: the target is NOT met

Shipping package of 2026-10-24 (before B10b, the shrine and the perf switches), `Scripts/RunBenchmark.ps1`, map `L_SevarogArena`, fight mode, 1920x1080 windowed, 5 s warm-up discarded, 60 s recorded, run by the owner on the physical console of the PC `GANPATIGAMERBOI` (session `console`, valid GPU: RTX 3060, driver 610.88, Ryzen 5 5500, 32 GB, Windows 11 25H2) with the benchmark kit (`BENCHKIT_README.md`, results zip in `Saved/bench_return/r1`). The RTX 3060 is accepted as the proxy of the 2060 Super (owner, 2026-10-24).

| Run | Avg FPS | p95 ms | p99 ms | Max ms | Game p99 | Render p99 | GPU p99 | fight_started |
|---|---|---|---|---|---|---|---|---|
| baseline_a | 29.10 | 38.33 | 40.31 | 184.51 | 4.11 | 3.85 | 39.79 | true |
| baseline_b | 28.37 | 39.32 | 41.45 | 44.11 | 3.51 | 4.01 | 40.99 | true |
| baseline_c | 29.38 | 37.81 | 39.59 | 40.69 | 3.41 | 3.77 | 39.10 | true |
| warm-up (thrown away) | 29.73 | 37.48 | 39.52 | 40.54 | 3.60 | 4.37 | 39.06 | true |
| smoke (empty arena, no fight) | 33.47 | 32.62 | 34.91 | 694.68 | 4.26 | 5.60 | 34.13 | n/a |

- Result: 28 to 29 fps average, p99 about 40 ms, every frame over the 16.67 ms budget: NOT met on this hardware. GPU frame time about 34 ms; the game and render threads cost 3 to 4 ms: the frame is GPU bound. The empty arena alone runs at 33 fps: the cost is the arena (its dressing and effects, or the render settings on it), not the fight.
- The same PC and the same project settings (Lumen GI, Lumen reflections, virtual shadow maps, TSR) ran the old greybox fight at 84 fps (GPU 10.5 ms) on 2026-10-18 (section above): the dressed arena costs about 24 ms more GPU time. The 29.6 fps of the 2026-10-23 Remote Desktop run was therefore probably true, not a Remote Display artefact.
- Next (2026-10-24): `Scripts/RunPerfExperiments.ps1` (about 26 one-minute fights with graphics settings and the `rpg.Perf.*` arena switches applied by `-RPGBenchmarkCvars`) and a `ProfileGPU` pass table from the Development build (`-RPGBenchmarkProfileGPUAt`), run on the same PC (kit round 2); the optimisation follows the data.

## Round 2 experiments, 2026-10-25 (same PC, console, Development stage)

`Scripts/RunPerfExperiments.ps1` (round 2 table, 25 one-minute fights, the game applies the variables itself with `-RPGBenchmarkCvars`) and two `ProfileGPU` frames (`-RPGBenchmarkProfileGPUAt`), results zip in `Saved/bench_return/r2`. The first run of E00 failed (empty `-ExtraArgs`, script bug, fixed); a rerun at the end gave 48.1 fps.

| Experiment | Avg FPS | p99 ms | GPU avg ms |
|---|---|---|---|
| E00 baseline (rerun, last) | 48.1 | 23.9 | 20.0 |
| E17 fire lights off (`rpg.Perf.FireLights=0`) | 77.7 | 14.2 | 12.0 |
| E18 fire light shadows off | 71.6 | 15.3 | 13.1 |
| E25 fire lights, fire fx, mists, embers off | 78.4 | 13.9 | 12.0 |
| E19 fire fx off / E20 gate mist off / E21 dressing mist off / E22 dressing off / E23 dressing shadows off / E24 embers off | 46.0 to 46.8 | 23.2 to 24.2 | 20.5 to 20.9 |
| E16 Lumen hardware ray tracing off | 49.2 | 22.6 | 19.5 |
| E11 GI and reflections low / E12 view distance low | 44.3 / 46.1 | 24.7 / 24.0 | 21.7 / 20.9 |
| E01 to E10 (resolution scale, Lumen off, VSM off, Nanite off, volumetric fog off, FXAA, post, effects, shadows low), E13, E14 (Lumen and VSM off) | 22.4 to 35.4 | 33.5 to 51.6 | 24.9 to 39.4 |

- The 12 brazier lights (intensity 5000, radius 3200 cm, all casting shadows) are the main cost: shadows off gives +23 fps, lights off +30 fps. Everything else on the arena (fire particles, mist cards, dressing meshes, embers) is within noise.
- `ProfileGPU` of one frame (22.4 ms of GPU): virtual shadow maps 8.2 ms (projection mask 4.1, non-Nanite raster 2.9, page allocation 0.7, Nanite 0.5), deferred lights 6.6 ms (unbatched lights 2.0), VOLUMETRIC CLOUDS 5.3 ms, post processing 4.1 ms (TSR 3.5 ms at 1400x788 to 1920x1080), base pass 0.4 ms, Nanite 0.3 ms: no Lumen pass shows.
- NOT reliable: the first ten experiments ran at 22 to 35 fps and all later ones, including no-op experiments, at 44 to 49 fps, and the baseline rerun at the end gave 48.1 against the 29 fps of round 1: either the machine state changed during the suite or some setting persisted (suspected GameUserSettings.ini, not proven). Only comparisons inside the later block (E11 onward) are trusted. Round 3 repeats the baseline four times and logs the GPU clocks (`smi_*.csv`) to settle it.

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

## 2026-10-24: Shipping benchmark pipeline check (NOT a valid hardware result)

First benchmark of the **Shipping** package in fight mode (`Scripts/RunBenchmark.ps1 -Label rdp_fightcheck`, 1920x1080, 5 s warm-up and 60 s recorded, 1926 frames) from a Remote Desktop session: `gpu` = "Microsoft Remote Display Adapter" (`SummarizeBenchmark.py` marks it INVALID, as designed), so the frame times (average 32.1 FPS, p99 36.9 ms, GPU p99 35.8 ms) say nothing about the RTX 3060 or the 2060 Super and must not be used. What the run proves: the pipeline works end to end on a Shipping build (`fight_started` true, `summary.json` and `frames.csv` written, the summary tool finds them). The CPU side does not depend on the GPU adapter and is the first useful number: **game thread p99 4.0 ms, render thread p99 5.35 ms** during a full fight (target budget 16.67 ms), so the project's per-frame systems (attribute cache, hit intake, trackers) are cheap.
Two defects found and fixed the same day: (1) the benchmark's fight mode looked for the retired `BP_SevarogBossPack` class and never found the arena boss (`BP_ExampleGreatSwordBoss`), so every earlier fight-mode result, including the 2026-10-20 baseline above, may have measured an idle arena (Codex B5); the runner now uses `URPGPlayerMovesSubsystem::IsPackBoss`, writes `fight_started` to `summary.json` and the summary tool rejects a fight-mode run where it is false; (2) a Shipping build writes its output to `%LOCALAPPDATA%\OneBossFight\Saved\Benchmark`, not next to the staged game: `RunBenchmark.ps1` and `SummarizeBenchmark.py` now search both.
The valid run still needs a real console session on this PC (`GATE4_RUNBOOK.md`, "Owner checklist").
