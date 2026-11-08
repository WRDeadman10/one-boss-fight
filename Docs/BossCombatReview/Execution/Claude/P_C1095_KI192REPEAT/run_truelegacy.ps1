# Lead PIE run (Claude, 2026-11-08, C-1095 / AR-C10 spec): pie_er_control_latency.py, 5 fresh processes per route, BUILD-269 binaries. Editor with -nosound, own ENGINE_LOCK.
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$root = 'C:\UnrealProject\OneBossFight'
$lock = "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$exe = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running' | Tee-Object "$dir\status.txt"; exit 2 }
if (Test-Path $lock) { 'ABORT: engine lock present' | Tee-Object "$dir\status.txt"; exit 2 }
@{ purpose = 'Lead PIE ER latency probe'; owner = 'C'; startTime = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') } | ConvertTo-Json | Out-File $lock -Encoding utf8
try {
  $short = (New-Object -ComObject Scripting.FileSystemObject).GetFile("$root\Scripts\Editor\pie_er_control_latency.py").ShortPath.ToLower().Replace([char]92, [char]47)
  $results = @()
  foreach ($rep in $(if ($env:REPS) { 1..[int]$env:REPS } else { 1..5 })) {
  foreach ($route in @(@{n='truelegacy'; v=''})) {
    $env:H019_ENCOUNTER_DEFINITION = $route.v
    $env:RPG_LEGACY_STARTUP = '1'  # since 2026-11-06 an unset selection means the DATA route; legacy needs this opt-out
    $log = "$dir\probe_$($route.n)_r$rep.log"
    $p = Start-Process -FilePath $exe -PassThru -ArgumentList @("`"$root\OneBossFight.uproject`"", "-ExecCmds=`"py $short`"", '-unattended', '-nosplash', '-nosound', "-abslog=`"$log`"")
    $deadline = (Get-Date).AddSeconds(480); $done = $false
    while (-not $p.HasExited -and (Get-Date) -lt $deadline) {
      Start-Sleep 3
      if ((Test-Path $log) -and (Select-String -Path $log -Pattern '\[ERControlLatency\] (SUMMARY )?finished:' -Quiet)) { $done = $true; Start-Sleep 5; break }
    }
    if (-not $p.HasExited) { $p.Kill(); $p.WaitForExit() }
    $results += "$($route.n)_r${rep}: finished=$done"
    Select-String -Path $log -Pattern '\[ERControlLatency\]|Fatal error' | ForEach-Object { $_.Line } | Out-File "$dir\probe_$($route.n)_r${rep}_lines.txt" -Encoding utf8
  }
  }
  $results -join '; ' | Tee-Object "$dir\status.txt"
} finally {
  $env:H019_ENCOUNTER_DEFINITION = $null; $env:RPG_LEGACY_STARTUP = $null
  Remove-Item $lock -Force -ErrorAction SilentlyContinue
}

