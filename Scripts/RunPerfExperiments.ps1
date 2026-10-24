<#
.SYNOPSIS
  Runs a table of performance experiments on the benchmark PC: one full-fight benchmark per console variable set, then prints and saves one comparison table.

.DESCRIPTION
  Uses Scripts\RunBenchmark.ps1 with -RPGBenchmarkCvars (the game applies the variables itself, so it works in a Shipping build). Each experiment takes about 2 minutes (loading, 5 s warm-up, 60 s recorded). Run it from the kit/project root in the CONSOLE session, with nothing else heavy running. The first run of the session is a thrown-away warm-up.
  Output: Saved\perf_experiments_<timestamp>.txt (the table) next to the individual run folders; BenchKit_Collect.ps1 then zips everything.
  -Only 'E00,E04' runs a subset. The experiments are defined in the $Experiments table below (name, console variables separated by ;).

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1
  powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1 -Only E00,E13
#>
param([string[]]$Only, [string]$StageDir = '')
if ($Only) { $Only = @($Only | ForEach-Object { $_ -split ',' }) }
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
# the experiments run on the DEVELOPMENT stage when the kit has one (it knows the rpg.Perf.* switches and ProfileGPU; its GPU time is the same as Shipping), else on the Shipping stage
if (-not $StageDir) {
    $dev = Join-Path $Root 'Saved\StagedBuilds_Development\Windows'
    if (Test-Path (Join-Path $dev 'OneBossFight.exe')) { $StageDir = $dev }
}
Write-Host "Stage: $(if ($StageDir) { $StageDir } else { 'Saved\StagedBuilds\Windows (Shipping)' })"
$Experiments = @(
    @{ N = 'E00_baseline';        C = '' },
    @{ N = 'E01_sp75';            C = 'r.ScreenPercentage=75' },
    @{ N = 'E02_sp60';            C = 'r.ScreenPercentage=60' },
    @{ N = 'E03_lumen_off';       C = 'r.DynamicGlobalIlluminationMethod=0;r.ReflectionMethod=2' },
    @{ N = 'E04_vsm_off';         C = 'r.Shadow.Virtual.Enable=0' },
    @{ N = 'E05_nanite_off';      C = 'r.Nanite=0' },
    @{ N = 'E06_volfog_off';      C = 'r.VolumetricFog=0' },
    @{ N = 'E07_fxaa';            C = 'r.AntiAliasingMethod=1' },
    @{ N = 'E08_post_low';        C = 'sg.PostProcessQuality=1' },
    @{ N = 'E09_effects_low';     C = 'sg.EffectsQuality=1' },
    @{ N = 'E10_shadow_low';      C = 'sg.ShadowQuality=1' },
    @{ N = 'E11_gi_refl_low';     C = 'sg.GlobalIlluminationQuality=1;sg.ReflectionQuality=1' },
    @{ N = 'E12_viewdist_low';    C = 'sg.ViewDistanceQuality=1' },
    @{ N = 'E13_lumen_vsm_off';   C = 'r.DynamicGlobalIlluminationMethod=0;r.ReflectionMethod=2;r.Shadow.Virtual.Enable=0' },
    @{ N = 'E14_lumen_vsm_off_sp75'; C = 'r.DynamicGlobalIlluminationMethod=0;r.ReflectionMethod=2;r.Shadow.Virtual.Enable=0;r.ScreenPercentage=75' },
    @{ N = 'E16_lumen_hwrt_off';  C = 'r.Lumen.HardwareRayTracing=0;r.Lumen.Reflections.HardwareRayTracing=0' },
    @{ N = 'E17_fire_lights_off'; C = 'rpg.Perf.FireLights=0' },
    @{ N = 'E18_fire_shadow_off'; C = 'rpg.Perf.FireShadows=0' },
    @{ N = 'E19_fire_fx_off';     C = 'rpg.Perf.FireFx=0' },
    @{ N = 'E20_gate_mist_off';   C = 'rpg.Perf.GateMist=0' },
    @{ N = 'E21_dress_mist_off';  C = 'rpg.Perf.DressingMist=0' },
    @{ N = 'E22_dressing_off';    C = 'rpg.Perf.DressingAll=0' },
    @{ N = 'E23_dress_shadow_off'; C = 'rpg.Perf.DressingShadows=0' },
    @{ N = 'E24_embers_off';      C = 'rpg.Perf.Embers=0' },
    @{ N = 'E25_fire_mist_embers_off'; C = 'rpg.Perf.FireLights=0;rpg.Perf.FireFx=0;rpg.Perf.GateMist=0;rpg.Perf.DressingMist=0;rpg.Perf.Embers=0' },
    @{ N = 'E15_all_low_sp75';    C = 'sg.PostProcessQuality=1;sg.EffectsQuality=1;sg.ShadowQuality=1;sg.GlobalIlluminationQuality=1;sg.ReflectionQuality=1;sg.ViewDistanceQuality=1;r.ScreenPercentage=75' }
)
if ($Only) { $Experiments = @($Experiments | Where-Object { $name = $_.N; $Only | Where-Object { $name -like "$_*" } }) }
$run = Join-Path $PSScriptRoot 'RunBenchmark.ps1'
Write-Host "Warm-up (thrown away) ..."
& powershell -NoProfile -ExecutionPolicy Bypass -File $run -Label 'pxwarm' -StageDir $StageDir | Out-Null
$rows = @()
foreach ($e in $Experiments) {
    $extra = ''
    if ($e.C) { $extra = '-RPGBenchmarkCvars="' + $e.C + '"' }
    Write-Host "=== $($e.N): $($e.C)"
    & powershell -NoProfile -ExecutionPolicy Bypass -File $run -Label $e.N -ExtraArgs $extra -StageDir $StageDir | Out-Null
    $stageForRoots = if ($StageDir) { $StageDir } else { Join-Path $Root 'Saved\StagedBuilds\Windows' }
    $roots = @((Join-Path $stageForRoots 'OneBossFight\Saved\Benchmark'), (Join-Path $env:LOCALAPPDATA 'OneBossFight\Saved\Benchmark'))
    $dir = $roots | ForEach-Object { Get-ChildItem $_ -Directory -Filter "$($e.N)_*" -ErrorAction SilentlyContinue } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $dir) { Write-Host "  no result for $($e.N)"; continue }
    $s = Get-Content (Join-Path $dir.FullName 'summary.json') -Raw | ConvertFrom-Json
    $rows += [pscustomobject]@{ Name = $e.N; avg_fps = [math]::Round($s.avg_fps, 1); p99_ms = [math]::Round($s.p99_ms, 1); gpu_avg_ms = [math]::Round($s.gpu_avg_ms, 1); gpu_p99_ms = [math]::Round($s.gpu_p99_ms, 1); game_p99 = [math]::Round($s.game_thread_p99_ms, 1); render_p99 = [math]::Round($s.render_thread_p99_ms, 1); gpu = $s.gpu; fight = $s.fight_started; cvars = $s.cvars }
    Write-Host ("  avg {0} fps, p99 {1} ms, gpu avg {2} ms" -f $rows[-1].avg_fps, $rows[-1].p99_ms, $rows[-1].gpu_avg_ms)
}
$out = Join-Path $Root ("Saved\perf_experiments_{0}.txt" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
($rows | Format-Table -AutoSize | Out-String -Width 400) | Out-File $out -Encoding utf8
$rows | Format-Table Name, avg_fps, p99_ms, gpu_avg_ms, gpu_p99_ms, game_p99, render_p99, fight -AutoSize
Write-Host "Table saved to $out"
