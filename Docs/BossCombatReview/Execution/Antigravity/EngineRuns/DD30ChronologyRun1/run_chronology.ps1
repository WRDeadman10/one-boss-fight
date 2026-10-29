$ErrorActionPreference = 'Stop'
$runDir = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\EngineRuns\DD30ChronologyRun1'
$jobFile = Join-Path $runDir 'chronology_job.json'
if (Test-Path $jobFile) { throw 'Already executed chronology run; STOP' }

# Pre-state capture
python -I (Join-Path $runDir 'capture_state.py') pre
if ($LASTEXITCODE -ne 0) { throw 'Pre-state failed; STOP BEFORE RUN' }

$editor = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$uproject = 'C:\UnrealProject\OneBossFight\OneBossFight.uproject'
$map = '/Game/OneBossFight/Levels/L_SevarogArena'
$driver = Join-Path $runDir 'dd30_chronology_pie.py'
$rawLog = Join-Path $runDir 'chronology_raw.log'

$launchArgs = @(
    $uproject,
    $map,
    '-nosound',
    '-nosplash',
    '-unattended',
    '-nullrhi',
    '-DD30Chronology',
    "-ExecutePythonScript=$driver",
    "-abslog=$rawLog"
)

$startUtc = (Get-Date).ToUniversalTime()
$s = Get-Date

Write-Host "Launching UnrealEditor (PID tracking active with 180s hard timeout)..."
$proc = Start-Process -FilePath $editor -ArgumentList $launchArgs -PassThru -NoNewWindow
$editorPid = $proc.Id
$procHandle = $proc.Handle
Write-Host "Launched UnrealEditor PID: $editorPid (Handle: $procHandle)"

$timeoutSeconds = 180
$killedDueToTimeout = $false
$completed = $proc.WaitForExit($timeoutSeconds * 1000)

if (-not $completed) {
    Write-Warning "Hard timeout ($timeoutSeconds s) exceeded! Stopping ONLY process ID $editorPid..."
    Stop-Process -Id $editorPid -Force -ErrorAction SilentlyContinue
    $killedDueToTimeout = $true
}

$e = Get-Date
$proc.Refresh()
$exitCode = if ($killedDueToTimeout) { -999 } else { $proc.ExitCode }
$outcome = if ($killedDueToTimeout) { 'TIMEOUT_KILL' } elseif ($exitCode -eq 0) { 'SUCCESS' } else { 'EXIT_NONZERO' }

$jobRecord = @{
    release = 'C-352'
    task = 'DD30ChronologyRun1'
    editor_pid = $editorPid
    start = $s.ToString('o')
    end = $e.ToString('o')
    seconds = ($e - $s).TotalSeconds
    exit_code = $exitCode
    outcome = $outcome
    killed_due_to_timeout = $killedDueToTimeout
    nullrhi = $true
}

$jobRecord | ConvertTo-Json -Depth 4 | Set-Content $jobFile
Write-Host "Chronology job completed with outcome: $outcome (exit: $exitCode, seconds: $(($e - $s).TotalSeconds))"
exit $exitCode
