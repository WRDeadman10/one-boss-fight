$ErrorActionPreference='Stop'
$r='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD27c'
if (Test-Path "$r\command.json") { throw 'One-run command already recorded; STOP' }
python -I "$r\preflight.py"
if ($LASTEXITCODE -ne 0) { throw 'Preflight failed; STOP BEFORE LAUNCH' }
if (!(Test-Path "$r\preflight_verified.json")) { throw 'Missing verified fresh pre-state; STOP' }
$verified=Get-Content "$r\preflight_verified.json" -Raw | ConvertFrom-Json
if (!$verified.passed) { throw 'Preflight not passed; STOP' }
$freshHash=(Get-FileHash -Algorithm SHA256 -LiteralPath "$r\pre_state.json").Hash.ToLower()
if ($freshHash -ne $verified.pre_state_sha256) { throw 'Pre-state pin mismatch; STOP' }
$script='C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/probe_unreal_api.py'
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $script).Hash.ToLower() -ne $verified.probe_expected_sha256) { throw 'Probe drift; STOP' }
$busy=@(Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' })
if ($busy.Count) { throw 'STOP: engine/compiler present' }
$engine='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$argsList=@('C:\UnrealProject\OneBossFight\OneBossFight.uproject',"-ExecutePythonScript=`"$script --instances`"",'-unattended','-nullrhi','-nosound','-nosplash',"-abslog=$r\editor_raw.log")
@{executable=$engine;arguments=$argsList;save_flag=$false;attempt=1;release='C-307'} | ConvertTo-Json -Depth 5 | Set-Content "$r\command.json"
$env:PYTHONDONTWRITEBYTECODE='1'
$start=Get-Date
$p=Start-Process -FilePath $engine -ArgumentList $argsList -PassThru -Wait -NoNewWindow -RedirectStandardOutput "$r\stdout.log" -RedirectStandardError "$r\stderr.log"
$end=Get-Date
@{start=$start.ToString('o');end=$end.ToString('o');seconds=($end-$start).TotalSeconds;exit_code=$p.ExitCode;process_id=$p.Id} | ConvertTo-Json | Set-Content "$r\job_record.json"
Write-Output "DD27c_EXIT=$($p.ExitCode)"
exit $p.ExitCode
