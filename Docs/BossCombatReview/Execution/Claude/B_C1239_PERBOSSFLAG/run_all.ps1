$root='C:\UnrealProject\OneBossFight'; Set-Location $root
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Docs\BossCombatReview\Execution\Claude\B_C1239_PERBOSSFLAG\run_build287.ps1"
$st = Get-Content "$root\Docs\BossCombatReview\Execution\Claude\B_C1239_PERBOSSFLAG\status.txt" -Raw
if ($st -notmatch 'BUILD exit 0' -or $st -notmatch 'fail=0') { "STOP: $st"; exit 1 }
# Sevarog read-only probe (A-718) under lock
$lock="$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"; $rl="$root\ENGINE_LOCK.json"
$j=@{owner='C';purpose='C-1239 Sevarog probe';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID}|ConvertTo-Json; Set-Content $lock $j; Set-Content $rl $j
try {
  $p="$root\Docs\BossCombatReview\Execution\Claude\P_C1239_SEVAROGPROBE"; New-Item -ItemType Directory -Force $p | Out-Null
  git status --porcelain -- Content | Out-File "$p\pre_content.txt" -Encoding utf8
  & 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\probe_sevarog_animations.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\probe_sevarog.log" | Out-Null
  "SEVAROG_PROBE exit=$LASTEXITCODE" | Tee-Object "$p\status.txt"
  git status --porcelain -- Content | Out-File "$p\post_content.txt" -Encoding utf8
} finally { Remove-Item $lock,$rl -ErrorAction SilentlyContinue }
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Scripts\RunLeadPie.ps1" -Script Scripts/Editor/pie_ember_notify_timing_parity.py -Routes data -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1239_EMBERPARITY5 -StopMarker "[EmberNotifyParity] finished:" -TimeoutSeconds 600
