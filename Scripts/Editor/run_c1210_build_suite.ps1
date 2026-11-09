$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$uproject = Join-Path $root 'OneBossFight.uproject'
$locks = @(
    (Join-Path $root 'ENGINE_LOCK.json'),
    (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json')
)
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { throw 'UnrealEditor is running.' }
foreach ($path in $locks) { if (Test-Path -LiteralPath $path) { throw "Lock exists: $path" } }
$token = [guid]::NewGuid().ToString('N')
$created = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($path in $locks) {
        $record = @{ owner='Codex'; task='C-1210'; command_id=$token; pid=$PID; purpose='C-1210 editor build and full automation suite'; start_utc=[DateTime]::UtcNow.ToString('o') } | ConvertTo-Json
        New-Item -Path $path -ItemType File -Value $record -ErrorAction Stop | Out-Null
        $created.Add($path)
    }
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$uproject" -WaitMutex
    if ($LASTEXITCODE -ne 0) { throw "OneBossFightEditor build failed: $LASTEXITCODE" }
    $log = Join-Path $root 'Saved\Logs\c1210_full_suite.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $uproject '-ExecCmds=Automation RunTests OneBossFight; Quit' '-DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec' -unattended -nosound -nosplash -nullrhi "-abslog=$log"
    if ($LASTEXITCODE -ne 0) { throw "Automation suite exit $LASTEXITCODE; see $log" }
    $started = @(Select-String -Path $log -Pattern 'Test Started\. Name=')
    $passed = @(Select-String -Path $log -Pattern 'Test Completed\. Result=\{Success\}')
    $failed = @(Select-String -Path $log -Pattern 'Test Completed\. Result=\{(Fail|Error)\}')
    $complete = Select-String -Path $log -Pattern 'TEST COMPLETE\. EXIT CODE: 0' | Select-Object -Last 1
    if (!$complete -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -ne 0) {
        throw "Suite summary invalid (started=$($started.Count), passed=$($passed.Count), failed=$($failed.Count)); see $log"
    }
    Write-Output "C-1210 build PASS; Automation RunTests OneBossFight passed=$($passed.Count), failed=0; $log"
} finally {
    foreach ($path in $created.ToArray()) {
        if (Test-Path -LiteralPath $path) {
            $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
            if ($record.command_id -eq $token -and $record.task -eq 'C-1210') { Remove-Item -LiteralPath $path -Force }
            else { Write-Error "Lock ownership changed; preserving $path" }
        }
    }
}
