$lockFile = "c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$editor = "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$project = "c:\UnrealProject\OneBossFight\OneBossFight.uproject"
$script = "c:\UnrealProject\OneBossFight\Scripts\Editor\rebuild_ppm_parry_distortion.py"
$logFile = "c:\UnrealProject\OneBossFight\Saved\Logs\ppm_rebuild.log"

if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) {
    Write-Error "UnrealEditor process is already running. Please close it before running editor script."
    exit 1
}

if (Test-Path $lockFile) {
    Write-Error "ENGINE_LOCK already held: $(Get-Content $lockFile -Raw)"
    exit 1
}

try {
    $lockData = @{
        owner = "AG"
        pid = $PID
        purpose = "Rebuild PPM_ParryDistortion post process material C-1037"
        startTime = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    }
    $lockData | ConvertTo-Json | Set-Content -Path $lockFile

    & $editor $project "-ExecutePythonScript=$script" -nosound -stdout -FullStdOutLogOutput -unattended -NoSplash -abslog="$logFile"
    $exitCode = $LASTEXITCODE
    Write-Output "UnrealEditor-Cmd exited with code $exitCode"
    if ($exitCode -ne 0) {
        exit $exitCode
    }
}
finally {
    if (Test-Path $lockFile) {
        Remove-Item $lockFile -Force
    }
}
