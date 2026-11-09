# Runs pie_ember_visual_weapon_trace.py under exclusive ENGINE_LOCK.json (C-1172, C-1183)
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$lockFile = Join-Path $repoRoot "ENGINE_LOCK.json"
$engineExe = "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$uproject = Join-Path $repoRoot "OneBossFight.uproject"
$scriptPath = (Join-Path $repoRoot "Scripts\Editor\pie_ember_visual_weapon_trace.py").Replace('\', '/')
$logFile = Join-Path $repoRoot "Docs\BossCombatReview\Execution\Codex\C1172_EMBER_VISUAL_TRACE\pie_probe_r9.log"

if (-not (Test-Path $engineExe)) {
    Write-Error "UnrealEditor-Cmd.exe not found at $engineExe"
    exit 1
}

if (Test-Path $lockFile) {
    $existing = Get-Content $lockFile -Raw
    Write-Error "ENGINE_LOCK.json already exists: $existing"
    exit 1
}

$lockContent = @{
    owner = "A"
    reason = "C-1172/C-1183 Post-Grip-Refinement Verification Probe (r9)"
    pid = $PID
    time = (Get-Date).ToString("o")
} | ConvertTo-Json

Set-Content -Path $lockFile -Value $lockContent
Write-Host "[EmberSwordProbe] Acquired ENGINE_LOCK.json (owner: A)"

try {
    Write-Host "[EmberSwordProbe] Launching UnrealEditor-Cmd with $scriptPath"
    & $engineExe $uproject "-ExecCmds=py `"$scriptPath`"" -unattended -nosound -nosplash -nullrhi "-abslog=$logFile"
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Error "Editor process exited with code $exitCode"
        exit $exitCode
    }
    Write-Host "[EmberSwordProbe] Execution completed successfully (ExitCode: 0)"
}
finally {
    if (Test-Path $lockFile) {
        Remove-Item -Path $lockFile -Force
        Write-Host "[EmberSwordProbe] Released ENGINE_LOCK.json"
    }
}
