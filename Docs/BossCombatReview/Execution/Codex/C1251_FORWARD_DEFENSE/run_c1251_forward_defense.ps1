$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$project = Join-Path $root 'OneBossFight.uproject'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1251_FORWARD_DEFENSE'
$hash = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
$token = [guid]::NewGuid().ToString('N')
$acquired = [System.Collections.Generic.List[string]]::new()
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $project)) { throw "Project missing: $project" }
$editors = @(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe' OR Name='UnrealEditor-Cmd.exe'" |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($editors.Count -gt 0) { throw "ABORT: project Unreal process active: $($editors.ProcessId -join ',')" }
foreach ($lock in $locks) {
    $parent = Split-Path -Parent $lock
    if (-not (Test-Path -LiteralPath $parent)) { throw "Lock directory missing: $parent" }
    if (Test-Path -LiteralPath $lock) { throw "ABORT: shared lock exists: $lock" }
}

try {
    foreach ($lock in $locks) {
        $record = [ordered]@{ agent='Codex'; party='X'; task='C-1251a'; command_id=$token; start_utc=(Get-Date).ToUniversalTime().ToString('o'); policy='C-1155' } | ConvertTo-Json
        $stream = [System.IO.File]::Open($lock, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try {
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($record + [Environment]::NewLine)
            $stream.Write($bytes, 0, $bytes.Length)
        } finally { $stream.Dispose() }
        $acquired.Add($lock)
    }
    $buildLog = Join-Path $evidence 'build.log'
    & "$engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 50; throw "BUILD FAILED exit=$buildExit" }

    $testLog = Join-Path $evidence 'suite.log'
    $stdoutLog = Join-Path $evidence 'suite_stdout.log'
    & "$engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$hash" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$testLog" *> $stdoutLog
    $suiteExit = $LASTEXITCODE
    $finished = (Select-String -Path $testLog -Pattern 'Test Completed' -ErrorAction SilentlyContinue).Count
    $success = (Select-String -Path $testLog -Pattern 'Result=\{Success\}' -ErrorAction SilentlyContinue).Count
    $failed = (Select-String -Path $testLog -Pattern 'Result=\{(Fail|Error)' -ErrorAction SilentlyContinue).Count
    @("BUILD_EXIT=$buildExit", "SUITE_EXIT=$suiteExit", "FINISHED=$finished", "SUCCESS=$success", "FAILED=$failed", "DD27J=$hash") |
        Set-Content (Join-Path $evidence 'status.txt')
    Get-Content (Join-Path $evidence 'status.txt')
    if ($suiteExit -ne 0 -or $finished -eq 0 -or $success -ne $finished -or $failed -ne 0) {
        Get-Content $testLog -Tail 80
        throw 'FULL SUITE FAILED OR INCOMPLETE'
    }
} finally {
    foreach ($lock in $acquired) {
        if (Test-Path -LiteralPath $lock) {
            $existing = Get-Content -LiteralPath $lock -Raw | ConvertFrom-Json
            if ($existing.command_id -eq $token) { Remove-Item -LiteralPath $lock -Force }
            else { Write-Error "Lock ownership changed; left in place: $lock" }
        }
    }
}
