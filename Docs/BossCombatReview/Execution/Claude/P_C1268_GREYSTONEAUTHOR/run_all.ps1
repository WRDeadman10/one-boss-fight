$root='C:\UnrealProject\OneBossFight'; Set-Location $root
"== trace" ; & powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Scripts\Editor\run_c1265b_clip_trace.ps1"
"trace exit=$LASTEXITCODE"
$lock="$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"; $rl="$root\ENGINE_LOCK.json"
if ((Test-Path $lock) -or (Test-Path $rl) -or (Get-Process UnrealEditor* -ErrorAction SilentlyContinue)) { 'busy after trace'; exit 2 }
$j=@{owner='C';purpose='C-1268 Greystone player authoring --write';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID}|ConvertTo-Json; Set-Content $lock $j; Set-Content $rl $j
try {
  $p="$root\Docs\BossCombatReview\Execution\Claude\P_C1268_GREYSTONEAUTHOR"
  git status --porcelain -- Content | Out-File "$p\pre_content.txt" -Encoding utf8
  & 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\author_greystone_player.py" --write -unattended -nosound -nosplash -nullrhi "-abslog=$p\author.log" | Out-Null
  "AUTHOR exit=$LASTEXITCODE" | Tee-Object "$p\status.txt"
  git status --porcelain -- Content | Out-File "$p\post_content.txt" -Encoding utf8
} finally { Remove-Item $lock,$rl -ErrorAction SilentlyContinue }
