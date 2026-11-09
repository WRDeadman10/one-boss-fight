# Runs author_boss01_heavyswordsocket.py under exclusive ENGINE_LOCK.json (C-1172, C-1183)
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$lockFile = Join-Path $repoRoot "ENGINE_LOCK.json"
$engineExe = "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$uproject = Join-Path $repoRoot "OneBossFight.uproject"
$scriptPath = Join-Path $repoRoot "Scripts\Editor\author_boss01_heavyswordsocket.py"
$logFile = Join-Path $repoRoot "Saved\Logs\author_boss01_heavyswordsocket.log"

if (-not (Test-Path $engineExe)) {
    Write-Error "UnrealEditor-Cmd.exe not found at $engineExe"
    exit 1
}

# 1. Acquire exclusive lock
if (Test-Path $lockFile) {
    $existing = Get-Content $lockFile -Raw
    Write-Error "ENGINE_LOCK.json already exists: $existing"
    exit 1
}

$lockContent = @{
    owner = "A"
    reason = "C-1172/C-1183 Author HeavySwordSocket_R transform adjustment"
    pid = $PID
    time = (Get-Date).ToString("o")
} | ConvertTo-Json

Set-Content -Path $lockFile -Value $lockContent
Write-Host "[HeavySwordSocket] Acquired ENGINE_LOCK.json (owner: A)"

try {
    # 2. Execute script in editor
    Write-Host "[HeavySwordSocket] Launching UnrealEditor-Cmd with $scriptPath"
    & $engineExe $uproject "-ExecutePythonScript=$scriptPath" -nosound -stdout -FullStdOutLogOutput -unattended -NoSplash -abslog="$logFile"
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Error "Editor process exited with code $exitCode"
        exit $exitCode
    }
    Write-Host "[HeavySwordSocket] Execution completed successfully (ExitCode: 0)"
}
finally {
    # 3. Always release lock
    if (Test-Path $lockFile) {
        Remove-Item -Path $lockFile -Force
        Write-Host "[HeavySwordSocket] Released ENGINE_LOCK.json"
    }
}
