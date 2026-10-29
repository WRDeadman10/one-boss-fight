$ErrorActionPreference='Stop'
$h='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD28'
$r="$h\run_2026-10-29"
if(Test-Path "$r\build_dd28_job_record.txt"){throw 'Build already attempted; STOP'}
python -I "$h\check_gate.py" before_build
if($LASTEXITCODE -ne 0){throw 'Fresh safety failed; NO BUILD'}
$s=Get-Date; $t0=$s.ToString('MM/dd/yyyy HH:mm:ss')
cmd /c "$r\build_dd28.cmd"; $ec=$LASTEXITCODE
$e=Get-Date
"start $t0`r`nend $($e.ToString('MM/dd/yyyy HH:mm:ss')) exit $ec seconds $([int]($e-$s).TotalSeconds)" | Set-Content "$r\build_dd28_job_record.txt"
exit $ec
