# KI-147 falsifiable check (Antigravity A-305): 5 F5 runs at a FIXED 60 FPS (-benchmark -fps=60). Prediction: AntiGreed hits 5 of 5.
$E = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F6\fixed60'
$P = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1'
if (@(Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor|UnrealBuildTool' }).Count -gt 0 -or (Test-Path 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json')) { 'STOP engine busy' | Set-Content "$E\DONE.txt"; exit 2 }
foreach ($i in 1..5) { powershell -NoProfile -ExecutionPolicy Bypass -File $P -Extra '-benchmark','-fps=60' -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF5 -OutDir "$E\run$i" -Task "C-424/KI147-fixed60-$i" | Set-Content "$E\result_$i.txt" }
'DONE' | Set-Content "$E\DONE.txt"
