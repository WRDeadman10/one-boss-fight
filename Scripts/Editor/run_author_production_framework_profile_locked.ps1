# BT-63 C-1155: Author DA_Boss_Sevarog_FrameworkProfile_Production and rebind DA_Sevarog_Framework_Encounter under exclusive lock.
param(
    [ValidateSet('Full', 'DryRun', 'Write', 'Readback')]
    [string]$Mode = 'Full',
    [double]$TargetHealth = 800.0,
    [switch]$SkipBuildGate
)

$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$editorCmd = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$driver = Join-Path $root 'Scripts\Editor\author_production_framework_profile.py'
$profileAsset = Join-Path $root 'Content\OneBossFight\Data\Sevarog\DA_Boss_Sevarog_FrameworkProfile_Production.uasset'
$encounterAsset = Join-Path $root 'Content\OneBossFight\Data\Sevarog\DA_Sevarog_Framework_Encounter.uasset'
$frameworkProfileCpp = Join-Path $root 'Source\OneBossFight\Player\RPGBossFrameworkProfile.cpp'
$frameworkRuntimeTestsCpp = Join-Path $root 'Source\OneBossFight\Tests\RPGFrameworkRuntimeTests.cpp'
$acceptanceRunner = Join-Path $root 'Scripts\Editor\run_sevarog_arena_route_acceptance.ps1'
$acceptanceDriver = Join-Path $root 'Scripts\Editor\pie_sevarog_arena_route_acceptance.py'
$pinnedManifestHash = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
$config = Join-Path $root 'Config\DefaultGame.ini'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))

$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\BT63ProductionProfileAuthoring\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0, 8))
$backupDir = Join-Path $run 'backup'
$encounterBackup = Join-Path $backupDir (Split-Path $encounterAsset -Leaf)
$profileBackup = Join-Path $backupDir (Split-Path $profileAsset -Leaf)
$statusPath = Join-Path $run 'status.json'

$owned = [System.Collections.Generic.List[string]]::new()
$temps = [System.Collections.Generic.List[string]]::new()
$launched = [System.Collections.Generic.List[int]]::new()

$stage = 'preflight'
$reason = ''
$initialEncounterHash = ''
$finalEncounterHash = ''
$initialProfileHash = ''
$finalProfileHash = ''
$configHashBefore = ''
$configHashAfter = ''
$dryRunReceipt = $null
$writeReceipt = $null
$readbackReceipt = $null
$encounterRestored = $false
$profileRestored = $false
$profileCleanedUp = $false
$verifiedBuildRun = $null

function Test-UnrealRunning {
    return [bool](@(Get-Process -Name UnrealEditor, UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count -gt 0)
}

function Wait-UnrealClosed([int]$Seconds = 45) {
    $deadline = [DateTime]::UtcNow.AddSeconds($Seconds)
    while (Test-UnrealRunning) {
        if ([DateTime]::UtcNow -ge $deadline) { return $false }
        Start-Sleep -Milliseconds 500
    }
    return $true
}

function Write-AtomicLock([string]$Path) {
    $temp = $Path + '.' + $token + '.tmp'
    $temps.Add($temp)
    $record = [ordered]@{
        agent = 'Antigravity'
        party = 'A'
        task = 'BT-63: Author production framework profile asset and encounter rebind'
        command_id = 'BT63.author-production-framework-profile'
        owner_token = $token
        pid = $PID
        start_utc = [DateTime]::UtcNow.ToString('o')
        policy = 'C-1155'
        scope = 'Author DA_Boss_Sevarog_FrameworkProfile_Production; rebind DA_Sevarog_Framework_Encounter; exact readback; rollback on error'
    } | ConvertTo-Json -Compress

    $stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($record + [Environment]::NewLine)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    }
    finally {
        $stream.Dispose()
    }
    [System.IO.File]::Move($temp, $Path)
    $temps.Remove($temp)
    $owned.Add($Path)
    $back = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ($back.owner_token -cne $token -or $back.policy -cne 'C-1155') {
        throw "ABORT: lock readback mismatch: $Path"
    }
}

function Invoke-AuthorStage([string]$StageName, [string]$ReceiptPath, [string]$LogPath) {
    Remove-Item Env:\PRODUCTION_PROFILE_DRY_RUN, Env:\PRODUCTION_PROFILE_WRITE, Env:\PRODUCTION_PROFILE_READBACK -ErrorAction SilentlyContinue
    $env:SEVAROG_TARGET_HEALTH = $TargetHealth.ToString('F1')
    $env:SEVAROG_AUTHOR_RECEIPT_PATH = $ReceiptPath
    $env:PRODUCTION_PROFILE_REBIND_ENCOUNTER = '1'

    $scriptArgs = @()
    if ($StageName -eq 'dry_run') {
        $env:PRODUCTION_PROFILE_DRY_RUN = '1'
        $scriptArgs += '--dry-run'
    }
    elseif ($StageName -eq 'write') {
        $env:PRODUCTION_PROFILE_WRITE = '1'
        $scriptArgs += '--write'
    }
    elseif ($StageName -eq 'readback') {
        $env:PRODUCTION_PROFILE_READBACK = '1'
        $scriptArgs += '--readback'
    }
    else {
        throw "Unknown author stage: $StageName"
    }
    $scriptArgs += '--rebind-encounter'
    $scriptArgs += "--target-health=$($TargetHealth.ToString('F1'))"
    $scriptArgs += "--receipt=$ReceiptPath"

    $argList = @(
        $project,
        "-ExecutePythonScript=$driver $($scriptArgs -join ' ')",
        '-nosound',
        '-stdout',
        '-FullStdOutLogOutput',
        '-unattended',
        '-NoSplash',
        "-abslog=$LogPath"
    )

    $proc = Start-Process -FilePath $editorCmd -ArgumentList $argList -WorkingDirectory $root -PassThru -WindowStyle Normal
    $launched.Add($proc.Id)
    $deadline = [DateTime]::UtcNow.AddMinutes(4)
    while (-not $proc.HasExited) {
        $proc.Refresh()
        if ([DateTime]::UtcNow -ge $deadline) {
            throw "TIMEOUT: Editor stage '$StageName' exceeded four minutes (PID $($proc.Id))"
        }
        Start-Sleep -Milliseconds 250
    }

    if ($proc.ExitCode -ne 0) {
        throw "FAIL: Editor stage '$StageName' exited with code $($proc.ExitCode); see $LogPath"
    }

    if (Test-Path -LiteralPath $LogPath -PathType Leaf) {
        $pyErrors = @(Select-String -LiteralPath $LogPath -Pattern 'LogPython:\s*Error:|LogEditorPythonExecuter:\s*Error:|\bTraceback \(most recent call last\):' -SimpleMatch:$false)
        if ($pyErrors.Count -gt 0) {
            $firstErr = $pyErrors[0].Line.Trim()
            throw "FAIL: Editor stage '$StageName' reported Python error in log ($firstErr); see $LogPath"
        }
    }

    if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf)) {
        throw "FAIL: Editor stage '$StageName' emitted no receipt at $ReceiptPath"
    }

    $data = Get-Content -Raw -LiteralPath $ReceiptPath | ConvertFrom-Json
    if ($data.task -cne 'author_production_framework_profile') {
        throw "FAIL: malformed receipt task: $($data.task)"
    }
    if ($data.target_health -ne 800.0) {
        throw "FAIL: receipt target_health mismatch: $($data.target_health) != 800.0"
    }
    if ($data.boss_max_health -ne 1500.0) {
        throw "FAIL: receipt boss_max_health mismatch: $($data.boss_max_health) != 1500.0"
    }
    if ($data.player_posture_hit_amount -ne 60.0) {
        throw "FAIL: receipt player_posture_hit_amount mismatch: $($data.player_posture_hit_amount) != 60.0"
    }
    if ($data.stagger_seconds -ne 2.5) {
        throw "FAIL: receipt stagger_seconds mismatch: $($data.stagger_seconds) != 2.5"
    }

    if (-not (Wait-UnrealClosed 45)) {
        throw "FAIL: Editor stage '$StageName' left an UnrealEditor process running after shutdown wait"
    }
    return $data
}

try {
    # 1. Exact Owner TargetHealth check
    if ($TargetHealth -ne 800.0) {
        throw "ABORT: TargetHealth $TargetHealth does not match owner-approved production value 800.0 HP"
    }

    # 2. Preflight process check
    if (Test-UnrealRunning) {
        throw 'ABORT: close UnrealEditor / UnrealEditor-Cmd before C-1155 BT-63 operation'
    }

    # 3. Required file verification
    $requiredFiles = @($editorCmd, $project, $driver, $encounterAsset, $frameworkProfileCpp, $frameworkRuntimeTestsCpp, $acceptanceRunner, $acceptanceDriver, $config)
    foreach ($p in $requiredFiles) {
        if (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
            throw "ABORT: required file missing: $p"
        }
    }

    # 4. Check for existing locks
    foreach ($lock in $locks) {
        if (Test-Path -LiteralPath $lock) {
            throw "ABORT: existing C-1155 lock: $lock"
        }
    }

    # 5. Pre-lock baseline hash capture
    $preLockDriverHash = (Get-FileHash -LiteralPath $driver -Algorithm SHA256).Hash
    $preLockCppHash = (Get-FileHash -LiteralPath $frameworkProfileCpp -Algorithm SHA256).Hash
    $preLockTestsHash = (Get-FileHash -LiteralPath $frameworkRuntimeTestsCpp -Algorithm SHA256).Hash
    $preLockRunnerHash = (Get-FileHash -LiteralPath $acceptanceRunner -Algorithm SHA256).Hash
    $preLockDriverAcceptanceHash = (Get-FileHash -LiteralPath $acceptanceDriver -Algorithm SHA256).Hash

    # 6. [X-2545] Acquire exclusive dual C-1155 locks FIRST (before any backup or disk mutation)
    foreach ($lock in $locks) {
        Write-AtomicLock $lock
    }

    # 7. [X-2545] Immediately verify no Editor appeared after lock acquisition
    if (Test-UnrealRunning) {
        throw 'ABORT: UnrealEditor appeared after C-1155 lock acquisition'
    }

    # 8. [X-2545] Recompute and compare all bound hashes under the active lock; verify zero drift
    $driverHash = (Get-FileHash -LiteralPath $driver -Algorithm SHA256).Hash
    $cppHash = (Get-FileHash -LiteralPath $frameworkProfileCpp -Algorithm SHA256).Hash
    $testsHash = (Get-FileHash -LiteralPath $frameworkRuntimeTestsCpp -Algorithm SHA256).Hash
    $runnerHash = (Get-FileHash -LiteralPath $acceptanceRunner -Algorithm SHA256).Hash
    $driverAcceptanceHash = (Get-FileHash -LiteralPath $acceptanceDriver -Algorithm SHA256).Hash

    if ($driverHash -cne $preLockDriverHash -or
        $cppHash -cne $preLockCppHash -or
        $testsHash -cne $preLockTestsHash -or
        $runnerHash -cne $preLockRunnerHash -or
        $driverAcceptanceHash -cne $preLockDriverAcceptanceHash) {
        throw 'ABORT: Source files drifted during C-1155 lock acquisition'
    }

    # 9. [X-2545] Revalidate the selected build receipt / current hash gate under lock
    if ($SkipBuildGate) {
        if ($Mode -ne 'DryRun') {
            throw "ABORT: -SkipBuildGate is only permitted when -Mode DryRun is specified. Write and Full modes strictly require a verified passing BT-64 build gate."
        }
    }
    else {
        $buildStatusDir = Join-Path $root 'Saved\C1619RouteBuild'
        if (-not (Test-Path -LiteralPath $buildStatusDir -PathType Container)) {
            throw "ABORT: BT-64 build directory missing at $buildStatusDir"
        }

        $runs = Get-ChildItem -Path $buildStatusDir -Directory | Sort-Object CreationTime -Descending
        $verifiedRun = $null
        $verifiedApproval = $null

        foreach ($r in $runs) {
            $candidateStatus = Join-Path $r.FullName 'status.json'
            $candidateApproval = Join-Path $r.FullName 'route_lead_approval.json'

            if ((Test-Path -LiteralPath $candidateStatus -PathType Leaf) -and
                (Test-Path -LiteralPath $candidateApproval -PathType Leaf)) {
                $st = Get-Content -Raw -LiteralPath $candidateStatus | ConvertFrom-Json
                $app = Get-Content -Raw -LiteralPath $candidateApproval | ConvertFrom-Json

                # Verify route_lead_approval.build_suite_run resolves to this exact run directory
                $suiteRunMatches = $false
                if ($app.build_suite_run) {
                    $resolvedSuiteRun = (Resolve-Path $app.build_suite_run -ErrorAction SilentlyContinue).Path
                    $resolvedCurrentRun = (Resolve-Path $r.FullName -ErrorAction SilentlyContinue).Path
                    if ($resolvedSuiteRun -ceq $resolvedCurrentRun) {
                        $suiteRunMatches = $true
                    }
                }

                # Verify all status fields matching run_c1619_route_build_locked.ps1 output
                $statusOk = ($st.result -ceq 'PASS' -and
                             $st.stage -ceq 'done' -and
                             $st.approved -eq $true -and
                             $st.lead -ceq 'Codex' -and
                             $st.source_build_exit -eq 0 -and
                             $st.suite_result -ceq 'PASS' -and
                             $st.suite_exit -eq 0 -and
                             $st.suite_complete -eq $true -and
                             $st.failed -eq 0 -and
                             $st.passed -ge 573 -and
                             $st.dd27j_manifest_hash -ceq $pinnedManifestHash -and
                             $st.framework_profile_cpp_sha256 -ceq $cppHash -and
                             $st.framework_runtime_tests_cpp_sha256 -ceq $testsHash -and
                             $st.acceptance_runner_sha256 -ceq $runnerHash -and
                             $st.acceptance_driver_sha256 -ceq $driverAcceptanceHash -and
                             $st.locks_released -eq 2 -and
                             (@($st.locks_kept).Count -eq 0))

                # Verify route lead approval receipt fields
                $approvalOk = ($app.approved -eq $true -and
                               $app.lead -ceq 'Codex' -and
                               $app.source_build_exit -eq 0 -and
                               $app.suite_result -ceq 'PASS' -and
                               $app.dd27j_manifest_hash -ceq $pinnedManifestHash -and
                               $app.framework_profile_cpp_sha256 -ceq $cppHash -and
                               $app.framework_runtime_tests_cpp_sha256 -ceq $testsHash -and
                               $app.acceptance_runner_sha256 -ceq $runnerHash -and
                               $app.acceptance_driver_sha256 -ceq $driverAcceptanceHash -and
                               $app.locks_released -ge 2 -and
                               $suiteRunMatches)

                if ($statusOk -and $approvalOk) {
                    $verifiedRun = $st
                    $verifiedApproval = $app
                    break
                }
            }
        }

        if ($null -eq $verifiedRun) {
            throw "ABORT: No passing BT-64 build found matching current source hashes (framework_profile_cpp: $cppHash, framework_runtime_tests_cpp: $testsHash, acceptance_runner: $runnerHash, acceptance_driver: $driverAcceptanceHash, pinned_manifest: $pinnedManifestHash). C-1155 build and DD27j suite must pass before BT-63 authoring."
        }
        $verifiedBuildRun = $verifiedRun.owner_token
    }

    # 10. [X-2545] Initialize run workspace and take backups strictly UNDER the acquired locks
    New-Item -ItemType Directory -Path $run | Out-Null
    New-Item -ItemType Directory -Path $backupDir | Out-Null

    $initialEncounterHash = (Get-FileHash -LiteralPath $encounterAsset -Algorithm SHA256).Hash
    $configHashBefore = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
    Copy-Item -LiteralPath $encounterAsset -Destination $encounterBackup
    if ((Get-FileHash -LiteralPath $encounterBackup -Algorithm SHA256).Hash -cne $initialEncounterHash) {
        throw 'ABORT: encounter backup hash mismatch'
    }

    $profilePreexisted = Test-Path -LiteralPath $profileAsset -PathType Leaf
    if ($profilePreexisted) {
        $initialProfileHash = (Get-FileHash -LiteralPath $profileAsset -Algorithm SHA256).Hash
        Copy-Item -LiteralPath $profileAsset -Destination $profileBackup
        if ((Get-FileHash -LiteralPath $profileBackup -Algorithm SHA256).Hash -cne $initialProfileHash) {
            throw 'ABORT: profile backup hash mismatch'
        }
    }

    # 11. Execution Stage 1: DryRun
    if ($Mode -eq 'Full' -or $Mode -eq 'DryRun') {
        $stage = 'dry_run'
        $dryRunReceipt = Invoke-AuthorStage 'dry_run' (Join-Path $run 'dry_run_receipt.json') (Join-Path $run 'dry_run.log')
        if ($dryRunReceipt.mode -cne 'dry_run') {
            throw 'ABORT: dry_run receipt did not record dry_run mode'
        }
        $encAfterDry = (Get-FileHash -LiteralPath $encounterAsset -Algorithm SHA256).Hash
        if ($encAfterDry -cne $initialEncounterHash) {
            throw 'ABORT: dry_run modified DA_Sevarog_Framework_Encounter package'
        }
    }

    # 12. Execution Stage 2: Write
    if ($Mode -eq 'Full' -or $Mode -eq 'Write') {
        $stage = 'write'
        $writeReceipt = Invoke-AuthorStage 'write' (Join-Path $run 'write_receipt.json') (Join-Path $run 'write.log')
        if ($writeReceipt.mode -cne 'write') {
            throw 'ABORT: write receipt did not record write mode'
        }

        # Verify profile asset exists on disk and is non-empty
        if (-not (Test-Path -LiteralPath $profileAsset -PathType Leaf)) {
            throw 'FAIL: write stage did not create DA_Boss_Sevarog_FrameworkProfile_Production.uasset'
        }
        $finalProfileHash = (Get-FileHash -LiteralPath $profileAsset -Algorithm SHA256).Hash
        $profileSize = (Get-Item -LiteralPath $profileAsset).Length
        if ($profileSize -le 0) {
            throw 'FAIL: created profile asset has zero length'
        }

        # Verify encounter asset hash changed
        $finalEncounterHash = (Get-FileHash -LiteralPath $encounterAsset -Algorithm SHA256).Hash
        if ($finalEncounterHash -ceq $initialEncounterHash) {
            throw 'FAIL: write stage did not update DA_Sevarog_Framework_Encounter package'
        }
    }

    # 13. Execution Stage 3: Fresh process Readback
    if ($Mode -eq 'Full' -or $Mode -eq 'Readback') {
        $stage = 'fresh_process_readback'
        $readbackReceipt = Invoke-AuthorStage 'readback' (Join-Path $run 'readback_receipt.json') (Join-Path $run 'readback.log')
        if ($readbackReceipt.mode -cne 'readback') {
            throw 'FAIL: readback receipt did not record readback mode'
        }
        if ($readbackReceipt.rebind_encounter -ne $true) {
            throw 'FAIL: readback receipt does not confirm rebind_encounter=true'
        }
        if ($readbackReceipt.encounter_manifest_hash -cne '62ecc592e0c2ad57ec0b5d70afd56ba7ea1dc7f9d0fd1dc7a3fc1b625ac6d305') {
            throw "FAIL: readback receipt encounter_manifest_hash mismatch: $($readbackReceipt.encounter_manifest_hash)"
        }
    }

    $configHashAfter = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
    if ($configHashAfter -cne $configHashBefore) {
        throw 'FAIL: DefaultGame.ini changed during BT-63 authoring'
    }

    $stage = 'done'
}
catch {
    $reason = $_.Exception.Message
    if ((Test-UnrealRunning) -and $launched.Count -gt 0) {
        foreach ($procId in $launched) {
            $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
            if ($p -and ($p.ProcessName -eq 'UnrealEditor' -or $p.ProcessName -eq 'UnrealEditor-Cmd')) {
                try { Stop-Process -Id $procId -Force } catch {}
            }
        }
    }

    # Rollback encounter asset if modified
    if ((Test-Path -LiteralPath $encounterBackup -PathType Leaf) -and -not (Test-UnrealRunning)) {
        $curEnc = (Get-FileHash -LiteralPath $encounterAsset -Algorithm SHA256).Hash
        if ($curEnc -cne $initialEncounterHash) {
            Copy-Item -LiteralPath $encounterBackup -Destination $encounterAsset -Force
            $restoredEncHash = (Get-FileHash -LiteralPath $encounterAsset -Algorithm SHA256).Hash
            if ($restoredEncHash -cne $initialEncounterHash) {
                $reason += '; encounter rollback hash mismatch'
            }
            else {
                $encounterRestored = $true
            }
        }
    }

    # Clean up or restore profile asset with explicit SHA256 verification
    if (-not (Test-UnrealRunning)) {
        if ($profilePreexisted -and (Test-Path -LiteralPath $profileBackup -PathType Leaf)) {
            Copy-Item -LiteralPath $profileBackup -Destination $profileAsset -Force
            $restoredProfHash = (Get-FileHash -LiteralPath $profileAsset -Algorithm SHA256).Hash
            if ($restoredProfHash -cne $initialProfileHash) {
                $reason += "; profile rollback hash mismatch: $restoredProfHash != $initialProfileHash"
                $profileRestored = $false
            }
            else {
                $profileRestored = $true
            }
        }
        elseif (-not $profilePreexisted -and (Test-Path -LiteralPath $profileAsset -PathType Leaf)) {
            Remove-Item -LiteralPath $profileAsset -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $profileAsset -PathType Leaf) {
                $reason += '; profile cleanup failed: file still exists'
                $profileCleanedUp = $false
            }
            else {
                $profileCleanedUp = $true
            }
        }
    }
    throw
}
finally {
    Remove-Item Env:\SEVAROG_TARGET_HEALTH, Env:\SEVAROG_AUTHOR_RECEIPT_PATH, Env:\PRODUCTION_PROFILE_REBIND_ENCOUNTER, Env:\PRODUCTION_PROFILE_DRY_RUN, Env:\PRODUCTION_PROFILE_WRITE, Env:\PRODUCTION_PROFILE_READBACK -ErrorAction SilentlyContinue
    foreach ($temp in $temps) {
        Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
    }

    # Retain locks while any Unreal process remains; remove only when no process running
    [void](Wait-UnrealClosed 30)
    $unrealRunningAtExit = Test-UnrealRunning
    $locksRetained = [System.Collections.Generic.List[string]]::new()

    if (-not $unrealRunningAtExit) {
        for ($index = $owned.Count - 1; $index -ge 0; $index--) {
            $lock = $owned[$index]
            if (Test-Path -LiteralPath $lock -PathType Leaf) {
                $record = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                if ($record.owner_token -ceq $token) {
                    Remove-Item -LiteralPath $lock -Force
                }
            }
        }
    }
    else {
        foreach ($lock in $owned) {
            $locksRetained.Add($lock)
        }
        $reason += "; Unreal process still running; C-1155 locks retained: $($owned -join ', ')"
    }

    $remaining = @($locks | Where-Object { Test-Path -LiteralPath $_ })
    $configHashAfter = if (Test-Path -LiteralPath $config) { (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash } else { '' }
    $finalEncounterHash = if (Test-Path -LiteralPath $encounterAsset) { (Get-FileHash -LiteralPath $encounterAsset -Algorithm SHA256).Hash } else { '' }
    $finalProfileHash = if (Test-Path -LiteralPath $profileAsset) { (Get-FileHash -LiteralPath $profileAsset -Algorithm SHA256).Hash } else { '' }

    $summary = [ordered]@{
        task = 'BT-63'
        status = if ($stage -eq 'done' -and $remaining.Count -eq 0 -and -not $unrealRunningAtExit) { 'PASS' } else { 'FAIL' }
        stage = $stage
        reason = $reason
        mode = $Mode
        target_health = $TargetHealth
        driver_sha256 = $driverHash
        framework_profile_cpp_sha256 = $cppHash
        framework_runtime_tests_cpp_sha256 = $testsHash
        acceptance_runner_sha256 = $runnerHash
        acceptance_driver_sha256 = $driverAcceptanceHash
        pinned_manifest_hash = $pinnedManifestHash
        initial_encounter_sha256 = $initialEncounterHash
        final_encounter_sha256 = $finalEncounterHash
        initial_profile_sha256 = $initialProfileHash
        final_profile_sha256 = $finalProfileHash
        config_before_sha256 = $configHashBefore
        config_after_sha256 = $configHashAfter
        encounter_restored = $encounterRestored
        profile_restored = $profileRestored
        profile_cleaned_up = $profileCleanedUp
        verified_build_token = $verifiedBuildRun
        dry_run_receipt = $dryRunReceipt
        write_receipt = $writeReceipt
        readback_receipt = $readbackReceipt
        owner_token = $token
        locks_retained = $locksRetained
        locks_remaining = $remaining
        editor_running = $unrealRunningAtExit
        evidence_directory = $run
    }

    # Ensure preflight failure before $run exists does not mask the refusal in finally
    if (Test-Path -LiteralPath $run -PathType Container) {
        $summary | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $statusPath -Encoding UTF8
    }
}

if ($stage -ne 'done' -or (Test-Path -LiteralPath $locks[0]) -or (Test-Path -LiteralPath $locks[1]) -or (Test-UnrealRunning)) {
    throw "BT-63 did not complete safely; see $statusPath"
}
Write-Output (Get-Content -Raw -LiteralPath $statusPath)
