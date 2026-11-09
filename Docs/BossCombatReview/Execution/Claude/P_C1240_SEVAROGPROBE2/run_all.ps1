$root='C:\UnrealProject\OneBossFight'; Set-Location $root
$lock="$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"; $rl="$root\ENGINE_LOCK.json"
if ((Test-Path $lock) -or (Test-Path $rl) -or (Get-Process UnrealEditor* -ErrorAction SilentlyContinue)) { 'busy'; exit 2 }
$j=@{owner='C';purpose='C-1240 Sevarog probe v2';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID}|ConvertTo-Json; Set-Content $lock $j; Set-Content $rl $j
try {
  $p="$root\Docs\BossCombatReview\Execution\Claude\P_C1240_SEVAROGPROBE2"; New-Item -ItemType Directory -Force $p | Out-Null
  git status --porcelain -- Content | Out-File "$p\pre_content.txt" -Encoding utf8
  & 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\probe_sevarog_animations.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\probe_sevarog.log" | Out-Null
  "SEVAROG_PROBE exit=$LASTEXITCODE" | Tee-Object "$p\status.txt"
  git status --porcelain -- Content | Out-File "$p\post_content.txt" -Encoding utf8
} finally { Remove-Item $lock,$rl -ErrorAction SilentlyContinue }
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Scripts\RunLeadPie.ps1" -Script Scripts/Editor/pie_ember_notify_timing_parity.py -Routes data -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1240_EMBERPARITY6 -StopMarker "[EmberNotifyParity] finished:" -TimeoutSeconds 900
