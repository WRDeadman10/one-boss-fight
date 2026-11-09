$lockFile = "c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$editor = "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$project = "c:\UnrealProject\OneBossFight\OneBossFight.uproject"
$script = "c:\UnrealProject\OneBossFight\Scripts\Editor\author_boss01_greatsword_sockets.py"
$logFile = "c:\UnrealProject\OneBossFight\Saved\Logs\author_boss01_greatsword_sockets.log"

if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) {
    Write-Error "UnrealEditor process is already running. Please close it before running editor script."
    exit 1
}

$lockAcquired = $false
try {
    New-Item -Path $lockFile -ItemType File -ErrorAction Stop | Out-Null
    $lockAcquired = $true
    $lockData = @{
        owner = "A"
        pid = $PID
        purpose = "Author sockets on SM_Boss01_Greatsword C-1172"
        startTime = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    }
    $lockData | ConvertTo-Json | Set-Content -Path $lockFile -ErrorAction Stop

    & $editor $project "-ExecutePythonScript=$script" -nosound -stdout -FullStdOutLogOutput -unattended -NoSplash -abslog="$logFile"
    $exitCode = $LASTEXITCODE
    Write-Output "UnrealEditor-Cmd exited with code $exitCode"
    if ($exitCode -ne 0) {
        exit $exitCode
    }
}
finally {
    if ($lockAcquired -and (Test-Path $lockFile)) {
        Remove-Item $lockFile -Force
    }
}
