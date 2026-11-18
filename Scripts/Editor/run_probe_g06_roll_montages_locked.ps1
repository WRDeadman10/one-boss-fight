# BT-103: Task-specific hash-bound C-1155 read-only runner for G-06 roll montage readback.
# Executes Scripts/Editor/probe_g06_roll_montages.py in the full Unreal Editor under policy C-1155.
# Strictly read-only on assets and config: snapshots all inspected packages before and after launch,
# verifying zero byte mutations. Requires fresh Codex lead approval receipt bound to exact source hashes.
# Enforces preflight editor absence, atomic dual locks with owner token readback, post-lock rehash,
# -nosound, bounded process timeout, fail-closed RESULT parsing, and lock release only after owned exit.

param(
    [Parameter(Mandatory=$true)][string]$LeadApprovalReceipt,
    [ValidateSet('Antigravity', 'Codex', 'Claude')][string]$Agent = 'Antigravity'
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor.exe'
$probe = Join-Path $root 'Scripts\Editor\probe_g06_roll_montages.py'
$editorModule = Join-Path $root 'Binaries\Win64\UnrealEditor-OneBossFightEditor.dll'
$locks = @(
    (Join-Path $root 'ENGINE_LOCK.json'),
    (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json')
)

$targetPackages = @(
    '/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage',
    '/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey',
    '/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM',
    '/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer'
)

$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\G06RollMontageReadback\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0, 8))
$snapshotDir = Join-Path $run 'package_snapshots'
$created = [System.Collections.Generic.List[string]]::new()
$temps = [System.Collections.Generic.List[string]]::new()
$editorPids = [System.Collections.Generic.List[int]]::new()
$steps = [System.Collections.Generic.List[object]]::new()
$stage = 'preflight'
$reason = ''
$manifestPath = ''
$manifestHash = ''

function Test-UnrealRunning {
    return [bool](@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count)
}

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $dir = Split-Path -Parent $Path
    if (-not [string]::IsNullOrEmpty($dir) -and -not (Test-Path -LiteralPath $dir -PathType Container)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $temp = $Path + '.' + $token + '.tmp'
    $bak = $Path + '.' + $token + '.bak'
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
        $temps.Add($bak)
        try {
            [System.IO.File]::Replace($temp, $Path, $bak)
        } catch {
            throw "ABORT: Write-JsonAtomic Replace failed for ${Path}: $($_.Exception.Message)"
        } finally {
            if (Test-Path -LiteralPath $bak) {
                Remove-Item -LiteralPath $bak -Force -ErrorAction SilentlyContinue
            }
            [void]$temps.Remove($bak)
        }
    } else {
        [System.IO.File]::Move($temp, $Path)
    }
    [void]$temps.Remove($temp)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "ABORT: Write-JsonAtomic target does not exist after write: $Path"
    }
    try {
        $null = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw "ABORT: Write-JsonAtomic readback verification failed for ${Path}: $($_.Exception.Message)"
    }
}

function Get-AssetPackageFiles([string]$PackagePath) {
    $relative = $PackagePath.Substring(6).Replace('/', '\')
    $folder = Join-Path (Join-Path $root 'Content') (Split-Path -Parent $relative)
    $stem = Split-Path -Leaf $relative
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) {
        throw "ABORT: package folder missing: $folder for $PackagePath"
    }
    $files = @(Get-ChildItem -LiteralPath $folder -File | Where-Object { $_.BaseName -eq $stem })
    if ($files.Count -eq 0) {
        throw "ABORT: no package files found for $PackagePath in $folder"
    }
    return $files
}

function Compute-DeterministicAssetHash {
    $hashList = [System.Collections.Generic.List[string]]::new()
    foreach ($pkg in $targetPackages) {
        $files = Get-AssetPackageFiles $pkg
        foreach ($file in ($files | Sort-Object Name)) {
            $h = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
            $hashList.Add($file.Name + '=' + $h)
        }
    }
    # Use ordinal ordering so this approval hash is invariant across Windows cultures/locales.
    $hashList.Sort([System.StringComparer]::Ordinal)
    $combined = $hashList -join "`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($combined)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($hashBytes).Replace('-', '').ToUpper())
    } finally {
        $sha.Dispose()
    }
}

# --- Preflight Mutual Exclusion & File Checks ---
if (Test-UnrealRunning) {
    throw 'ABORT: UnrealEditor process is running (preflight)'
}
foreach ($lock in $locks) {
    if (Test-Path -LiteralPath $lock) {
        throw "ABORT: C-1155 lock exists: $lock"
    }
}

foreach ($path in @($project, $editor, $probe, $editorModule)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "ABORT: required file missing: $path"
    }
}

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

$runnerPath = $PSCommandPath
if ([string]::IsNullOrWhiteSpace($runnerPath)) {
    $runnerPath = Join-Path $root 'Scripts\Editor\run_probe_g06_roll_montages_locked.ps1'
}
$runnerHash = (Get-FileHash -LiteralPath $runnerPath -Algorithm SHA256).Hash
$probeHash = (Get-FileHash -LiteralPath $probe -Algorithm SHA256).Hash
$projectHash = (Get-FileHash -LiteralPath $project -Algorithm SHA256).Hash
$editorModuleHash = (Get-FileHash -LiteralPath $editorModule -Algorithm SHA256).Hash
$assetsHash = Compute-DeterministicAssetHash

if ($approval.task -cne 'BT-103 G-06 roll montage property readback' -or
    $approval.lead -cne 'Codex' -or
    $approval.agent -cne $Agent -or
    $approval.approved -cne $true -or
    $approval.mode -cne 'read_only' -or
    $approval.source_hashes.runner -cne $runnerHash -or
    $approval.source_hashes.probe -cne $probeHash -or
    $approval.source_hashes.project -cne $projectHash -or
    $approval.source_hashes.editor_module -cne $editorModuleHash -or
    $approval.source_hashes.assets -cne $assetsHash) {
    throw 'ABORT: lead approval receipt must explicitly authorize this agent in read_only mode and bind exact runner, probe, project, editor_module, and asset hashes'
}

$approvalHash = (Get-FileHash -LiteralPath $LeadApprovalReceipt -Algorithm SHA256).Hash

if (Test-Path -LiteralPath $run) {
    throw "ABORT: run evidence directory already exists: $run"
}

New-Item -ItemType Directory -Path $snapshotDir -Force | Out-Null

$record = [ordered]@{
    agent = $Agent
    task = 'BT-103 G-06 roll montage property readback'
    command_id = 'run_probe_g06_roll_montages_locked'
    owner_token = $token
    pid = $PID
    start_utc = [DateTime]::UtcNow.ToString('o')
    policy = 'C-1155'
    lead_approval_receipt = $LeadApprovalReceipt
    lead_approval_sha256 = $approvalHash
    runner_sha256 = $runnerHash
    probe_sha256 = $probeHash
    project_sha256 = $projectHash
    editor_module_sha256 = $editorModuleHash
    assets_sha256 = $assetsHash
    mode = 'read_only'
    scope = 'Full Unreal Editor only; probe_g06_roll_montages.py read-only inspection; zero asset or config modifications; no build, PIE, package, cook or map save'
} | ConvertTo-Json -Compress

try {
    # --- Stage 1: Atomic Dual Locking ---
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
        if ($readBack.owner_token -cne $token -or $readBack.policy -cne 'C-1155') {
            throw "ABORT: lock owner token or policy mismatch: $lock"
        }
    }

    if (Test-UnrealRunning) {
        throw 'ABORT: UnrealEditor process appeared after lock acquisition'
    }

    # --- Stage 2: Pre-launch Snapshot and Pre-launch Rehash ---
    $stage = 'prelaunch-snapshot'
    $snapshots = [System.Collections.Generic.List[object]]::new()
    foreach ($pkg in $targetPackages) {
        $files = Get-AssetPackageFiles $pkg
        foreach ($file in $files) {
            $sub = $file.FullName.Substring((Join-Path $root 'Content').Length).TrimStart('\')
            $dest = Join-Path $snapshotDir $sub
            New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
            $sourceHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
            Copy-Item -LiteralPath $file.FullName -Destination $dest -Force
            $backupHash = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
            if ($sourceHash -ne $backupHash) {
                throw "ABORT: pre-launch snapshot hash mismatch for $($file.FullName)"
            }
            $snapshots.Add([ordered]@{
                package = $pkg
                source = $file.FullName
                snapshot = $dest
                sha256 = $sourceHash
            })
        }
    }

    # Recheck source hashes immediately prior to process launch
    $recheckAssetsHash = Compute-DeterministicAssetHash
    if ($recheckAssetsHash -ne $assetsHash) {
        throw "ABORT: asset hash changed between preflight and pre-launch! Expected $assetsHash, got $recheckAssetsHash"
    }

    # --- Stage 3: Launch Editor Probe ---
    $stage = 'launch-probe'
    $log = Join-Path $run 'probe.log'
    $stdout = Join-Path $run 'probe_stdout.log'
    $stderr = Join-Path $run 'probe_stderr.log'

    $editorArgs = @(
        $project,
        "-ExecutePythonScript=$probe",
        '-nosplash',
        '-nosound',
        "-abslog=$log"
    )

    $proc = Start-Process -FilePath $editor -ArgumentList $editorArgs -WorkingDirectory $root -PassThru -WindowStyle Normal `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $editorPids.Add($proc.Id)
    $processHandle = $proc.Handle

    # 300 second timeout (5 minutes)
    if (-not $proc.WaitForExit(300000)) {
        try { [void]$proc.CloseMainWindow() } catch {}
        if (-not $proc.WaitForExit(30000)) {
            throw "FAIL: probe Editor timed out; Editor PID $($proc.Id) remains open and locks will be retained"
        }
    }
    $proc.Refresh()
    $exit = $proc.ExitCode

    $steps.Add([ordered]@{
        stage = 'probe_run'
        pid = $proc.Id
        exit_code = $exit
        log = $log
    })

    if ($exit -ne 0) {
        throw "FAIL: probe Editor exited with non-zero exit code: $exit"
    }

    # --- Stage 4: Post-execution Invariant Checks ---
    $stage = 'post-execution-validation'

    # Check 1: Zero asset mutations (recompute all package hashes against pre-launch snapshots)
    foreach ($snap in $snapshots) {
        if (-not (Test-Path -LiteralPath $snap.source -PathType Leaf)) {
            throw "FAIL: package file $($snap.source) was deleted during read-only probe!"
        }
        $currentHash = (Get-FileHash -LiteralPath $snap.source -Algorithm SHA256).Hash
        if ($currentHash -ne $snap.sha256) {
            throw "FAIL: package $($snap.source) was mutated during read-only probe! Expected $($snap.sha256), got $currentHash"
        }
    }

    # Check 1b: Recompute deterministic asset hash across all target package folders to detect any added/modified sidecars
    $postRunAssetsHash = Compute-DeterministicAssetHash
    if ($postRunAssetsHash -ne $assetsHash) {
        throw "FAIL: target assets hash changed after probe run! Pre-launch: $assetsHash, Post-run: $postRunAssetsHash. Sidecar files were modified, created, or deleted."
    }

    # Also verify exact file count per package to prevent phantom sidecars
    $postRunFilesCount = 0
    foreach ($pkg in $targetPackages) {
        $currentFiles = Get-AssetPackageFiles $pkg
        $postRunFilesCount += $currentFiles.Count
    }
    if ($postRunFilesCount -ne $snapshots.Count) {
        throw "FAIL: target asset package files count changed! Snapshot count: $($snapshots.Count), Post-run count: $postRunFilesCount"
    }

    # Check 2: Parse result markers from log
    $resultLines = @()
    if (Test-Path -LiteralPath $log) {
        $resultLines = @(Select-String -LiteralPath $log -Pattern '\[G06RollProbe\] RESULT=' -CaseSensitive -ErrorAction SilentlyContinue)
    }
    if ($resultLines.Count -eq 0) {
        throw "FAIL: probe log contains no [G06RollProbe] RESULT= line"
    }
    if (@($resultLines | Where-Object { $_.Line -cmatch 'RESULT=FAIL\b' }).Count) {
        throw "FAIL: probe reported RESULT=FAIL"
    }
    if (@($resultLines | Where-Object { $_.Line -cmatch 'RESULT=PARTIAL\b' }).Count) {
        throw "FAIL: probe reported RESULT=PARTIAL (missing root extractions or incomplete fields)"
    }
    if (-not (@($resultLines | Where-Object { $_.Line -cmatch 'RESULT=PASS\b' }).Count)) {
        throw "FAIL: probe did not produce exact RESULT=PASS"
    }

    # Check 3: Parse and validate evidence manifest JSON
    $manifestLines = @(Select-String -LiteralPath $log -Pattern '\[G06RollProbe\] OUTPUT_MANIFEST ' -CaseSensitive -ErrorAction SilentlyContinue)
    if ($manifestLines.Count -eq 0) {
        throw "FAIL: probe log contains no OUTPUT_MANIFEST marker"
    }
    $manifestPath = ($manifestLines[0].Line.Trim() -split 'OUTPUT_MANIFEST ')[1].Trim()
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "FAIL: output manifest JSON does not exist at reported path: $manifestPath"
    }
    $manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash

    $manifestData = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
    if ($manifestData.task -cne 'BT-102' -or
        $manifestData.outcome -cne 'PASS' -or
        $manifestData.montages.Count -ne 3 -or
        $null -eq $manifestData.child_blueprint -or
        $null -eq $manifestData.total_segments -or
        $manifestData.total_segments -lt 3 -or
        $null -eq $manifestData.extraction_errors -or
        $manifestData.extraction_errors.Count -ne 0 -or
        $null -eq $manifestData.property_errors -or
        $manifestData.property_errors.Count -ne 0) {
        throw "FAIL: output manifest does not satisfy complete PASS criteria (montages=$($manifestData.montages.Count), total_segments=$($manifestData.total_segments), outcome=$($manifestData.outcome), extraction_errors=$($manifestData.extraction_errors.Count))"
    }

    # Validate child Blueprint identity and component defaults
    $cb = $manifestData.child_blueprint
    if ($cb.blueprint_path -cne '/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer' -or
        $cb.timing_component_class -cne 'RPGDodgeTiming' -or
        [string]::IsNullOrWhiteSpace($cb.quick_montage) -or
        $null -eq $cb.quick_play_rate -or $cb.quick_play_rate -le 0 -or
        [string]::IsNullOrWhiteSpace($cb.full_montage) -or
        $null -eq $cb.full_play_rate -or $cb.full_play_rate -le 0 -or
        [string]::IsNullOrWhiteSpace($cb.backstep_montage) -or
        $null -eq $cb.backstep_play_rate -or $cb.backstep_play_rate -le 0) {
        throw "FAIL: child Blueprint defaults missing or invalid in manifest (path=$($cb.blueprint_path), class=$($cb.timing_component_class), quick_montage=$($cb.quick_montage), quick_rate=$($cb.quick_play_rate))"
    }

    # Validate exact montage identities and paths
    $expectedMontages = @{
        'pack_quick' = '/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage'
        'grey_quick' = '/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey'
        'candidate_quick_rm' = '/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM'
    }

    $seenLabels = [System.Collections.Generic.HashSet[string]]::new()
    $validatedSegments = 0

    foreach ($m in $manifestData.montages) {
        if (-not $expectedMontages.ContainsKey($m.label)) {
            throw "FAIL: unexpected montage label in manifest: $($m.label)"
        }
        if ($m.path -cne $expectedMontages[$m.label]) {
            throw "FAIL: montage $($m.label) path mismatch. Expected $($expectedMontages[$m.label]), got $($m.path)"
        }
        [void]$seenLabels.Add($m.label)

        # Validate top-level montage timing and blend properties
        if ($null -eq $m.play_length -or $m.play_length -le 0) {
            throw "FAIL: montage $($m.label) play_length missing or non-positive: $($m.play_length)"
        }
        if ($null -eq $m.sequence_length -or $m.sequence_length -le 0) {
            throw "FAIL: montage $($m.label) sequence_length missing or non-positive: $($m.sequence_length)"
        }
        if ($null -eq $m.rate_scale -or $m.rate_scale -le 0) {
            throw "FAIL: montage $($m.label) rate_scale missing or non-positive: $($m.rate_scale)"
        }
        if ($null -eq $m.blend_in -or $null -eq $m.blend_in.blend_time -or [string]::IsNullOrEmpty($m.blend_in.blend_option)) {
            throw "FAIL: montage $($m.label) blend_in properties missing or invalid"
        }
        if ($null -eq $m.blend_out -or $null -eq $m.blend_out.blend_time -or [string]::IsNullOrEmpty($m.blend_out.blend_option)) {
            throw "FAIL: montage $($m.label) blend_out properties missing or invalid"
        }
        if ($null -eq $m.blend_out_trigger_time) {
            throw "FAIL: montage $($m.label) blend_out_trigger_time missing"
        }
        if ($null -eq $m.composite_sections -or $m.composite_sections.Count -eq 0) {
            throw "FAIL: montage $($m.label) composite_sections missing or empty"
        }

        # Validate tracks and segment fields
        if ($null -eq $m.slot_anim_tracks -or $m.slot_anim_tracks.Count -eq 0) {
            throw "FAIL: montage $($m.label) has missing or empty slot_anim_tracks"
        }
        $montageSegments = 0
        foreach ($t in $m.slot_anim_tracks) {
            foreach ($s in $t.segments) {
                $montageSegments++
                $validatedSegments++

                # FAnimSegment fields
                if ([string]::IsNullOrWhiteSpace($s.anim_reference_path)) {
                    throw "FAIL: montage $($m.label) segment has missing or empty anim_reference_path"
                }
                if ($null -eq $s.anim_start_time) {
                    throw "FAIL: montage $($m.label) segment has null anim_start_time"
                }
                if ($null -eq $s.anim_end_time) {
                    throw "FAIL: montage $($m.label) segment has null anim_end_time"
                }
                if ($null -eq $s.anim_play_rate -or $s.anim_play_rate -le 0) {
                    throw "FAIL: montage $($m.label) segment has non-positive or null anim_play_rate"
                }
                if ($null -eq $s.start_pos -or -not [string]::IsNullOrEmpty($s.start_pos_error)) {
                    throw "FAIL: montage $($m.label) segment has null start_pos or start_pos_error: $($s.start_pos_error)"
                }
                if ($null -eq $s.looping_count -or -not [string]::IsNullOrEmpty($s.looping_count_error)) {
                    throw "FAIL: montage $($m.label) segment has null looping_count or looping_count_error: $($s.looping_count_error)"
                }

                # Referenced sequence fields
                $seq = $s.referenced_sequence
                if ($null -eq $seq) {
                    throw "FAIL: montage $($m.label) segment has null referenced_sequence"
                }
                if ([string]::IsNullOrWhiteSpace($seq.path)) {
                    throw "FAIL: montage $($m.label) referenced sequence has empty path"
                }
                if ($null -eq $seq.play_length -or $seq.play_length -le 0) {
                    throw "FAIL: montage $($m.label) referenced sequence play_length missing or non-positive"
                }
                if ($null -eq $seq.enable_root_motion) {
                    throw "FAIL: montage $($m.label) referenced sequence enable_root_motion missing"
                }
                if ([string]::IsNullOrWhiteSpace($seq.root_motion_root_lock)) {
                    throw "FAIL: montage $($m.label) referenced sequence root_motion_root_lock missing"
                }
                if ($null -eq $seq.force_root_lock) {
                    throw "FAIL: montage $($m.label) referenced sequence force_root_lock missing"
                }
                if ($null -eq $seq.number_of_sampled_frames -or -not [string]::IsNullOrEmpty($seq.number_of_sampled_frames_error)) {
                    throw "FAIL: montage $($m.label) referenced sequence number_of_sampled_frames null or error: $($seq.number_of_sampled_frames_error)"
                }
                if ($null -eq $seq.raw_root_xy_displacement_cm -or -not [string]::IsNullOrEmpty($seq.extraction_error)) {
                    throw "FAIL: montage $($m.label) segment has null root displacement or extraction error: $($seq.extraction_error)"
                }
            }
        }
        if ($montageSegments -eq 0) {
            throw "FAIL: montage $($m.label) has 0 anim segments"
        }
    }

    if ($seenLabels.Count -ne 3) {
        throw "FAIL: not all 3 expected montages were found in manifest (found $($seenLabels.Count))"
    }
    if ($validatedSegments -lt 3) {
        throw "FAIL: validated segments count ($validatedSegments) is less than required minimum 3"
    }

    $stage = 'done'
} catch {
    $reason = $_.Exception.Message
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
        task = 'BT-103'
        subtask = 'G-06 roll montage property readback runner'
        stage = $stage
        result = $result
        reason = $reason
        owner_token = $token
        mode = 'read_only'
        approval_sha256 = $(if ($approvalHash) { $approvalHash } else { '' })
        runner_sha256 = $(if ($runnerHash) { $runnerHash } else { '' })
        probe_sha256 = $(if ($probeHash) { $probeHash } else { '' })
        project_sha256 = $(if ($projectHash) { $projectHash } else { '' })
        editor_module_sha256 = $(if ($editorModuleHash) { $editorModuleHash } else { '' })
        assets_sha256 = $(if ($assetsHash) { $assetsHash } else { '' })
        manifest_path = $manifestPath
        manifest_sha256 = $manifestHash
        locks_created = $created.Count
        locks_released = $released
        locks_kept = @($kept)
        steps = @($steps)
        invariants = [ordered]@{
            no_build = 1
            no_pie = 1
            no_package = 1
            no_map_save = 1
            zero_asset_mutations = 1
            zero_config_mutations = 1
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
            "MODE=read_only",
            "LOCKS_CREATED=$($created.Count)",
            "LOCKS_RELEASED=$released",
            "LOCKS_KEPT=$($kept -join '; ')",
            "MANIFEST_PATH=$manifestPath",
            "MANIFEST_SHA256=$manifestHash",
            'NO_BUILD=1',
            'NO_PIE=1',
            'NO_PACKAGE=1',
            'NO_MAP_SAVE=1',
            'ZERO_ASSET_MUTATIONS=1',
            'ZERO_CONFIG_MUTATIONS=1'
        ) -join "`n"
        try {
            Set-Content -LiteralPath (Join-Path $run 'status.txt') -Value $statusText
            Write-Output $statusText
        } catch {
            Write-Warning ('Could not write status.txt: ' + $_.Exception.Message)
        }
    }
}
