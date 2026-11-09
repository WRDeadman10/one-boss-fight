# Runs export_sfx_batch3.py under exclusive ENGINE_LOCK.json (C-1204)
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$lockFile1 = Join-Path $repoRoot "ENGINE_LOCK.json"
$lockFile2 = Join-Path $repoRoot "Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$engineExe = "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$uproject = Join-Path $repoRoot "OneBossFight.uproject"
$scriptPath = Join-Path $repoRoot "Scripts\Editor\export_sfx_batch3.py"
$logFile = Join-Path $repoRoot "Saved\Logs\export_sfx_batch3.log"

if (-not (Test-Path $engineExe)) {
    Write-Error "UnrealEditor-Cmd.exe not found at $engineExe"
    exit 1
}

# 1. Acquire exclusive lock in both root and Execution dir
if ((Test-Path $lockFile1) -or (Test-Path $lockFile2)) {
    Write-Error "ENGINE_LOCK.json already exists in root or Execution dir"
    exit 1
}

$lockContent = @{
    owner = "A"
    reason = "C-1204 Export SFX Batch 3 attack whooshes (A1-A3, Mid01, Sprint)"
    pid = $PID
    time = (Get-Date).ToString("o")
} | ConvertTo-Json

Set-Content -Path $lockFile1 -Value $lockContent
Set-Content -Path $lockFile2 -Value $lockContent
Write-Host "[ExportSFXBatch3] Acquired ENGINE_LOCK.json in root and Docs/BossCombatReview/Execution/ (owner: A)"

try {
    # 2. Execute export script
    Write-Host "[ExportSFXBatch3] Launching UnrealEditor-Cmd with $scriptPath"
    & $engineExe $uproject "-ExecutePythonScript=$scriptPath" -nosound -stdout -FullStdOutLogOutput -unattended -NoSplash -abslog="$logFile"
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Error "Editor process exited with code $exitCode"
        exit $exitCode
    }
    Write-Host "[ExportSFXBatch3] Export completed successfully (ExitCode: 0)"
}
finally {
    # 3. Always release both locks
    if (Test-Path $lockFile1) {
        Remove-Item -Path $lockFile1 -Force
    }
    if (Test-Path $lockFile2) {
        Remove-Item -Path $lockFile2 -Force
    }
    Write-Host "[ExportSFXBatch3] Released ENGINE_LOCK.json from both locations"
}
