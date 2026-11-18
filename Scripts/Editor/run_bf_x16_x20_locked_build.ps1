$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$evidence = Join-Path $root ('Docs\BossCombatReview\Execution\Codex\BF_X16_X20_MOVE_CARD_VALIDATION\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss'))
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$manifest = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='Queue BF X16-X20'; command_id='BF_X16_X20.locked-build-suite'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Development editor target and DD27j-pinned OneBossFight full suite; no asset authoring' } | ConvertTo-Json
$temps = [System.Collections.Generic.List[string]]::new()
$created = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($lock in $locks) {
        $temp = $lock + '.' + $token + '.tmp'
        $temps.Add($temp)
        $stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try {
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($record + [Environment]::NewLine)
            $stream.Write($bytes, 0, $bytes.Length)
            $stream.Flush($true)
        } finally { $stream.Dispose() }
        [System.IO.File]::Move($temp, $lock)
        $created.Add($lock)
    }
    Set-Location -LiteralPath $root
    $buildLog = Join-Path $evidence 'build.log'
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 120; throw 'BF-X16–X20 Development editor build failed.' }
    $suiteLog = Join-Path $evidence 'suite.log'
    $suiteStdout = Join-Path $evidence 'suite_stdout.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $project '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$manifest" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$suiteLog" *> $suiteStdout
    $suiteExit = $LASTEXITCODE
    $started = @(Select-String -Path $suiteLog -Pattern 'Test Started\. Name=' -ErrorAction SilentlyContinue)
    $passed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\}' -ErrorAction SilentlyContinue)
    $failed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{(Fail|Error)\}' -ErrorAction SilentlyContinue)
    $complete = Select-String -Path $suiteLog -Pattern 'TEST COMPLETE\. EXIT CODE: 0' -ErrorAction SilentlyContinue | Select-Object -Last 1
    $status = "BUILD_EXIT=$buildExit`nSUITE_EXIT=$suiteExit`nSTARTED=$($started.Count)`nPASSED=$($passed.Count)`nFAILED=$($failed.Count)`nCOMPLETE=$([bool]$complete)`nDD27J=$manifest`nNO_ASSETS=1"
    Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status
    Write-Output $status
    if ($suiteExit -ne 0 -or !$complete -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -gt 0) { Get-Content $suiteLog -Tail 120; throw 'BF-X16–X20 full suite failed or incomplete.' }
} finally {
    foreach ($temp in $temps) { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'lock_result.txt')
}
