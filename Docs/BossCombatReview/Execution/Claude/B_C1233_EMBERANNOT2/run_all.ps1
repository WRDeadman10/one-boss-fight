& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_C1233_EMBERANNOT2\run_build285.ps1"
$st = Get-Content "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\B_C1233_EMBERANNOT2\status.txt" -Raw
if ($st -notmatch 'AUTHOR exit 0 complete=1' -or $st -notmatch 'fail=0') { "SKIP PIE: $st"; exit 1 }
& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\UnrealProject\OneBossFight\Scripts\RunLeadPie.ps1" -Script Scripts/Editor/pie_ember_notify_timing_parity.py -Routes data -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1233_EMBERPARITY -StopMarker "[EmberNotifyParity] finished:" -TimeoutSeconds 480
