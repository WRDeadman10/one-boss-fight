# C334 / P1-P4 performance kit — OFFLINE ONLY

No run/build/package permission. Requires owner physical-console session plus explicit lead release of one frozen packaged Development build and engine lane. No automatic build if stage missing. Do not mix Shipping and Development baselines. A packaged binary is not certified from the Editor DLL or current Source alone; pin launcher and actual OneBossFight/Binaries/Win64 executable, cooked content/manifest and script versions on the measurement PC.

## Current source support / material limitation

- Benchmark/RPGBenchmarkRunner.cpp:90-117 parses -RPGBenchmarkCvars="name=value;name=value", resolves each IConsoleVariable and calls Set(...ECVF_SetByConsole). Unknown names get an UNKNOWN variable note. AppliedCvars logs requested strings, not Get-value readback; success cannot be assumed from echoed text alone.
- Arena/RPGPerfSwitches.cpp:6-27 defines project switches ONLY in non-Shipping builds: FireLights, FireShadows, FireFx, GateMist, DressingAll, DressingMist, DressingShadows, Embers (all prefixed rpg.Perf.). Boolean switches default1; FireShadows default-1 authored, 0 off, positive N budget. Shipping returns constants and has no registrations for these names. RPGFireSource.cpp:96 onward also compiles their Tick effects out in Shipping. Thus P2/P3 DO NOT test fire-shadow changes in Shipping with current Source. RunPerfExperiments.ps1 comments about Shipping support refer to the generic parser, not availability of these custom switches. This must be corrected in A220's Shipping interpretation before measuring.
- r.VolumetricCloud and r.AntiAliasingMethod can use the SAME generic parser when registered in the staged engine. Cloud registration is local UE5.5 VolumetricCloudRendering.cpp:38; renderer looks up AA in RendererScene.cpp:1344. AA2=TAA, AA1=FXAA, AA4=TSR in UE5 (A220's AA3=TSR is incorrect; AA3 is MSAA). Stage/version/flag priority and actual effect still require raw logs/runtime verification; no engine setting was changed here.
- FireShadows positive-N implementation RPGFireSource.cpp:108-113 budgets by actor label BrazierFire_XX and authored bCastShadows, not an unconditional N arbitrary lights. Record actual actor coverage. Do not claim N effective lights solely from cvar string.

## Commands (owner PC, ONE line at a time after release)

Use physical console, consistent power/display/driver state; no RDP comparison. Explicit packaged Development stage below is a proposed location, not verified present. Set to exact accepted stage; missing EXE => STOP, never invoke Package.ps1. Warm-up5s and recorded60s are source defaults (RPGBenchmarkRunner.h:41,45), verify staged summary. All runs same map/full fight/window1920x1080, no -Empty. RunBenchmark.ps1 defaults clear ONLY staged/local GameUserSettings.ini (lines47-51); this is a real per-run settings-file deletion and must be part of owner-approved controls. Preserve config baseline before first run; do not secretly add KeepConfig or mix protocols.

```powershell
Set-Location 'C:\UnrealProject\OneBossFight'
$stage='C:\UnrealProject\OneBossFight\Saved\StagedBuilds_Development\Windows'
if(!(Test-Path -LiteralPath (Join-Path $stage 'OneBossFight.exe'))){throw 'STOP: accepted packaged stage missing; no build released'}
# Discarded session warm-up; retain raw evidence but exclude from comparison.
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_warmup -ResX 1920 -ResY 1080
# P1: three unchanged baselines (lead C334 requires baseline x3).
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_P1_base1 -ResX 1920 -ResY 1080
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_P1_base2 -ResX 1920 -ResY 1080
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_P1_base3 -ResX 1920 -ResY 1080
# P2: only fire shadows off, compare against same-build baseline.
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_P2_shadows0 -ResX 1920 -ResY 1080 -ExtraArgs '-RPGBenchmarkCvars="rpg.Perf.FireShadows=0"'
# P3: two independent authored shadow budgets; separate processes reset state.
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_P3_shadows2 -ResX 1920 -ResY 1080 -ExtraArgs '-RPGBenchmarkCvars="rpg.Perf.FireShadows=2"'
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_P3_shadows4 -ResX 1920 -ResY 1080 -ExtraArgs '-RPGBenchmarkCvars="rpg.Perf.FireShadows=4"'
# P4: clouds only off; NOT combined with fire changes.
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_P4_clouds0 -ResX 1920 -ResY 1080 -ExtraArgs '-RPGBenchmarkCvars="r.VolumetricCloud=0"'
# End repeat detects machine-state drift; preserve/reject unstable comparisons.
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunBenchmark.ps1 -StageDir $stage -Label C334_P1_end -ResX 1920 -ResY 1080
```

Do not paste the whole block as an unattended chain. After EACH process: require printed game exit0, a NEW uniquely labelled result directory, full60s frames/summary, fight_started true, requested build/GPU/resolution, no UNKNOWN variable or rejected-priority warning. RunBenchmark.ps1 prints game exit but does not explicitly propagate it; shell success alone is insufficient. Stop/preserve/report any failure or drift before proceeding. No retries inferred. RunPerfExperiments.ps1 auto-selects Dev/fallback Shipping and chains experiments; do not use its fallback for these P2/P3 controls.

Record summary avg_fps, p99_ms, gpu_avg_ms/gpu_p99_ms, game_thread_p99_ms, render_thread_p99_ms and exact conditions, raw game/stdout, frames.csv, summary.json, console-variable diagnostics and SHA256. Optional nvidia-smi sampling requires separate owner/lead release; P1 cannot assert clock/throttle stability without that evidence. Fixed1800MHz or75FPS proxy thresholds are heuristics, not established acceptance. No RTX3060 margin guarantees RTX2060Super60FPS. Performance acceptance remains target-hardware packaged1080p60FPS/p99<=16.67ms, not a proxy average alone. P2/P3 quantify cost vs visual shadow budget; P4 frame/GPU delta is not isolated cloud-pass GPU time without a GPU capture. A220's >=4.5ms cloud replacement gate is a proposal, not measured proof or asset-edit release.
