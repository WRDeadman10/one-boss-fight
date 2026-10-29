$ErrorActionPreference='Stop'
$r='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD27'
if (Test-Path "$r\job_record.json") { throw 'One-run record already exists' }
$busy=@(Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' })
if ($busy.Count) { throw 'STOP: engine/compiler present' }
$engine='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$script='C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py'
$inputFile='C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json'
$argsList=@('C:\UnrealProject\OneBossFight\OneBossFight.uproject',"-ExecutePythonScript=`"$script --input-json $inputFile --apply`"",'-unattended','-nullrhi','-nosound','-nosplash',"-abslog=$r\editor_raw.log")
@{executable=$engine;arguments=$argsList;save_flag=$false;attempt=1} | ConvertTo-Json -Depth 5 | Set-Content "$r\command.json"
$env:PYTHONDONTWRITEBYTECODE='1'
$start=Get-Date
$p=Start-Process -FilePath $engine -ArgumentList $argsList -PassThru -Wait -NoNewWindow -RedirectStandardOutput "$r\stdout.log" -RedirectStandardError "$r\stderr.log"
$end=Get-Date
@{start=$start.ToString('o');end=$end.ToString('o');seconds=($end-$start).TotalSeconds;exit_code=$p.ExitCode;process_id=$p.Id} | ConvertTo-Json | Set-Content "$r\job_record.json"
Write-Output "DD27_EXIT=$($p.ExitCode)"
exit $p.ExitCode
