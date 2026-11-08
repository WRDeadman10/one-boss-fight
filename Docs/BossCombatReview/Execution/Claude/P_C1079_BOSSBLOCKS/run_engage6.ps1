# Lead PIE run (Claude, 2026-11-08, C-1079): ACTIVE camera-inside-boss engagement, both routes, rpg.Camera.BossBlocks 0 vs 1. -nosound, own ENGINE_LOCK.
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$root = 'C:\UnrealProject\OneBossFight'
$lock = "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$exe = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running' | Tee-Object "$dir\status_engage6.txt"; exit 2 }
if (Test-Path $lock) { 'ABORT: engine lock present' | Tee-Object "$dir\status_engage6.txt"; exit 2 }
@{ purpose = 'Lead camera BossBlocks probe'; owner = 'C'; startTime = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') } | ConvertTo-Json | Out-File $lock -Encoding utf8
try {
  $short = (New-Object -ComObject Scripting.FileSystemObject).GetFile("$dir\pie_camera_engage.py").ShortPath.ToLower().Replace([char]92, [char]47)
  $results = @()
  foreach ($cv in @('fixed_off')) {
    $env:CAM_MODE = $cv.Split('_')[0]; $env:CAM_VERBOSE = '1'
    foreach ($route in @(@{n='legacy'; v=''})) {
      $env:H019_ENCOUNTER_DEFINITION = $route.v
      $env:CAMERA_CVARS = @{ retreat_off = "rpg.Camera.HideBossInside 0;rpg.Camera.LockOnFraming 0"; retreat_hide = "rpg.Camera.HideBossInside 1;rpg.Camera.LockOnFraming 0"; fixed_off = "rpg.Camera.HideBossInside 0;rpg.Camera.LockOnFraming 0"; fixed_lock = "rpg.Camera.HideBossInside 0;rpg.Camera.LockOnFraming 1" }[$cv]
      $tag = "$($route.n)_$cv"
      $log = "$dir\engage6_$tag.log"
      $p = Start-Process -FilePath $exe -PassThru -ArgumentList @("`"$root\OneBossFight.uproject`"", "-ExecCmds=`"py $short`"", '-unattended', '-nosplash', '-nosound', "-abslog=`"$log`"")
      $deadline = (Get-Date).AddSeconds(240); $done = $false
      while (-not $p.HasExited -and (Get-Date) -lt $deadline) {
        Start-Sleep 3
        if ((Test-Path $log) -and (Select-String -Path $log -Pattern '\[CamEngage\] SUMMARY' -Quiet)) { $done = $true; Start-Sleep 5; break }
      }
      if (-not $p.HasExited) { $p.Kill(); $p.WaitForExit() }
      $results += "${tag}: finished=$done"
      Select-String -Path $log -Pattern '\[CamEngage\]|LogRPGCamera|Fatal error' | ForEach-Object { $_.Line } | Out-File "$dir\engage6_${tag}_lines.txt" -Encoding utf8
    }
  }
  $results -join '; ' | Tee-Object "$dir\status_engage6.txt"
} finally {
  $env:H019_ENCOUNTER_DEFINITION = $null; $env:CAMERA_CVARS = $null; $env:CAM_MODE = $null
  Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
