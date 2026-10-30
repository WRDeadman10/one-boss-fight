# F4 cycle 2: build, 3 F4 PIE runs, 1 F3 PIE regression run, full suite with the DD27j hash. DONE2.txt last.
$E = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5'
if (@(Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor|UnrealBuildTool' }).Count -gt 0 -or (Test-Path "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json")) { 'STOP engine busy' | Set-Content "$E\DONE2.txt"; exit 2 }
(Get-FileHash "$root\Binaries\Win64\UnrealEditor-OneBossFight.dll").Hash.ToLower() | Set-Content "$E\c2_pre_dll.txt"
& "$engine\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$root\OneBossFight.uproject" -WaitMutex *> "$E\c2_build_raw.log"
$b = $LASTEXITCODE
"build exit=$b" | Set-Content "$E\c2_build_result.txt"
if ($b -ne 0) { 'STOP build failed' | Set-Content "$E\DONE2.txt"; exit 3 }
(Get-FileHash "$root\Binaries\Win64\UnrealEditor-OneBossFight.dll").Hash.ToLower() | Set-Content "$E\c2_post_dll.txt"
foreach ($i in 1..3) { powershell -NoProfile -ExecutionPolicy Bypass -File "$E\run_pie.ps1" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF4 -OutDir "$E\final_f4_run$i" -Task "C-404/F4-final-$i" | Set-Content "$E\c2_pie_f4_$i.txt" }
powershell -NoProfile -ExecutionPolicy Bypass -File "$E\run_pie.ps1" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProof -OutDir "$E\final_f3_regression" -Task "C-404/F3-regression" | Set-Content "$E\c2_pie_f3.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1" -Out "$E\c2_full_pre_state.txt" | Set-Content "$E\c2_full_pre_summary.txt"
$hash = (Get-FileHash "$root\Docs\BossCombatReview\Execution\Codex\DD27j\run_C339\EmberWarden_PhaseTwo_fields_manifest.json" -Algorithm SHA256).Hash.ToLower()
$p = Start-Process -FilePath "$engine\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" -ArgumentList @("$root\OneBossFight.uproject", '-ExecCmds="Automation RunTests OneBossFight; Quit"', '-unattended', '-nullrhi', '-nosound', '-nosplash', "-DD27jManifestHash=$hash", "-abslog=$E\c2_full_raw.log") -PassThru -WindowStyle Hidden
$p.WaitForExit()
"full exit=$($p.ExitCode)" | Set-Content "$E\c2_full_result.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1" -Out "$E\c2_full_post_state.txt" | Set-Content "$E\c2_full_post_summary.txt"
'DONE' | Set-Content "$E\DONE2.txt"
