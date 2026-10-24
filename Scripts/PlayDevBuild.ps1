<#
.SYNOPSIS
  Starts the packaged DEVELOPMENT build for the owner's hand tests: windowed 1920x1080, sound ON, log ON, console available (press the key left of 1 to type commands such as rpg.CloseTelegraph 0).

.DESCRIPTION
  The Development stage lives in Saved\StagedBuilds\Windows (made by Scripts\Package.ps1 -Configuration Development); its log is Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs\OneBossFight.log, which the development Claude reads while you play.
  Use -Cvar to start with a console variable value, for example -Cvar 'rpg.CloseTelegraph 0'.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\PlayDevBuild.ps1
  powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\PlayDevBuild.ps1 -Cvar 'rpg.CloseTelegraph 0'
#>
param([string]$Cvar = '')
$Root = Split-Path -Parent $PSScriptRoot
$Exe = Join-Path $Root 'Saved\StagedBuilds\Windows\OneBossFight.exe'
if (-not (Test-Path $Exe)) { throw "No Development build at $Exe: run Scripts\Package.ps1 -Configuration Development first." }
$args2 = @('/Game/OneBossFight/Levels/L_SevarogArena', '-windowed', '-ResX=1920', '-ResY=1080', '-ForceRes', '-nosplash', '-log')
if ($Cvar) { $args2 += "-ExecCmds=`"$Cvar`"" }
Write-Host "Starting $Exe"
Start-Process -FilePath $Exe -ArgumentList $args2
