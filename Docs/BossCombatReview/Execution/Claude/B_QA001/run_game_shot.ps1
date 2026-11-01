# One STANDALONE game run with evidence (lead, Claude), for BOSS-QA-001: the game window renders itself (no editor viewport), the engine's own screenshot request writes the game view, the game quits.
# Usage: run_game_shot.ps1 -Map <asset path> -OutDir <dir> -Task <name> -ShotPath <png> [-At 6] [-ShowUI 0] [-TimeoutSeconds 150] [-ResX 1280] [-ResY 720]
# Refuses to start when an Unreal process or ENGINE_LOCK.json exists. Writes the lock, pre/post snapshots, the raw log, result.json; releases the lock last.
param(
    [Parameter(Mandatory = $true)][string]$Map, [Parameter(Mandatory = $true)][string]$OutDir, [Parameter(Mandatory = $true)][string]$Task, [Parameter(Mandatory = $true)][string]$ShotPath,
    [double]$At = 6, [int]$ShowUI = 0, [int]$TimeoutSeconds = 150, [int]$ResX = 1280, [int]$ResY = 720
)
$root = 'C:\UnrealProject\OneBossFight'
$lock = "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$snap = "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1"
$exe = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
if (@(Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor|UnrealBuildTool' }).Count -gt 0) { 'STOP: engine process running' | Set-Content "$OutDir\STOP.txt"; exit 2 }
if (Test-Path $lock) { 'STOP: engine lock present' | Set-Content "$OutDir\STOP.txt"; exit 2 }
@{ agent = 'Claude'; party = 'C'; task = $Task; start_utc = (Get-Date).ToUniversalTime().ToString('o'); policy = 'C-321' } | ConvertTo-Json | Set-Content $lock
try {
    & $snap -Out "$OutDir\pre_state.txt" | Set-Content "$OutDir\pre_state_summary.txt"
    $log = "$OutDir\editor_raw.log"
    $cmds = "rpg.BossOverlay 1,rpg.ScreenshotShowUI $ShowUI,rpg.ScreenshotQuit 1,rpg.ScreenshotPath $($ShotPath -replace '\\','/'),rpg.ScreenshotAt $At"
    $args = @("$root\OneBossFight.uproject", $Map, '-game', '-windowed', "-ResX=$ResX", "-ResY=$ResY", '-nosound', '-nosplash', '-unattended', "-ExecCmds=`"$cmds`"", "-abslog=`"$log`"")
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $p = Start-Process -FilePath $exe -ArgumentList $args -PassThru
    $timedOut = -not $p.WaitForExit($TimeoutSeconds * 1000)
    if ($timedOut) { try { $p.Kill() } catch {} }
    $sw.Stop(); Start-Sleep -Seconds 4   # the engine closes its log a moment after the process ends
    $hash = if (Test-Path $log) { (Get-FileHash $log -Algorithm SHA256).Hash.ToLower() } else { 'no-log' }
    @{ timed_out = $timedOut; seconds = [int]$sw.Elapsed.TotalSeconds; task = $Task; raw_sha256 = $hash; exit_code = $(if ($timedOut) { -1 } else { $p.ExitCode }); command = $args } | ConvertTo-Json | Set-Content "$OutDir\result.json"
    "exit=$(if ($timedOut) { -1 } else { $p.ExitCode }) timedOut=$timedOut seconds=$([int]$sw.Elapsed.TotalSeconds) raw=$hash"
    & $snap -Out "$OutDir\post_state.txt" | Set-Content "$OutDir\post_state_summary.txt"
}
finally { Remove-Item $lock -ErrorAction SilentlyContinue }


