$ErrorActionPreference='Stop'
$root='C:\UnrealProject\OneBossFight'
$r="$root\Docs\BossCombatReview\Execution\Codex\DD27i"
if(Test-Path "$r\command.json"){throw 'DD27i already attempted; STOP'}
python -I "$r\preflight.py"
if($LASTEXITCODE -ne 0){throw 'Preflight failed; STOP BEFORE LAUNCH'}
if(!(Test-Path "$r\preflight_verified.json")){throw 'Missing preflight; STOP'}
$v=Get-Content "$r\preflight_verified.json" -Raw | ConvertFrom-Json
if(!$v.passed){throw 'Preflight not passed; STOP'}
if((Get-FileHash -LiteralPath "$r\pre_state.json" -Algorithm SHA256).Hash.ToLower() -ne $v.pre_state_sha256){throw 'Pre-state drift; STOP'}
foreach($pin in $v.pins){if((Get-FileHash -LiteralPath (Join-Path $root $pin.path) -Algorithm SHA256).Hash.ToLower() -ne $pin.expected_sha256){throw 'Toolkit drift; STOP'}}
foreach($property in $v.binary.PSObject.Properties){if((Get-FileHash -LiteralPath (Join-Path $root $property.Name) -Algorithm SHA256).Hash.ToLower() -ne $property.Value){throw 'Binary drift; STOP'}}
$busy=@(Get-Process | Where-Object {$_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$'})
if($busy.Count){throw 'Engine/compiler present; STOP'}
python -I "$r\engine_lock.py" acquire
if($LASTEXITCODE -ne 0){throw 'C321 engine lock unavailable; STOP BEFORE LAUNCH'}
$engine='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$script='C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py'
$inputFile='C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json'
$argsList=@("$root\OneBossFight.uproject","-ExecutePythonScript=`"$script --input-json $inputFile --apply --save`"",'-unattended','-nullrhi','-nosound','-nosplash',"-abslog=$r\editor_raw.log")
@{executable=$engine;arguments=$argsList;release=$v.release;attempt=1;save_flag=$true} | ConvertTo-Json -Depth 5 | Set-Content "$r\command.json"
$env:PYTHONDONTWRITEBYTECODE='1'
$start=Get-Date
$p=Start-Process -FilePath $engine -ArgumentList $argsList -PassThru -Wait -NoNewWindow -RedirectStandardOutput "$r\stdout.log" -RedirectStandardError "$r\stderr.log"
$end=Get-Date
@{start=$start.ToString('o');end=$end.ToString('o');seconds=($end-$start).TotalSeconds;exit_code=$p.ExitCode;process_id=$p.Id} | ConvertTo-Json | Set-Content "$r\job_record.json"
Write-Output "DD27i_EXIT=$($p.ExitCode)"
exit $p.ExitCode
