param([string]$Filter,[string]$Tag)
$r='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD25\run_2026-10-29'
$log="$r\automation_${Tag}.log"
$s=Get-Date; $t0=$s.ToString('MM/dd/yyyy HH:mm:ss')
$p=Start-Process -FilePath 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' -ArgumentList @('C:\UnrealProject\OneBossFight\OneBossFight.uproject',"-ExecCmds=`"Automation RunTests $Filter; Quit`"",'-unattended','-nullrhi','-nosound','-nosplash',"-abslog=$log") -PassThru -Wait -NoNewWindow
$e=Get-Date
"start $t0 filter=$Filter`r`nend $($e.ToString('MM/dd/yyyy HH:mm:ss')) exit $($p.ExitCode) seconds $([int]($e-$s).TotalSeconds)" | Set-Content "$r\automation_${Tag}_job_record.txt"
exit $p.ExitCode
