$ErrorActionPreference='Stop'
$r='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD27j\run_C339'
if(Test-Path "$r\build_job.json"){throw 'Build already attempted; STOP'}
python -I "$r\capture_state.py" pre
if($LASTEXITCODE -ne 0){throw 'Pre-state failed; NO BUILD'}
python -I "$r\engine_lock.py" acquire
if($LASTEXITCODE -ne 0){throw 'Exclusive lock failed; NO BUILD'}
$s=Get-Date
cmd /c "$r\build_once.cmd"
$ec=$LASTEXITCODE;$e=Get-Date
@{release='C-339';start=$s.ToString('o');end=$e.ToString('o');seconds=($e-$s).TotalSeconds;exit_code=$ec} | ConvertTo-Json | Set-Content "$r\build_job.json"
exit $ec
