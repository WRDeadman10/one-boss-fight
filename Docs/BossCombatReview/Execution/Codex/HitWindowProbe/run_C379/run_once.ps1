$ErrorActionPreference='Stop'
$root='C:\UnrealProject\OneBossFight'
$r="$root\Docs\BossCombatReview\Execution\Codex\HitWindowProbe\run_C379"
if(Test-Path "$r\command.json"){throw 'Already attempted; STOP'}
$pins=Get-Content "$r\probe_dependency_pins.json" -Raw | ConvertFrom-Json
if((Get-FileHash -LiteralPath (Join-Path $root $pins.receipt_path) -Algorithm SHA256).Hash.ToLower() -ne $pins.receipt_sha256){throw 'Receipt drift; STOP'}
foreach($p in $pins.pins){if((Get-FileHash -LiteralPath (Join-Path $root $p.path) -Algorithm SHA256).Hash.ToLower() -ne $p.sha256){throw 'Dependency drift; STOP'}}
python -I "$r\capture_state.py" pre
if($LASTEXITCODE -ne 0){throw 'Prestate failure; STOP'}
$base=Get-Content "$r\baseline.json" -Raw | ConvertFrom-Json
foreach($p in $base.binary_before_build.PSObject.Properties){if((Get-FileHash -LiteralPath (Join-Path $root $p.Name) -Algorithm SHA256).Hash.ToLower() -ne $p.Value){throw 'Binary drift; STOP'}}
$lock=Get-Content "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json" -Raw | ConvertFrom-Json
if($lock.agent -ne 'Codex' -or $lock.task -ne 'C-379/HitWindowProbe'){throw 'Not own lock; STOP'}
. "$root\Docs\BossCombatReview\Execution\Codex\DD30Chronology\run_chronology_v2.ps1" -FunctionsOnly
$engine='C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$argsList=@("$root\OneBossFight.uproject","-ExecutePythonScript=`"$r\run_probe_observed.py`"",'-unattended','-nullrhi','-nosound','-nosplash',"-abslog=$r\editor_raw.log")
@{executable=$engine;arguments=$argsList;release='C-379';attempt=1;wrapper_sha256=(Get-FileHash "$r\run_probe_observed.py" -Algorithm SHA256).Hash.ToLower()} | ConvertTo-Json -Depth 4 | Set-Content "$r\command.json"
$env:PYTHONDONTWRITEBYTECODE='1'
$result=Invoke-CachedHandleProcess -FilePath $engine -Arguments $argsList -TimeoutSeconds 180 -StdoutPath "$r\stdout.log" -StderrPath "$r\stderr.log"
$result | ConvertTo-Json -Depth 4 | Set-Content "$r\job_record.json" -Encoding utf8
if($result.timed_out){exit 124}
if($null -eq $result.exit_code){exit 125}
exit $result.exit_code
