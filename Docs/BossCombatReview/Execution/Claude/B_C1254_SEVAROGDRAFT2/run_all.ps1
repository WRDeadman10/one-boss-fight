$root='C:\UnrealProject\OneBossFight'; Set-Location $root
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Docs\BossCombatReview\Execution\Claude\B_C1254_SEVAROGDRAFT2\run_build291.ps1"
$st = Get-Content "$root\Docs\BossCombatReview\Execution\Claude\B_C1254_SEVAROGDRAFT2\status.txt" -Raw
if ($st -notmatch 'BUILD exit 0' -or $st -notmatch 'fail=0') { "STOP: $st"; exit 1 }
$lock="$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"; $rl="$root\ENGINE_LOCK.json"
$j=@{owner='C';purpose='C-1254 Sevarog authoring run 5 (real)';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID}|ConvertTo-Json; Set-Content $lock $j; Set-Content $rl $j
try {
  $p="$root\Docs\BossCombatReview\Execution\Claude\P_C1254_SEVAROGAUTHOR"; New-Item -ItemType Directory -Force $p | Out-Null
  git status --porcelain -- Content | Out-File "$p\pre_content.txt" -Encoding utf8
  & 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\author_sevarog_draft_cards.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\author.log" | Out-Null
  "AUTHOR exit=$LASTEXITCODE" | Tee-Object "$p\status.txt"
  git status --porcelain -- Content | Out-File "$p\post_content.txt" -Encoding utf8
} finally { Remove-Item $lock,$rl -ErrorAction SilentlyContinue }

