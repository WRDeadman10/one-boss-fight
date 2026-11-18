# BT-18 C-1155: inspect the saved profile, write only definition.Animations, reload/read back.
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$editor = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$driver = Join-Path $root 'Scripts\Editor\repair_sevarog_definition_animation_dependencies.py'
$asset = Join-Path $root 'Content\OneBossFight\Data\Sevarog\DA_Boss_Sevarog_Draft.uasset'
$config = Join-Path $root 'Config\DefaultGame.ini'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\BT18SevarogDependencies\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0,8))
$backupDir = Join-Path $run 'backup'
$assetBackup = Join-Path $backupDir (Split-Path $asset -Leaf)
$statusPath = Join-Path $run 'status.json'
$owned = [System.Collections.Generic.List[string]]::new()
$temps = [System.Collections.Generic.List[string]]::new()
$launched = [System.Collections.Generic.List[int]]::new()
$editorProcess = $null
$stage = 'preflight'
$reason = ''
$initialAssetHash = ''
$finalAssetHash = ''
$configHashBefore = ''
$configHashAfter = ''
$inspect = $null
$writeReceipt = $null
$verify = $null
$restored = $false

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
    $record = [ordered]@{agent='Codex';party='X';task='BT-18 Sevarog definition animation dependency repair';command_id='BT18.sevarog-animation-dependencies';owner_token=$token;pid=$PID;start_utc=[DateTime]::UtcNow.ToString('o');policy='C-1155';scope='Read saved profile; write only DA_Boss_Sevarog_Draft.Animations; reload/readback; rollback on failure'} | ConvertTo-Json -Compress
    $stream = [IO.File]::Open($temp,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $bytes=[Text.UTF8Encoding]::new($false).GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) }
    finally { $stream.Dispose() }
    [IO.File]::Move($temp,$Path)
    $temps.Remove($temp)
    $owned.Add($Path)
    $back=Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ($back.owner_token -cne $token -or $back.policy -cne 'C-1155') { throw "ABORT: lock readback mismatch: $Path" }
}
function Invoke-EditorAction([string]$Action, [string]$Receipt, [string]$LogPath) {
    $env:BT18_ACTION = $Action
    $env:BT18_RECEIPT = $Receipt
    $env:BT18_ASSET_HASH = $initialAssetHash
    if ($Action -eq 'verify') { $env:BT18_WRITE_RECEIPT = (Join-Path $run 'write_receipt.json') }
    else { Remove-Item Env:\BT18_WRITE_RECEIPT -ErrorAction SilentlyContinue }
    $proc = Start-Process -FilePath $editor -ArgumentList @($project,"-ExecutePythonScript=$driver",'-nosplash','-nosound',"-abslog=$LogPath") -WorkingDirectory $root -PassThru -WindowStyle Normal
    $launched.Add($proc.Id)
    $deadline = [DateTime]::UtcNow.AddMinutes(4)
    while (-not $proc.HasExited) {
        $proc.Refresh()
        if ([DateTime]::UtcNow -ge $deadline) { throw "TIMEOUT: Editor action '$Action' exceeded four minutes (PID $($proc.Id))" }
        Start-Sleep -Milliseconds 250
    }
    if ($proc.ExitCode -ne 0) { throw "FAIL: Editor action '$Action' exited $($proc.ExitCode); see $LogPath" }
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) { throw "FAIL: Editor action '$Action' emitted no receipt" }
    $data = Get-Content -Raw -LiteralPath $Receipt | ConvertFrom-Json
    if ($data.complete -ne $true -or $data.stage -cne $Action) { throw "FAIL: malformed/incomplete '$Action' receipt" }
    if (-not (Wait-UnrealClosed 45)) { throw "FAIL: Editor action '$Action' left an UnrealEditor process running after shutdown wait" }
    return $data
}

try {
    if (Test-UnrealRunning) { throw 'ABORT: close UnrealEditor before C-1155 BT-18 operation' }
    foreach ($path in @($editor,$project,$driver,$asset,$config)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "ABORT: required file missing: $path" }
    }
    foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: existing C-1155 lock: $lock" } }
    New-Item -ItemType Directory -Path $run | Out-Null
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    $initialAssetHash = (Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash
    $configHashBefore = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
    Copy-Item -LiteralPath $asset -Destination $assetBackup
    if ((Get-FileHash -LiteralPath $assetBackup -Algorithm SHA256).Hash -cne $initialAssetHash) { throw 'ABORT: backup hash mismatch' }
    foreach ($lock in $locks) { Write-AtomicLock $lock }
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor appeared after C-1155 lock acquisition' }

    $stage = 'inspect_saved_profile'
    $inspect = Invoke-EditorAction 'inspect' (Join-Path $run 'inspect_receipt.json') (Join-Path $run 'inspect.log')
    $expected = @(
        '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Medium.Swing1_Medium',
        '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium.Swing2_Medium',
        '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow.Swing3_Slow',
        '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Speedburst.Speedburst',
        '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Ultimate_Swing_120fps.Ultimate_Swing_120fps',
        '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Subjugation.Subjugation',
        '/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Soul_Siphon.Soul_Siphon'
    )
    if ($inspect.animation_paths.Count -ne 7 -or @(Compare-Object $expected @($inspect.animation_paths)).Count -ne 0) { throw 'ABORT: saved profile sequence set is not the reviewed seven-path allowlist' }
    if ($inspect.definition_hash_prewrite -cne $initialAssetHash) { throw 'ABORT: inspect was not bound to the definition preimage hash' }

    $stage = 'write_animations_only'
    $writeReceipt = Invoke-EditorAction 'write' (Join-Path $run 'write_receipt.json') (Join-Path $run 'write.log')
    $currentHash = (Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash
    if ($currentHash -ceq $initialAssetHash) { throw 'FAIL: write stage did not change the definition package' }

    $stage = 'fresh_process_readback'
    $verify = Invoke-EditorAction 'verify' (Join-Path $run 'verify_receipt.json') (Join-Path $run 'verify.log')
    $finalAssetHash = (Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash
    if ($verify.animation_count -ne 7 -or $verify.all_skeletons_match -ne $true -or $verify.non_target_fields_preserved -ne $true) { throw 'FAIL: post-save definition verification did not satisfy acceptance' }
    $configHashAfter = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
    if ($configHashAfter -cne $configHashBefore) { throw 'FAIL: DefaultGame.ini changed during BT-18' }
    $stage = 'done'
} catch {
    $reason = $_.Exception.Message
    if ((Test-UnrealRunning) -and $launched.Count -gt 0) {
        foreach ($procId in $launched) {
            $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
            if ($p -and $p.ProcessName -eq 'UnrealEditor') { try { Stop-Process -Id $procId -Force } catch {} }
        }
    }
    if ((Test-Path -LiteralPath $assetBackup -PathType Leaf) -and -not (Test-UnrealRunning)) {
        $current = (Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash
        if ($current -cne $initialAssetHash) {
            Copy-Item -LiteralPath $assetBackup -Destination $asset -Force
            $restoredHash = (Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash
            if ($restoredHash -cne $initialAssetHash) { $reason += '; rollback hash mismatch' }
            else { $restored = $true }
        }
    }
    throw
} finally {
    Remove-Item Env:\BT18_ACTION,Env:\BT18_RECEIPT,Env:\BT18_ASSET_HASH,Env:\BT18_WRITE_RECEIPT -ErrorAction SilentlyContinue
    foreach ($temp in $temps) { Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue }
    for ($index = $owned.Count - 1; $index -ge 0; $index--) {
        $lock = $owned[$index]
        if (Test-Path -LiteralPath $lock -PathType Leaf) {
            $record = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
            if ($record.owner_token -ceq $token) { Remove-Item -LiteralPath $lock -Force }
        }
    }
    $remaining = @($locks | Where-Object { Test-Path -LiteralPath $_ })
    $configHashAfter = if (Test-Path -LiteralPath $config) { (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash } else { '' }
    $finalAssetHash = if (Test-Path -LiteralPath $asset) { (Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash } else { '' }
    $summary = [ordered]@{task='BT-18';status=if ($stage -eq 'done' -and $remaining.Count -eq 0) {'PASS'} else {'FAIL'};stage=$stage;reason=$reason;initial_asset_sha256=$initialAssetHash;final_asset_sha256=$finalAssetHash;config_before_sha256=$configHashBefore;config_after_sha256=$configHashAfter;restored=$restored;inspect_receipt=$inspect;write_receipt=$writeReceipt;verify_receipt=$verify;locks_remaining=$remaining;editor_running=(Test-UnrealRunning);evidence_directory=$run}
    $summary | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $statusPath -Encoding UTF8
}
if ($stage -ne 'done' -or (Test-Path -LiteralPath $locks[0]) -or (Test-Path -LiteralPath $locks[1]) -or (Test-UnrealRunning)) { throw "BT-18 did not complete safely; see $statusPath" }
Write-Output (Get-Content -Raw -LiteralPath $statusPath)
