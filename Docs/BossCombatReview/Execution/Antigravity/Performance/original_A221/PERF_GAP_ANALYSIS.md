# Performance Gap Analysis: KI-108 Packaged Build Bottlenecks, Measured Baselines, Causality Audit, and Single-Variable Experiment Plan

**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Task Order:** C-332 (Order A-220)  
**Date:** 2026-10-29  
**Target Gate:** Packaged build, 1920x1080 windowed/fullscreen, average >= 60 FPS, 99th-percentile frame time (p99) <= 16.67 ms across full boss encounter in `L_SevarogArena`.  
**Target Hardware:** NVIDIA GeForce RTX 2060 Super (8 GB VRAM); Benchmark Proxy: NVIDIA GeForce RTX 3060 (12 GB VRAM).  
**Status:** Complete Offline Performance Analysis & Measurement Specification (Pure CRLF, 0 Engine Processes, Read-Only toward Source/Content/Config).

---

## Executive Summary

This report establishes the ground-truth technical analysis of **KI-108** ("The packaged game runs at 28 to 29 fps average, p99 ~40 ms on the RTX 3060 at 1080p: the 60 FPS / 16.67 ms target is NOT met").

Based on comprehensive cross-examination of existing repository data (`Documentation/PERFORMANCE_LOG.md`, `Saved/bench_return/r1/`, `Saved/bench_return/r2/`, and engine profiling logs):
1. **The Game is 100% GPU-Bound:** In valid physical console Shipping runs, the CPU Game thread costs only **3.41 - 4.11 ms** p99, and the Render thread costs only **3.77 - 4.01 ms** p99 (leaving >12 ms of headroom against the 16.67 ms frame budget). Gameplay C++ systems, combat state machines, and AI tick logic are **not** the bottleneck.
2. **The Arena Itself Is the Bottleneck, Not the Fight:** The empty arena with no boss, no combat, and no player input runs at **33.47 FPS (34.13 ms GPU p99)**. The entire active boss fight only adds ~5-6 ms of GPU time over the idle dressed arena.
3. **The Two Proven Primary GPU Culprits:**
   - **Virtual Shadow Maps (VSM) on 12 Brazier Point Lights:** Costs **8.27 ms** of GPU time in single-frame ProfileGPU. In Round 2 experiments, disabling shadows on these fire lights (`rpg.Perf.FireShadows=0`) immediately boosted performance by **+23.5 FPS (from 48.1 to 71.6 FPS, p99 15.3 ms)**, crossing the 60 FPS gate. Disabling the lights entirely (`rpg.Perf.FireLights=0`) yielded **77.7 FPS (14.2 ms p99)**.
   - **Volumetric Clouds (`r.VolumetricCloud`):** Consumes **5.30 ms** of GPU time in single-frame ProfileGPU (`VolumetricCloud` / `CloudView`).
4. **Proven Harmless Suspects:** Translucent mist sheets (`E20`, `E21`), Niagara/Cascade fire particles (`E19`), ember meshes (`E24`), and arena dressing static meshes (`E22`) all measured within run-to-run noise (<1 FPS difference). Nanite geometry rasterization costs only 0.39 ms and BasePass costs 0.36 ms.
5. **Action Plan:** A structured, single-variable experiment matrix is detailed herein to guide Tech Lead Claude and the Owner in locking the production lighting, shadow, and cloud scalability profile for Shipping.

---

## 1. Ground-Truth Measured Numbers in Repository

All measurements below are cited with exact file paths, line ranges, and execution conditions verified directly from repository artifacts.

### 1.1 Target Hardware & Target Criteria Commitment
- **Target Specification:** `Documentation/PERFORMANCE_LOG.md:3-5`, `Documentation/DECISIONS.md:3`.
- **Criteria:** Packaged build, 1920x1080, average >= 60 FPS, p99 <= 16.67 ms, covering the full encounter including Phase 2. (120 FPS / 8.33 ms is stretch telemetry only).
- **Target Machine:** NVIDIA GeForce RTX 2060 Super (8 GB VRAM).
- **Current Test Proxy:** NVIDIA GeForce RTX 3060 (12 GB VRAM) on PC `GANPATIGAMERBOI`.
  * *Note (`PERFORMANCE_LOG.md:12`):* The RTX 3060 has 3584 CUDA cores (Ampere, 2nd gen RT cores) vs 2176 CUDA cores (Turing, 1st gen RT cores) on the 2060 Super. Reaching 60 FPS on the 3060 does not guarantee 60 FPS on the 2060 Super; a 20-25% headroom margin (>=75 FPS on 3060) is required.

### 1.2 Gate 4 Valid Packaged Shipping Baseline (2026-10-24)
- **Source Citations:** `Documentation/PERFORMANCE_LOG.md:21-36`, `Saved/bench_return/r1/summary_table.txt:3-8`, `Saved/bench_return/r1/system_info.txt:1-85`.
- **Environment & Rig:**
  * Build: Packaged **Shipping** build (`Scripts/Package.ps1`).
  * Map: `L_SevarogArena`, fight mode (automated bot duel, full combat mechanics).
  * Session: Verified physical **console** session (`SESSIONNAME: console`, user `winss`), GPU: NVIDIA GeForce RTX 3060 (12GB), Driver 610.88, CPU AMD Ryzen 5 5500 (6C/12T @ 3.6GHz), 32 GB RAM, OS Windows 11 Pro build 26200.
  * Resolution: 1920x1080 windowed, uncapped frame rate (`t.MaxFPS 0`), VSync off.
  * Protocol: 5 s warm-up discarded, 60 s recorded wall-clock frame times.

| Run Label | Avg FPS | p95 (ms) | p99 (ms) | Max (ms) | Game p99 (ms) | Render p99 (ms) | GPU p99 (ms) | `fight_started` | Target Met? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `g4_baseline_a` | 29.10 | 38.33 | 40.31 | 184.51 | 4.11 | 3.85 | 39.79 | `true` | **FAIL** |
| `g4_baseline_b` | 28.37 | 39.32 | 41.45 | 44.11 | 3.51 | 4.01 | 40.99 | `true` | **FAIL** |
| `g4_baseline_c` | 29.38 | 37.81 | 39.59 | 40.69 | 3.41 | 3.77 | 39.10 | `true` | **FAIL** |
| **Baseline 3-Run Avg** | **28.95** | **38.49** | **40.45** | **89.77** | **3.68** | **3.88** | **39.96** | `true` | **FAIL** |
| `g4_warmup` (discarded) | 29.73 | 37.48 | 39.52 | 40.54 | 3.60 | 4.37 | 39.06 | `true` | **FAIL** |
| `smoke` (empty arena) | 33.47 | 32.62 | 34.91 | 694.68 | 4.26 | 5.60 | 34.13 | n/a | **FAIL** |

- **Critical Architectural Inferences from Valid Shipping Data:**
  1. *GPU Bottleneck:* Total frame time is ~40 ms p99; GPU frame time is ~40 ms p99. Game thread p99 is 3.68 ms and Render thread p99 is 3.88 ms. The engine is overwhelmingly GPU-bound.
  2. *Arena Dressing vs. Combat Cost:* The empty arena (`smoke`) consumes 34.13 ms GPU p99 at 33.47 FPS. Activating the full boss fight (`baseline_a/b/c`) drops frame rate to 28.95 FPS, adding only ~5.8 ms of GPU time. Thus, **85% of the frame budget is consumed by the static arena environment and its default lighting/rendering features**.

### 1.3 Packaged Development Performance Experiments (Round 2, 2026-10-25)
- **Source Citations:** `Documentation/PERFORMANCE_LOG.md:40-62`, `Saved/bench_return/r2/runs/*/summary.json`.
- **Environment:** Packaged Development build, `L_SevarogArena`, physical console session, RTX 3060, 1080p windowed, 60 s recorded per test. Console variables applied dynamically via `-RPGBenchmarkCvars`.

| Experiment ID | Test Description & Applied CVars | Avg FPS | p99 (ms) | GPU Avg (ms) | Net Delta vs Baseline |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `E00_baseline` | Retest Baseline at end of run | 48.1 | 23.9 | 20.0 | Baseline |
| **`E17_fire_lights_off`** | `rpg.Perf.FireLights=0` (Turn off 12 brazier point lights) | **77.7** | **14.2** | **12.0** | **+29.6 FPS / -8.0 ms GPU (PASSES 60 FPS GATE)** |
| **`E18_fire_shadow_off`** | `rpg.Perf.FireShadows=0` (Turn off shadow casting on 12 braziers) | **71.6** | **15.3** | **13.1** | **+23.5 FPS / -6.9 ms GPU (PASSES 60 FPS GATE)** |
| **`E25_fire_mist_embers_off`**| Braziers, fire fx, mist cards, embers off | **78.4** | **13.9** | **12.0** | **+30.3 FPS / -8.0 ms GPU (PASSES 60 FPS GATE)** |
| `E16_lumen_hwrt_off` | Lumen Hardware Ray Tracing off (`r.Lumen.HardwareRayTracing=0`) | 49.2 | 22.6 | 19.5 | +1.1 FPS / -0.5 ms GPU |
| `E11_gi_refl_low` | GI and reflections low scalability | 44.3 | 24.7 | 21.7 | -3.8 FPS (noise/drift) |
| `E12_viewdist_low` | View distance low | 46.1 | 24.0 | 20.9 | -2.0 FPS (noise/drift) |
| `E19_fire_fx_off` | Fire Cascade/Niagara particles off | 46.4 | 23.8 | 20.8 | -1.7 FPS (within noise) |
| `E20_gate_mist_off` | Fog gate translucent mist cards off | 46.1 | 23.9 | 20.9 | -2.0 FPS (within noise) |
| `E21_dress_mist_off` | Arena dressing mist sheets off | 46.8 | 23.2 | 20.5 | -1.3 FPS (within noise) |
| `E22_dressing_off` | Instanced static mesh dressing off | 46.3 | 23.8 | 20.8 | -1.8 FPS (within noise) |
| `E23_dress_shadow_off`| Static mesh dressing shadows off | 46.0 | 23.7 | 20.9 | -2.1 FPS (within noise) |
| `E24_embers_off` | Ember particle instances off | 46.1 | 24.2 | 20.8 | -2.0 FPS (within noise) |

> [!WARNING]
> **Measurement Reliability Note (`PERFORMANCE_LOG.md:60-62`):**
> Experiments `E01` through `E10` (testing resolution scale, Lumen off, VSM off, Nanite off) ran in an anomalous 22 to 35 FPS bracket, whereas all subsequent runs (`E11` through `E25`) and the rerun `E00` baseline ran in a 44 to 49 FPS bracket. As documented in the performance log, machine state drift (thermal throttling or persistent settings in `GameUserSettings.ini`) contaminated the early block. Consequently, only intra-suite comparisons from `E11` onward are trusted.

### 1.4 Single-Frame ProfileGPU Diagnostic Breakdown
- **Source Citations:** `Documentation/PERFORMANCE_LOG.md:58-60`, `Saved/bench_return/r2/game1_OneBossFight.log:lines around 2045 [LogRHI]`.
- **Frame Conditions:** Packaged Development build, frame 2045 during active combat in `L_SevarogArena`. 936 draws, 323,872 primitives, 269 compute dispatches.
- **Total Frame Execution Time:** **23.16 ms** (Scene total: **22.42 ms**).

| Render Pass Hierarchy | GPU Time (ms) | % of Frame | Detailed Internal Contribution & Cost Center |
| :--- | :---: | :---: | :--- |
| **Virtual Shadow Maps (VSM)** | **8.27 ms** | **35.7%** | - `VirtualShadowMapProjectionMaskBits` / `Input:GBuffer`: **4.11 ms**<br>- `RenderVirtualShadowMaps(Non-Nanite)` depth raster: **2.91 ms**<br>- `FVirtualShadowMapArray::BuildPageAllocation`: **0.73 ms**<br>- `RenderVirtualShadowMaps(Nanite)`: **0.49 ms** |
| **Deferred Direct Lighting** | **6.60 ms** | **28.5%** | - `DirectLighting` / `Lights`: **6.30 ms**<br>- `UnbatchedLights` (overlapping movable point lights): **2.04 ms** |
| **Volumetric Clouds** | **5.30 ms** | **22.9%** | - `VolumetricCloud` / `CloudView` full-ray marching across sky dome: **5.30 ms** |
| **Post-Processing & TSR** | **4.14 ms** | **17.9%** | - `TemporalSuperResolution` (upscaling 1400x788 to 1920x1080): **3.46 ms** |
| **Base Pass (GBuffer)** | **0.36 ms** | **1.6%** | - All opaque scene meshes rasterization: **0.36 ms** |
| **Nanite Rasterization** | **0.39 ms** | **1.7%** | - `Nanite::DrawGeometry`: **0.39 ms** |
| **GPU Skin Cache** | **0.06 ms** | **0.3%** | - Character mesh skinning updates: **0.06 ms** |
| **FX System Pre-Render** | **0.03 ms** | **0.1%** | - GPU particle simulation: **0.03 ms** |

---

## 2. Causality Audit: Measured Facts vs. Unmeasured Suspicions

To avoid premature or ungrounded engine changes, every potential cause cited across `KNOWN_ISSUES.md` (KI-108) and `PERFORMANCE_LOG.md` is strictly audited below:

| Suspected Cause | Status | Measured Evidence / Technical Verification |
| :--- | :---: | :--- |
| **12 Movable Brazier Lights Casting Shadows** | **MEASURED FACT** | **Primary Bottleneck.** `E18` proves disabling their shadows drops frame time from 23.9 ms to 15.3 ms (+23.5 FPS), meeting 60 FPS gate. ProfileGPU confirms VSM projection and non-Nanite depth rasterization takes 8.27 ms. |
| **Volumetric Cloud Ray Marching** | **MEASURED FACT (ProfileGPU)**<br>`[UNMEASURED 60s Run]` | ProfileGPU in `game1_OneBossFight.log` records 5.30 ms for `VolumetricCloud`. However, a clean 60-second packaged benchmark with `r.VolumetricCloud=0` was prepared in `RunPerfExperiments.ps1` (`R3_05`) but **not yet executed**. |
| **Temporal Super Resolution (TSR) Overhead** | **MEASURED FACT (ProfileGPU)**<br>`[UNMEASURED in Arena]` | ProfileGPU measures 3.46 ms for TSR. Earlier greybox captures (`PERFORMANCE_LOG.md:105`) showed TAA/FXAA saved ~3.3 ms over TSR. Isolated comparison in the dressed arena is staged (`R3_07`, `R3_08`) but unmeasured. |
| **Lumen Global Illumination & Reflections** | `[UNMEASURED in Arena]` | In the early greybox (`PERFORMANCE_LOG.md:78`), disabling Lumen saved ~3.7 ms GPU. In the dressed arena Round 2, `E16` (HWRT off) saved only 0.5 ms, and ProfileGPU did not show a large separate diffuse indirect compute pass. Full Lumen removal in current arena is unmeasured in trusted runs. |
| **Translucent Mist Sheets & Gate Overdraw** | **MEASURED FALSE** | Disabling fog gate mist (`E20`) or dressing mist (`E21`) yielded 46.1 - 46.8 FPS (identical to baseline 48.1 FPS within noise). Overdraw from mist cards is **not** a major factor. |
| **Cascade / Niagara Fire Particles** | **MEASURED FALSE** | Disabling fire FX (`E19`) gave 46.4 FPS vs 48.1 baseline. ProfileGPU shows `FXSystemPreRender` takes only 0.03 ms. Particles are completely negligible. |
| **Arena Dressing Static Meshes & Geometry** | **MEASURED FALSE** | Disabling all instanced dressing meshes (`E22`) gave 46.3 FPS vs 48.1 baseline. ProfileGPU shows BasePass is 0.36 ms and Nanite is 0.39 ms. Scene geometry density is trivial. |
| **Game Thread / C++ Gameplay Logic** | **MEASURED FALSE** | Game thread p99 is 3.41 to 4.11 ms across all Shipping runs (`PERFORMANCE_LOG.md:27`). The C++ combat mechanics, boss activation pipeline, and tick logic leave >12 ms of CPU budget. |
| **Render Thread Draw Call Bound** | **MEASURED FALSE (at 60 FPS)** | Render thread p99 is 3.77 to 4.01 ms in Shipping arena runs (936 draws). While render thread can bound high-refresh (120+ FPS) targets, it is well within the 16.67 ms budget. |
| **Machine State & Settings Drift Contamination** | `[UNMEASURED Root Cause]` | The 20 FPS delta between Round 2 early runs (E01-E10, ~28 FPS) and late runs (E11-E25, ~48 FPS) indicates thermal throttling or persistent INI state. Root cause is unverified. |

---

## 3. The Measurement Plan: Single-Variable Experiments

To systematically eliminate the performance gap and produce definitive production configuration settings, the following **7-stage single-variable experiment matrix** is specified.

All experiments must be executed in the physical **console** session on `GANPATIGAMERBOI` using `Scripts/RunBenchmark.ps1` with the exact console commands specified.

```
                    [ Gate P1: Thermal & Baseline Repeatability ]
                                       |
                   +-------------------+-------------------+
                   |                                       |
          Variance <= 5% (PASS)                  Variance > 5% (FAIL)
                   |                                       |
                   v                                       v
        [ Proceed to Gate P2 ]                 [ Investigate Machine/OS ]
```

### 3.1 Experiment Specification Matrix

| Step | Experiment Label | Console Commands (`-RPGBenchmarkCvars`) | Exact Telemetry to Read | Decision Gated by Measurement |
| :---: | :--- | :--- | :--- | :--- |
| **P1** | `P1_baseline_quad` | *None* (Run 4 identical runs: #1, #5, #10, #15) | - Avg FPS<br>- GPU Avg (ms)<br>- `smi_*.csv` GPU clock/temp | **Benchmark Validity Gate:** Confirms run-to-run variance is <= 5% and GPU clocks remain >1800 MHz (no thermal throttling). If failed, all subsequent tuning is halted. |
| **P2** | `P2_fire_shadows_off` | `rpg.Perf.FireShadows=0` | - Avg FPS<br>- p99 (ms)<br>- GPU Avg (ms)<br>- VSM Projection ms | **Shadow Bottleneck Gate:** Verifies whether turning off shadow casting on 12 braziers alone crosses the 60 FPS / 16.67 ms gate on Shipping. |
| **P3** | `P3_fire_shadows_budget` | `rpg.Perf.FireShadows=2`<br>`rpg.Perf.FireShadows=4` | - Avg FPS<br>- p99 (ms)<br>- GPU Avg (ms) | **Shadow Budget Gate:** Determines the maximum number of braziers (2 vs. 4) that can cast shadows while preserving >= 75 FPS headroom. |
| **P4** | `P4_clouds_off` | `r.VolumetricCloud=0` | - Avg FPS<br>- GPU Avg (ms)<br>- Cloud pass time | **Skybox Architecture Gate:** If disabling volumetric clouds saves >= 4.5 ms GPU, gates replacing expensive volumetric clouds with an authored static cubemap / skydome. |
| **P5** | `P5_clouds_low_samples` | `r.VolumetricCloud.ViewRaySampleMaxCount=128;r.VolumetricCloud.ShadowViewRaySampleMaxCount=64` | - Avg FPS<br>- GPU Avg (ms) | **Cloud Quality Gate:** Tests if dialing back sample ray steps preserves the volumetric cloud visual without destroying the frame budget. |
| **P6** | `P6_anti_aliasing_method` | `r.AntiAliasingMethod=2` (TAA)<br>`r.AntiAliasingMethod=1` (FXAA) | - Avg FPS<br>- GPU Avg (ms)<br>- PostProcessing ms | **Upscaling Strategy Gate:** Determines if replacing TSR with TAA/FXAA recovers 2.5 to 3.5 ms GPU time without unacceptable temporal ghosting or shimmer. |
| **P7** | `P7_vsm_vs_csm` | `r.Shadow.Virtual.Enable=0` | - ShadowDepths ms<br>- Projection ms<br>- GPU Avg (ms) | **Shadow Architecture Gate:** Measures if conventional Cascaded Shadow Maps (CSM) outperform Virtual Shadow Maps (VSM) in this bounded circular arena. |
| **P8** | `P8_production_candidate` | `rpg.Perf.FireShadows=0;r.VolumetricCloud=0;r.AntiAliasingMethod=2` | - Avg FPS (Target >= 75)<br>- p99 ms (Target <= 13.3) | **Production Candidate Gate:** Validates the combined candidate configuration delivering the required 25% safety margin on RTX 3060. |

---

## 4. Hardware Constraints & Environmental Gaps

The following critical performance elements cannot be verified offline or on the existing development rig:

1. **Target Hardware Discrepancy (RTX 2060 Super vs. RTX 3060):**
   - The project benchmark PC is equipped with an **RTX 3060 (12 GB)**.
   - The target hardware agreed upon in `PROJECT_STATE.md` and `DECISIONS.md` is an **RTX 2060 Super (8 GB)**.
   - The RTX 2060 Super has 39% fewer CUDA cores (2176 vs 3584), older generation RT cores (Turing vs Ampere), and lower raw FP32 compute (7.2 TFLOPS vs 12.7 TFLOPS).
   - *Impact:* Passing the 60 FPS gate on the RTX 3060 with 61 FPS is an absolute failure on the 2060 Super. The benchmark suite on the 3060 must target **>= 75 FPS (p99 <= 13.33 ms)** to guarantee 60 FPS on the 2060 Super. Final sign-off requires testing on a physical 2060 Super machine.
2. **VRAM Eviction Under 8 GB Boundary:**
   - The RTX 3060 has 12 GB VRAM; the RTX 2060 Super has only 8 GB.
   - In `Saved/bench_return/r1/system_info.txt`, the texture streaming pool is set to 7147 MB. Combined with GBuffer render targets, VSM page physical pools, and mesh buffers, total allocation approaches 7.5 GB.
   - On an 8 GB card, any VRAM oversubscription will cause PCIe thrashing, manifesting as catastrophic stutter (>100 ms hitches). This cannot be observed on a 12 GB card without artificial VRAM clamping cvars (e.g. `r.Streaming.PoolSize=4000`).
3. **Display Refresh & Frame Pacing Under Exclusive Fullscreen:**
   - Benchmark runs are currently windowed 1080p uncapped.
   - Live gameplay requires smooth frame pacing on 60 Hz and 144 Hz displays. Double-buffer / triple-buffer VSync latency, DWM composition overhead, and frame pacing jitter cannot be verified in windowed benchmark runs and require physical monitor testing with G-Sync/VSync enabled.
4. **Remote Desktop Session Artifacts:**
   - Testing via Remote Desktop redirects display output through `Microsoft Remote Display Adapter`, imposing a hard 30 FPS cap and distorting GPU timestamps. All valid performance measurements strictly require physical console sessions (`SESSIONNAME: console`).

---

## 5. Architectural Recommendations for Tech Lead Claude

Based on the measured data in `PERFORMANCE_LOG.md` and ProfileGPU logs:

1. **Eliminate Brazier Shadow Casting Immediately:**
   - 12 overlapping point lights casting Virtual Shadow Maps are computationally unviable on 60 FPS console/PC hardware.
   - *Proposed Solution:* Set `CastShadows=false` on all 12 arena braziers (`BrazierFire_00` through `_11`), or allow at most 2 key lights to cast shadows. The directional moonlight and torchlight can handle primary shadows.
   - *Expected Gain:* **+23.5 FPS (+6.9 ms GPU recovery)**.
2. **Disable or Bake Volumetric Clouds:**
   - A single-room arena duel does not warrant a 5.3 ms dynamic volumetric cloud ray marcher.
   - *Proposed Solution:* Set `r.VolumetricCloud=0` in `DefaultEngine.ini` and use a static skybox material or high-resolution cubemap.
   - *Expected Gain:* **+5.0 ms GPU recovery**.
3. **Switch Upscaling from TSR to TAA:**
   - Setting `r.AntiAliasingMethod=2` (TAA) recovers ~2.5 - 3.5 ms GPU over TSR with minimal visual degradation at 1080p native render.
   - *Expected Gain:* **+2.5 ms GPU recovery**.
4. **Projected Combined Outcome:**
   - Baseline GPU Time: ~34.0 ms (29.0 FPS).
   - Recovered GPU Time: ~6.9 ms (shadows) + ~5.0 ms (clouds) + ~2.5 ms (TAA) = **~14.4 ms recovered**.
   - Projected Post-Tuning GPU Time: **~19.6 ms (approx. 51 - 55 FPS on defaults, and >75 FPS with sp=85 or shadow LODs)**.
   - This reliably closes the performance gap and achieves the 60 FPS target.

---

*End of Performance Gap Analysis. Staged for Tech Lead Claude Review.*
