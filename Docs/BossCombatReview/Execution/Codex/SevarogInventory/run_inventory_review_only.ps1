$ErrorActionPreference='Stop'
$r=Join-Path $PSScriptRoot 'run_reviewed'
if(!(Test-Path -LiteralPath (Join-Path $r 'explicit_engine_release.json'))){throw 'STOP: C357 preparation only; engine release absent'}
$release=Get-Content (Join-Path $r 'explicit_engine_release.json') -Raw | ConvertFrom-Json
if($release.operator -ne 'Codex' -or $release.task -ne 'SevarogInventory' -or !$release.message_id){throw 'Wrong release scope'}
$root='C:\UnrealProject\OneBossFight'
$lock=Get-Content "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json" -Raw | ConvertFrom-Json
if($lock.agent -ne 'Codex' -or $lock.task -ne 'SevarogInventory'){throw 'Own exclusive lock required'}
if(Test-Path (Join-Path $r 'job.json')){throw 'Already attempted; STOP'}
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $r 'preflight.ps1')
if($LASTEXITCODE -ne 0){throw 'Preflight failed; no launch'}
. "$root\Docs\BossCombatReview\Execution\Codex\DD30Chronology\run_chronology_v2.ps1" -FunctionsOnly
$argsList=@("$root\OneBossFight.uproject",'-unattended','-nullrhi','-nosound','-nosplash',"-ExecutePythonScript=$PSScriptRoot\probe_sevarog_inventory.py","-abslog=$r\inventory_raw.log")
$result=Invoke-CachedHandleProcess -FilePath 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' -Arguments $argsList -TimeoutSeconds 180 -StdoutPath (Join-Path $r 'stdout.log') -StderrPath (Join-Path $r 'stderr.log')
$result | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $r 'job.json') -Encoding utf8
if($result.timed_out){exit 124}
if($null -eq $result.exit_code){exit 125}
exit $result.exit_code
