# C-807 live order measurement. Claude runs this after ensuring the editor is idle.
param([Parameter(Mandatory=$true)][string]$OutDir)
$root = 'C:\UnrealProject\OneBossFight'
$here = "$root\Docs\BossCombatReview\Execution\Codex\H019_ORDER"
"$OutDir\editor_raw.log" | Set-Content "$here\current_log.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1" `
    -Script "$here\drive_pie.py" -OutDir $OutDir -Task 'H019-C804-live-order' `
    -NullRhi 0 -PyCmd 1 -TimeoutSeconds 180
