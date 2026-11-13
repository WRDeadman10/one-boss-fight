# B_GATE1_BQ (X-2406): C-1155 locked runner for Gate 1 of Queue BQ.
# Scope: Development editor build of OneBossFightEditor plus the complete `Automation RunTests OneBossFight` suite, pinned to
# DD27j. NOTHING else: no PIE, package, cook, asset authoring, map save or Python tool main.
# Copied from the latest run_build template (run_bf_x16_x20_locked_build.ps1) and hardened per X-2406:
#   - both ENGINE_LOCK.json files are acquired atomically (CreateNew temp + Move, which fails if the target exists);
#   - each created lock is read back and its exact owner token verified before any engine work;
#   - abort on any UnrealEditor* process, checked before AND after lock acquisition (closes the race window);
#   - unique evidence directory per invocation (UTC stamp + token prefix, refused if it already exists);
#   - status.txt is attempted on every post-evidence exit path; preflight refusals precede evidence creation;
#   - only locks whose on-disk owner token equals this invocation's token are removed; the receipt counts what was released.
# Launch only after the Lead approves (X-2406 lead review); do not run from a second editor.
param(
    [ValidateSet('Codex', 'Claude')][string]$Agent = 'Codex'
)
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$manifest = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
$token = [guid]::NewGuid().ToString('N')
$evidence = Join-Path $root ('Docs\BossCombatReview\Execution\' + $Agent + '\B_GATE1_BQ\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0, 8))
$originalLocation = Get-Location

function Test-UnrealRunning { return [bool](@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) }

# --- preflight (no lock taken yet, nothing to release) ---
if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor process is running (preflight)' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
if (Test-Path -LiteralPath $evidence) { throw "ABORT: evidence directory already exists: $evidence" }
New-Item -ItemType Directory -Path $evidence | Out-Null

$record = [ordered]@{
    agent = $Agent; party = $(if ($Agent -eq 'Codex') { 'X' } else { 'C' }); task = 'Queue BQ Gate 1 (X-2406)'
    command_id = 'B_GATE1_BQ.locked-build-suite'; owner_token = $token; pid = $PID
    start_utc = [DateTime]::UtcNow.ToString('o'); policy = 'C-1155'
    scope = 'Development editor build and DD27j-pinned complete OneBossFight suite; no PIE, package, assets or map saves'
} | ConvertTo-Json
$temps = [System.Collections.Generic.List[string]]::new()
$created = [System.Collections.Generic.List[string]]::new()
$stage = 'acquire'
$reason = ''
$buildExit = 'not-run'; $suiteExit = 'not-run'
$started = @(); $passed = @(); $failed = @(); $complete = $null
try {
    foreach ($lock in $locks) {
        $temp = $lock + '.' + $token + '.tmp'
        $stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $temps.Add($temp)   # track only after CreateNew proves this run created it
        try {
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($record + [Environment]::NewLine)
            $stream.Write($bytes, 0, $bytes.Length)
            $stream.Flush($true)
        } finally { $stream.Dispose() }
        [System.IO.File]::Move($temp, $lock)   # throws if another party created the lock meanwhile
        $created.Add($lock)
        $readBack = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
        if ($readBack.owner_token -ne $token) { throw "ABORT: lock owner token mismatch after acquisition: $lock" }
    }
    $stage = 'post-lock-check'
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor process appeared after lock acquisition' }

    $stage = 'build'
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor process appeared before build launch' }
    Set-Location -LiteralPath $root
    $buildLog = Join-Path $evidence 'build.log'
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 120; throw 'Gate 1 Development editor build failed.' }

    $stage = 'suite'
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor process appeared before suite launch' }
    $suiteLog = Join-Path $evidence 'suite.log'
    $suiteStdout = Join-Path $evidence 'suite_stdout.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $project '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$manifest" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$suiteLog" *> $suiteStdout
    $suiteExit = $LASTEXITCODE
    $started = @(Select-String -Path $suiteLog -Pattern 'Test Started\. Name=' -ErrorAction SilentlyContinue)
    $passed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\}' -ErrorAction SilentlyContinue)
    $failed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{(Fail|Error)\}' -ErrorAction SilentlyContinue)
    $complete = Select-String -Path $suiteLog -Pattern 'TEST COMPLETE\. EXIT CODE: 0' -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($suiteExit -ne 0 -or !$complete -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -gt 0) {
        Get-Content $suiteLog -Tail 120; throw 'Gate 1 full suite failed or incomplete.'
    }
    $stage = 'done'
} catch {
    $reason = $_.Exception.Message
    throw
} finally {
    $tempFailures = [System.Collections.Generic.List[string]]::new()
    foreach ($temp in $temps) {
        try { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }
        catch { $tempFailures.Add($temp + ' (' + $_.Exception.Message + ')') }
    }
    $released = 0
    $kept = [System.Collections.Generic.List[string]]::new()
    foreach ($lock in $created) {
        try {
            if (Test-Path -LiteralPath $lock) {
                $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force; $released++ }
                else { $kept.Add($lock + ' (owner token differs; not ours)') }
            }
        } catch { $kept.Add($lock + ' (ownership could not be verified or removed)') }
    }
    try { Set-Location -LiteralPath $originalLocation.Path } catch { $kept.Add('working directory restore failed: ' + $_.Exception.Message) }
    $result = if ($stage -eq 'done' -and $kept.Count -eq 0 -and $tempFailures.Count -eq 0) { 'PASS' } else { 'FAIL' }
    $status = @(
        "RESULT=$result", "STAGE=$stage", "REASON=$reason",
        "BUILD_EXIT=$buildExit", "SUITE_EXIT=$suiteExit",
        "STARTED=$($started.Count)", "PASSED=$($passed.Count)", "FAILED=$($failed.Count)", "COMPLETE=$([bool]$complete)",
        "DD27J=$manifest", "OWNER_TOKEN=$token", "LOCKS_CREATED=$($created.Count)", "LOCKS_RELEASED=$released",
        "LOCKS_KEPT=$($kept -join '; ')", "TEMPS_KEPT=$($tempFailures -join '; ')", "NO_PIE=1", "NO_PACKAGE=1", "NO_ASSETS=1"
    ) -join "`n"
    try {
        Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status
        Write-Output $status
    } catch { Write-Warning ('Could not write Gate 1 status receipt: ' + $_.Exception.Message) }
}
