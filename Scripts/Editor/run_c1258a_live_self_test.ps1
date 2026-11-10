$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5'
$project = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root 'Scripts\Editor\pie_sevarog_framework_live.py'
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1258A_RANGE_RETRY'
$log = Join-Path $evidence 'pie_self_test.log'
$statusPath = Join-Path $evidence 'pie_self_test_status.txt'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
if (-not (Test-Path -LiteralPath $script)) { throw "Missing driver: $script" }
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1258a'; command_id='C1258A.pie-range-retry'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='PIE through S1-S3 card starts and CARD_END; stop before S4; no map save' } | ConvertTo-Json
$created = [System.Collections.Generic.List[string]]::new()
$proc = $null
try {
    foreach ($lock in $locks) {
        $stream = [System.IO.File]::Open($lock,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[System.Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
        $created.Add($lock)
    }
    $fso = New-Object -ComObject Scripting.FileSystemObject
    $short = $fso.GetFile($script).ShortPath.ToLower() -replace '\\','/'
    $env:SEVAROG_LIVE_SELF_TEST = '1'
    $env:SEVAROG_LIVE_SELF_TEST_CARDS = '3'
    $execCmd = '-ExecCmds="py ' + $short + '"'
    $proc = Start-Process -FilePath (Join-Path $engine 'Engine\Binaries\Win64\UnrealEditor.exe') -PassThru -ArgumentList @(
        $project, $execCmd, '-nosound', '-nosplash', '-unattended', "-abslog=$log"
    )
    $deadline = [DateTime]::UtcNow.AddMinutes(10)
    $passSignal = $false
    while ([DateTime]::UtcNow -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Seconds 2
        if (Test-Path -LiteralPath $log) {
            if (Select-String -Path $log -Pattern '\[SevarogLive\] SELF_TEST CARD_WINDOW_ELAPSED count=3' -Quiet) { $passSignal=$true; break }
            if (Select-String -Path $log -Pattern '\[SevarogLive\] ERROR|Fatal error|Assertion failed|SELF_TEST FAIL' -Quiet) { break }
        }
    }
    if ($passSignal) {
        Start-Sleep -Seconds 3
        if (-not $proc.HasExited) { [void]$proc.CloseMainWindow(); Start-Sleep -Seconds 5 }
    }
    if (-not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    $starts = @{}
    $ends = @{}
    foreach ($move in @('Move_Sevarog_Swing1_Medium','Move_Sevarog_Swing2_Medium','Move_Sevarog_Swing3_Slow')) {
        $starts[$move] = if (Test-Path -LiteralPath $log) { [bool](Select-String -Path $log -Pattern (('\[CARD_START\].*card=' + [regex]::Escape($move) + '\s') ) -Quiet) } else { $false }
        $ends[$move] = if (Test-Path -LiteralPath $log) { [bool](Select-String -Path $log -Pattern (('\[CARD_END\].*card=' + [regex]::Escape($move) + '\s+reason=Finished') ) -Quiet) } else { $false }
    }
    $setups = @{}
    foreach ($move in $starts.Keys) {
        $setups[$move] = if (Test-Path -LiteralPath $log) { [bool](Select-String -Path $log -Pattern (('\[SevarogLive\] SETUP .*move=' + [regex]::Escape($move) + ' .*inBand=1') ) -Quiet) } else { $false }
    }
    $controller = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern '\[SevarogLive\] NAV_DIAG' | Select-Object -First 1 } else { $null }
    $navRequest = if (Test-Path -LiteralPath (Join-Path $evidence 'nav_failure_baseline.log')) { Select-String -Path (Join-Path $evidence 'nav_failure_baseline.log') -Pattern '\[FrameworkProof\] nav request=.*fullPath=1' | Select-Object -First 1 } else { $null }
    $navFailure = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern 'Framework.Nav.MoveFailed' | Select-Object -First 1 } else { $null }
    $spawnProjection = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern '\[FrameworkProof\] test_nav_probe system=1 spawnProjected=1' | Select-Object -First 1 } else { $null }
    $inBandSkip = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern '\[FrameworkProof\] test_walk_skipped reason=target_in_profile_band' | Select-Object -First 1 } else { $null }
    $testHook = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern '\[SevarogLive\] TEST_HOOK skip_initial_walk=1 scope=standalone_test_authorized_target_in_profile_band' | Select-Object -First 1 } else { $null }
    $baselineFailure = if (Test-Path -LiteralPath (Join-Path $evidence 'nav_failure_baseline.log')) { Select-String -Path (Join-Path $evidence 'nav_failure_baseline.log') -Pattern 'Framework.Nav.MoveFailed' | Select-Object -First 1 } else { $null }
    $s4Start = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern '\[CARD_START\].*card=Move_Sevarog_Speedburst\s' -Quiet } else { $false }
    $status = @(
        ('EDITOR_EXITED=' + $proc.HasExited)
        ('SELF_TEST_WINDOW_SIGNAL=' + $passSignal)
        ('S1_START_END=' + ($starts['Move_Sevarog_Swing1_Medium'] -and $ends['Move_Sevarog_Swing1_Medium']))
        ('S2_START_END=' + ($starts['Move_Sevarog_Swing2_Medium'] -and $ends['Move_Sevarog_Swing2_Medium']))
        ('S3_START_END=' + ($starts['Move_Sevarog_Swing3_Slow'] -and $ends['Move_Sevarog_Swing3_Slow']))
        ('S1_IN_BAND=' + $setups['Move_Sevarog_Swing1_Medium'])
        ('S2_IN_BAND=' + $setups['Move_Sevarog_Swing2_Medium'])
        ('S3_IN_BAND=' + $setups['Move_Sevarog_Swing3_Slow'])
        ('CONTROLLER_DIAG=' + [bool]$controller)
        ('NAV_FULL_PATH_FAILURE_BASELINE=' + [bool]($navRequest -and $baselineFailure))
        ('SPAWN_PROJECTED_TO_NAVMESH=' + [bool]$spawnProjection)
        ('IN_BAND_INIT_SKIPPED_NAV=' + [bool]$inBandSkip)
        ('TEST_ONLY_SKIP_WALK_HOOK_ENABLED=' + [bool]$testHook)
        ('NAV_MOVE_FAILED=' + [bool]$navFailure)
        ('S4_STARTED=' + [bool]$s4Start)
        'MAP_SAVED=0'
    ) -join [Environment]::NewLine
    Set-Content -LiteralPath $statusPath -Value $status
    Write-Output $status
    if (-not ($passSignal -and $starts.Values -notcontains $false -and $ends.Values -notcontains $false -and $setups.Values -notcontains $false -and $controller -and $spawnProjection -and $inBandSkip -and $testHook -and $navRequest -and $baselineFailure -and -not $navFailure -and -not $s4Start)) {
        if (Test-Path -LiteralPath $log) { Get-Content $log -Tail 120 }
        throw 'C-1258a PIE self-test failed or incomplete.'
    }
} finally {
    Remove-Item Env:\SEVAROG_LIVE_SELF_TEST -ErrorAction SilentlyContinue
    Remove-Item Env:\SEVAROG_LIVE_SELF_TEST_CARDS -ErrorAction SilentlyContinue
    if ($proc -and -not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try {
                $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force }
            } catch {
                Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock)
            }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'pie_lock_result.txt')
}
