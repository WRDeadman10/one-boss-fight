$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor.exe'
$editorCmd = Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe'
$evidenceRoot = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1275A_TRANSIENT_NOTIFY_READBACK'
$runName = 'Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss')
$evidence = Join-Path $evidenceRoot $runName
$script = Join-Path $root 'Scripts\Editor\verify_greystone_wrapper_readback.py'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$manifest = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
if (Test-Path -LiteralPath $evidence) { throw "ABORT: evidence run already exists: $evidence" }
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1275a'; command_id='C1275A.locked-build-suite-transient-editor-readback'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Editor Development build, pinned full suite, and non-saving source-to-transient-wrapper readback; no package/assets/PIE' } | ConvertTo-Json
$created = [System.Collections.Generic.List[string]]::new()
$proc = $null
try {
    foreach ($lock in $locks) {
        $stream = [System.IO.File]::Open($lock,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[System.Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
        $created.Add($lock)
    }
    $buildLog = Join-Path $evidence 'build.log'
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 120; throw 'C-1275a Editor Development build failed.' }

    $suiteLog = Join-Path $evidence 'suite.log'
    $suiteStdout = Join-Path $evidence 'suite_stdout.log'
    & $editorCmd $project '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$manifest" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$suiteLog" *> $suiteStdout
    $suiteExit = $LASTEXITCODE
    $started = @(Select-String -Path $suiteLog -Pattern 'Test Started\. Name=' -ErrorAction SilentlyContinue)
    $passed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\}' -ErrorAction SilentlyContinue)
    $failed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{(Fail|Error)\}' -ErrorAction SilentlyContinue)
    $complete = Select-String -Path $suiteLog -Pattern 'TEST COMPLETE\. EXIT CODE: 0' -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($suiteExit -ne 0 -or !$complete -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -gt 0) {
        Get-Content $suiteLog -Tail 120
        throw 'C-1275a full suite failed or incomplete.'
    }

    $fso = New-Object -ComObject Scripting.FileSystemObject
    $short = $fso.GetFile($script).ShortPath.ToLower() -replace '\\','/'
    $editorLog = Join-Path $evidence 'transient_readback.log'
    $execCmd = '-ExecCmds="py ' + $short + '"'
    $proc = Start-Process -FilePath $editor -PassThru -WindowStyle Hidden -ArgumentList @($project,$execCmd,'-nosound','-nosplash','-unattended',"-abslog=$editorLog")
    $deadline = [DateTime]::UtcNow.AddMinutes(12)
    while ([DateTime]::UtcNow -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Seconds 2
        if ((Test-Path -LiteralPath $editorLog) -and (Select-String -Path $editorLog -Pattern '\[GreystoneWrapperReadback\] RESULT=PASS wrappers=4 transient=1 saves=0' -Quiet)) { break }
        if ((Test-Path -LiteralPath $editorLog) -and (Select-String -Path $editorLog -Pattern '\[GreystoneWrapperReadback\] RESULT=FAIL' -Quiet)) { break }
    }
    if (-not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    $editorText = if (Test-Path -LiteralPath $editorLog) { Get-Content -Raw -LiteralPath $editorLog } else { '' }
    $readbackPass = $editorText.Contains('[GreystoneWrapperReadback] RESULT=PASS wrappers=4 transient=1 saves=0')
    $readbackFail = $editorText.Contains('[GreystoneWrapperReadback] RESULT=FAIL')
    $status = "BUILD_EXIT=$buildExit`nSUITE_EXIT=$suiteExit`nSTARTED=$($started.Count)`nPASSED=$($passed.Count)`nFAILED=$($failed.Count)`nCOMPLETE=$([bool]$complete)`nDD27J=$manifest`nEDITOR_EXITED=$($proc.HasExited)`nTRANSIENT_READBACK_PASS=$readbackPass`nTRANSIENT_READBACK_FAIL=$readbackFail`nSAVED_ASSETS=0`nPIE=0"
    Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status
    Write-Output $status
    if (-not $proc.HasExited -or -not $readbackPass -or $readbackFail) { Get-Content $editorLog -Tail 160; throw 'C-1275a transient readback failed or incomplete.' }
} finally {
    if ($proc -and -not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'lock_result.txt')
}
