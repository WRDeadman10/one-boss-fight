# F3d cycle 3: build, one F3d PIE run (windowed editor), full suite with the DD27j hash. Writes DONE3.txt last. Refuses if an engine process or lock exists.
$E = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F3d'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5'
if (@(Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor|UnrealBuildTool' }).Count -gt 0 -or (Test-Path "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json")) { 'STOP engine busy' | Set-Content "$E\DONE3.txt"; exit 2 }
(Get-FileHash "$root\Binaries\Win64\UnrealEditor-OneBossFight.dll").Hash.ToLower() | Set-Content "$E\c3_pre_dll.txt"
& "$engine\Engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$root\OneBossFight.uproject" -WaitMutex *> "$E\c3_build_raw.log"
"build exit=$LASTEXITCODE" | Set-Content "$E\c3_build_result.txt"
if ($LASTEXITCODE -ne 0) { 'STOP build failed' | Set-Content "$E\DONE3.txt"; exit 3 }
(Get-FileHash "$root\Binaries\Win64\UnrealEditor-OneBossFight.dll").Hash.ToLower() | Set-Content "$E\c3_post_dll.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1" -Script "$E\drive_f3d.py" -OutDir "$E\run5" -Task "C-398/F3d-pie-proof-final" -NullRhi 0 -PyCmd 1 -TimeoutSeconds 240 | Set-Content "$E\c3_pie_result.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1" -Out "$E\c3_full_pre_state.txt" | Set-Content "$E\c3_full_pre_summary.txt"
$hash = (Get-FileHash "$root\Docs\BossCombatReview\Execution\Codex\DD27j\run_C339\EmberWarden_PhaseTwo_fields_manifest.json" -Algorithm SHA256).Hash.ToLower()
$p = Start-Process -FilePath "$engine\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" -ArgumentList @("$root\OneBossFight.uproject", '-ExecCmds="Automation RunTests OneBossFight; Quit"', '-unattended', '-nullrhi', '-nosound', '-nosplash', "-DD27jManifestHash=$hash", "-abslog=$E\c3_full_raw.log") -PassThru -WindowStyle Hidden
$p.WaitForExit()
"full exit=$($p.ExitCode)" | Set-Content "$E\c3_full_result.txt"
& "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1" -Out "$E\c3_full_post_state.txt" | Set-Content "$E\c3_full_post_summary.txt"
'DONE' | Set-Content "$E\DONE3.txt"
