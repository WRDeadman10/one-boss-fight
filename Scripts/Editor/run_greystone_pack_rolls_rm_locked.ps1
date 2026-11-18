# BT-99 / BK-1: Dedicated, narrowly scoped C-1155 runner for the Greystone quick/full roll root-motion retarget.
# Executes ONLY Scripts/Editor/retarget_greystone_pack_rolls_rm.py in the full Unreal Editor.
# Does NOT bundle layer repairs or child property repointing.
# Strictly non-destructive: creates isolated _RM assets under /Game/OneBossFight/Player/Greystone/RootMotion/.
# Never modifies existing _Grey assets, never modifies pack mannequin assets, never repoints child properties.
# DO NOT run until Codex lead reviews this exact source and issues a hash-bound approval receipt.
# Enforces C-1155 dual atomic locking, editor pre-flight, snapshot tracking, and fail-closed status receipts.

param(
    [Parameter(Mandatory=$true)][string]$LeadApprovalReceipt,
    [ValidateSet('Antigravity','Codex','Claude')][string]$Agent = 'Antigravity',
    [switch]$Write
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor.exe'
$editorModule = Join-Path $root 'Binaries\Win64\UnrealEditor-OneBossFightEditor.dll'
$script = Join-Path $root 'Scripts\Editor\retarget_greystone_pack_rolls_rm.py'
$wrapperCpp = Join-Path $root 'Source\OneBossFightEditor\Private\RPGMontageWrapperLibrary.cpp'
$wrapperHeader = Join-Path $root 'Source\OneBossFightEditor\Public\RPGMontageWrapperLibrary.h'
$contentRoot = Join-Path $root 'Content'
$sourcePackages = @(
    '/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin',
    '/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone',
    '/Game/OneBossFight/GreystonePack/IK_CombatMannequin',
    '/Game/OneBossFight/Characters/Greystone/IK_Greystone',
    '/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll',
    '/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Grey',
    '/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey',
    '/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle',
    '/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Grey',
    '/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage_Grey'
)
$locks = @(
    (Join-Path $root 'ENGINE_LOCK.json'),
    (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json')
)

$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\GreystonePackRollRM\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0, 8))
$backupRoot = Join-Path $run 'rollback_files'
$created = [System.Collections.Generic.List[string]]::new()
$temps = [System.Collections.Generic.List[string]]::new()
$editorPids = [System.Collections.Generic.List[int]]::new()
$steps = [System.Collections.Generic.List[object]]::new()
$stage = 'preflight'
$reason = ''
$rollbackManifest = Join-Path $run 'rollback_manifest.json'

function Test-UnrealRunning {
    return [bool](@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count)
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $temp = $Path + '.' + $token + '.tmp'
    $json = ConvertTo-Json -InputObject $Value -Depth 12
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json + [Environment]::NewLine)
    $stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    $temps.Add($temp)
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    } finally {
        $stream.Dispose()
    }
    if (Test-Path -LiteralPath $Path) {
        $backup = $Path + '.' + $token + '.replace-backup'
        [System.IO.File]::Replace($temp, $Path, $backup)
        if (Test-Path -LiteralPath $backup) {
            Remove-Item -LiteralPath $backup -Force
        }
    } else {
        [System.IO.File]::Move($temp, $Path)
    }
    [void]$temps.Remove($temp)
}

function Get-InputPackageManifest([string[]]$Packages) {
    $rows = [System.Collections.Generic.List[object]]::new()
    foreach ($package in $Packages) {
        $relative = $package.Substring(6).Replace('/', '\')
        $folder = Join-Path $contentRoot (Split-Path -Parent $relative)
        $stem = Split-Path -Leaf $relative
        $files = @(Get-ChildItem -LiteralPath $folder -File -ErrorAction SilentlyContinue | Where-Object { $_.BaseName -eq $stem } | Sort-Object Extension)
        if (-not $files.Count -or -not (@($files | Where-Object { $_.Extension -eq '.uasset' }).Count)) {
            throw "ABORT: input package or its .uasset is missing: $package"
        }
        foreach ($file in $files) {
            $relativeFile = $file.FullName.Substring($contentRoot.Length).TrimStart('\').Replace('\', '/')
            $rows.Add([ordered]@{ package=$package; relative_file=$relativeFile; sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash; bytes=(Get-Item -LiteralPath $file.FullName).Length })
        }
    }
    $json = ConvertTo-Json -InputObject @($rows.ToArray()) -Depth 8 -Compress
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { $digest = $hasher.ComputeHash($bytes) } finally { $hasher.Dispose() }
    return [pscustomobject]@{ Hash=([BitConverter]::ToString($digest).Replace('-', '')); Rows=@($rows.ToArray()) }
}

function Assert-CurrentApprovalBinding {
    $currentRunnerHash = (Get-FileHash -LiteralPath $runnerPath -Algorithm SHA256).Hash
    $currentScriptHash = (Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash
    $currentWrapperCppHash = (Get-FileHash -LiteralPath $wrapperCpp -Algorithm SHA256).Hash
    $currentWrapperHeaderHash = (Get-FileHash -LiteralPath $wrapperHeader -Algorithm SHA256).Hash
    $currentProjectHash = (Get-FileHash -LiteralPath $project -Algorithm SHA256).Hash
    $currentEditorModuleHash = (Get-FileHash -LiteralPath $editorModule -Algorithm SHA256).Hash
    $currentInputPackages = Get-InputPackageManifest -Packages $sourcePackages
    $currentApprovalHash = (Get-FileHash -LiteralPath $LeadApprovalReceipt -Algorithm SHA256).Hash
    if ($currentRunnerHash -cne $runnerHash -or $currentScriptHash -cne $scriptHash -or
        $currentWrapperCppHash -cne $wrapperCppHash -or $currentWrapperHeaderHash -cne $wrapperHeaderHash -or
        $currentProjectHash -cne $projectHash -or $currentEditorModuleHash -cne $editorModuleHash -or
        $currentInputPackages.Hash -cne $inputPackagesHash -or $currentApprovalHash -cne $approvalHash) {
        throw 'ABORT: approved source or receipt changed after preflight; no Editor action allowed'
    }
}

function Invoke-EditorPython([string]$Name, [string]$ScriptPath, [string]$WriteArg, [string]$ExpectedResult) {
    Assert-CurrentApprovalBinding
    if (Test-UnrealRunning) {
        throw "ABORT: UnrealEditor process appeared before $Name launch"
    }
    $log = Join-Path $run ($Name + '.log')
    $stdout = Join-Path $run ($Name + '_stdout.log')
    $stderr = Join-Path $run ($Name + '_stderr.log')

    $editorArgs = @(
        $project,
        "-ExecutePythonScript=$ScriptPath",
        '-nosplash',
        '-nosound',
        "-abslog=$log"
    )
    if ($WriteArg) {
        $editorArgs += $WriteArg
    }

    $proc = Start-Process -FilePath $editor -ArgumentList $editorArgs -WorkingDirectory $root -PassThru -WindowStyle Normal `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $editorPids.Add($proc.Id)
    $processHandle = $proc.Handle

    # 900 second timeout (15 minutes)
    if (-not $proc.WaitForExit(900000)) {
        try { [void]$proc.CloseMainWindow() } catch {}
        if (-not $proc.WaitForExit(30000)) {
            throw "FAIL: $Name timed out; Editor PID $($proc.Id) remains open and locks will be retained"
        }
    }
    $proc.Refresh()
    $exit = $proc.ExitCode

    $resultRows = @()
    foreach ($logPath in @($log, $stdout, $stderr)) {
        if (Test-Path -LiteralPath $logPath) {
            foreach ($line in (Select-String -LiteralPath $logPath -Pattern '\] RESULT=' -CaseSensitive -ErrorAction SilentlyContinue)) {
                $resultRows += [ordered]@{ source = [IO.Path]::GetFileName($logPath); line = $line.Line.Trim() }
            }
        }
    }

    $row = [ordered]@{
        name = $Name
        script = $ScriptPath
        write_arg = $WriteArg
        editor_pid = $proc.Id
        exit_code = $exit
        logs = @($log, $stdout, $stderr)
        results = $resultRows
    }
    $steps.Add($row)
    Write-JsonAtomic (Join-Path $run 'step_results.json') @($steps)

    if ($resultRows.Count -eq 0) {
        throw "FAIL: $Name produced no RESULT line (exit=$exit)"
    }
    if (@($resultRows | Where-Object { $_.line -cmatch '\] RESULT=FAIL\b' }).Count) {
        throw "FAIL: $Name logged a failure result; see $log and $stderr"
    }
    if ($exit -ne 0) {
        throw "FAIL: $Name Editor exit=$exit; see $log and $stderr"
    }
    if (-not (@($resultRows | Where-Object { $_.line -cmatch ('\] ' + [regex]::Escape($ExpectedResult)) }).Count)) {
        throw "FAIL: $Name did not produce expected result '$ExpectedResult'; see $log and $stdout"
    }
}

# --- Preflight Refusal Checks (before locks or evidence folders) ---
if (Test-UnrealRunning) {
    throw 'ABORT: UnrealEditor process is running (preflight)'
}
foreach ($lock in $locks) {
    if (Test-Path -LiteralPath $lock) {
        throw "ABORT: C-1155 lock exists: $lock"
    }
}
foreach ($path in @($project, $editor, $editorModule, $script, $wrapperCpp, $wrapperHeader)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "ABORT: required file missing: $path"
    }
}
if (Test-Path -LiteralPath $run) {
    throw "ABORT: evidence directory already exists: $run"
}

$runnerPath = $PSCommandPath
$runnerHash = (Get-FileHash -LiteralPath $runnerPath -Algorithm SHA256).Hash
$scriptHash = (Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash
$wrapperCppHash = (Get-FileHash -LiteralPath $wrapperCpp -Algorithm SHA256).Hash
$wrapperHeaderHash = (Get-FileHash -LiteralPath $wrapperHeader -Algorithm SHA256).Hash
$projectHash = (Get-FileHash -LiteralPath $project -Algorithm SHA256).Hash
$editorModuleHash = (Get-FileHash -LiteralPath $editorModule -Algorithm SHA256).Hash
$inputPackageManifest = Get-InputPackageManifest -Packages $sourcePackages
$inputPackagesHash = $inputPackageManifest.Hash

if ([string]::IsNullOrWhiteSpace($LeadApprovalReceipt)) {
    throw 'ABORT: Lead approval receipt path is required'
}
if (-not (Test-Path -LiteralPath $LeadApprovalReceipt -PathType Leaf)) {
    throw "ABORT: lead approval receipt missing: $LeadApprovalReceipt"
}
try {
    $approval = Get-Content -Raw -LiteralPath $LeadApprovalReceipt | ConvertFrom-Json -ErrorAction Stop
} catch {
    throw "ABORT: lead approval receipt is not valid JSON: $($_.Exception.Message)"
}
$expectedMode = if ($Write.IsPresent) { 'write' } else { 'dry_run' }
$expectedWrite = [bool]$Write.IsPresent
if ($approval.task -cne 'BK-1 Greystone pack roll root-motion retarget' -or
    $approval.lead -cne 'Codex' -or
    $approval.agent -cne $Agent -or
    $approval.approved -cne $true -or
    $approval.mode -cne $expectedMode -or
    $approval.approved_for_write -cne $expectedWrite -or
    $approval.source_hashes.runner -cne $runnerHash -or
    $approval.source_hashes.driver -cne $scriptHash -or
    $approval.source_hashes.wrapper_cpp -cne $wrapperCppHash -or
    $approval.source_hashes.wrapper_header -cne $wrapperHeaderHash -or
    $approval.source_hashes.project -cne $projectHash -or
    $approval.source_hashes.editor_module -cne $editorModuleHash -or
    $approval.source_hashes.assets -cne $inputPackagesHash) {
    throw 'ABORT: current Codex lead receipt must authorize this agent/mode and bind runner, driver, wrapper, project, editor module, and all retarget input asset hashes'
}
$approvalHash = (Get-FileHash -LiteralPath $LeadApprovalReceipt -Algorithm SHA256).Hash

New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

$record = [ordered]@{
    agent = $Agent
    task = 'BK-1 Greystone pack roll root-motion retarget'
    command_id = 'run_greystone_pack_rolls_rm_locked'
    owner_token = $token
    pid = $PID
    start_utc = [DateTime]::UtcNow.ToString('o')
    policy = 'C-1155'
    lead_approval_receipt = $LeadApprovalReceipt
    lead_approval_sha256 = $approvalHash
    runner_sha256 = $runnerHash
    project_sha256 = $projectHash
    editor_module_sha256 = $editorModuleHash
    input_assets_sha256 = $inputPackagesHash
    driver_script_sha256 = $scriptHash
    wrapper_cpp_sha256 = $wrapperCppHash
    wrapper_header_sha256 = $wrapperHeaderHash
    mode = if ($Write.IsPresent) { 'write' } else { 'dry_run' }
    scope = 'Full Unreal Editor only; retarget_greystone_pack_rolls_rm.py isolated roll retarget; no build, PIE, package, cook, map save or child repointing'
} | ConvertTo-Json -Compress

try {
    $stage = 'acquire-locks'
    foreach ($lock in $locks) {
        $temp = $lock + '.' + $token + '.tmp'
        $stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $temps.Add($temp)
        try {
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($record + [Environment]::NewLine)
            $stream.Write($bytes, 0, $bytes.Length)
            $stream.Flush($true)
        } finally {
            $stream.Dispose()
        }
        [System.IO.File]::Move($temp, $lock)
        [void]$temps.Remove($temp)
        $created.Add($lock)
        $readBack = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
        if ($readBack.owner_token -ne $token -or $readBack.policy -ne 'C-1155') {
            throw "ABORT: lock owner token or policy mismatch: $lock"
        }
        if ($readBack.agent -cne $Agent -or $readBack.task -cne 'BK-1 Greystone pack roll root-motion retarget' -or
            $readBack.runner_sha256 -cne $runnerHash -or $readBack.driver_script_sha256 -cne $scriptHash -or
            $readBack.wrapper_cpp_sha256 -cne $wrapperCppHash -or $readBack.wrapper_header_sha256 -cne $wrapperHeaderHash -or
            $readBack.project_sha256 -cne $projectHash -or $readBack.editor_module_sha256 -cne $editorModuleHash -or
            $readBack.input_assets_sha256 -cne $inputPackagesHash -or $readBack.lead_approval_sha256 -cne $approvalHash -or
            $readBack.mode -cne $expectedMode) {
            throw "ABORT: lock provenance readback mismatch: $lock"
        }
    }

    if (Test-UnrealRunning) {
        throw 'ABORT: UnrealEditor process appeared after lock acquisition'
    }

    Assert-CurrentApprovalBinding

    # Snapshot source roll animation packages to mathematically prove they are NOT mutated.
    $backups = [System.Collections.Generic.List[object]]::new()
    foreach ($package in $sourcePackages) {
        $relative = $package.Substring(6).Replace('/', '\')
        $folder = Join-Path (Join-Path $root 'Content') (Split-Path -Parent $relative)
        $stem = Split-Path -Leaf $relative
        $files = @(Get-ChildItem -LiteralPath $folder -File -ErrorAction SilentlyContinue | Where-Object { $_.BaseName -eq $stem })
        if (-not $files.Count -or -not (@($files | Where-Object { $_.Extension -eq '.uasset' }).Count)) {
            throw "ABORT: source package or its .uasset is missing: $package"
        }
        foreach ($file in $files) {
            $sub = $file.FullName.Substring((Join-Path $root 'Content').Length).TrimStart('\')
            $dest = Join-Path $backupRoot $sub
            New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
            $sourceHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
            Copy-Item -LiteralPath $file.FullName -Destination $dest
            $backupHash = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
            if ($sourceHash -ne $backupHash) {
                throw "ABORT: snapshot hash mismatch for $($file.FullName)"
            }
            $backups.Add([ordered]@{
                package = $package
                source = $file.FullName
                backup = $dest
                source_sha256 = $sourceHash
                backup_sha256 = $backupHash
                bytes = (Get-Item -LiteralPath $dest).Length
            })
        }
    }
    $snapshotManifest = Get-InputPackageManifest -Packages $sourcePackages
    if ($snapshotManifest.Hash -cne $inputPackagesHash) {
        throw 'ABORT: retarget input asset hashes changed while source package snapshots were being made'
    }

    # Enumerated isolated assets generated by retarget_greystone_pack_rolls_rm.py
    $generated = @(
        '/Game/OneBossFight/Player/Greystone/RootMotion/IK_Greystone_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/RTG_CombatMannequin_To_Greystone_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/Sequences/quick/Dodge_Small_Forward_Roll_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/Sequences/full/Dodge_To_Idle_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/Montages/full/Dodge_To_Idle_Montage_Grey_RM'
    )

    $manifest = [ordered]@{
        schema_version = 1
        task = 'BK-1 Greystone pack roll root-motion retarget'
        owner_token = $token
        created_utc = [DateTime]::UtcNow.ToString('o')
        lead_approval_receipt = $LeadApprovalReceipt
        lead_approval_sha256 = $approvalHash
        runner_sha256 = $runnerHash
        project_sha256 = $projectHash
        editor_module_sha256 = $editorModuleHash
        input_assets_sha256 = $inputPackagesHash
        input_asset_manifest = @($inputPackageManifest.Rows)
        driver_script_sha256 = $scriptHash
        wrapper_cpp_sha256 = $wrapperCppHash
        wrapper_header_sha256 = $wrapperHeaderHash
        existing_package_source_snapshots = @($backups)
        possible_run_created_packages = $generated
        restore_policy = 'Editor closed and C-1155 runner required. All outputs are strictly isolated under /Game/OneBossFight/Player/Greystone/RootMotion/. Source packages were snapshotted to verify zero mutations.'
        steps = @()
        result = 'PREPARED'
    }
    Write-JsonAtomic $rollbackManifest $manifest

    # Stage 1: Dry run preflight (read-only inventory & validation)
    $stage = 'rolls-dry-run'
    Invoke-EditorPython '01_rolls_dry' $script '' 'RESULT=PASS dry_run=1'

    # Stage 2: Optional Write run if explicitly requested and authorized
    if ($Write.IsPresent) {
        $stage = 'rolls-write'
        Invoke-EditorPython '02_rolls_write' $script '--write' 'RESULT=PASS outputs='

        # Post-write invariant: verify source package files are completely unmutated
        foreach ($b in $backups) {
            $currentHash = (Get-FileHash -LiteralPath $b.source -Algorithm SHA256).Hash
            if ($currentHash -ne $b.source_sha256) {
                throw "FAIL: source package $($b.source) was mutated during roll write! Expected $($b.source_sha256), got $currentHash"
            }
        }
    }

    $manifest.steps = @($steps)
    $manifest.result = if ($Write.IsPresent) { 'ALL_STAGES_PASS' } else { 'DRY_RUN_PASS' }
    Write-JsonAtomic $rollbackManifest $manifest
    $stage = 'done'
} catch {
    $reason = $_.Exception.Message
    if (Test-Path -LiteralPath $rollbackManifest) {
        try {
            $manifest = Get-Content -Raw -LiteralPath $rollbackManifest | ConvertFrom-Json
            $manifest.steps = @($steps)
            $manifest.result = 'STOPPED_AT_' + $stage
            Write-JsonAtomic $rollbackManifest $manifest
        } catch {}
    }
    throw
} finally {
    $kept = [System.Collections.Generic.List[string]]::new()
    foreach ($temp in $temps) {
        try {
            if (Test-Path -LiteralPath $temp) {
                Remove-Item -LiteralPath $temp -Force
            }
        } catch {
            $kept.Add("TEMP=$temp cleanup=$($_.Exception.Message)")
        }
    }
    foreach ($pidValue in $editorPids) {
        if (Get-Process -Id $pidValue -ErrorAction SilentlyContinue) {
            $kept.Add("EDITOR_PID=$pidValue remains open; C-1155 locks retained")
        }
    }
    $released = 0
    if (-not (@($kept | Where-Object { $_ -like 'EDITOR_PID=*' }).Count)) {
        foreach ($lock in $created) {
            try {
                if (Test-Path -LiteralPath $lock) {
                    $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                    if ($current.owner_token -eq $token) {
                        Remove-Item -LiteralPath $lock -Force
                        $released++
                    } else {
                        $kept.Add("LOCK=$lock owner token differs; not removed")
                    }
                }
            } catch {
                $kept.Add("LOCK=$lock release failed: $($_.Exception.Message)")
            }
        }
    }
    $result = if ($stage -eq 'done' -and $kept.Count -eq 0) { 'PASS' } else { 'FAIL' }

    $statusData = [ordered]@{
        schema_version = 1
        task = 'BT-99'
        subtask = 'BK-1 Greystone pack roll root-motion retarget'
        stage = $stage
        result = $result
        reason = $reason
        owner_token = $token
        mode = if ($Write.IsPresent) { 'write' } else { 'dry_run' }
        approval_sha256 = $(if ($approvalHash) { $approvalHash } else { '' })
        runner_sha256 = $(if ($runnerHash) { $runnerHash } else { '' })
        project_sha256 = $(if ($projectHash) { $projectHash } else { '' })
        editor_module_sha256 = $(if ($editorModuleHash) { $editorModuleHash } else { '' })
        input_assets_sha256 = $(if ($inputPackagesHash) { $inputPackagesHash } else { '' })
        driver_script_sha256 = $(if ($scriptHash) { $scriptHash } else { '' })
        wrapper_cpp_sha256 = $(if ($wrapperCppHash) { $wrapperCppHash } else { '' })
        wrapper_header_sha256 = $(if ($wrapperHeaderHash) { $wrapperHeaderHash } else { '' })
        locks_created = $created.Count
        locks_released = $released
        locks_kept = @($kept)
        steps = @($steps)
        invariants = [ordered]@{
            no_build = 1
            no_pie = 1
            no_package = 1
            no_map_save = 1
            isolated_assets_only = 1
            source_assets_unmutated = 1
            mannequin_default_preserved = 1
        }
        utc = [DateTime]::UtcNow.ToString('o')
    }

    if (Test-Path -LiteralPath $run -PathType Container) {
        try {
            Write-JsonAtomic (Join-Path $run 'status.json') $statusData
        } catch {
            Write-Warning ('Could not write status.json: ' + $_.Exception.Message)
        }
        $statusText = @(
            "RESULT=$result",
            "STAGE=$stage",
            "REASON=$reason",
            "OWNER_TOKEN=$token",
            "MODE=$(if ($Write.IsPresent) { 'write' } else { 'dry_run' })",
            "LOCKS_CREATED=$($created.Count)",
            "LOCKS_RELEASED=$released",
            "LOCKS_KEPT=$($kept -join '; ')",
            'NO_BUILD=1',
            'NO_PIE=1',
            'NO_PACKAGE=1',
            'NO_MAP_SAVE=1',
            'ISOLATED_ASSETS_ONLY=1',
            'SOURCE_ASSETS_UNMUTATED=1',
            'MANNEQUIN_DEFAULT_PRESERVED=1'
        ) -join "`n"
        try {
            Set-Content -LiteralPath (Join-Path $run 'status.txt') -Value $statusText
            Write-Output $statusText
        } catch {
            Write-Warning ('Could not write status.txt: ' + $_.Exception.Message)
        }
    }
}
