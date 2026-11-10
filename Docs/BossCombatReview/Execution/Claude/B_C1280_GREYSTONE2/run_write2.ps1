# C-1280 Lead rerun 2 (2026-11-10): author_greystone_player.py --write after the create_retarget_wrapper out-param fix, then transient readback and BB-A15 materials probe. Engine lock held throughout.
$root='C:\UnrealProject\OneBossFight'; Set-Location $root
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running'; exit 2 }
$lock="$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"; $rl="$root\ENGINE_LOCK.json"
if (Test-Path $lock) { 'ABORT: engine lock present'; exit 2 }
$cmd='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$p="$root\Docs\BossCombatReview\Execution\Claude\B_C1280_GREYSTONE2"
$j=@{owner='C';purpose='C-1280 Greystone authoring rerun 2 + readback + materials probe';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID}|ConvertTo-Json; Set-Content $lock $j; Set-Content $rl $j
try {
  git status --porcelain -- Content | Out-File "$p\pre_content2.txt" -Encoding utf8
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\author_greystone_player.py" --write -unattended -nosound -nosplash -nullrhi "-abslog=$p\author2.log" | Out-Null
  "AUTHOR2 exit=$LASTEXITCODE" | Out-File "$p\author2_status.txt" -Encoding ascii
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\verify_greystone_wrapper_readback.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\readback2.log" | Out-Null
  "READBACK2 exit=$LASTEXITCODE" | Out-File "$p\readback2_status.txt" -Encoding ascii
  & $cmd "$root\OneBossFight.uproject" -run=pythonscript "-script=$root\Scripts\Editor\probe_greystone_materials_textures.py" -unattended -nosound -nosplash -nullrhi "-abslog=$p\materials2.log" | Out-Null
  "MATERIALS2 exit=$LASTEXITCODE" | Out-File "$p\materials2_status.txt" -Encoding ascii
  git status --porcelain -- Content | Out-File "$p\post_content2.txt" -Encoding utf8
} finally { Remove-Item $lock,$rl -ErrorAction SilentlyContinue }
'RUN_WRITE2_DONE'
