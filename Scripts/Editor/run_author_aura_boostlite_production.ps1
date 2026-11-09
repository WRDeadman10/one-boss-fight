# Runs author_aura_boostlite_production.py under exclusive ENGINE_LOCK.json (C-1168, C-1196, C-1197)
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$lockFile1 = Join-Path $repoRoot "ENGINE_LOCK.json"
$lockFile2 = Join-Path $repoRoot "Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$engineExe = "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$uproject = Join-Path $repoRoot "OneBossFight.uproject"
$scriptPath = Join-Path $repoRoot "Scripts\Editor\author_aura_boostlite_production.py"
$logFile = Join-Path $repoRoot "Saved\Logs\author_aura_boostlite_production.log"

if (-not (Test-Path $engineExe)) {
    Write-Error "UnrealEditor-Cmd.exe not found at $engineExe"
    exit 1
}

# 1. Acquire exclusive lock in both root and execution folder
if ((Test-Path $lockFile1) -or (Test-Path $lockFile2)) {
    Write-Error "ENGINE_LOCK.json already exists in root or Execution dir"
    exit 1
}

$lockContent = @{
    owner = "A"
    reason = "C-1196/C-1197 Promote BoostLite parameters into production NS_Boss_PhaseTwoAura"
    pid = $PID
    time = (Get-Date).ToString("o")
} | ConvertTo-Json

Set-Content -Path $lockFile1 -Value $lockContent
Set-Content -Path $lockFile2 -Value $lockContent
Write-Host "[AuraBoostLiteProduction] Acquired ENGINE_LOCK.json in root and Docs/BossCombatReview/Execution/ (owner: A)"

try {
    # 2. Execute script in editor
    Write-Host "[AuraBoostLiteProduction] Launching UnrealEditor-Cmd with $scriptPath"
    & $engineExe $uproject "-ExecutePythonScript=$scriptPath" -nosound -stdout -FullStdOutLogOutput -unattended -NoSplash -abslog="$logFile"
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Error "Editor process exited with code $exitCode"
        exit $exitCode
    }
    Write-Host "[AuraBoostLiteProduction] Execution completed successfully (ExitCode: 0)"
}
finally {
    # 3. Always release both locks
    if (Test-Path $lockFile1) {
        Remove-Item -Path $lockFile1 -Force
    }
    if (Test-Path $lockFile2) {
        Remove-Item -Path $lockFile2 -Force
    }
    Write-Host "[AuraBoostLiteProduction] Released ENGINE_LOCK.json from both locations"
}
