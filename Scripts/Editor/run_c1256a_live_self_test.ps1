$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5'
$project = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root 'Scripts\Editor\pie_sevarog_framework_live.py'
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1256A_SPAWN_BRIDGE'
$log = Join-Path $evidence 'pie_self_test.log'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
if (@(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) }).Count) { throw 'ABORT: project UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
if (-not (Test-Path -LiteralPath $script)) { throw "Missing driver: $script" }
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1256a'; command_id='C1256A.pie-self-test'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='PIE until spawned plus S1 start only' } | ConvertTo-Json
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
    $execCmd = '-ExecCmds="py ' + $short + '"'
    $proc = Start-Process -FilePath (Join-Path $engine 'Engine\Binaries\Win64\UnrealEditor.exe') -PassThru -ArgumentList @(
        $project, $execCmd, '-nosound', '-nosplash', '-unattended', "-abslog=$log"
    )
    $deadline = [DateTime]::UtcNow.AddMinutes(10)
    $passed = $false
    while ([DateTime]::UtcNow -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Seconds 2
        if (Test-Path -LiteralPath $log) {
            if (Select-String -Path $log -Pattern '\[SevarogLive\] SELF_TEST PASS spawned=1 first_card=Move_Sevarog_Swing1_Medium started=1' -Quiet) { $passed=$true; break }
            if (Select-String -Path $log -Pattern '\[SevarogLive\] ERROR|Fatal error|Assertion failed|SELF_TEST FAIL' -Quiet) { break }
        }
    }
    if ($passed) {
        Start-Sleep -Seconds 3
        if (-not $proc.HasExited) { [void]$proc.CloseMainWindow(); Start-Sleep -Seconds 5 }
    }
    if (-not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    $spawn = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern '\[SevarogLive\] SPAWN PASS' -Quiet } else { $false }
    $card = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern '\[SevarogLive\] CARD accepted move=Move_Sevarog_Swing1_Medium' -Quiet } else { $false }
    $finished = if (Test-Path -LiteralPath $log) { Select-String -Path $log -Pattern '\[SevarogLive\] finished: self-test passed: spawned and started S1' -Quiet } else { $false }
    $status = @(
        ('EDITOR_EXITED=' + $proc.HasExited)
        ('SPAWN_PASS=' + $spawn)
        ('S1_STARTED=' + $card)
        ('SELF_TEST_PASS=' + $passed)
        ('FINISHED=' + $finished)
        'PIE_SCOPE=spawn_plus_one_S1_only'
        'MAP_SAVED=0'
    ) -join [Environment]::NewLine
    Set-Content -LiteralPath (Join-Path $evidence 'pie_self_test_status.txt') -Value $status
    Write-Output $status
    if (-not ($spawn -and $card -and $passed -and $finished)) { if (Test-Path -LiteralPath $log) { Get-Content $log -Tail 100 }; throw 'C-1256a PIE self-test failed or incomplete.' }
} finally {
    Remove-Item Env:\SEVAROG_LIVE_SELF_TEST -ErrorAction SilentlyContinue
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
