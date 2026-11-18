$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$driver = Join-Path $root 'Scripts\Editor\pie_sevarog_framework_live.py'
$run = [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss')
$evidence = Join-Path $root ('Docs\BossCombatReview\Execution\Codex\BK2_X26_DRIVER\Run_' + $run)
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$manifest = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
$editorProcesses = @(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe' OR Name='UnrealEditor-Cmd.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($editorProcesses.Count) { throw 'ABORT: project UnrealEditor process is running; close it before acquiring C-1155.' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
if (-not (Test-Path -LiteralPath $driver)) { throw "Missing PIE driver: $driver" }
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='Queue BK-2 X26'; command_id='BK2_X26.build-suite-pie-selftest'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Development editor build, DD27j-pinned OneBossFight suite, bounded one-card Sevarog PIE self-test; no asset saves' } | ConvertTo-Json
$created = [System.Collections.Generic.List[string]]::new()
$proc = $null
$oldSelfTest = $env:SEVAROG_LIVE_SELF_TEST
$oldSelfTestCards = $env:SEVAROG_LIVE_SELF_TEST_CARDS
$oldCards = $env:SEVAROG_LIVE_CARDS
$oldHealthFraction = $env:SEVAROG_LIVE_BOSS_HEALTH_FRACTION
$oldS7Dodge = $env:SEVAROG_LIVE_S7_DODGE_OUT
function Invoke-BoundedCardSelfTest([string]$stage, [string]$card, [string]$healthFraction) {
    $pieLog = Join-Path $evidence ("pie_{0}.log" -f $stage)
    $fso = New-Object -ComObject Scripting.FileSystemObject
    $short = $fso.GetFile($driver).ShortPath.ToLower() -replace '\\','/'
    $env:SEVAROG_LIVE_SELF_TEST = '1'
    $env:SEVAROG_LIVE_SELF_TEST_CARDS = '1'
    $env:SEVAROG_LIVE_CARDS = $card
    if ($healthFraction) { $env:SEVAROG_LIVE_BOSS_HEALTH_FRACTION = $healthFraction }
    else { Remove-Item Env:\SEVAROG_LIVE_BOSS_HEALTH_FRACTION -ErrorAction SilentlyContinue }
    Remove-Item Env:\SEVAROG_LIVE_S7_DODGE_OUT -ErrorAction SilentlyContinue
    $execCmd = '-ExecCmds="py ' + $short + '"'
    $pieProcess = Start-Process -FilePath (Join-Path $engine 'Binaries\Win64\UnrealEditor.exe') -PassThru -ArgumentList @($project,$execCmd,'-nosound','-nosplash','-unattended',"-abslog=$pieLog") -WindowStyle Hidden
    $deadline = [DateTime]::UtcNow.AddMinutes(10)
    $style = $spawn = $accepted = $window = $finished = $healthHook = $false
    $escapedCard = [regex]::Escape($card)
    try {
        while ([DateTime]::UtcNow -lt $deadline -and -not $pieProcess.HasExited) {
            Start-Sleep -Seconds 2
            if (-not (Test-Path -LiteralPath $pieLog)) { continue }
            $style = Select-String -Path $pieLog -Pattern '\[SevarogLive\] PACK_STYLE_READY component=BP_CombatComponent_C' -Quiet -ErrorAction SilentlyContinue
            $spawn = Select-String -Path $pieLog -Pattern '\[SevarogLive\] SPAWN PASS' -Quiet -ErrorAction SilentlyContinue
            $accepted = Select-String -Path $pieLog -Pattern ("\[SevarogLive\] CARD accepted move={0} targetDistanceCm=.* inBand=1" -f $escapedCard) -Quiet -ErrorAction SilentlyContinue
            $window = Select-String -Path $pieLog -Pattern ("\[SevarogLive\] SELF_TEST CARD_WINDOW_ELAPSED count=1 last_card={0}" -f $escapedCard) -Quiet -ErrorAction SilentlyContinue
            $finished = Select-String -Path $pieLog -Pattern '\[SevarogLive\] finished: self-test completed requested card windows' -Quiet -ErrorAction SilentlyContinue
            if ($healthFraction) { $healthHook = Select-String -Path $pieLog -Pattern ("\[SevarogLive\] TEST_HOOK boss_health_fraction={0}" -f ([regex]::Escape($healthFraction))) -Quiet -ErrorAction SilentlyContinue }
            if (Select-String -Path $pieLog -Pattern '\[SevarogLive\] ERROR|Fatal error|Assertion failed' -Quiet -ErrorAction SilentlyContinue) { break }
            if ($style -and $spawn -and $accepted -and $window -and $finished -and (!$healthFraction -or $healthHook)) { break }
        }
    } finally {
        if (-not $pieProcess.HasExited) { [void]$pieProcess.CloseMainWindow(); Start-Sleep -Seconds 5 }
        if (-not $pieProcess.HasExited) { $pieProcess.Kill(); $pieProcess.WaitForExit() }
    }
    $logText = if (Test-Path -LiteralPath $pieLog) { Get-Content -Raw -LiteralPath $pieLog } else { '' }
    $styleIndex = $logText.IndexOf('PACK_STYLE_READY')
    $spawnIndex = $logText.IndexOf('SPAWN PASS')
    $cardIndex = $logText.IndexOf(('CARD accepted move=' + $card))
    $order = $styleIndex -ge 0 -and $spawnIndex -gt $styleIndex -and $cardIndex -gt $spawnIndex
    $ok = $style -and $spawn -and $accepted -and $window -and $finished -and $order -and (!$healthFraction -or $healthHook)
    "${stage}_PACK_STYLE_READY=$style`n${stage}_SPAWN_PASS=$spawn`n${stage}_CARD_ACCEPTED=$accepted`n${stage}_CARD_WINDOW_ELAPSED=$window`n${stage}_FINISHED=$finished`n${stage}_HEALTH_HOOK=$healthHook`n${stage}_ORDER_VALID=$order`n${stage}_PASS=$ok" |
        Add-Content -LiteralPath (Join-Path $evidence 'status.txt')
    if (-not $ok) { if (Test-Path -LiteralPath $pieLog) { Get-Content $pieLog -Tail 120 }; throw "$stage bounded PIE self-test failed or incomplete." }
    return $ok
}
try {
    foreach ($lock in $locks) {
        $stream = [System.IO.File]::Open($lock,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[System.Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
        $created.Add($lock)
    }
    Set-Location -LiteralPath $root
    $buildLog = Join-Path $evidence 'build.log'
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 100; throw 'BK-2 Development editor build failed.' }

    $suiteLog = Join-Path $evidence 'suite.log'
    $suiteStdout = Join-Path $evidence 'suite_stdout.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $project '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$manifest" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$suiteLog" *> $suiteStdout
    $suiteExit = $LASTEXITCODE
    $started = @(Select-String -Path $suiteLog -Pattern 'Test Started\. Name=' -ErrorAction SilentlyContinue)
    $passed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\}' -ErrorAction SilentlyContinue)
    $failed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{(Fail|Error)\}' -ErrorAction SilentlyContinue)
    $complete = Select-String -Path $suiteLog -Pattern 'TEST COMPLETE\. EXIT CODE: 0' -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($suiteExit -ne 0 -or !$complete -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -gt 0) { Get-Content $suiteLog -Tail 120; throw 'DD27j-pinned OneBossFight suite failed or incomplete.' }

    $status = "BUILD_EXIT=$buildExit`nSUITE_EXIT=$suiteExit`nSUITE_STARTED=$($started.Count)`nSUITE_PASSED=$($passed.Count)`nSUITE_FAILED=$($failed.Count)`nDD27J=$manifest`nNO_ASSET_SAVES=1"
    Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status
    Write-Output $status
    Invoke-BoundedCardSelfTest 'S1' 'Move_Sevarog_Swing1_Medium' '' | Out-Null
    Invoke-BoundedCardSelfTest 'S6' 'Move_Sevarog_Ultimate_Swing_120fps_C1277' '0.5' | Out-Null
} finally {
    if ($null -eq $oldSelfTest) { Remove-Item Env:\SEVAROG_LIVE_SELF_TEST -ErrorAction SilentlyContinue } else { $env:SEVAROG_LIVE_SELF_TEST = $oldSelfTest }
    if ($null -eq $oldSelfTestCards) { Remove-Item Env:\SEVAROG_LIVE_SELF_TEST_CARDS -ErrorAction SilentlyContinue } else { $env:SEVAROG_LIVE_SELF_TEST_CARDS = $oldSelfTestCards }
    if ($null -eq $oldCards) { Remove-Item Env:\SEVAROG_LIVE_CARDS -ErrorAction SilentlyContinue } else { $env:SEVAROG_LIVE_CARDS = $oldCards }
    if ($null -eq $oldHealthFraction) { Remove-Item Env:\SEVAROG_LIVE_BOSS_HEALTH_FRACTION -ErrorAction SilentlyContinue } else { $env:SEVAROG_LIVE_BOSS_HEALTH_FRACTION = $oldHealthFraction }
    if ($null -eq $oldS7Dodge) { Remove-Item Env:\SEVAROG_LIVE_S7_DODGE_OUT -ErrorAction SilentlyContinue } else { $env:SEVAROG_LIVE_S7_DODGE_OUT = $oldS7Dodge }
    if ($proc -and -not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'lock_result.txt')
}
