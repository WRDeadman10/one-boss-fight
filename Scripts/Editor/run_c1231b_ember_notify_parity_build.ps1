$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$uproject = Join-Path $root 'OneBossFight.uproject'
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1231B_EMBER_NOTIFY_PARITY'
$manifestHash = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
$locks = @(
    (Join-Path $root 'ENGINE_LOCK.json'),
    (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json')
)

if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { throw 'UnrealEditor process exists; aborting per C-1155.' }
foreach ($path in $locks) {
    if (Test-Path -LiteralPath $path) { throw "Lock exists: $path; aborting per C-1155." }
}

New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$created = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($path in $locks) {
        $record = @{
            owner = 'Codex'
            task = 'C-1231b'
            command_id = $token
            pid = $PID
            purpose = 'Ember notify parity driver Development build and full Automation suite; no PIE run'
            start_utc = [DateTime]::UtcNow.ToString('o')
        } | ConvertTo-Json
        New-Item -Path $path -ItemType File -Value $record -ErrorAction Stop | Out-Null
        $created.Add($path)
    }

    $buildLog = Join-Path $evidence 'build.log'
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$uproject" -WaitMutex *> $buildLog
    $buildExit = $LASTEXITCODE
    "BUILD_EXIT=$buildExit" | Set-Content (Join-Path $evidence 'build_result.txt')
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 60; throw "Development build failed: $buildExit" }

    if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { throw 'Unexpected UnrealEditor process before strict audit; aborting.' }
    $auditLog = Join-Path $evidence 'strict_audit.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $uproject '-run=EmberMontageTimingAudit' '-Strict' "-DD27jManifestHash=$manifestHash" -unattended -nosound -nosplash -nullrhi "-abslog=$auditLog" *> (Join-Path $evidence 'strict_audit_console.log')
    $auditExit = $LASTEXITCODE
    "STRICT_AUDIT_EXIT=$auditExit" | Set-Content (Join-Path $evidence 'strict_audit_result.txt')
    if ($auditExit -ne 0) { Get-Content $auditLog -Tail 100; throw "Strict Ember montage timing audit exited $auditExit" }

    if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { throw 'Unexpected UnrealEditor process before full suite; aborting.' }
    $suiteLog = Join-Path $evidence 'suite.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $uproject '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$manifestHash" -unattended -nosound -nosplash -nullrhi "-abslog=$suiteLog" *> (Join-Path $evidence 'suite_console.log')
    $suiteExit = $LASTEXITCODE
    $started = @(Select-String -Path $suiteLog -Pattern 'Test Started\. Name=')
    $passed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{Success\}')
    $failed = @(Select-String -Path $suiteLog -Pattern 'Test Completed\. Result=\{(Fail|Error)\}')
    $complete = Select-String -Path $suiteLog -Pattern 'TEST COMPLETE\. EXIT CODE: 0' | Select-Object -Last 1
    "SUITE_EXIT=$suiteExit`nSTARTED=$($started.Count)`nPASSED=$($passed.Count)`nFAILED=$($failed.Count)`nCOMPLETE=$([bool]$complete)" | Set-Content (Join-Path $evidence 'suite_result.txt')
    if ($suiteExit -ne 0 -or !$complete -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -gt 0) {
        Get-Content $suiteLog -Tail 100
        throw 'Full Automation suite failed or incomplete.'
    }

    Get-Content (Join-Path $evidence 'build_result.txt')
    Select-String -Path $auditLog -Pattern '\[EmberTimingAudit\] (SUMMARY|MISSING|MISMATCH|DUPLICATE|INVALID|UNTRACKED)'
    Get-Content (Join-Path $evidence 'suite_result.txt')
}
finally {
    foreach ($path in $created) { Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue }
    "LOCKS_RELEASED=$($created.Count)" | Set-Content (Join-Path $evidence 'lock_result.txt')
}
