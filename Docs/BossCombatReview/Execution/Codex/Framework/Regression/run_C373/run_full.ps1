$ErrorActionPreference='Stop'
$r='C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\Framework\Regression\run_C373'
$root='C:\UnrealProject\OneBossFight'
if(Test-Path "$r\focused_command.json"){throw 'Focused already attempted; STOP'}
$identity=Get-Content "$r\manifest_identity.json" -Raw | ConvertFrom-Json
$hash=(Get-FileHash -LiteralPath (Join-Path $root $identity.path) -Algorithm SHA256).Hash.ToLower()
if($hash -ne $identity.sha256){throw 'Manifest drift; STOP'}
$lock=Get-Content "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json" -Raw | ConvertFrom-Json
if($lock.agent -ne 'Codex' -or $lock.task -ne 'C-373/FullRegression'){throw 'Not own lock; STOP'}
$busy=@(Get-Process | Where-Object {$_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$'})
if($busy.Count){throw 'Engine/compiler already present; STOP'}
. "$root\Docs\BossCombatReview\Execution\Codex\DD30Chronology\run_chronology_v2.ps1" -FunctionsOnly
$engine='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$argsList=@("$root\OneBossFight.uproject",'-ExecCmds="Automation RunTests OneBossFight; Quit"',"-DD27jManifestHash=$hash",'-unattended','-nullrhi','-nosound','-nosplash',"-abslog=$r\focused_raw.log")
@{executable=$engine;arguments=$argsList;release='C-373';attempt=1;manifest_path=$identity.path;manifest_sha256=$hash} | ConvertTo-Json -Depth 4 | Set-Content "$r\focused_command.json"
$result=Invoke-CachedHandleProcess -FilePath $engine -Arguments $argsList -TimeoutSeconds 180 -StdoutPath "$r\focused_stdout.log" -StderrPath "$r\focused_stderr.log"
$result | ConvertTo-Json -Depth 4 | Set-Content "$r\focused_job.json" -Encoding utf8
if($result.timed_out){exit 124}
if($null -eq $result.exit_code){exit 125}
exit $result.exit_code
