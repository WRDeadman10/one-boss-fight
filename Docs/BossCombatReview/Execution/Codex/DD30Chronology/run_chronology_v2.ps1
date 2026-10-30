param([switch]$FunctionsOnly, [string]$RunDirectory = (Join-Path $PSScriptRoot 'run_chronology_v2'))
$ErrorActionPreference='Stop'
function Invoke-CachedHandleProcess {
    param([string]$FilePath,[string[]]$Arguments,[int]$TimeoutSeconds,[string]$StdoutPath,[string]$StderrPath)
    $started=Get-Date
    $proc=Start-Process -FilePath $FilePath -ArgumentList $Arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
    $cachedHandle=$proc.Handle # MUST cache immediately, before WaitForExit or ExitCode reads.
    $ownedProcessId=$proc.Id
    $finished=$proc.WaitForExit($TimeoutSeconds * 1000)
    $timeoutKill=$false
    if(!$finished){
        $timeoutKill=$true
        if(!$proc.HasExited){Stop-Process -Id $ownedProcessId -Force -ErrorAction Stop}
        $null=$proc.WaitForExit(5000)
    }
    if($finished){$proc.WaitForExit()} # flush redirected asynchronous streams
    $proc.Refresh()
    $exitCode=if($finished){$proc.ExitCode}else{$null}
    $outcome=if($timeoutKill){'TIMEOUT_KILL'}elseif($null -eq $exitCode){'EXIT_CODE_UNKNOWN'}elseif($exitCode -eq 0){'SUCCESS'}else{'EXIT_NONZERO'}
    [pscustomobject]@{process_id=$ownedProcessId;cached_handle=$cachedHandle.ToInt64();exit_code=$exitCode;outcome=$outcome;timed_out=$timeoutKill;seconds=((Get-Date)-$started).TotalSeconds;start=$started.ToString('o');end=(Get-Date).ToString('o')}
}
if($FunctionsOnly){return}
# C355 authorizes implementation/offline fake tests ONLY. Engine path is gated, not released.
$releaseFile=Join-Path $RunDirectory 'explicit_engine_release.json'
if(!(Test-Path -LiteralPath $releaseFile)){throw 'STOP: wrapper staged only; no engine run release'}
$release=Get-Content -LiteralPath $releaseFile -Raw | ConvertFrom-Json
if(!$release.message_id -or $release.operator -ne 'Codex' -or $release.task -ne 'DD30ChronologyV2'){throw 'STOP: wrong release scope'}
$root='C:\UnrealProject\OneBossFight'
$mail=Get-Content -LiteralPath (Join-Path $root 'Documentation\TEAM_MAILBOX.md') -Raw
if(!$mail.Contains("### [$($release.message_id)] Claude ->")){throw 'STOP: no actual lead release message'}
$lock=Get-Content -LiteralPath (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json') -Raw | ConvertFrom-Json
if($lock.agent -ne 'Codex' -or $lock.task -ne 'DD30ChronologyV2'){throw 'STOP: no owned exclusive lane lock'}
$job=Join-Path $RunDirectory 'chronology_job_v2.json'
if(Test-Path -LiteralPath $job){throw 'STOP: attempt already recorded'}
$preflight=Join-Path $RunDirectory 'preflight.ps1'
if(!(Test-Path -LiteralPath $preflight)){throw 'STOP: missing reviewed fresh preflight'}
& powershell -NoProfile -ExecutionPolicy Bypass -File $preflight
if($LASTEXITCODE -ne 0){throw 'STOP: preflight failed'}
$command=Get-Content -LiteralPath (Join-Path $RunDirectory 'reviewed_command.json') -Raw | ConvertFrom-Json
# The next lead release must review launch mode (ExecCmds vs ExecutePythonScript); no blind inherited arguments.
$result=Invoke-CachedHandleProcess -FilePath $command.executable -Arguments $command.arguments -TimeoutSeconds 180 -StdoutPath (Join-Path $RunDirectory 'stdout_v2.log') -StderrPath (Join-Path $RunDirectory 'stderr_v2.log')
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $job -Encoding utf8
if($result.outcome -eq 'TIMEOUT_KILL'){exit 124}
if($null -eq $result.exit_code){exit 125}
exit $result.exit_code
