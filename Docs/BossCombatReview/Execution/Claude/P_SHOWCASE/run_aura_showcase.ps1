# Lead showcase capture (owner 2026-11-08 "Yes, showcase clips"). Usage: run_showcase.ps1 -Frames D:\FightVideo\showcase -Route data -Tag s1
param([string]$Frames = 'D:\FightVideo\showcase', [string]$Route = 'data', [string]$Tag = 's1', [int]$TimeoutMin = 90)
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'; $dir = $PSScriptRoot; $lock = "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running' | Tee-Object "$dir\status_$Tag.txt"; exit 2 }
if (Test-Path $lock) { 'ABORT: engine lock present' | Tee-Object "$dir\status_$Tag.txt"; exit 2 }
@{ purpose = "Lead showcase capture ($Tag)"; owner = 'C'; startTime = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') } | ConvertTo-Json | Out-File $lock -Encoding utf8
try {
  New-Item -ItemType Directory -Force $Frames | Out-Null
  Get-ChildItem $Frames -Filter 'f_*.png' -ErrorAction SilentlyContinue | Remove-Item -Force
  $env:SHOWCASE_FRAMES = $Frames.Replace('\', '/')
  $env:H019_ENCOUNTER_DEFINITION = if ($Route -eq 'data') { '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter' } else { '' }
  $short = (New-Object -ComObject Scripting.FileSystemObject).GetFile("$dir\pie_aura_showcase.py").ShortPath.ToLower().Replace([char]92, [char]47)
  $log = "$dir\showcase_$Tag.log"
  $p = Start-Process -FilePath 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe' -PassThru -ArgumentList @("`"$root\OneBossFight.uproject`"", "-ExecCmds=`"py $short`"", '-unattended', '-nosplash', '-nosound', "-abslog=`"$log`"")
  $deadline = (Get-Date).AddMinutes($TimeoutMin); $done = $false
  while (-not $p.HasExited -and (Get-Date) -lt $deadline) { Start-Sleep 5; if ((Test-Path $log) -and (Select-String -Path $log -Pattern '\[Showcase\] finished:' -Quiet)) { $done = $true; Start-Sleep 8; break } }
  if (-not $p.HasExited) { $p.Kill(); $p.WaitForExit() }
  Select-String -Path $log -Pattern '\[Showcase\] (SEG_BEGIN|SEG_END|draw|aura_|SUMMARY|finished|ERROR)|Traceback' | ForEach-Object { $_.Line -replace '^.*?\[Showcase\] ', '' } | Out-File "$dir\showcase_${Tag}_lines.txt" -Encoding utf8
  "finished=$done frames=$((Get-ChildItem $Frames -Filter 'f_*.png').Count)" | Tee-Object "$dir\status_$Tag.txt"
} finally {
  $env:SHOWCASE_FRAMES = $null; $env:H019_ENCOUNTER_DEFINITION = $null
  Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
