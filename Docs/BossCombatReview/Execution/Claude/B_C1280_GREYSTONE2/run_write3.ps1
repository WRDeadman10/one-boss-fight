# C-1280 Lead rerun 3 (after the is_root fix) (2026-11-10): author_greystone_player.py --write after the create_retarget_wrapper out-param fix, then transient readback and BB-A15 materials probe. Engine lock held throughout.
$root='C:\UnrealProject\OneBossFight'; Set-Location $root
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running'; exit 2 }
$lock="$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"; $rl="$root\ENGINE_LOCK.json"
if (Test-Path $lock) { 'ABORT: engine lock present'; exit 2 }
$cmd='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$p="$root\Docs\BossCombatReview\Execution\Claude\B_C1280_GREYSTONE2"
$j=@{owner='C';purpose='C-1280 Greystone authoring rerun 3 (after the is_root fix) + readback + materials probe';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID}|ConvertTo-Json; Set-Content $lock $j; Set-Content $rl $j
try {
  git status --porcelain -- Content | Out-File "$p\pre_content3.txt" -Encoding utf8
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\author_greystone_player.py" --write -unattended -nosound -nosplash -nullrhi "-abslog=$p\author3.log" | Out-Null
  "AUTHOR3 exit=$LASTEXITCODE" | Out-File "$p\author3_status.txt" -Encoding ascii
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\verify_greystone_wrapper_readback.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\readback3.log" | Out-Null
  "READBACK3 exit=$LASTEXITCODE" | Out-File "$p\readback3_status.txt" -Encoding ascii
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\probe_greystone_materials_textures.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\materials3.log" | Out-Null
  "MATERIALS3 exit=$LASTEXITCODE" | Out-File "$p\materials3_status.txt" -Encoding ascii
  git status --porcelain -- Content | Out-File "$p\post_content3.txt" -Encoding utf8
} finally { Remove-Item $lock,$rl -ErrorAction SilentlyContinue }
'RUN_WRITE3_DONE'
