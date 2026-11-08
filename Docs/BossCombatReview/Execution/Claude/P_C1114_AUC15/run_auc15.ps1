# Lead PIE run (Claude, 2026-11-09, C-1116 / AU-C15): pie_aura_comparison.py approved-only, DATA route, one process. Editor with -nosound, own ENGINE_LOCK.
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$root = 'C:\UnrealProject\OneBossFight'
$lock = "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$exe = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running' | Tee-Object "$dir\status.txt"; exit 2 }
if (Test-Path $lock) { 'ABORT: engine lock present' | Tee-Object "$dir\status.txt"; exit 2 }
@{ purpose = 'Lead PIE ER latency probe'; owner = 'C'; startTime = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') } | ConvertTo-Json | Out-File $lock -Encoding utf8
try {
  $short = (New-Object -ComObject Scripting.FileSystemObject).GetFile("$root\Scripts\Editor\pie_aura_comparison.py").ShortPath.ToLower().Replace([char]92, [char]47)
  $results = @()
  foreach ($rep in 1..1) {
  foreach ($route in @(@{n='data'; v='/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'})) {
    $env:H019_ENCOUNTER_DEFINITION = $route.v
    $env:AURA_COMPARE_APPROVED_ONLY = '1'; $env:AURA_COMPARE_RUN = 'AU_C15_c1116'
    $log = "$dir\probe_$($route.n)_r$rep.log"
    $p = Start-Process -FilePath $exe -PassThru -ArgumentList @("`"$root\OneBossFight.uproject`"", "-ExecCmds=`"py $short`"", '-unattended', '-nosplash', '-nosound', "-abslog=`"$log`"")
    $deadline = (Get-Date).AddSeconds(360); $done = $false
    while (-not $p.HasExited -and (Get-Date) -lt $deadline) {
      Start-Sleep 3
      if ((Test-Path $log) -and (Select-String -Path $log -Pattern '\[AuraCompare\] SUMMARY' -Quiet)) { $done = $true; Start-Sleep 5; break }
    }
    if (-not $p.HasExited) { $p.Kill(); $p.WaitForExit() }
    $results += "$($route.n)_r${rep}: finished=$done"
    Select-String -Path $log -Pattern '\[AuraCompare\]|EncounterActivation\] route|Fatal error|Traceback' | ForEach-Object { $_.Line } | Out-File "$dir\probe_$($route.n)_r${rep}_lines.txt" -Encoding utf8
  }
  }
  $results -join '; ' | Tee-Object "$dir\status.txt"
} finally {
  $env:H019_ENCOUNTER_DEFINITION = $null; $env:AURA_COMPARE_APPROVED_ONLY = $null; $env:AURA_COMPARE_RUN = $null
  Remove-Item $lock -Force -ErrorAction SilentlyContinue
}

