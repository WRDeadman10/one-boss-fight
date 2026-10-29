$ErrorActionPreference='Stop'
$r='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD27j\run_C339'
$root='C:\UnrealProject\OneBossFight'
if(Test-Path "$r\focused_command.json"){throw 'Focused test already attempted; STOP'}
$build=Get-Content "$r\build_job.json" -Raw | ConvertFrom-Json
if($build.exit_code -ne 0){throw 'Build failed; NO TEST'}
$identity=Get-Content "$r\manifest_identity.json" -Raw | ConvertFrom-Json
$hash=(Get-FileHash -LiteralPath (Join-Path $root $identity.path) -Algorithm SHA256).Hash.ToLower()
if($hash -ne $identity.sha256){throw 'Manifest file drift; STOP'}
$lock=Get-Content "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json" -Raw | ConvertFrom-Json
if($lock.agent -ne 'Codex' -or $lock.task -ne 'C-339/DD27j'){throw 'Not own lock; STOP'}
$busy=@(Get-Process | Where-Object {$_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$'})
if($busy.Count){throw 'Engine/compiler already present; STOP'}
$engine='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$argsList=@("$root\OneBossFight.uproject",'-ExecCmds="Automation RunTests OneBossFight.Binding.AuthoredDraft; Quit"',"-DD27jManifestHash=$hash",'-unattended','-nullrhi','-nosound','-nosplash',"-abslog=$r\focused_raw.log")
@{executable=$engine;arguments=$argsList;release='C-339';attempt=1;manifest_file=$identity.path;manifest_sha256=$hash} | ConvertTo-Json -Depth 5 | Set-Content "$r\focused_command.json"
$s=Get-Date
$p=Start-Process -FilePath $engine -ArgumentList $argsList -PassThru -Wait -NoNewWindow -RedirectStandardOutput "$r\focused_stdout.log" -RedirectStandardError "$r\focused_stderr.log"
$e=Get-Date
@{start=$s.ToString('o');end=$e.ToString('o');seconds=($e-$s).TotalSeconds;exit_code=$p.ExitCode;process_id=$p.Id} | ConvertTo-Json | Set-Content "$r\focused_job.json"
exit $p.ExitCode
