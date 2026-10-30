# F5 cycle: PIE F5 x2 more, F4 x1, F3 x1 regression, then the full suite with the DD27j hash. DONE1.txt last. Build is done before.
$E = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F5'
$P = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5'
if (@(Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor|UnrealBuildTool' }).Count -gt 0 -or (Test-Path "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json")) { 'STOP engine busy' | Set-Content "$E\DONE1.txt"; exit 2 }
(Get-FileHash "$root\Binaries\Win64\UnrealEditor-OneBossFight.dll").Hash.ToLower() | Set-Content "$E\c1_dll.txt"
foreach ($i in 2..3) { powershell -NoProfile -ExecutionPolicy Bypass -File $P -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF5 -OutDir "$E\pie_run$i" -Task "C-412/F5-pie-$i" | Set-Content "$E\c1_pie_f5_$i.txt" }
powershell -NoProfile -ExecutionPolicy Bypass -File $P -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF4 -OutDir "$E\regression_f4" -Task "C-412/F4-regression" | Set-Content "$E\c1_pie_f4.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File $P -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProof -OutDir "$E\regression_f3" -Task "C-412/F3-regression" | Set-Content "$E\c1_pie_f3.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1" -Out "$E\c1_full_pre_state.txt" | Set-Content "$E\c1_full_pre_summary.txt"
$hash = (Get-FileHash "$root\Docs\BossCombatReview\Execution\Codex\DD27j\run_C339\EmberWarden_PhaseTwo_fields_manifest.json" -Algorithm SHA256).Hash.ToLower()
$p = Start-Process -FilePath "$engine\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" -ArgumentList @("$root\OneBossFight.uproject", '-ExecCmds="Automation RunTests OneBossFight; Quit"', '-unattended', '-nullrhi', '-nosound', '-nosplash', "-DD27jManifestHash=$hash", "-abslog=$E\c1_full_raw.log") -PassThru -WindowStyle Hidden
$p.WaitForExit()
"full exit=$($p.ExitCode)" | Set-Content "$E\c1_full_result.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1" -Out "$E\c1_full_post_state.txt" | Set-Content "$E\c1_full_post_summary.txt"
'DONE' | Set-Content "$E\DONE1.txt"
