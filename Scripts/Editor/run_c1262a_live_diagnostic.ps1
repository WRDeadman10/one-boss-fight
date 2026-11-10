$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5'
$project = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root 'Scripts\Editor\pie_sevarog_framework_live.py'
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1262A_SEVAROG_DIAG'
$log = Join-Path $evidence 'pie_live.log'
$statusPath = Join-Path $evidence 'pie_live_status.txt'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
if (-not (Test-Path -LiteralPath $script)) { throw "Missing driver: $script" }
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1262a'; command_id='C1262A.pie-diagnostic'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='PIE S1-S3 standalone, S4 whiff combo gate to S5, sweep geometry, warmed screenshots; no map save' } | ConvertTo-Json
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
    $env:SEVAROG_LIVE_SHOTS = '1'
    $env:SEVAROG_LIVE_TRACE_GEOMETRY = '1'
    $execCmd = '-ExecCmds="py ' + $short + '"'
    $proc = Start-Process -FilePath (Join-Path $engine 'Engine\Binaries\Win64\UnrealEditor.exe') -PassThru -WindowStyle Hidden -ArgumentList @(
        $project, $execCmd, '-nosound', '-nosplash', '-unattended', "-abslog=$log"
    )
    $deadline = [DateTime]::UtcNow.AddMinutes(12)
    $finished = $false
    while ([DateTime]::UtcNow -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Seconds 2
        if (Test-Path -LiteralPath $log) {
            if (Select-String -Path $log -Pattern '\[SevarogLive\] finished: driver complete: S1-S3 standalone and S4->S5 combo receipts' -Quiet) { $finished = $true; break }
            if (Select-String -Path $log -Pattern '\[SevarogLive\] ERROR|Fatal error|Assertion failed|SHOT_CAPTURE_FAIL|SHOT_WARMUP_FAIL|SHOT_FINAL_FAIL' -Quiet) { break }
        }
    }
    if ($finished) {
        Start-Sleep -Seconds 3
        if (-not $proc.HasExited) { [void]$proc.CloseMainWindow(); Start-Sleep -Seconds 5 }
    }
    if (-not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    $text = if (Test-Path -LiteralPath $log) { Get-Content -Raw -LiteralPath $log } else { '' }
    $moves = @('Move_Sevarog_Swing1_Medium','Move_Sevarog_Swing2_Medium','Move_Sevarog_Swing3_Slow','Move_Sevarog_Speedburst')
    $startCount = 0
    $endCount = 0
    foreach ($move in $moves) {
        if ($text -match ('\[CARD_START\].*card=' + [regex]::Escape($move) + '\s')) { $startCount++ }
        if ($text -match ('\[CARD_END\].*card=' + [regex]::Escape($move) + '\s+reason=Finished')) { $endCount++ }
    }
    $s5Start = $text -match '\[FrameworkProof\] combo_step node=S5 move=Move_Sevarog_Swing1_Medium'
    $whiffGate = $text -match '\[FrameworkProof\] combo_gate .*outcome=Whiff .*result=Continue next=S5'
    $s1s2Geometry = $text -match 'sweep_geometry instance=1 window=Window_Move_Sevarog_Swing1_Medium' -and $text -match 'sweep_geometry instance=2 window=Window_Move_Sevarog_Swing2_Medium'
    $shots = [regex]::Matches($text,'\[SevarogLive\] SHOT_READY move=').Count
    $s4Delta = $text -match '\[CARD_END\].*card=Move_Sevarog_Speedburst reason=Finished cardHitsAccepted=0 cardAppliedDamage=0.*totalHitsAccepted='
    $healthAbort = $text -match 'target_health_mismatch|\[CARD_ABORT\].*TargetLifeOrHealthChanged'
    $result = @(
        ('EDITOR_EXITED=' + $proc.HasExited)
        ('DRIVER_FINISHED=' + $finished)
        ('PRIMARY_CARD_STARTS=' + $startCount)
        ('PRIMARY_CARD_ENDS=' + $endCount)
        ('S4_CARD_DELTA_ZERO=' + $s4Delta)
        ('WHIFF_GATE_TO_S5=' + $whiffGate)
        ('S5_COMBO_CARD_STARTED=' + $s5Start)
        ('S1_S2_GEOMETRY_READBACK=' + $s1s2Geometry)
        ('BRIGHT_WARMED_SHOTS=' + $shots)
        ('TARGET_HEALTH_ABORT=' + $healthAbort)
        'MAP_SAVED=0'
    ) -join [Environment]::NewLine
    Set-Content -LiteralPath $statusPath -Value $result
    Write-Output $result
    if (-not ($finished -and $startCount -eq 4 -and $endCount -eq 4 -and $s4Delta -and $whiffGate -and $s5Start -and $s1s2Geometry -and $shots -eq 4 -and -not $healthAbort)) {
        if (Test-Path -LiteralPath $log) { Get-Content $log -Tail 100 }
        throw 'C-1262a live diagnostic failed or incomplete.'
    }
} finally {
    Remove-Item Env:\SEVAROG_LIVE_SHOTS -ErrorAction SilentlyContinue
    Remove-Item Env:\SEVAROG_LIVE_TRACE_GEOMETRY -ErrorAction SilentlyContinue
    if ($proc -and -not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'pie_lock_result.txt')
}
