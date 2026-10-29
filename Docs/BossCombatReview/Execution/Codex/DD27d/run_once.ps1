$ErrorActionPreference='Stop'
$root='C:\UnrealProject\OneBossFight'
$r="$root\Docs\BossCombatReview\Execution\Codex\DD27d"
if(Test-Path "$r\command.json"){throw 'One-run command exists; STOP'}
python -I "$r\preflight.py"
if($LASTEXITCODE -ne 0){throw 'Preflight failed; STOP BEFORE LAUNCH'}
if(!(Test-Path "$r\preflight_verified.json")){throw 'Missing verification; STOP'}
$v=Get-Content "$r\preflight_verified.json" -Raw | ConvertFrom-Json
if(!$v.passed){throw 'Preflight not passed; STOP'}
if((Get-FileHash -Algorithm SHA256 "$r\pre_state.json").Hash.ToLower() -ne $v.pre_state_sha256){throw 'Pre-state drift; STOP'}
foreach($pin in $v.pins){if((Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $pin.path)).Hash.ToLower() -ne $pin.expected_sha256){throw 'Toolkit drift; STOP'}}
$busy=@(Get-Process | Where-Object {$_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$'})
if($busy.Count){throw 'Engine/compiler present; STOP'}
$engine='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$script='C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py'
$inputFile='C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json'
$argsList=@("$root\OneBossFight.uproject","-ExecutePythonScript=`"$script --input-json $inputFile --apply`"",'-unattended','-nullrhi','-nosound','-nosplash',"-abslog=$r\editor_raw.log")
@{executable=$engine;arguments=$argsList;save_flag=$false;attempt=1;release='C-312'} | ConvertTo-Json -Depth 5 | Set-Content "$r\command.json"
$env:PYTHONDONTWRITEBYTECODE='1'
$start=Get-Date
$p=Start-Process -FilePath $engine -ArgumentList $argsList -PassThru -Wait -NoNewWindow -RedirectStandardOutput "$r\stdout.log" -RedirectStandardError "$r\stderr.log"
$end=Get-Date
@{start=$start.ToString('o');end=$end.ToString('o');seconds=($end-$start).TotalSeconds;exit_code=$p.ExitCode;process_id=$p.Id} | ConvertTo-Json | Set-Content "$r\job_record.json"
Write-Output "DD27d_EXIT=$($p.ExitCode)"
exit $p.ExitCode
