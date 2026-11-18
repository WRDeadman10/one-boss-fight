param(
    [Parameter(Mandatory = $true)][string]$LeadApprovalReceipt,
    [ValidateSet('Smoke', 'Full')][string]$Mode = 'Smoke',
    [ValidateRange(1, 86400)][int]$FullTimeoutSeconds = 3600
)
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$editor = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$driver = Join-Path $root 'Scripts\Editor\pie_sevarog_arena_route_acceptance.py'
$runner = Join-Path $root 'Scripts\Editor\run_sevarog_arena_route_acceptance.ps1'
$config = Join-Path $root 'Config\DefaultGame.ini'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\SevarogArenaRoute\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0, 8))
$log = Join-Path $run 'editor.log'
$receipt = Join-Path $run 'acceptance.json'
$status = Join-Path $run 'status.txt'
$configBackup = Join-Path $run 'DefaultGame.ini.original'
$createdLocks = [System.Collections.Generic.List[string]]::new()
$createdTemps = [System.Collections.Generic.List[string]]::new()
$editorProcess = $null
$configChanged = $false
$stage = 'preflight'
$reason = ''
$result = 'PREPARED'
$sourceCpp = Join-Path $root 'Source\OneBossFight\Player\RPGPlayerMovesSubsystem.cpp'
$sourceH = Join-Path $root 'Source\OneBossFight\Player\RPGPlayerMovesSubsystem.h'
$bossCpp = Join-Path $root 'Source\OneBossFight\Boss\RPGFrameworkBossCharacter.cpp'
$bossH = Join-Path $root 'Source\OneBossFight\Boss\RPGFrameworkBossCharacter.h'
$blueprintCallH = Join-Path $root 'Source\OneBossFight\Pack\RPGBlueprintCall.h'
$frameworkProfileCpp = Join-Path $root 'Source\OneBossFight\Player\RPGBossFrameworkProfile.cpp'
$frameworkRuntimeTestsCpp = Join-Path $root 'Source\OneBossFight\Tests\RPGFrameworkRuntimeTests.cpp'
$routeDefinition = '/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter.DA_Sevarog_Framework_Encounter'

function Test-EditorRunning {
    return [bool](@(Get-Process -Name UnrealEditor, UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count -gt 0)
}
function Get-RuntimeHashes {
    return @{
        subsystem_cpp = (Get-FileHash -LiteralPath $sourceCpp -Algorithm SHA256).Hash
        subsystem_h   = (Get-FileHash -LiteralPath $sourceH -Algorithm SHA256).Hash
        boss_cpp      = (Get-FileHash -LiteralPath $bossCpp -Algorithm SHA256).Hash
        boss_h        = (Get-FileHash -LiteralPath $bossH -Algorithm SHA256).Hash
        blueprint_call_h = (Get-FileHash -LiteralPath $blueprintCallH -Algorithm SHA256).Hash
        framework_profile_cpp = (Get-FileHash -LiteralPath $frameworkProfileCpp -Algorithm SHA256).Hash
        framework_runtime_tests_cpp = (Get-FileHash -LiteralPath $frameworkRuntimeTestsCpp -Algorithm SHA256).Hash
        acceptance_runner = (Get-FileHash -LiteralPath $runner -Algorithm SHA256).Hash
        acceptance_driver = (Get-FileHash -LiteralPath $driver -Algorithm SHA256).Hash
    }
}
function Write-Status([string]$Text) {
    if (Test-Path -LiteralPath $run -PathType Container) {
        [IO.File]::WriteAllText($status, $Text + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    }
}
function Acquire-Lock([string]$Path) {
    $temp = $Path + '.' + $token + '.tmp'
    $createdTemps.Add($temp)
    $record = [ordered]@{
        agent = 'Codex'; party = 'X'; task = 'C-1619 Sevarog route PIE acceptance'; command_id = 'run_sevarog_arena_route_acceptance'
        owner_token = $token; pid = $PID; start_utc = [DateTime]::UtcNow.ToString('o'); policy = 'C-1155'
        scope = "L_SevarogArena route PIE acceptance ($Mode); temporary route switch; no build, package, map or asset save"
    }
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes(($record | ConvertTo-Json -Depth 5) + [Environment]::NewLine)
    $stream = [IO.File]::Open($temp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    try { [IO.File]::Move($temp, $Path) }
    catch { throw "ABORT: atomic lock acquisition failed: $Path" }
    $createdTemps.Remove($temp)
    $createdLocks.Add($Path)
    $readBack = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ($readBack.owner_token -cne $token -or $readBack.policy -ne 'C-1155') { throw "ABORT: lock readback mismatch: $Path" }
}
function Set-RouteConfig([string]$Text, [string]$NewLine) {
    $section = '[/Script/OneBossFight.RPGPlayerMovesSubsystem]'
    $start = $Text.IndexOf($section, [StringComparison]::Ordinal)
    if ($start -lt 0) { throw 'ABORT: RPGPlayerMovesSubsystem config section is missing' }
    $bodyStart = $start + $section.Length
    $next = [regex]::Match($Text.Substring($bodyStart), '(?m)^\s*\[.+\]\s*$')
    $bodyEnd = if ($next.Success) { $bodyStart + $next.Index } else { $Text.Length }
    $body = $Text.Substring($bodyStart, $bodyEnd - $bodyStart)
    $body = [regex]::Replace($body, '(?m)^\s*bEnableSevarogFrameworkArenaRoute\s*=.*(?:\r?\n|$)', '')
    $body = [regex]::Replace($body, '(?m)^\s*SevarogFrameworkRouteDefinition\s*=.*(?:\r?\n|$)', '')
    $body = $body.TrimEnd([char[]]"`r`n") + $NewLine + 'bEnableSevarogFrameworkArenaRoute=True' + $NewLine +
        'SevarogFrameworkRouteDefinition=' + $routeDefinition + $NewLine
    return $Text.Substring(0, $bodyStart) + $body + $Text.Substring($bodyEnd)
}

try {
    if (Test-EditorRunning) { throw 'ABORT: close UnrealEditor before acquiring C-1155 locks' }
    foreach ($path in @($editor, $project, $driver, $runner, $config, $sourceCpp, $sourceH, $bossCpp, $bossH, $blueprintCallH, $frameworkProfileCpp, $frameworkRuntimeTestsCpp, $LeadApprovalReceipt)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "ABORT: required file missing: $path" }
    }
    $approval = Get-Content -Raw -LiteralPath $LeadApprovalReceipt | ConvertFrom-Json
    if ($approval.task -ne 'C-1619 route acceptance' -or $approval.lead -notin @('Claude','Codex') -or $approval.approved -ne $true -or $approval.source_build_exit -ne 0 -or $approval.suite_result -ne 'PASS') {
        throw 'ABORT: current lead approval receipt must authorize this task and bind a passing source build/suite'
    }
    $initialHashes = Get-RuntimeHashes
    if ($approval.subsystem_cpp_sha256 -cne $initialHashes.subsystem_cpp -or
        $approval.subsystem_h_sha256 -cne $initialHashes.subsystem_h -or
        $approval.boss_cpp_sha256 -cne $initialHashes.boss_cpp -or
        $approval.boss_h_sha256 -cne $initialHashes.boss_h -or
        $approval.blueprint_call_h_sha256 -cne $initialHashes.blueprint_call_h -or
        $approval.framework_profile_cpp_sha256 -cne $initialHashes.framework_profile_cpp -or
        $approval.framework_runtime_tests_cpp_sha256 -cne $initialHashes.framework_runtime_tests_cpp -or
        $approval.acceptance_runner_sha256 -cne $initialHashes.acceptance_runner -or
        $approval.acceptance_driver_sha256 -cne $initialHashes.acceptance_driver) {
        throw 'ABORT: approved subsystem and boss character source hashes do not match the current files'
    }
    if (Test-Path -LiteralPath $run) { throw "ABORT: run directory already exists: $run" }
    New-Item -ItemType Directory -Path $run | Out-Null
    foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: existing lock $lock" } }
    foreach ($lock in $locks) { Acquire-Lock $lock }
    if (Test-EditorRunning) { throw 'ABORT: UnrealEditor appeared during lock acquisition' }
    $lockedHashes = Get-RuntimeHashes
    if ($approval.subsystem_cpp_sha256 -cne $lockedHashes.subsystem_cpp -or
        $approval.subsystem_h_sha256 -cne $lockedHashes.subsystem_h -or
        $approval.boss_cpp_sha256 -cne $lockedHashes.boss_cpp -or
        $approval.boss_h_sha256 -cne $lockedHashes.boss_h -or
        $approval.blueprint_call_h_sha256 -cne $lockedHashes.blueprint_call_h -or
        $approval.framework_profile_cpp_sha256 -cne $lockedHashes.framework_profile_cpp -or
        $approval.framework_runtime_tests_cpp_sha256 -cne $lockedHashes.framework_runtime_tests_cpp -or
        $approval.acceptance_runner_sha256 -cne $lockedHashes.acceptance_runner -or
        $approval.acceptance_driver_sha256 -cne $lockedHashes.acceptance_driver) {
        throw 'ABORT: runtime sources changed after lock acquisition'
    }

    $originalConfigHash = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
    $sourceBytes = [IO.File]::ReadAllBytes($config)
    [IO.File]::WriteAllBytes($configBackup, $sourceBytes)
    if ((Get-FileHash -LiteralPath $configBackup -Algorithm SHA256).Hash -cne $originalConfigHash) { throw 'ABORT: byte-for-byte config backup verification failed' }
    $encoding = [Text.UTF8Encoding]::new($false)
    $hasBom = $sourceBytes.Length -ge 3 -and $sourceBytes[0] -eq 0xEF -and $sourceBytes[1] -eq 0xBB -and $sourceBytes[2] -eq 0xBF
    $textBytes = if ($hasBom) { $sourceBytes[3..($sourceBytes.Length - 1)] } else { $sourceBytes }
    $text = $encoding.GetString($textBytes)
    $newline = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }
    $patched = Set-RouteConfig $text $newline
    $patchedBytes = $encoding.GetBytes($patched)
    if ($hasBom) { $patchedBytes = [byte[]](@(0xEF,0xBB,0xBF) + $patchedBytes) }
    $configChanged = $true
    [IO.File]::WriteAllBytes($config, $patchedBytes)
    if (-not (Select-String -LiteralPath $config -Pattern '^bEnableSevarogFrameworkArenaRoute=True$' -Quiet)) { throw 'ABORT: temporary route switch readback failed' }

    $env:SEVAROG_ARENA_ROUTE_LOG = $log
    $env:SEVAROG_ARENA_ROUTE_RECEIPT = $receipt
    $env:SEVAROG_ARENA_ROUTE_MODE = $Mode
    $stage = 'editor_pie'
    $editorArgs = @($project, "-ExecutePythonScript=$driver", '-nosplash', '-nosound', "-abslog=$log")
    if ($Mode -eq 'Smoke') {
        $editorArgs += '-rpg.Build=Starter'
    }
    $editorProcess = Start-Process -FilePath $editor -ArgumentList $editorArgs -WorkingDirectory $root -PassThru -WindowStyle Normal
    $processHandle = $editorProcess.Handle
    $deadline = if ($Mode -eq 'Smoke') { [DateTime]::UtcNow.AddSeconds(900) } else { [DateTime]::UtcNow.AddSeconds($FullTimeoutSeconds) }
    $hasTimedOut = $false
    while ($true) {
        $editorProcess.Refresh()
        $receiptExists = Test-Path -LiteralPath $receipt -PathType Leaf
        if ($receiptExists) {
            $receiptWriteTime = [IO.File]::GetLastWriteTimeUtc($receipt)
            if ($receiptWriteTime -gt $deadline) {
                $hasTimedOut = $true
            }
            break
        }
        if ($editorProcess.HasExited) {
            $exitTime = try { $editorProcess.ExitTime.ToUniversalTime() } catch { [DateTime]::UtcNow }
            if ($exitTime -gt $deadline) {
                $hasTimedOut = $true
            }
            break
        }
        if ([DateTime]::UtcNow -ge $deadline) {
            $hasTimedOut = $true
            break
        }
        Start-Sleep -Milliseconds 250
    }
    if ($editorProcess) {
        Start-Sleep -Seconds 2
        $editorProcess.Refresh()
        if (-not $editorProcess.HasExited) {
            [void]$editorProcess.CloseMainWindow()
            if (-not $editorProcess.WaitForExit(30000)) { throw 'TIMEOUT: close the acceptance Editor to allow config restoration and lock release' }
        }
    }
    $editorProcess.Refresh()
    $editorExit = $editorProcess.ExitCode

    $postRunHashes = Get-RuntimeHashes
    if ($postRunHashes.subsystem_cpp -cne $lockedHashes.subsystem_cpp -or
        $postRunHashes.subsystem_h -cne $lockedHashes.subsystem_h -or
        $postRunHashes.boss_cpp -cne $lockedHashes.boss_cpp -or
        $postRunHashes.boss_h -cne $lockedHashes.boss_h -or
        $postRunHashes.blueprint_call_h -cne $lockedHashes.blueprint_call_h -or
        $postRunHashes.framework_profile_cpp -cne $lockedHashes.framework_profile_cpp -or
        $postRunHashes.framework_runtime_tests_cpp -cne $lockedHashes.framework_runtime_tests_cpp -or
        $postRunHashes.acceptance_runner -cne $lockedHashes.acceptance_runner -or
        $postRunHashes.acceptance_driver -cne $lockedHashes.acceptance_driver) {
        throw 'FAIL: runtime sources modified during Editor PIE run'
    }
    if ($hasTimedOut) {
        if ($Mode -eq 'Smoke') {
            throw 'TIMEOUT: smoke driver timed out at 900 seconds (including Editor startup allowance)'
        } else {
            throw "TIMEOUT: full-mode driver timed out at $FullTimeoutSeconds seconds"
        }
    }
    if ($editorExit -ne 0) { throw "FAIL: UnrealEditor exited with code $editorExit" }
    if (-not (Test-Path -LiteralPath $receipt -PathType Leaf)) { throw 'FAIL: PIE driver exited without an acceptance receipt' }
    $evidence = Get-Content -Raw -LiteralPath $receipt | ConvertFrom-Json
    if ($evidence.result -ne 'PASS') { throw "FAIL: route PIE result=$($evidence.result) reason=$($evidence.failure)" }
    if ($evidence.accepted -ne $true) {
        $result = if ($Mode -eq 'Smoke') { 'SMOKE_PASS' } else { 'BLOCKED' }
        $btVerified = [bool]($evidence.criteria.raw_behavior_tree_tick_count -eq $true)
        $reason = if ($Mode -eq 'Smoke') {
            if ($btVerified) { 'smoke passed; boss-death lifecycle was not exercised; raw BehaviorTree attack-task ticks verified zero' }
            else { 'smoke passed; boss-death lifecycle was not exercised and raw BehaviorTree ticks are uninstrumented' }
        } else {
            if ($btVerified) { 'observable route checks passed; raw BehaviorTree attack-task ticks verified zero' }
            else { 'observable route checks passed, but raw BehaviorTree attack-tick count is not instrumented' }
        }
    } else { $result = 'PASS' }
    $stage = 'completed'
} catch {
    $reason = $_.Exception.Message
    if ($reason.StartsWith('ABORT:')) { $result = 'ABORTED' } elseif ($reason.StartsWith('TIMEOUT:')) { $result = 'TIMED_OUT' } else { $result = 'FAILED' }
    throw
} finally {
    foreach ($temp in $createdTemps) { try { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } } catch {} }
    if ($editorProcess) {
        try {
            $editorProcess.Refresh()
            if (-not $editorProcess.HasExited) { [void]$editorProcess.CloseMainWindow(); [void]$editorProcess.WaitForExit(30000) }
        } catch {}
    }
    $ownedEditorStillRunning = $false
    if ($editorProcess) {
        try { $editorProcess.Refresh(); $ownedEditorStillRunning = -not $editorProcess.HasExited }
        catch { $ownedEditorStillRunning = $true }
    }
    $ownedEditorId = if ($editorProcess) { $editorProcess.Id } else { -1 }
    $otherEditorsStillRunning = [bool](@(Get-Process -Name UnrealEditor, UnrealEditor-Cmd -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne $ownedEditorId }).Count -gt 0)
    $editorStillRunning = $ownedEditorStillRunning -or $otherEditorsStillRunning
    $configRestored = $false
    $released = 0
    $kept = [System.Collections.Generic.List[string]]::new()
    if (-not $editorStillRunning) {
        if ($configChanged -and (Test-Path -LiteralPath $configBackup -PathType Leaf)) {
            try {
                [IO.File]::WriteAllBytes($config, [IO.File]::ReadAllBytes($configBackup))
                $configRestored = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash -eq (Get-FileHash -LiteralPath $configBackup -Algorithm SHA256).Hash
                if (-not $configRestored) { $kept.Add('DefaultGame.ini restore hash mismatch') }
            } catch { $kept.Add('DefaultGame.ini restore failed: ' + $_.Exception.Message) }
        }
        $safeToRelease = -not $configChanged -or $configRestored
        if ($safeToRelease) {
            foreach ($lock in $createdLocks) {
                try {
                    if (Test-Path -LiteralPath $lock) {
                        $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                        if ($current.owner_token -ceq $token) { Remove-Item -LiteralPath $lock -Force; $released++ }
                        else { $kept.Add($lock + ' owner token mismatch') }
                    }
                } catch { $kept.Add($lock + ' release failed: ' + $_.Exception.Message) }
            }
        } else { $kept.Add('Config restore not verified; owned locks intentionally retained for recovery') }
    } else { $kept.Add('Editor is still running; temporary route config and owned locks intentionally retained') }
    if ($editorStillRunning) { $result = 'TIMED_OUT_LOCKS_RETAINED' }
    elseif ($kept.Count -gt 0) { $result = 'RESTORE_OR_LOCK_CLEANUP_FAILED' }
    $criterionSummary = if (Test-Path -LiteralPath $receipt) { try { (Get-Content -Raw $receipt | ConvertFrom-Json).criteria | ConvertTo-Json -Compress } catch { 'unreadable' } } else { 'no_driver_receipt' }
    $acceptanceStatus = if (Test-Path -LiteralPath $receipt) { try { (Get-Content -Raw $receipt | ConvertFrom-Json).runtime_acceptance_status } catch { 'unreadable' } } else { 'no_driver_receipt' }
    $lines = @(
        "RESULT=$result", "MODE=$Mode", "STAGE=$stage", "REASON=$reason", "RUN=$run", "EDITOR_PID=$($editorProcess.Id)",
        "DRIVER_RECEIPT=$receipt", "EDITOR_LOG=$log", "TEMP_CONFIG_ENABLED=$configChanged", "CONFIG_RESTORED=$configRestored",
        "EDITOR_STILL_RUNNING=$editorStillRunning", "LOCKS_CREATED=$($createdLocks.Count)", "LOCKS_RELEASED=$released",
        "LOCKS_KEPT=$($kept -join ';')", "ACCEPTANCE_STATUS=$acceptanceStatus", "CRITERIA=$criterionSummary", 'NO_BUILD=1', 'NO_ASSET_SAVE=1', 'NO_COMMIT=1'
    ) -join "`n"
    try { Write-Status $lines; Write-Output $lines } catch { Write-Warning ('Could not write status receipt: ' + $_.Exception.Message) }
    Remove-Item Env:\SEVAROG_ARENA_ROUTE_LOG -ErrorAction SilentlyContinue
    Remove-Item Env:\SEVAROG_ARENA_ROUTE_RECEIPT -ErrorAction SilentlyContinue
    Remove-Item Env:\SEVAROG_ARENA_ROUTE_MODE -ErrorAction SilentlyContinue
}
