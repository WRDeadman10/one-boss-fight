param(
    [Parameter(Mandatory = $true)][string]$LeadApprovalReceipt,
    [ValidateRange(1, 300)][int]$TimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$editor = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$runner = $MyInvocation.MyCommand.Path
if (-not $runner) { $runner = Join-Path $root 'Scripts\Editor\run_greystone_visual_smoke.ps1' }
$driver = Join-Path $root 'Scripts\Editor\pie_greystone_visual_smoke.py'
$config = Join-Path $root 'Config\DefaultGame.ini'
$sourceRetargetCpp = Join-Path $root 'Source\OneBossFightEditor\Private\RPGGreystoneRuntimeRetargetLibrary.cpp'
$sourceMovesCpp = Join-Path $root 'Source\OneBossFight\Player\RPGPlayerMovesSubsystem.cpp'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$createdLocks = [System.Collections.Generic.List[string]]::new()
$createdTemps = [System.Collections.Generic.List[string]]::new()

function Test-EditorRunning {
    return [bool](@(Get-Process -Name UnrealEditor, UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count -gt 0)
}

function Acquire-Lock([string]$Path) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $temp = $Path + '.' + $token + '.tmp'
    $createdTemps.Add($temp)
    $record = [ordered]@{
        agent = 'Antigravity'; party = 'X'; task = 'BT-79 Greystone visual smoke PIE'; command_id = 'run_greystone_visual_smoke'
        owner_token = $token; pid = $PID; start_utc = [DateTime]::UtcNow.ToString('o'); policy = 'C-1155'
        scope = "L_SevarogArena Greystone opt-in visual smoke; temporary CVar test pawn switch; no build, package, map or asset save"
    }
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes(($record | ConvertTo-Json -Depth 5) + [Environment]::NewLine)
    $stream = [IO.File]::Open($temp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    try { [IO.File]::Move($temp, $Path) }
    catch { throw "ABORT: atomic lock acquisition failed: $Path" }
    $createdTemps.Remove($temp)
    $createdLocks.Add($Path)
    $readBack = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ($readBack.owner_token -cne $token -or
        $readBack.policy -ne 'C-1155' -or
        $readBack.party -cne 'X' -or
        $readBack.agent -cne 'Antigravity' -or
        $readBack.task -cne 'BT-79 Greystone visual smoke PIE' -or
        $readBack.command_id -cne 'run_greystone_visual_smoke') {
        throw "ABORT: lock readback mismatch: $Path"
    }
}

# 1. Preflight safety checks
if (-not (Test-Path -LiteralPath $editor -PathType Leaf)) {
    throw "ABORT: UnrealEditor executable not found at $editor"
}
if (-not (Test-Path -LiteralPath $project -PathType Leaf)) {
    throw "ABORT: project file not found at $project"
}
if (-not (Test-Path -LiteralPath $driver -PathType Leaf)) {
    throw "ABORT: visual smoke driver not found at $driver"
}
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    throw "ABORT: visual smoke runner not found at $runner"
}
if (-not (Test-Path -LiteralPath $LeadApprovalReceipt -PathType Leaf)) {
    throw "ABORT: lead approval receipt not found at $LeadApprovalReceipt"
}

# Ensure Editor is not already running
if (Test-EditorRunning) {
    throw 'ABORT: close UnrealEditor before acquiring C-1155 locks'
}

# 2. Strict Lead approval receipt validation per [X-2584] and [X-2585]
$approvalRaw = Get-Content -LiteralPath $LeadApprovalReceipt -Raw -Encoding utf8
$approval = $approvalRaw | ConvertFrom-Json
if (-not $approval) {
    throw "ABORT: could not parse lead approval receipt JSON from $LeadApprovalReceipt"
}

# Exact APPROVED AND accepted attestation required (no permissive OR)
if ($approval.status -cne 'APPROVED' -or $approval.result -cne 'PASS' -or $approval.accepted -ne $true) {
    throw "ABORT: lead approval receipt does not attest an approved state (requires status==APPROVED AND result==PASS AND accepted==true; got status='$($approval.status)', result='$($approval.result)', accepted=$($approval.accepted))"
}

# Mandatory map match
if (-not $approval.map -or $approval.map -cne '/Game/OneBossFight/Maps/L_SevarogArena') {
    throw "ABORT: lead approval receipt map mismatch or missing (expected '/Game/OneBossFight/Maps/L_SevarogArena', got '$($approval.map)')"
}

# Mandatory run token in approval envelope
if (-not $approval.run_token -or [string]::IsNullOrWhiteSpace($approval.run_token)) {
    throw "ABORT: lead approval receipt missing mandatory bound run_token"
}
$token = [string]$approval.run_token

# Source-hash binding check including the runner script itself per [X-2585]
$lockedHashes = [ordered]@{
    runner = (Get-FileHash -LiteralPath $runner -Algorithm SHA256).Hash
    driver = (Get-FileHash -LiteralPath $driver -Algorithm SHA256).Hash
    retarget_cpp = (Get-FileHash -LiteralPath $sourceRetargetCpp -Algorithm SHA256).Hash
    moves_cpp = (Get-FileHash -LiteralPath $sourceMovesCpp -Algorithm SHA256).Hash
}

if (-not $approval.source_hashes) {
    throw "ABORT: lead approval receipt missing mandatory source_hashes block"
}
if (-not $approval.source_hashes.runner -or $approval.source_hashes.runner -cne $lockedHashes.runner) {
    throw "ABORT: runner source hash mismatch with lead approval receipt (expected '$($lockedHashes.runner)', got '$($approval.source_hashes.runner)')"
}
if (-not $approval.source_hashes.driver -or $approval.source_hashes.driver -cne $lockedHashes.driver) {
    throw "ABORT: driver source hash mismatch with lead approval receipt (expected '$($lockedHashes.driver)', got '$($approval.source_hashes.driver)')"
}
if (-not $approval.source_hashes.retarget_cpp -or $approval.source_hashes.retarget_cpp -cne $lockedHashes.retarget_cpp) {
    throw "ABORT: retarget cpp source hash mismatch with lead approval receipt (expected '$($lockedHashes.retarget_cpp)', got '$($approval.source_hashes.retarget_cpp)')"
}
if (-not $approval.source_hashes.moves_cpp -or $approval.source_hashes.moves_cpp -cne $lockedHashes.moves_cpp) {
    throw "ABORT: moves cpp source hash mismatch with lead approval receipt (expected '$($lockedHashes.moves_cpp)', got '$($approval.source_hashes.moves_cpp)')"
}

# Record baseline config hash to guarantee no configuration mutation
$originalConfigHash = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash

# C-1155 Two-lock discipline per [X-2593] and [X-2594]
# Refuse existing locks before acquiring
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: existing lock $lock" } }

$editorProcess = $null
$hasTimedOut = $false
$cleanupFailures = [System.Collections.Generic.List[string]]::new()

try {
    # 1. Atomically acquire both locks under try/finally protection per [X-2594]
    foreach ($lock in $locks) { Acquire-Lock $lock }

    # 2. Recheck Editor state immediately after locking
    if (Test-EditorRunning) { throw 'ABORT: UnrealEditor appeared during lock acquisition' }

    # 3. Re-verify source hashes after lock acquisition to guarantee zero modification
    $postLockHashes = [ordered]@{
        runner = (Get-FileHash -LiteralPath $runner -Algorithm SHA256).Hash
        driver = (Get-FileHash -LiteralPath $driver -Algorithm SHA256).Hash
        retarget_cpp = (Get-FileHash -LiteralPath $sourceRetargetCpp -Algorithm SHA256).Hash
        moves_cpp = (Get-FileHash -LiteralPath $sourceMovesCpp -Algorithm SHA256).Hash
    }
    if ($postLockHashes.runner -cne $lockedHashes.runner -or
        $postLockHashes.driver -cne $lockedHashes.driver -or
        $postLockHashes.retarget_cpp -cne $lockedHashes.retarget_cpp -or
        $postLockHashes.moves_cpp -cne $lockedHashes.moves_cpp) {
        throw "ABORT: runtime sources changed after lock acquisition"
    }

    # 4. Prepare run directory using bound token
    $runDir = Join-Path $root ('Saved\GreystoneVisualSmoke\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0, [Math]::Min(8, $token.Length)))
    New-Item -ItemType Directory -Path $runDir -Force | Out-Null
    $log = Join-Path $runDir 'editor.log'
    $receipt = Join-Path $runDir 'receipt.json'

    Write-Host "[RunGreystoneSmoke] Preparing opt-in visual smoke in L_SevarogArena..."
    Write-Host "[RunGreystoneSmoke] RunDir: $runDir"
    Write-Host "[RunGreystoneSmoke] Token:  $token"

    $env:GREYSTONE_SMOKE_RUN_TOKEN = $token
    $env:GREYSTONE_SMOKE_RECEIPT = $receipt
    $env:GREYSTONE_SMOKE_LOG = $log
    $env:GREYSTONE_SMOKE_SOURCE_HASHES = ($lockedHashes | ConvertTo-Json -Compress)

    $editorArgs = @(
        $project,
        "-ExecutePythonScript=$driver",
        "-nosplash",
        "-nosound",
        "-abslog=$log"
    )

    $editorProcess = Start-Process -FilePath $editor -ArgumentList $editorArgs -WorkingDirectory $root -PassThru -WindowStyle Normal
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)

    while ($true) {
        $editorProcess.Refresh()
        $receiptExists = Test-Path -LiteralPath $receipt -PathType Leaf
        if ($receiptExists) {
            Write-Host "[RunGreystoneSmoke] Receipt observed on disk."
            break
        }
        if ($editorProcess.HasExited) {
            Write-Host "[RunGreystoneSmoke] Editor process exited."
            break
        }
        if ([DateTime]::UtcNow -ge $deadline) {
            $hasTimedOut = $true
            Write-Host "[RunGreystoneSmoke] Execution reached timeout deadline ($TimeoutSeconds s)."
            break
        }
        Start-Sleep -Milliseconds 250
    }

    # Per [X-2584]: remove force-Kill fallback, retain timed-out owned process and report recovery-needed
    if ($editorProcess -and (-not $editorProcess.HasExited)) {
        Start-Sleep -Seconds 1
        $editorProcess.Refresh()
        if (-not $editorProcess.HasExited) {
            [void]$editorProcess.CloseMainWindow()
            if (-not $editorProcess.WaitForExit(10000)) {
                Write-Warning "[RunGreystoneSmoke] RECOVERY_NEEDED: Editor process $($editorProcess.Id) failed to exit cleanly within 10s of CloseMainWindow; retained without force-kill for diagnostic recovery"
            }
        }
    }
}
finally {
    # 1. Clean up temporary files
    foreach ($temp in $createdTemps) { try { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } } catch {} }

    # 2. Check Editor process state per [X-2593]
    if ($editorProcess) {
        try {
            $editorProcess.Refresh()
            if (-not $editorProcess.HasExited) { [void]$editorProcess.CloseMainWindow(); [void]$editorProcess.WaitForExit(10000) }
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

    # 3. Verify DefaultGame.ini hash BEFORE releasing locks per [X-2595] and [X-2596]
    $configUnchanged = $false
    $configError = $null
    if ($originalConfigHash) {
        try {
            $currentConfigHash = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
            if ($currentConfigHash -cne $originalConfigHash) {
                $configError = "DefaultGame.ini was modified during smoke run (expected '$originalConfigHash', got '$currentConfigHash')"
                Write-Warning "[RunGreystoneSmoke] CRITICAL: $configError!"
            } else {
                $configUnchanged = $true
                Write-Host "[RunGreystoneSmoke] Verified DefaultGame.ini unchanged (hash match)."
            }
        } catch {
            $configError = "DefaultGame.ini integrity unverified (hash read failed: $($_.Exception.Message))"
            Write-Warning "[RunGreystoneSmoke] CRITICAL: $configError!"
        }
    }

    # 4. Release locks ONLY if Editor is not running AND config is verified unchanged per [X-2593], [X-2595], and [X-2596]
    $released = 0
    $kept = [System.Collections.Generic.List[string]]::new()
    if ($editorStillRunning) {
        $kept.Add('Editor is still running; owned locks intentionally retained')
        $editorPidStr = if ($editorProcess) { [string]$editorProcess.Id } else { 'external' }
        $msg = "Editor process $editorPidStr is still running; owned C-1155 locks retained"
        $cleanupFailures.Add("RECOVERY_NEEDED: $msg")
        Write-Warning "[RunGreystoneSmoke] RECOVERY_NEEDED: $msg"
    } elseif (-not $configUnchanged) {
        $kept.Add('DefaultGame.ini integrity unverified or modified; owned locks intentionally retained for recovery')
        $msg = "DefaultGame.ini integrity unverified or modified ($configError); owned C-1155 locks retained without auto-overwrite for diagnostic recovery"
        $cleanupFailures.Add("RECOVERY_NEEDED: $msg")
        Write-Warning "[RunGreystoneSmoke] RECOVERY_NEEDED: $msg"
    } else {
        foreach ($lock in $createdLocks) {
            try {
                if (Test-Path -LiteralPath $lock) {
                    $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                    if ($current.owner_token -ceq $token) { Remove-Item -LiteralPath $lock -Force; $released++ }
                    else {
                        $kept.Add($lock + ' owner token mismatch')
                        $cleanupFailures.Add("Lock $lock owner token mismatch; lock retained")
                    }
                }
            } catch {
                $kept.Add($lock + ' release failed: ' + $_.Exception.Message)
                $cleanupFailures.Add("Lock $lock release failed: $($_.Exception.Message)")
            }
        }
    }

    # 5. Clear environment variables (always executes per [X-2595] and [X-2596])
    Remove-Item Env:\GREYSTONE_SMOKE_RUN_TOKEN -ErrorAction SilentlyContinue
    Remove-Item Env:\GREYSTONE_SMOKE_RECEIPT -ErrorAction SilentlyContinue
    Remove-Item Env:\GREYSTONE_SMOKE_LOG -ErrorAction SilentlyContinue
    Remove-Item Env:\GREYSTONE_SMOKE_SOURCE_HASHES -ErrorAction SilentlyContinue
}

# Surface cleanup/recovery failure if any occurred during finally per [X-2596]
if ($cleanupFailures.Count -gt 0) {
    throw "FAIL: Cleanup/recovery errors detected: $($cleanupFailures -join '; ')"
}

if ($hasTimedOut) {
    throw "TIMEOUT: Greystone visual smoke run timed out after $TimeoutSeconds seconds"
}

if (-not (Test-Path -LiteralPath $receipt -PathType Leaf)) {
    throw "FAIL: Receipt file was not created: $receipt"
}

# 3. Verify resulting receipt bindings, source hashes, and criteria per [X-2584] and [X-2585]
$receiptData = Get-Content -LiteralPath $receipt -Raw -Encoding utf8 | ConvertFrom-Json
if (-not $receiptData) {
    throw "ABORT: could not parse smoke receipt JSON from $receipt"
}

Write-Host "[RunGreystoneSmoke] Result: $($receiptData.result) Accepted: $($receiptData.accepted)"

if ($receiptData.run_token -cne $token) {
    throw "FAIL: receipt run_token mismatch (expected '$token', got '$($receiptData.run_token)')"
}
if ($receiptData.map -cne '/Game/OneBossFight/Maps/L_SevarogArena') {
    throw "FAIL: receipt map mismatch (expected '/Game/OneBossFight/Maps/L_SevarogArena', got '$($receiptData.map)')"
}
if ($receiptData.result -cne 'PASS') {
    throw "FAIL: receipt result is not PASS ($($receiptData.result))"
}
if ($receiptData.accepted -ne $true) {
    throw "FAIL: receipt accepted flag is false"
}

# Source-hashes verification in receipt per [X-2585]
if (-not $receiptData.source_hashes) {
    throw "FAIL: receipt missing source_hashes binding block"
}
if ($receiptData.source_hashes.runner -cne $lockedHashes.runner) {
    throw "FAIL: receipt runner hash mismatch (expected '$($lockedHashes.runner)', got '$($receiptData.source_hashes.runner)')"
}
if ($receiptData.source_hashes.driver -cne $lockedHashes.driver) {
    throw "FAIL: receipt driver hash mismatch (expected '$($lockedHashes.driver)', got '$($receiptData.source_hashes.driver)')"
}
if ($receiptData.source_hashes.retarget_cpp -cne $lockedHashes.retarget_cpp) {
    throw "FAIL: receipt retarget_cpp hash mismatch (expected '$($lockedHashes.retarget_cpp)', got '$($receiptData.source_hashes.retarget_cpp)')"
}
if ($receiptData.source_hashes.moves_cpp -cne $lockedHashes.moves_cpp) {
    throw "FAIL: receipt moves_cpp hash mismatch (expected '$($lockedHashes.moves_cpp)', got '$($receiptData.source_hashes.moves_cpp)')"
}

# Criteria verification
$criteria = $receiptData.criteria
if (-not $criteria.exact_pawn_possessed -or $criteria.exact_pawn_possessed -ne $true) {
    throw "FAIL: exact_pawn_possessed criterion failed"
}
if (-not $criteria.source_mesh_hidden -or $criteria.source_mesh_hidden -ne $true) {
    throw "FAIL: source_mesh_hidden criterion failed"
}
if (-not $criteria.runtime_visual_visible -or $criteria.runtime_visual_visible -ne $true) {
    throw "FAIL: runtime_visual_visible criterion failed"
}
if (-not $criteria.log_monitored_continuous -or $criteria.log_monitored_continuous -ne $true) {
    throw "FAIL: log_monitored_continuous criterion failed"
}
if (-not $criteria.zero_get_main_anim_bp_errors -or $criteria.zero_get_main_anim_bp_errors -ne $true) {
    throw "FAIL: zero_get_main_anim_bp_errors criterion failed"
}
if (-not $criteria.cvar_restored_zero -or $criteria.cvar_restored_zero -ne $true) {
    throw "FAIL: cvar_restored_zero criterion failed"
}

# Real readback value check per [X-2585]
if ($receiptData.observations.cleanup.cvar_readback_value -cne '0') {
    throw "FAIL: cvar real readback value is not '0' ($($receiptData.observations.cleanup.cvar_readback_value))"
}

Write-Host "[RunGreystoneSmoke] Possessed: $($receiptData.observations.possessed_pawn.class)"
Write-Host "[RunGreystoneSmoke] Errors (GetMainAnimBP): $($receiptData.observations.get_main_anim_bp_errors)"
Write-Host "[RunGreystoneSmoke] Log monitoring: bytes=$($receiptData.observations.log_monitored.total_bytes_read) reads=$($receiptData.observations.log_monitored.read_count)"
Write-Host "[RunGreystoneSmoke] CVar readback: $($receiptData.observations.cleanup.cvar_readback_value)"
Write-Host "[RunGreystoneSmoke] Visual art review: $($receiptData.visual_art_judgment.status)"

exit 0
