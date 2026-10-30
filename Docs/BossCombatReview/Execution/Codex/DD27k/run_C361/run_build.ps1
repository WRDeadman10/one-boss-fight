$ErrorActionPreference='Stop'
$r='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD27k\run_C361'
if(Test-Path "$r\build_job.json"){throw 'Already built; STOP'}
python -I "$r\capture_state.py" pre
if($LASTEXITCODE -ne 0){throw 'Pre-state failed; STOP BEFORE BUILD'}
$s=Get-Date
cmd /c "$r\build_once.cmd"
$ec=$LASTEXITCODE;$e=Get-Date
@{release='C-361';start=$s.ToString('o');end=$e.ToString('o');seconds=($e-$s).TotalSeconds;exit_code=$ec} | ConvertTo-Json | Set-Content "$r\build_job.json"
exit $ec
