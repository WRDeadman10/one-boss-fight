$root='C:\UnrealProject\OneBossFight'; Set-Location $root
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\Docs\BossCombatReview\Execution\Claude\B_C1280_GREYSTONE2\run_build297.ps1"
$st = Get-Content "$root\Docs\BossCombatReview\Execution\Claude\B_C1280_GREYSTONE2\status.txt" -Raw
if ($st -notmatch 'BUILD exit 0' -or $st -notmatch 'fail=0') { "STOP: $st"; exit 1 }
$lock="$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"; $rl="$root\ENGINE_LOCK.json"
$cmd='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$p="$root\Docs\BossCombatReview\Execution\Claude\B_C1280_GREYSTONE2"
$j=@{owner='C';purpose='C-1280 Greystone authoring + readback + materials probe';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID}|ConvertTo-Json; Set-Content $lock $j; Set-Content $rl $j
try {
  git status --porcelain -- Content | Out-File "$p\pre_content.txt" -Encoding utf8
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\author_greystone_player.py" --write -unattended -nosound -nosplash -nullrhi "-abslog=$p\author.log" | Out-Null
  "AUTHOR exit=$LASTEXITCODE" | Tee-Object "$p\author_status.txt"
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\verify_greystone_wrapper_readback.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\readback.log" | Out-Null
  "READBACK exit=$LASTEXITCODE" | Tee-Object "$p\readback_status.txt"
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\probe_greystone_materials_textures.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\materials.log" | Out-Null
  "MATERIALS exit=$LASTEXITCODE" | Tee-Object "$p\materials_status.txt"
  git status --porcelain -- Content | Out-File "$p\post_content.txt" -Encoding utf8
} finally { Remove-Item $lock,$rl -ErrorAction SilentlyContinue }

