# One F4 PIE run: run_pie.ps1 -Map <asset path> -OutDir <dir> -Task <name>
param([string[]]$Extra=@(),[switch]$Restart,[string]$Inject='',[string]$Dodge='',[string]$Live='',[string]$InjectPie='',[switch]$DiagLong,[Parameter(Mandatory=$true)][string]$Map,[Parameter(Mandatory=$true)][string]$OutDir,[Parameter(Mandatory=$true)][string]$Task)
$E = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Map | Set-Content "$E\current_map.txt"
if ($Restart) { "1" | Set-Content "$E\current_restart.txt" } else { Remove-Item "$E\current_restart.txt" -ErrorAction SilentlyContinue }
if ($Inject) { $Inject | Set-Content "$E\current_inject.txt" } else { Remove-Item "$E\current_inject.txt" -ErrorAction SilentlyContinue }
if ($InjectPie) { $InjectPie | Set-Content "$E\current_inject_pie.txt" } else { Remove-Item "$E\current_inject_pie.txt" -ErrorAction SilentlyContinue }
if ($DiagLong) { "1" | Set-Content "$E\current_diag_long.txt" } else { Remove-Item "$E\current_diag_long.txt" -ErrorAction SilentlyContinue }
if ($Live) { $Live | Set-Content "$E\current_live.txt" } else { Remove-Item "$E\current_live.txt" -ErrorAction SilentlyContinue }
if ($Dodge) { $Dodge | Set-Content "$E\current_dodge.txt" } else { Remove-Item "$E\current_dodge.txt" -ErrorAction SilentlyContinue }
"$OutDir\editor_raw.log" | Set-Content "$E\current_log.txt"
$more = @{}; if ($Extra.Count -gt 0) { $more.ExtraArgs = $Extra }
& 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1' @more -Script "$E\drive_pie.py" -OutDir $OutDir -Task $Task -NullRhi 0 -PyCmd 1 -TimeoutSeconds 240
