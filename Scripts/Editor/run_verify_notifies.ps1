$lockFile = "c:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$editor = "C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$project = "c:\UnrealProject\OneBossFight\OneBossFight.uproject"
$script = "c:\UnrealProject\OneBossFight\Scripts\Editor\verify_er_notifies.py"

try {
    $lockData = @{ owner = "AG"; pid = $PID; reason = "verify ER montage notifies batch AB-A01..A05" }
    $lockData | ConvertTo-Json | Set-Content -Path $lockFile
    & $editor $project "-ExecutePythonScript=$script" -nosound -stdout -FullStdOutLogOutput -unattended -NoSplash
} finally {
    if (Test-Path $lockFile) {
        Remove-Item $lockFile -Force
    }
}
