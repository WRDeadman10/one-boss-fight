$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root 'Scripts\Editor\author_sevarog_draft_cards.py'
$run = [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss')
$evidence = Join-Path $root ('Docs\BossCombatReview\Execution\Codex\C1280_X26_PHASE_ELIGIBILITY\Run_' + $run)
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$manifest = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1280 X26'; command_id='C1280.X26.dryrun-build-suite'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Sevarog card validator dry-run, Development build, pinned OneBossFight suite; no asset authoring or save' } | ConvertTo-Json
$created = [System.Collections.Generic.List[string]]::new()
$proc = $null
$oldDryRun = $env:SEVAROG_DRY_RUN
try {
    foreach ($lock in $locks) {
        $stream = [System.IO.File]::Open($lock,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[System.Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
        $created.Add($lock)
    }
    Set-Location -LiteralPath $root
    $buildLog = Join-Path $evidence 'build.log'
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 120; throw 'X26 Development editor build failed.' }

    $env:SEVAROG_DRY_RUN = '1'
    $editorLog = Join-Path $evidence 'dryrun.log'
    $editorStdout = Join-Path $evidence 'dryrun_stdout.log'
    $editorStderr = Join-Path $evidence 'dryrun_stderr.log'
    $editorArgs = @($project,"-ExecutePythonScript=$script",'-unattended','-nopause','-nosplash','-nosound','-NullRHI',"-abslog=$editorLog")
    $proc = Start-Process -FilePath (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') -ArgumentList $editorArgs -PassThru -Wait -WindowStyle Hidden -RedirectStandardOutput $editorStdout -RedirectStandardError $editorStderr
    $editorExit = $proc.ExitCode
    $editorPass = Select-String -Path $editorLog -Pattern '\[SevarogDraft\] DRY-RUN COMPLETE all validators passed, 0 saved' -Quiet -ErrorAction SilentlyContinue
    $noSave = -not (Select-String -Path $editorLog -Pattern '\[SevarogDraft\] SAVED ' -Quiet -ErrorAction SilentlyContinue)
    if ($editorExit -ne 0 -or !$editorPass -or !$noSave) { Get-Content $editorLog -Tail 120; throw 'X26 transient validator bridge dry-run failed or saved an asset.' }
    $proc = $null

    $suiteLog = Join-Path $evidence 'suite.log'
    $suiteStdout = Join-Path $evidence 'suite_stdout.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $project '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$manifest" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$suiteLog" *> $suiteStdout
    $suiteExit = $LASTEXITCODE
    $started = @(Select-String -Path $suiteLog -Pattern 'Test Started\. Name=' -ErrorAction SilentlyContinue)
    $passed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\}' -ErrorAction SilentlyContinue)
    $failed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{(Fail|Error)\}' -ErrorAction SilentlyContinue)
    $complete = Select-String -Path $suiteLog -Pattern 'TEST COMPLETE\. EXIT CODE: 0' -ErrorAction SilentlyContinue | Select-Object -Last 1
    $moveCard = Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\} Name=\{Rejections\} Path=\{OneBossFight\.Framework\.MoveCard\.Rejections\}' -Quiet -ErrorAction SilentlyContinue
    $moveModel = Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\} Name=\{Eligibility\} Path=\{OneBossFight\.Framework\.MoveModel\.Eligibility\}' -Quiet -ErrorAction SilentlyContinue
    $profile = Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\} Name=\{SelectorProfile\} Path=\{OneBossFight\.Framework\.Runtime\.SelectorProfile\}' -Quiet -ErrorAction SilentlyContinue
    $status = "BUILD_EXIT=$buildExit`nEDITOR_EXIT=$editorExit`nDRYRUN_PASS=$editorPass`nNO_SAVES=$noSave`nSUITE_EXIT=$suiteExit`nSTARTED=$($started.Count)`nPASSED=$($passed.Count)`nFAILED=$($failed.Count)`nCOMPLETE=$([bool]$complete)`nMOVE_CARD_PHASE_TEST=$moveCard`nMOVE_MODEL_PHASE_TEST=$moveModel`nPROFILE_PHASE_POOL_TEST=$profile`nDD27J=$manifest`nNO_ASSETS=1"
    Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status
    Write-Output $status
    if ($suiteExit -ne 0 -or !$complete -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -gt 0 -or !$moveCard -or !$moveModel -or !$profile) { Get-Content $suiteLog -Tail 120; throw 'X26 full suite failed, incomplete, or missed a phase-eligibility test.' }
} finally {
    if ($proc -and -not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    if ($null -eq $oldDryRun) { Remove-Item Env:\SEVAROG_DRY_RUN -ErrorAction SilentlyContinue } else { $env:SEVAROG_DRY_RUN = $oldDryRun }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'lock_result.txt')
}
