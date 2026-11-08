# Lead PIE run (Claude, 2026-11-07, C-1006): runtime-assigned AirLight/AirHeavy montages, grounded R1/R2 unchanged; both routes. Editor -nosound, own ENGINE_LOCK.
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$root = 'C:\UnrealProject\OneBossFight'
$lock = "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$exe = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running' | Tee-Object "$dir\synth_status.txt"; exit 2 }
if (Test-Path $lock) { 'ABORT: engine lock present' | Tee-Object "$dir\synth_status.txt"; exit 2 }
@{ purpose = 'Lead PIE ER guard counter check'; owner = 'C'; startTime = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') } | ConvertTo-Json | Out-File $lock -Encoding utf8
try {
  $short = (New-Object -ComObject Scripting.FileSystemObject).GetFile("$root\Scripts\Editor\pie_er_guard_counter.py").ShortPath.ToLower().Replace([char]92, [char]47)
  $results = @()
  foreach ($route in @(@{n='legacy'; v=''}, @{n='data'; v='/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'})) {
    $env:H019_ENCOUNTER_DEFINITION = $route.v
    $env:ER_GC_ASSIGN = '1'
    $env:ER_GC_SYNTHETIC = '1'
    $log = "$dir\synth_$($route.n).log"
    $p = Start-Process -FilePath $exe -PassThru -ArgumentList @("`"$root\OneBossFight.uproject`"", "-ExecCmds=`"py $short`"", '-unattended', '-nosplash', '-nosound', "-abslog=`"$log`"")
    $deadline = (Get-Date).AddSeconds(240); $done = $false
    while (-not $p.HasExited -and (Get-Date) -lt $deadline) {
      Start-Sleep 3
      if ((Test-Path $log) -and (Select-String -Path $log -Pattern '\[ERGuardCounter\] SUMMARY reason=' -Quiet)) { $done = $true; Start-Sleep 5; break }
    }
    if (-not $p.HasExited) { $p.Kill(); $p.WaitForExit() }
    $results += "$($route.n): finished=$done"
    Select-String -Path $log -Pattern '\[ERGuardCounter\]|Fatal error' | ForEach-Object { $_.Line } | Out-File "$dir\synth_$($route.n)_lines.txt" -Encoding utf8
  }
  $results -join '; ' | Tee-Object "$dir\synth_status.txt"
} finally {
  $env:H019_ENCOUNTER_DEFINITION = $null
  $env:ER_GC_SYNTHETIC = $null
  $env:ER_GC_ASSIGN = $null
  Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
