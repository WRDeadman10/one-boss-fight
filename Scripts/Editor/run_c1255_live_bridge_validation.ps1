$ErrorActionPreference = 'Stop'
$project = 'C:\UnrealProject\OneBossFight\OneBossFight.uproject'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$locks = @(
    'C:\UnrealProject\OneBossFight\ENGINE_LOCK.json',
    'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json'
)
$evidence = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\C1255_LIVE_BRIDGE'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
if (@(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) }).Count) { throw 'ABORT: project UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1254a/C-1255'; command_id='C1255.live-bridge-build-suite'; owner_token=$token; start_utc=(Get-Date).ToUniversalTime().ToString('o'); policy='C-1155' } | ConvertTo-Json
$createdLocks = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($lock in $locks) {
        $stream = [System.IO.File]::Open($lock, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try { $bytes=[System.Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
        $createdLocks.Add($lock)
    }
    $buildLog = Join-Path $evidence 'build.log'
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 60; throw "BUILD FAILED exit=$buildExit" }
    $suiteLog = Join-Path $evidence 'suite.log'
    $suiteStdout = Join-Path $evidence 'suite_stdout.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $project '-ExecCmds=Automation RunTests OneBossFight; Quit' '-DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec' -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$suiteLog" *> $suiteStdout
    $suiteExit = $LASTEXITCODE
    $finished = (Select-String -Path $suiteLog -Pattern 'Test Completed' -ErrorAction SilentlyContinue).Count
    $failed = (Select-String -Path $suiteLog -Pattern 'Result=\{(Fail|Error)' -ErrorAction SilentlyContinue).Count
    $status = "BUILD_EXIT=$buildExit`nSUITE_EXIT=$suiteExit`nFINISHED=$finished`nFAILED=$failed`nDD27J=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec"
    Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status
    Write-Output $status
    if ($suiteExit -ne 0 -or $finished -eq 0 -or $failed -ne 0) { Get-Content $suiteStdout -Tail 50; Get-Content $suiteLog -Tail 60; throw 'FULL SUITE FAILED OR INCOMPLETE' }
} finally {
    foreach ($lock in $createdLocks) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning "Could not verify lock ownership before cleanup: $lock" }
        }
    }
}
