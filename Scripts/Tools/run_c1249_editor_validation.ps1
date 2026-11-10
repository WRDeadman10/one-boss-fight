$ErrorActionPreference = 'Stop'
$project = 'C:\UnrealProject\OneBossFight\OneBossFight.uproject'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$lock = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json'
$evidence = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\C1249_EDITOR_VALIDATION_BRIDGE'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
if (Test-Path -LiteralPath $lock) { throw 'ABORT: shared engine lock already exists' }
$owned = @(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($owned.Count -gt 0) { throw 'ABORT: project UnrealEditor process is running' }
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1249/SevarogValidationBridge'; command_id='C1249.build-and-full-suite'; start_utc=(Get-Date).ToUniversalTime().ToString('o'); policy='C-1155' } | ConvertTo-Json
[System.IO.File]::WriteAllText($lock, $record + [Environment]::NewLine)
try {
    $buildLog = Join-Path $evidence 'build.log'
    & "$engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 35; throw "BUILD FAILED exit=$buildExit" }
    $testLog = Join-Path $evidence 'suite.log'
    $stdoutLog = Join-Path $evidence 'suite_stdout.log'
    & "$engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project '-ExecCmds=Automation RunTests OneBossFight; Quit' '-DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec' -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$testLog" *> $stdoutLog
    $suiteExit = $LASTEXITCODE
    $success = (Select-String -Path $testLog -Pattern 'Result=\{Success\}' -ErrorAction SilentlyContinue).Count
    $failed = (Select-String -Path $testLog -Pattern 'Result=\{(Fail|Error)' -ErrorAction SilentlyContinue).Count
    $finished = (Select-String -Path $testLog -Pattern 'Test Completed' -ErrorAction SilentlyContinue).Count
    $status = "BUILD_EXIT=$buildExit`nSUITE_EXIT=$suiteExit`nFINISHED=$finished`nSUCCESS=$success`nFAILED=$failed`nDD27J=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec"
    Set-Content (Join-Path $evidence 'status.txt') $status
    Write-Output $status
    if ($suiteExit -ne 0 -or $finished -eq 0 -or $success -ne $finished -or $failed -ne 0) { Get-Content $testLog -Tail 60; throw 'FULL SUITE FAILED OR INCOMPLETE' }
}
finally {
    if (Test-Path -LiteralPath $lock) { Remove-Item -LiteralPath $lock -Force }
}
