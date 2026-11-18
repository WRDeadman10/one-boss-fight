$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5'
$project = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root 'Scripts\Editor\pie_sevarog_framework_live.py'
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1269_X03_TRACE'
$log = Join-Path $evidence 'pie_clip_trace.log'
$statusPath = Join-Path $evidence 'pie_clip_trace_status.txt'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
if (-not (Test-Path -LiteralPath $script)) { throw "Missing driver: $script" }
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1269-X03-hotfix'; command_id='C1269X03.full-clip-trace-self-test'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='PIE test-only per-frame weapon socket-to-player-capsule trace for S1/S2 at 140 cm; no save' } | ConvertTo-Json
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
    $env:SEVAROG_LIVE_SELF_TEST_CARDS = '2'
    $env:SEVAROG_LIVE_TRACE_CLIP = '1'
    $execCmd = '-ExecCmds="py ' + $short + '"'
    $proc = Start-Process -FilePath (Join-Path $engine 'Engine\Binaries\Win64\UnrealEditor.exe') -PassThru -WindowStyle Hidden -ArgumentList @(
        $project, $execCmd, '-nosound', '-nosplash', '-unattended', "-abslog=$log"
    )
    $deadline = [DateTime]::UtcNow.AddMinutes(6)
    $finished = $false
    while ([DateTime]::UtcNow -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Seconds 2
        if (Test-Path -LiteralPath $log) {
            if (Select-String -Path $log -Pattern '\[SevarogLive\] finished: self-test completed requested card windows' -Quiet) { $finished = $true; break }
            if (Select-String -Path $log -Pattern '\[SevarogLive\] ERROR|Fatal error|Assertion failed' -Quiet) { break }
        }
    }
    if ($finished) { Start-Sleep -Seconds 3; if (-not $proc.HasExited) { [void]$proc.CloseMainWindow(); Start-Sleep -Seconds 5 } }
    if (-not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    $text = if (Test-Path -LiteralPath $log) { Get-Content -Raw -LiteralPath $log } else { '' }
    $moves = @('Move_Sevarog_Swing1_Medium','Move_Sevarog_Swing2_Medium')
    $status = [System.Collections.Generic.List[string]]::new()
    $ok = $finished
    foreach ($move in $moves) {
        $escaped = [regex]::Escape($move)
        $start = [regex]::Match($text, '\[SevarogLive\] CLIP_TRACE_START move=' + $escaped + ' ')
        $end = [regex]::Match($text, '\[SevarogLive\] CLIP_TRACE_END move=' + $escaped + ' .*samples=(\d+) maxLocalSeconds=([0-9.]+) expectedClipSeconds=1\.1333 endToleranceSeconds=0\.0600 fullClip=(\d+)')
        $frames = [regex]::Matches($text, '\[SevarogLive\] CLIP_TRACE_FRAME frame=\d+ move=' + $escaped + ' ')
        $complete = $end.Success -and [int]$end.Groups[1].Value -gt 0 -and [int]$end.Groups[3].Value -eq 1 -and $frames.Count -gt 0
        $ok = $ok -and $start.Success -and $complete
        $status.Add(("{0}_TRACE_START={1}; FRAMES={2}; MAX_LOCAL_SECONDS={3}; FULL_CLIP={4}" -f $move,$start.Success,$frames.Count,($end.Groups[2].Value),$complete))
    }
    $status.Insert(0,('EDITOR_EXITED=' + $proc.HasExited))
    $status.Insert(1,('SELF_TEST_FINISHED=' + $finished))
    $status.Add('REQUESTED_RANGE_CM=140')
    $status.Add('MAP_SAVED=0')
    $result = $status -join [Environment]::NewLine
    Set-Content -LiteralPath $statusPath -Value $result
    Write-Output $result
    if (-not $ok) { if (Test-Path -LiteralPath $log) { Get-Content $log -Tail 100 }; throw 'C-1265b trace self-test incomplete or not full-clip.' }
} finally {
    Remove-Item Env:\SEVAROG_LIVE_SELF_TEST -ErrorAction SilentlyContinue
    Remove-Item Env:\SEVAROG_LIVE_SELF_TEST_CARDS -ErrorAction SilentlyContinue
    Remove-Item Env:\SEVAROG_LIVE_TRACE_CLIP -ErrorAction SilentlyContinue
    if ($proc -and -not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'pie_lock_result.txt')
}
