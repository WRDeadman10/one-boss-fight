# F6a cycle: build, 3 PIE runs with injected hits on the F6 map, regressions F5/F4/F3, then the full suite with the DD27j hash. DONE1.txt last.
$E = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F6'
$P = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5'
if (@(Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor|UnrealBuildTool' }).Count -gt 0 -or (Test-Path "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json")) { 'STOP engine busy' | Set-Content "$E\DONE1.txt"; exit 2 }
& "$engine\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$root\OneBossFight.uproject" -WaitMutex *> "$E\c1_build_raw.log"
$b = $LASTEXITCODE
"build exit=$b" | Set-Content "$E\c1_build_result.txt"
if ($b -ne 0) { 'STOP build failed' | Set-Content "$E\DONE1.txt"; exit 3 }
(Get-FileHash "$root\Binaries\Win64\UnrealEditor-OneBossFight.dll").Hash.ToLower() | Set-Content "$E\c1_dll.txt"
foreach ($i in 1..3) { powershell -NoProfile -ExecutionPolicy Bypass -File $P -Inject "0.5,0.9,1.2" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF6 -OutDir "$E\final_f6_run$i" -Task "C-417/F6-final-$i" | Set-Content "$E\c1_pie_f6_$i.txt" }
powershell -NoProfile -ExecutionPolicy Bypass -File $P -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF5 -OutDir "$E\regression_f5" -Task "C-417/F5-regression" | Set-Content "$E\c1_pie_f5.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File $P -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF4 -OutDir "$E\regression_f4" -Task "C-417/F4-regression" | Set-Content "$E\c1_pie_f4.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File $P -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProof -OutDir "$E\regression_f3" -Task "C-417/F3-regression" | Set-Content "$E\c1_pie_f3.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1" -Out "$E\c1_full_pre_state.txt" | Set-Content "$E\c1_full_pre_summary.txt"
$hash = (Get-FileHash "$root\Docs\BossCombatReview\Execution\Codex\DD27j\run_C339\EmberWarden_PhaseTwo_fields_manifest.json" -Algorithm SHA256).Hash.ToLower()
$p = Start-Process -FilePath "$engine\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" -ArgumentList @("$root\OneBossFight.uproject", '-ExecCmds="Automation RunTests OneBossFight; Quit"', '-unattended', '-nullrhi', '-nosound', '-nosplash', "-DD27jManifestHash=$hash", "-abslog=$E\c1_full_raw.log") -PassThru -WindowStyle Hidden
$p.WaitForExit()
"full exit=$($p.ExitCode)" | Set-Content "$E\c1_full_result.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1" -Out "$E\c1_full_post_state.txt" | Set-Content "$E\c1_full_post_summary.txt"
'DONE' | Set-Content "$E\DONE1.txt"
