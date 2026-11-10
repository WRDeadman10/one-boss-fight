$root='C:\UnrealProject\OneBossFight'; Set-Location $root
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Docs\BossCombatReview\Execution\Claude\B_C1257_SEVAROGLIVE2\run_build293.ps1"
$st = Get-Content "$root\Docs\BossCombatReview\Execution\Claude\B_C1257_SEVAROGLIVE2\status.txt" -Raw
if ($st -notmatch 'BUILD exit 0' -or $st -notmatch 'fail=0') { "STOP: $st"; exit 1 }
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Scripts\RunLeadPie.ps1" -Script Scripts/Editor/pie_sevarog_framework_live.py -Routes data -Env SEVAROG_LIVE_SHOTS=1 -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1257_SEVAROGLIVE2 -StopMarker "[SevarogLive] finished:" -TimeoutSeconds 1200

