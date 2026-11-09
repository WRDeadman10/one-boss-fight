param(
    [ValidateSet('InspectOnly', 'Write', 'Update', 'Verify')][string]$Mode = 'InspectOnly',
    [switch]$Build,
    [switch]$RunSuite
)

$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$uproject = Join-Path $root 'OneBossFight.uproject'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe'
$buildBat = Join-Path $engine 'Build\BatchFiles\Build.bat'
$lockPaths = @(
    (Join-Path $root 'ENGINE_LOCK.json'),
    (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json')
)
$token = [guid]::NewGuid().ToString('N')
$created = [System.Collections.Generic.List[string]]::new()

if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { throw 'Refusing to run while any UnrealEditor process is active.' }
foreach ($path in $lockPaths) {
    if (Test-Path -LiteralPath $path) { throw "Refusing to run: existing lock $path" }
}

try {
    foreach ($path in $lockPaths) {
        $record = @{ owner='Codex'; task='C-1202'; command_id=$token; pid=$PID; purpose="C-1202 Niagara graph $Mode"; start_utc=[DateTime]::UtcNow.ToString('o') } | ConvertTo-Json
        New-Item -Path $path -ItemType File -Value $record -ErrorAction Stop | Out-Null
        $created.Add($path)
    }

    if ($Build) {
        & $buildBat OneBossFightEditor Win64 Development "-Project=$uproject" -WaitMutex
        if ($LASTEXITCODE -ne 0) { throw "Editor module build failed with exit code $LASTEXITCODE" }
    }

    $log = Join-Path $root 'Saved\Logs\c1202_aura_graph_commandlet.log'
    if ($RunSuite) {
        $log = Join-Path $root 'Saved\Logs\c1205_full_suite.log'
        & $editor $uproject '-ExecCmds=Automation RunTests OneBossFight; Quit' '-DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec' -unattended -nosound -nosplash -nullrhi "-abslog=$log"
    } else {
        & $editor $uproject '-run=AuraBoostLiteGraphAuthoring' "-$Mode" -unattended -nosound -nosplash -nullrhi "-abslog=$log"
    }
    if ($LASTEXITCODE -ne 0) { throw "Aura graph commandlet failed with exit code $LASTEXITCODE; see $log" }
    if ($RunSuite) {
        $started = @(Select-String -Path $log -Pattern 'Test Started\. Name=')
        $passed = @(Select-String -Path $log -Pattern 'Test Completed\. Result=\{Success\}')
        $failed = @(Select-String -Path $log -Pattern 'Test Completed\. Result=\{(Fail|Error)\}')
        $cleanExit = Select-String -Path $log -Pattern 'TEST COMPLETE\. EXIT CODE: 0' | Select-Object -Last 1
        if (!$cleanExit -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -ne 0) {
            throw "Full automation suite did not report a clean complete pass (started=$($started.Count), passed=$($passed.Count), failed=$($failed.Count)); see $log"
        }
        Write-Output "Automation RunTests OneBossFight: passed=$($passed.Count), failed=0"
    }
} finally {
    foreach ($path in @($created.ToArray())) {
        if (Test-Path -LiteralPath $path) {
            $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
            if ($record.command_id -eq $token -and $record.task -eq 'C-1202') {
                Remove-Item -LiteralPath $path -Force
            } else {
                Write-Error "Lock ownership changed; preserving $path"
            }
        }
    }
}
