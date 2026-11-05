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
  powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1 -Round6 -TsrAnchorScreenPercentage <measured>
  powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunPerfExperiments.ps1 -Round6Tuning -TsrAnchorScreenPercentage <measured> -BestDlssMode Performance -BestDlssScreenPercentage <measured> -Phase1Accepted -OwnerImageQualityAccepted
#>
param([string[]]$Only, [string]$StageDir = '', [switch]$Round5, [switch]$Round6, [switch]$Round6Tuning, [switch]$Phase1Accepted, [switch]$OwnerImageQualityAccepted, [ValidateRange(1,400)][double]$TsrAnchorScreenPercentage = 0, [ValidateSet('DLAA','Quality','Balanced','Performance')][string]$BestDlssMode, [ValidateRange(1,400)][double]$BestDlssScreenPercentage = 0, [switch]$DryRun)
if ($Only) { $Only = @($Only | ForEach-Object { $_ -split ',' }) }
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
# the experiments run on the DEVELOPMENT stage when the kit has one (it knows the rpg.Perf.* switches and ProfileGPU; its GPU time is the same as Shipping), else on the Shipping stage
if (-not $StageDir) {
    $dev = Join-Path $Root 'Saved\StagedBuilds_Development\Windows'
    if (Test-Path (Join-Path $dev 'OneBossFight.exe')) { $StageDir = $dev }
}
if ($DryRun) { Write-Host 'Stage: not used in dry-run; no game will launch.' }
else { Write-Host "Stage: $(if ($StageDir) { $StageDir } else { 'Saved\StagedBuilds\Windows (Shipping)' })" }
$Experiments = @(
    # round 3 (2026-10-25): the fire shadows are the main cost (round 2); the GPU profile also shows the volumetric clouds (5.3 ms) and TSR (3.5 ms). R3_00 is repeated at the end and after every fourth experiment to see whether the machine state drifts (round 2 had slow early runs and fast later ones with no explanation).
    @{ N = 'R3_00_baseline';          C = '' },
    @{ N = 'R3_01_fire_shadows_0';    C = 'rpg.Perf.FireShadows=0' },
    @{ N = 'R3_02_fire_shadows_2';    C = 'rpg.Perf.FireShadows=2' },
    @{ N = 'R3_03_fire_shadows_4';    C = 'rpg.Perf.FireShadows=4' },
    @{ N = 'R3_04_baseline';          C = '' },
    @{ N = 'R3_05_clouds_off';        C = 'r.VolumetricCloud=0' },
    @{ N = 'R3_06_cloud_samples_low'; C = 'r.VolumetricCloud.ViewRaySampleMaxCount=128;r.VolumetricCloud.Shadow.ViewRaySampleMaxCount=64' },
    @{ N = 'R3_07_taa';               C = 'r.AntiAliasingMethod=2' },
    @{ N = 'R3_08_fxaa';              C = 'r.AntiAliasingMethod=1' },
    @{ N = 'R3_09_baseline';          C = '' },
    @{ N = 'R3_10_candidate_a';       C = 'rpg.Perf.FireShadows=2;r.VolumetricCloud.ViewRaySampleMaxCount=128;r.VolumetricCloud.Shadow.ViewRaySampleMaxCount=64;r.AntiAliasingMethod=2' },
    @{ N = 'R3_11_candidate_b';       C = 'rpg.Perf.FireShadows=0;r.VolumetricCloud=0;r.AntiAliasingMethod=2' },
    @{ N = 'R3_12_candidate_a_sp85';  C = 'rpg.Perf.FireShadows=2;r.VolumetricCloud.ViewRaySampleMaxCount=128;r.VolumetricCloud.Shadow.ViewRaySampleMaxCount=64;r.AntiAliasingMethod=2;r.ScreenPercentage=85' },
    @{ N = 'R3_13_baseline';          C = '' },
    @{ N = 'R3_14_floor_lights_off';  C = 'rpg.Perf.FireLights=0' },
    @{ N = 'R3_15_baseline_end';      C = '' }
)
if ($Round5) {
    $planPath = Join-Path $PSScriptRoot 'round5_experiments.json'
    $plan = Get-Content $planPath -Raw | ConvertFrom-Json
    if ($plan.schema -ne 'onebossfight.round5-experiment-plan/v1' -or $plan.round -ne 5) { throw "Invalid Round 5 plan: $planPath" }
    $Experiments = @($plan.experiments | ForEach-Object { @{ N = $_.name; C = $_.cvar; Kind = $_.kind; Group = $_.baseline_group } })
}
if (@($Round5, $Round6, $Round6Tuning).Where({ $_ }).Count -gt 1) { throw 'Select one experiment round or phase, not multiple.' }
if ($Round6 -or $Round6Tuning) {
    if ($Only) { throw 'Round 6 cannot be subset with -Only; anchor spacing and the three-trial balance must remain intact.' }
    if ($TsrAnchorScreenPercentage -le 0) { throw 'Round 6 requires -TsrAnchorScreenPercentage from P2a measured active TSR screen percentage; do not guess.' }
    if ($Round6Tuning -and (-not $BestDlssMode -or $BestDlssScreenPercentage -le 0)) { throw 'Round 6 tuning requires the owner-selected -BestDlssMode and its measured -BestDlssScreenPercentage.' }
    if ($Round6Tuning -and -not ($Phase1Accepted -and $OwnerImageQualityAccepted)) { throw 'Round 6 tuning requires accepted Phase 1 performance evidence and owner image-quality acceptance.' }
    $round6Plan = Get-Content (Join-Path $PSScriptRoot 'round6_experiments.json') -Raw | ConvertFrom-Json
    if ($round6Plan.schema -ne 'onebossfight.round6-experiment-plan/v1' -or $round6Plan.round -ne 6) { throw 'Invalid Round 6 experiment plan.' }
    $Experiments = @()
    $treatmentCount = 0
    $anchorIndex = 0
    $phaseSuffix = if ($Round6Tuning) { 'T' } else { 'M' }
    $modeLabel = if ($Round6Tuning) { $BestDlssMode } else { 'all' }
    $trialOrders = if ($Round6Tuning) { $round6Plan.phase2_order } else { $round6Plan.phase1_order }
    $anchorCvars = "r.NGX.DLSS.Enable=0;r.ScreenPercentage=$TsrAnchorScreenPercentage"
    $Experiments += @{ N = ('R6{0}_{1}_{2:D2}_TSR_anchor_{3}' -f $phaseSuffix, $modeLabel, $Experiments.Count, $anchorIndex); C = $anchorCvars; Kind = 'baseline'; Group = 0; ExpectedPercent = $TsrAnchorScreenPercentage; Extra = '' }
    for ($trial = 0; $trial -lt $trialOrders.Count; $trial++) {
        foreach ($key in $trialOrders[$trial]) {
            $spec = $round6Plan.treatments | Where-Object { $_.key -eq $key } | Select-Object -First 1
            if (-not $spec) { throw "Round 6 plan is missing treatment: $key" }
            $mode = if ($spec.mode -eq 'best') { $BestDlssMode } else { $spec.mode }
            $screenPercentage = if ($spec.mode -eq 'best') { $BestDlssScreenPercentage } else { [double]$spec.screen_percentage }
            $cvars = "r.NGX.DLSS.Enable=1;r.ScreenPercentage=$screenPercentage"
            if ($spec.cvar) { $cvars += ";$($spec.cvar)" }
            $treatmentCount++
            $group = [math]::Floor(($treatmentCount - 1) / $round6Plan.anchor_every_treatments)
            $Experiments += @{ N = ('R6{0}_{1}_{2:D2}_{3}_t{4}' -f $phaseSuffix, $mode, $Experiments.Count, $key, ($trial + 1)); C = $cvars; Kind = 'treatment'; Group = $group; ExpectedPercent = $screenPercentage; ExpectedMode = $mode; Extra = '-LogCmds="LogDLSS Verbose,LogDLSSNGXRHI Verbose"' }
            if (($treatmentCount % $round6Plan.anchor_every_treatments) -eq 0) {
                $anchorIndex++
                $Experiments += @{ N = ('R6{0}_{1}_{2:D2}_TSR_anchor_{3}' -f $phaseSuffix, $modeLabel, $Experiments.Count, $anchorIndex); C = $anchorCvars; Kind = 'baseline'; Group = $group + 1; ExpectedPercent = $TsrAnchorScreenPercentage; Extra = '' }
            }
        }
    }
    if (($treatmentCount % $round6Plan.anchor_every_treatments) -ne 0) {
        $Experiments += @{ N = ('R6{0}_{1}_{2:D2}_TSR_anchor_end' -f $phaseSuffix, $modeLabel, $Experiments.Count); C = $anchorCvars; Kind = 'baseline'; Group = [math]::Ceiling($treatmentCount / $round6Plan.anchor_every_treatments); ExpectedPercent = $TsrAnchorScreenPercentage; Extra = '' }
    }
}
if ($Only) { $Experiments = @($Experiments | Where-Object { $name = $_.N; $Only | Where-Object { $name -like "$_*" } }) }
if ($DryRun) {
    $Experiments | ForEach-Object { [pscustomobject]@{ Name = $_.N; Kind = $(if ($_.Kind) { $_.Kind } else { 'experiment' }); BaselineGroup = $_.Group; CVar = $_.C; ExtraArgs = $_.Extra } } | Format-Table -AutoSize
    exit 0
}
$run = Join-Path $PSScriptRoot 'RunBenchmark.ps1'
if ($Round5 -and $env:H019_ENCOUNTER_DEFINITION -ne '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter') {
    throw 'Round 5 must measure the selected data route; set H019_ENCOUNTER_DEFINITION to the Queue U README value first.'
}
if (($Round6 -or $Round6Tuning) -and $env:H019_ENCOUNTER_DEFINITION -ne '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter') {
    throw 'Round 6 must measure the selected data route; set H019_ENCOUNTER_DEFINITION to the Queue U README value first.'
}
$warmLabel = if ($Round6Tuning) { 'R6T_warmup' } elseif ($Round6) { 'R6M_warmup' } elseif ($Round5) { 'R5_warmup' } else { 'pxwarm' }
Write-Host "Warm-up (thrown away) ..."
$wargs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $run, '-Label', $warmLabel)
if ($StageDir) { $wargs += @('-StageDir', $StageDir) }
& powershell @wargs | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Benchmark warm-up failed with exit code $LASTEXITCODE" }
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
    $launchExtra = (@($extra, $e.Extra) | Where-Object { $_ }) -join ' '
    if ($launchExtra) { $rargs += @('-ExtraArgs', $launchExtra) }
    if ($StageDir) { $rargs += @('-StageDir', $StageDir) }
    try {
        & powershell @rargs | Out-Null
        $runExitCode = $LASTEXITCODE
        if ($runExitCode -ne 0) { throw "Benchmark experiment $($e.N) failed with exit code $runExitCode" }
    }
    finally {
        if ($smi -and -not $smi.HasExited) { Stop-Process -Id $smi.Id -Force -ErrorAction SilentlyContinue }
    }
    $stageForRoots = if ($StageDir) { $StageDir } else { Join-Path $Root 'Saved\StagedBuilds\Windows' }
    $roots = @((Join-Path $stageForRoots 'OneBossFight\Saved\Benchmark'), (Join-Path $env:LOCALAPPDATA 'OneBossFight\Saved\Benchmark'))
    $dir = $roots | ForEach-Object { Get-ChildItem $_ -Directory -Filter "$($e.N)_*" -ErrorAction SilentlyContinue } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $dir) {
        if ($Round6 -or $Round6Tuning) { throw "Round 6 result missing for $($e.N); stopping series to preserve the balanced trial set." }
        Write-Host "  no result for $($e.N)"
        continue
    }
    $s = Get-Content (Join-Path $dir.FullName 'summary.json') -Raw | ConvertFrom-Json
    if ($Round6 -or $Round6Tuning) {
        if ($s.fight_mode -ne $true -or $s.fight_started -ne $true) { throw "Round 6 intake failed for $($e.N): selected-route fight did not start. Run retained; stopping series." }
        if ($s.gpu -match 'remote display|virtual') { throw "Round 6 intake failed for $($e.N): invalid remote/virtual GPU '$($s.gpu)'. Run retained; stopping series." }
        $expectedUpscaler = if ($e.Kind -eq 'baseline') { 'TSR' } else { 'DLSS' }
        if ($s.temporal_upscaler -ne $expectedUpscaler) { throw "Round 6 preflight failed for $($e.N): expected active upscaler '$expectedUpscaler', got '$($s.temporal_upscaler)'. Run retained; stopping series." }
        if ($null -eq $s.effective_primary_screen_percentage -or $null -eq $s.anti_aliasing_method) { throw "Round 6 preflight failed for $($e.N): summary lacks primary fraction upper bound or anti_aliasing_method. Run retained; stopping series." }
        $expectedPercent = $e.ExpectedPercent
        if ([math]::Abs([double]$s.effective_primary_screen_percentage - $expectedPercent) -gt 0.5) { throw "Round 6 preflight failed for $($e.N): primary fraction upper bound $($s.effective_primary_screen_percentage) != requested $expectedPercent. Run retained; stopping series." }
        if ($e.ExpectedMode) {
            $gameLogPath = Join-Path $dir.FullName 'game.log'
            $modeNames = @()
            if (Test-Path $gameLogPath) {
                $modeNames = @(Select-String -Path $gameLogPath -Pattern 'Creating\s+NGX DLSS Feature.*NGXPerfQuality=(?<mode>[^ (]+)' | ForEach-Object {
                    switch ($_.Matches[0].Groups['mode'].Value) {
                        'DLAA' { 'DLAA' }
                        'MaxQuality' { 'Quality' }
                        'Balanced' { 'Balanced' }
                        'MaxPerf' { 'Performance' }
                        default { 'UNKNOWN' }
                    }
                } | Select-Object -Unique)
            }
            if ($modeNames.Count -ne 1 -or $modeNames[0] -ne $e.ExpectedMode) { throw "Round 6 preflight failed for $($e.N): creation log mode(s) '$($modeNames -join ',')' != requested '$($e.ExpectedMode)'. Run retained; stopping series." }
        }
    }
    if (($Round5 -or $Round6 -or $Round6Tuning) -and $e.C -and $s.cvars -match '\(UNKNOWN variable\)') {
        throw "Experiment $($e.N) requested an unknown console variable; see $((Join-Path $dir.FullName 'summary.json')) and its game log. The run is retained and the experiment series is stopped."
    }
    $rows += [pscustomobject]@{ Name = $e.N; Kind = $e.Kind; Group = $e.Group; ExpectedMode = $e.ExpectedMode; avg_fps = [math]::Round($s.avg_fps, 1); p99_ms = [math]::Round($s.p99_ms, 1); gpu_avg_ms = [math]::Round($s.gpu_avg_ms, 1); gpu_p99_ms = [math]::Round($s.gpu_p99_ms, 1); game_p99 = [math]::Round($s.game_thread_p99_ms, 1); render_p99 = [math]::Round($s.render_thread_p99_ms, 1); gpu = $s.gpu; fight = $s.fight_started; cvars = $s.cvars }
    Write-Host ("  avg {0} fps, p99 {1} ms, gpu avg {2} ms" -f $rows[-1].avg_fps, $rows[-1].p99_ms, $rows[-1].gpu_avg_ms)
}
if ($Round6 -or $Round6Tuning) {
    $anchors = @($rows | Where-Object { $_.Kind -eq 'baseline' })
    if ($anchors.Count -lt 2) { throw 'Round 6 intake failed: fewer than two TSR anchors completed.' }
    $firstAnchor = $anchors[0]
    foreach ($anchor in $anchors | Select-Object -Skip 1) {
        $fpsDrift = [math]::Abs(($anchor.avg_fps - $firstAnchor.avg_fps) / $firstAnchor.avg_fps) * 100
        $p99Drift = [math]::Abs(($anchor.p99_ms - $firstAnchor.p99_ms) / $firstAnchor.p99_ms) * 100
        if ($fpsDrift -gt 5 -or $p99Drift -gt 5) { throw "Round 6 intake failed: baseline drift exceeded 5% at $($anchor.Name) (avg FPS $([math]::Round($fpsDrift,1))%, p99 $([math]::Round($p99Drift,1))%). Data retained; do not select a mode." }
    }
    if ($Round6) {
        $anchorP99 = @($anchors | Sort-Object p99_ms | ForEach-Object { $_.p99_ms })
        if (($anchorP99.Count % 2) -eq 0) {
            $middleUpper = [int]($anchorP99.Count / 2)
            $anchorP99Median = ($anchorP99[$middleUpper - 1] + $anchorP99[$middleUpper]) / 2
        }
        else { $anchorP99Median = $anchorP99[[math]::Floor($anchorP99.Count / 2)] }
        $eligibleModes = @()
        foreach ($mode in @('Quality','Balanced','Performance')) {
            $modeRows = @($rows | Where-Object { $_.ExpectedMode -eq $mode })
            $modeAvg = @($modeRows | Sort-Object avg_fps | ForEach-Object { $_.avg_fps })
            $modeP99 = @($modeRows | Sort-Object p99_ms | ForEach-Object { $_.p99_ms })
            $p99Median = if ($modeP99.Count -eq 3) { $modeP99[1] } else { [double]::PositiveInfinity }
            $fpsMedian = if ($modeAvg.Count -eq 3) { $modeAvg[1] } else { 0 }
            $qualifies = $modeRows.Count -eq 3 -and $p99Median -le ($anchorP99Median * 1.05)
            Write-Host ("Phase 1 mode {0}: trials={1}, median avg FPS={2}, median p99={3} ms, p99 gate={4}" -f $mode, $modeRows.Count, $fpsMedian, $p99Median, $qualifies)
            if ($qualifies) { $eligibleModes += [pscustomobject]@{ Mode = $mode; MedianAvgFps = $fpsMedian } }
        }
        if ($eligibleModes.Count -gt 0) { Write-Host ("Performance-ranked mode candidates (owner image-quality review still required): {0}" -f (($eligibleModes | Sort-Object MedianAvgFps -Descending | ForEach-Object { $_.Mode }) -join ', ')) }
        else { Write-Host 'No DLSS mode qualifies for tuning under the 5% p99 gate.' }
    }
}
$out = Join-Path $Root ("Saved\perf_experiments_{0}.txt" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
($rows | Format-Table -AutoSize | Out-String -Width 400) | Out-File $out -Encoding utf8
$rows | Format-Table Name, avg_fps, p99_ms, gpu_avg_ms, gpu_p99_ms, game_p99, render_p99, fight -AutoSize
Write-Host "Table saved to $out"
