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
    # round 3 (2026-10-25): the fire shadows are the main cost (round 2); the GPU profile also shows the volumetric clouds (5.3 ms) and TSR (3.5 ms). R3_00 is repeated at the end and after every fourth experiment to see whether the machine state drifts (round 2 had slow early runs and fast later ones with no explanation).
    @{ N = 'R3_00_baseline';          C = '' },
    @{ N = 'R3_01_fire_shadows_0';    C = 'rpg.Perf.FireShadows=0' },
    @{ N = 'R3_02_fire_shadows_2';    C = 'rpg.Perf.FireShadows=2' },
    @{ N = 'R3_03_fire_shadows_4';    C = 'rpg.Perf.FireShadows=4' },
    @{ N = 'R3_04_baseline';          C = '' },
    @{ N = 'R3_05_clouds_off';        C = 'r.VolumetricCloud=0' },
    @{ N = 'R3_06_cloud_samples_low'; C = 'r.VolumetricCloud.ViewRaySampleMaxCount=128;r.VolumetricCloud.ShadowViewRaySampleMaxCount=64' },
    @{ N = 'R3_07_taa';               C = 'r.AntiAliasingMethod=2' },
    @{ N = 'R3_08_fxaa';              C = 'r.AntiAliasingMethod=1' },
    @{ N = 'R3_09_baseline';          C = '' },
    @{ N = 'R3_10_candidate_a';       C = 'rpg.Perf.FireShadows=2;r.VolumetricCloud.ViewRaySampleMaxCount=128;r.VolumetricCloud.ShadowViewRaySampleMaxCount=64;r.AntiAliasingMethod=2' },
    @{ N = 'R3_11_candidate_b';       C = 'rpg.Perf.FireShadows=0;r.VolumetricCloud=0;r.AntiAliasingMethod=2' },
    @{ N = 'R3_12_candidate_a_sp85';  C = 'rpg.Perf.FireShadows=2;r.VolumetricCloud.ViewRaySampleMaxCount=128;r.VolumetricCloud.ShadowViewRaySampleMaxCount=64;r.AntiAliasingMethod=2;r.ScreenPercentage=85' },
    @{ N = 'R3_13_baseline';          C = '' },
    @{ N = 'R3_14_floor_lights_off';  C = 'rpg.Perf.FireLights=0' },
    @{ N = 'R3_15_baseline_end';      C = '' }
)
if ($Only) { $Experiments = @($Experiments | Where-Object { $name = $_.N; $Only | Where-Object { $name -like "$_*" } }) }
$run = Join-Path $PSScriptRoot 'RunBenchmark.ps1'
Write-Host "Warm-up (thrown away) ..."
$wargs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $run, '-Label', 'pxwarm')
if ($StageDir) { $wargs += @('-StageDir', $StageDir) }
& powershell @wargs | Out-Null
$rows = @()
foreach ($e in $Experiments) {
    $extra = ''
    if ($e.C) { $extra = '-RPGBenchmarkCvars="' + $e.C + '"' }
    Write-Host "=== $($e.N): $($e.C)"
    # GPU clock, power, temperature, utilisation and throttle reasons once per second during the run (to see state drift)
    $smiOut = Join-Path $Root ("Saved\smi_{0}.csv" -f $e.N)
    $smi = Start-Process -FilePath 'nvidia-smi' -ArgumentList @('--query-gpu=timestamp,clocks.gr,clocks.max.gr,clocks.mem,power.draw,temperature.gpu,utilization.gpu,clocks_throttle_reasons.active,pstate','--format=csv','-l','1') -RedirectStandardOutput $smiOut -PassThru -WindowStyle Hidden -ErrorAction SilentlyContinue
    # empty values are not passed at all (an empty -ExtraArgs made round 2's E00 fail: PowerShell drops the empty argument and then misses the value)
    $rargs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $run, '-Label', $e.N)
    if ($extra) { $rargs += @('-ExtraArgs', $extra) }
    if ($StageDir) { $rargs += @('-StageDir', $StageDir) }
    & powershell @rargs | Out-Null
    $stageForRoots = if ($StageDir) { $StageDir } else { Join-Path $Root 'Saved\StagedBuilds\Windows' }
    $roots = @((Join-Path $stageForRoots 'OneBossFight\Saved\Benchmark'), (Join-Path $env:LOCALAPPDATA 'OneBossFight\Saved\Benchmark'))
    if ($smi) { Stop-Process -Id $smi.Id -Force -ErrorAction SilentlyContinue }
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
