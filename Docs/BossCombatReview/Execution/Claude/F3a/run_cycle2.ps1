# F3a cycle 2: snapshot, build, full suite with the DD27j manifest hash, snapshot; writes DONE.txt last. No editor may run.
$E = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F3a'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$uproject = 'C:\UnrealProject\OneBossFight\OneBossFight.uproject'
if (@(Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor|UnrealBuildTool' }).Count -gt 0) { 'STOP: engine process running' | Set-Content "$E\DONE2.txt"; exit 2 }
if (Test-Path 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json') { 'STOP: engine lock present' | Set-Content "$E\DONE2.txt"; exit 2 }
& "$E\snapshot.ps1" -Out "$E\pre_state2.txt" | Set-Content "$E\pre_state2_summary.txt"
(Get-FileHash 'C:\UnrealProject\OneBossFight\Binaries\Win64\UnrealEditor-OneBossFight.dll').Hash.ToLower() | Set-Content "$E\pre_dll2_sha256.txt"
$sw = [Diagnostics.Stopwatch]::StartNew()
& "$engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$uproject" -WaitMutex *> "$E\build2_raw.log"
$buildExit = $LASTEXITCODE
"build exit=$buildExit seconds=$([int]$sw.Elapsed.TotalSeconds)" | Set-Content "$E\build2_result.txt"
if ($buildExit -ne 0) { 'STOP: build failed' | Set-Content "$E\DONE2.txt"; exit 3 }
(Get-FileHash 'C:\UnrealProject\OneBossFight\Binaries\Win64\UnrealEditor-OneBossFight.dll').Hash.ToLower() | Set-Content "$E\post_dll2_sha256.txt"
$hash = (Get-FileHash 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD27j\run_C339\EmberWarden_PhaseTwo_fields_manifest.json' -Algorithm SHA256).Hash.ToLower()
$hash | Set-Content "$E\manifest_hash2.txt"
$sw.Restart()
$p = Start-Process -FilePath "$engine\Binaries\Win64\UnrealEditor-Cmd.exe" -ArgumentList @($uproject, '-ExecCmds="Automation RunTests OneBossFight; Quit"', '-unattended', '-nullrhi', '-nosound', '-nosplash', "-DD27jManifestHash=$hash", "-abslog=$E\full2_raw.log") -PassThru -WindowStyle Hidden
$p.WaitForExit()
"full exit=$($p.ExitCode) seconds=$([int]$sw.Elapsed.TotalSeconds)" | Set-Content "$E\full2_result.txt"
& "$E\snapshot.ps1" -Out "$E\post_state2.txt" | Set-Content "$E\post_state2_summary.txt"
'DONE' | Set-Content "$E\DONE2.txt"
