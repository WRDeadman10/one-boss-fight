# X-2436 / Claude C-1618 Step 1: prepare and optionally execute the staged Greystone fix.
# DO NOT run until Claude reviews this runner and schedules C-1155. This is the full Unreal Editor,
# not UnrealEditor-Cmd: dry-run/write pairs for layer parents, isolated root-motion rolls, child repoint.
# The runner takes both C-1155 locks atomically, snapshots every existing package it may edit,
# records the generated-package rollback list, stops at first failure, captures RESULT lines,
# writes status in finally, and only releases locks it created whose owner_token still matches.
param(
    [ValidateSet('Codex')][string]$Agent = 'Codex',
    [string]$LeadApprovalReceipt
)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor.exe'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$scripts = [ordered]@{
    layer = Join-Path $root 'Scripts\Editor\repair_grey_layer_parents.py'
    rolls = Join-Path $root 'Scripts\Editor\retarget_greystone_pack_rolls_rm.py'
    repoint = Join-Path $root 'Scripts\Editor\repoint_greystone_rolls_rm.py'
}
$stageAdapter = Join-Path $root 'Scripts\Editor\greystone_fix_stage.py'
$approvalPath = Join-Path $root 'Saved\B_GREYSTONE_FIX\lead_approval.json'
$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\B_GREYSTONE_FIX\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0, 8))
$backupRoot = Join-Path $run 'rollback_files'
$originalLocation = Get-Location
$created = [System.Collections.Generic.List[string]]::new()
$temps = [System.Collections.Generic.List[string]]::new()
$editorPids = [System.Collections.Generic.List[int]]::new()
$steps = [System.Collections.Generic.List[object]]::new()
$stage = 'preflight'
$reason = ''
$rollbackManifest = Join-Path $run 'rollback_manifest.json'

function Test-UnrealRunning { return [bool](@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) }

function Write-JsonAtomic([string]$Path, [object]$Value) {
    $temp = $Path + '.' + $token + '.tmp'
    $json = ConvertTo-Json -InputObject $Value -Depth 12
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json + [Environment]::NewLine)
    $stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    $temps.Add($temp) # track only after CreateNew proves this invocation owns the temp
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    if (Test-Path -LiteralPath $Path) { [System.IO.File]::Replace($temp, $Path, $null) }
    else { [System.IO.File]::Move($temp, $Path) }
    [void]$temps.Remove($temp)
}

function Invoke-EditorPython([string]$Name, [string]$ScriptPath, [string]$WriteToken, [string]$ExpectedResult) {
    if (Test-UnrealRunning) { throw "ABORT: UnrealEditor process appeared before $Name launch" }
    $log = Join-Path $run ($Name + '.log')
    $stdout = Join-Path $run ($Name + '_stdout.log')
    $stderr = Join-Path $run ($Name + '_stderr.log')
    $stageName = if ($Name -match '_layer_') { 'layer' } elseif ($Name -match '_rolls_') { 'rolls' } else { 'repoint' }
    $editorArgs = @($project, "-ExecutePythonScript=$stageAdapter", "-BGreystoneStage=$stageName", '-nosplash', '-nosound', "-abslog=$log")
    if ($WriteToken) { $editorArgs += $WriteToken }
    $proc = Start-Process -FilePath $editor -ArgumentList $editorArgs -WorkingDirectory $root -PassThru -WindowStyle Normal `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $editorPids.Add($proc.Id)
    # Materialize the native process handle before WaitForExit; otherwise the Process
    # wrapper can report a null ExitCode even after the child has exited.
    $processHandle = $proc.Handle
    if (-not $proc.WaitForExit(900000)) {
        try { [void]$proc.CloseMainWindow() } catch {}
        if (-not $proc.WaitForExit(30000)) { throw "FAIL: $Name timed out; Editor PID $($proc.Id) remains open and locks will be retained" }
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
    $row = [ordered]@{ name=$Name; script=$ScriptPath; write_token=$WriteToken; editor_pid=$proc.Id; exit_code=$exit; logs=@($log,$stdout,$stderr); results=$resultRows }
    $steps.Add($row)
    Write-JsonAtomic (Join-Path $run 'step_results.json') @($steps)
    if ($resultRows.Count -eq 0) { throw "FAIL: $Name produced no RESULT line (exit=$exit)" }
    if (@($resultRows | Where-Object { $_.line -cmatch '\] RESULT=FAIL\b' }).Count) { throw "FAIL: $Name logged a failure result; see $log and $stderr" }
    if ($exit -ne 0) { throw "FAIL: $Name Editor exit=$exit; see $log and $stderr" }
    if (-not (@($resultRows | Where-Object { $_.line -cmatch ('\] ' + $ExpectedResult) }).Count)) {
        throw "FAIL: $Name did not produce expected result '$ExpectedResult'; see $log and $stdout"
    }
}

# Preflight refusals happen before evidence or locks are created. Claude must create this
# receipt only after reviewing/scheduling the run; merely invoking the file cannot launch UE.
if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor process is running (preflight)' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: C-1155 lock exists: $lock" } }
if ([string]::IsNullOrWhiteSpace($LeadApprovalReceipt)) { throw 'ABORT: Claude lead approval receipt path is required' }
if (-not (Test-Path -LiteralPath $LeadApprovalReceipt -PathType Leaf)) { throw "ABORT: lead approval receipt missing: $LeadApprovalReceipt" }
$approval = Get-Content -Raw -LiteralPath $LeadApprovalReceipt | ConvertFrom-Json
if ($approval.task -ne 'C-1618' -or $approval.lead -ne 'Claude' -or $approval.approved -ne $true) { throw 'ABORT: lead approval receipt is not a valid C-1618 Step 1 approval' }
$approvalHash = (Get-FileHash -LiteralPath $LeadApprovalReceipt -Algorithm SHA256).Hash
foreach ($path in @($project, $editor, $stageAdapter) + @($scripts.Values)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "ABORT: required file missing: $path" }
}
if (Test-Path -LiteralPath $run) { throw "ABORT: evidence directory already exists: $run" }
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

$record = [ordered]@{
    agent=$Agent; party='X'; task='Claude C-1618 Greystone fix runner'; command_id='B_GREYSTONE_FIX.locked-editor-stages'; owner_token=$token
    pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'
    lead_approval_receipt=$LeadApprovalReceipt; lead_approval_sha256=$approvalHash
    scope='Full Unreal Editor only; layer dry/write, isolated roll retarget dry/write, child repoint dry/write; stop first failure; no build, PIE, package, cook or map save'
} | ConvertTo-Json -Compress

try {
    $stage = 'acquire-locks'
    foreach ($lock in $locks) {
        $temp = $lock + '.' + $token + '.tmp'
        $stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $temps.Add($temp) # track only after CreateNew proves this invocation owns the temp
        try { $bytes=[System.Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
        [System.IO.File]::Move($temp,$lock)
        [void]$temps.Remove($temp)
        $created.Add($lock)
        $readBack = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
        if ($readBack.owner_token -ne $token) { throw "ABORT: lock owner token mismatch: $lock" }
    }
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor process appeared after lock acquisition' }

    # Every existing package that the authoring stages can change is snapshotted before any Editor call.
    $existingPackages = @(
        '/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/LinkedLayers/ABP_UnarmedLayer_Grey',
        '/Game/OneBossFight/GreystonePack/MagicCombatSystem/Blueprints/Animation/ABP_MagicStaffLayer_Grey',
        '/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_2HandedSwordLayer_Grey',
        '/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_DualSwordLayer_Grey',
        '/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_SwordLayer_Grey',
        '/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_SwordnShieldLayer_Grey',
        '/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_TwinbladeLayer_Grey',
        '/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Blueprints/Animation/AnimLayers/ABP_UnarmednShieldLayer_Grey',
        '/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer'
    )
    $backups = [System.Collections.Generic.List[object]]::new()
    foreach ($package in $existingPackages) {
        $relative = $package.Substring(6).Replace('/', '\')
        $folder = Join-Path (Join-Path $root 'Content') (Split-Path -Parent $relative)
        $stem = Split-Path -Leaf $relative
        $files = @(Get-ChildItem -LiteralPath $folder -File | Where-Object { $_.BaseName -eq $stem })
        if (-not (@($files | Where-Object { $_.Extension -eq '.uasset' }).Count)) { throw "ABORT: package .uasset missing for $package" }
        foreach ($file in $files) {
            $sub = $file.FullName.Substring((Join-Path $root 'Content').Length).TrimStart('\')
            $dest = Join-Path $backupRoot $sub
            New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
            $sourceHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
            Copy-Item -LiteralPath $file.FullName -Destination $dest
            $backupHash = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
            if ($sourceHash -ne $backupHash) { throw "ABORT: snapshot hash mismatch for $($file.FullName)" }
            $backups.Add([ordered]@{ package=$package; source=$file.FullName; backup=$dest; source_sha256=$sourceHash; backup_sha256=$backupHash; bytes=(Get-Item -LiteralPath $dest).Length })
        }
    }
    $generated = @(
        '/Game/ABP_CombatAnimLayersBase_Grey',
        '/Game/OneBossFight/Player/Greystone/RootMotion/IK_Greystone_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/RTG_CombatMannequin_To_Greystone_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/Sequences/quick/Dodge_Small_Forward_Roll_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/Sequences/full/Dodge_To_Idle_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM',
        '/Game/OneBossFight/Player/Greystone/RootMotion/Montages/full/Dodge_To_Idle_Montage_Grey_RM'
    )
    $manifest = [ordered]@{
        schema_version=1; task='Claude C-1618 Step 1'; owner_token=$token; created_utc=[DateTime]::UtcNow.ToString('o')
        lead_approval_receipt=$LeadApprovalReceipt; lead_approval_sha256=$approvalHash
        existing_package_file_backups=@($backups); possible_run_created_packages=$generated
        restore_policy='Editor closed and C-1155 runner required. Restore snapshots only after hash verification; remove generated packages only after Asset Registry referencer checks. This manifest is evidence, not an automatic rollback.'
        steps=@(); result='PREPARED'
    }
    Write-JsonAtomic $rollbackManifest $manifest

    $stage = 'layer-dry-run'
    Invoke-EditorPython '01_layer_dry' $scripts.layer '' 'RESULT=DRY_RUN'
    $stage = 'layer-write'
    Invoke-EditorPython '02_layer_write' $scripts.layer '-GreyLayerRepairWrite' 'RESULT=PASS'
    $stage = 'rolls-dry-run'
    Invoke-EditorPython '03_rolls_dry' $scripts.rolls '' 'RESULT=PASS dry_run=1'
    $stage = 'rolls-write'
    Invoke-EditorPython '04_rolls_write' $scripts.rolls '--write' 'RESULT=PASS outputs='
    $stage = 'repoint-dry-run'
    Invoke-EditorPython '05_repoint_dry' $scripts.repoint '' 'RESULT=DRY_RUN'
    $stage = 'repoint-write'
    Invoke-EditorPython '06_repoint_write' $scripts.repoint '-RMRepointWrite' 'RESULT=PASS repointed='
    $manifest.steps = @($steps)
    $manifest.result = 'ALL_STAGES_PASS'
    Write-JsonAtomic $rollbackManifest $manifest
    $stage = 'done'
} catch {
    $reason = $_.Exception.Message
    if (Test-Path -LiteralPath $rollbackManifest) {
        try { $manifest = Get-Content -Raw -LiteralPath $rollbackManifest | ConvertFrom-Json; $manifest.steps=@($steps); $manifest.result='STOPPED_AT_' + $stage; Write-JsonAtomic $rollbackManifest $manifest } catch {}
    }
    throw
} finally {
    $kept = [System.Collections.Generic.List[string]]::new()
    foreach ($temp in $temps) { try { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } } catch { $kept.Add("TEMP=$temp cleanup=$($_.Exception.Message)") } }
    foreach ($pidValue in $editorPids) {
        if (Get-Process -Id $pidValue -ErrorAction SilentlyContinue) { $kept.Add("EDITOR_PID=$pidValue remains open; C-1155 locks retained") }
    }
    $released = 0
    if (-not (@($kept | Where-Object { $_ -like 'EDITOR_PID=*' }).Count)) {
        foreach ($lock in $created) {
            try {
                if (Test-Path -LiteralPath $lock) {
                    $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                    if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force; $released++ }
                    else { $kept.Add("LOCK=$lock owner token differs; not removed") }
                }
            } catch { $kept.Add("LOCK=$lock release failed: $($_.Exception.Message)") }
        }
    }
    $result = if ($stage -eq 'done' -and $kept.Count -eq 0) { 'PASS' } else { 'FAIL' }
    $status = @("RESULT=$result", "STAGE=$stage", "REASON=$reason", "OWNER_TOKEN=$token", "LOCKS_CREATED=$($created.Count)", "LOCKS_RELEASED=$released", "LOCKS_KEPT=$($kept -join '; ')", 'NO_BUILD=1', 'NO_PIE=1', 'NO_PACKAGE=1', 'NO_MAP_SAVE=1') -join "`n"
    try { Set-Content -LiteralPath (Join-Path $run 'status.txt') -Value $status; Write-Output $status } catch { Write-Warning ('Could not write status receipt: ' + $_.Exception.Message) }
}
