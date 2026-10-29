$r='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD26\run_2026-10-29'
$s=Get-Date; $t0=$s.ToString('MM/dd/yyyy HH:mm:ss')
cmd /c "$r\build_dd26.cmd"; $ec=$LASTEXITCODE
$e=Get-Date
"start $t0`r`nend $($e.ToString('MM/dd/yyyy HH:mm:ss')) exit $ec seconds $([int]($e-$s).TotalSeconds)" | Set-Content "$r\build_dd26_job_record.txt"
exit $ec
