# Lead run C-1110 (AU-C01..C05): MAINTAINED Scripts/Editor/pie_full_fight.py with live A4 parry watch, DATA route, Tier 2 on. Based on P_FIGHTVIDEO runner (owner 2026-11-07). Usage: run_fight.ps1 -Max 480 -Frames D:\FightVideo\fight -Route data -Tag full
param([double]$Max = 480, [string]$Frames = 'D:\FightVideo\fight', [string]$Route = 'data', [string]$Tag = 'full', [int]$TimeoutMin = 150)
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'; $dir = $PSScriptRoot; $lock = "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running' | Tee-Object "$dir\status_$Tag.txt"; exit 2 }
if (Test-Path $lock) { 'ABORT: engine lock present' | Tee-Object "$dir\status_$Tag.txt"; exit 2 }
@{ purpose = "Lead full-fight video ($Tag)"; owner = 'C'; startTime = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') } | ConvertTo-Json | Out-File $lock -Encoding utf8
try {
  New-Item -ItemType Directory -Force $Frames | Out-Null
  Get-ChildItem $Frames -Filter 'f_*.png' -ErrorAction SilentlyContinue | Remove-Item -Force
  $env:FIGHT_MAX = "$Max"; $env:ER_FIGHT_TIER2 = '1'; $env:FIGHT_FRAMES = $Frames.Replace('\', '/')
  $env:H019_ENCOUNTER_DEFINITION = if ($Route -eq 'data') { '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter' } else { '' }
  $short = (New-Object -ComObject Scripting.FileSystemObject).GetFile("$root\Scripts\Editor\pie_full_fight.py").ShortPath.ToLower().Replace([char]92, [char]47)
  $log = "$dir\fight_$Tag.log"
  $p = Start-Process -FilePath 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe' -PassThru -ArgumentList @("`"$root\OneBossFight.uproject`"", "-ExecCmds=`"py $short`"", '-unattended', '-nosplash', '-nosound', "-abslog=`"$log`"")
  $deadline = (Get-Date).AddMinutes($TimeoutMin); $done = $false
  while (-not $p.HasExited -and (Get-Date) -lt $deadline) { Start-Sleep 5; if ((Test-Path $log) -and (Select-String -Path $log -Pattern '\[FullFight\] finished:' -Quiet)) { $done = $true; Start-Sleep 8; break } }
  if (-not $p.HasExited) { $p.Kill(); $p.WaitForExit() }
  Select-String -Path $log -Pattern '\[FullFight\] (route|setup|FIGHT_START|ACTION|COUNTER|PARRY|BOSS_DEAD|SUMMARY|finished|driver error)|Traceback|EncounterActivation\] route' | ForEach-Object { $_.Line -replace '^.*?\[FullFight\] ', '' } | Out-File "$dir\fight_${Tag}_lines.txt" -Encoding utf8
  "finished=$done frames=$((Get-ChildItem $Frames -Filter 'f_*.png').Count)" | Tee-Object "$dir\status_$Tag.txt"
} finally {
  $env:FIGHT_MAX = $null; $env:ER_FIGHT_TIER2 = $null; $env:FIGHT_FRAMES = $null; $env:H019_ENCOUNTER_DEFINITION = $null
  Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
