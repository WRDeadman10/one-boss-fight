$root='C:\UnrealProject\OneBossFight'; Set-Location $root
$deadline=(Get-Date).AddMinutes(60)
while ((Get-Process UnrealEditor* -ErrorAction SilentlyContinue) -or (Test-Path "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json") -or (Test-Path "$root\ENGINE_LOCK.json")) { if ((Get-Date) -gt $deadline) { 'gave up waiting'; exit 3 }; Start-Sleep -Seconds 20 }
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Scripts\RunLeadPie.ps1" -Script Scripts/Editor/pie_sevarog_clip_frames.py -Routes data -Env SEVAROG_CLIPS=LevelStart+Death_front -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1271_SEVAROGFRAMES3 -StopMarker "[SevarogFrames] finished:" -TimeoutSeconds 3600
