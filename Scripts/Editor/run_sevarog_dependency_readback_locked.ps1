# Read-only C-1155 diagnostic of the saved Sevarog definition's soft dependencies.
# No PIE, build, config change, asset save, package, or cook.
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$editor = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$driver = Join-Path $root 'Scripts\Editor\read_sevarog_definition_dependencies.py'
$assetPackage = Join-Path $root 'Content\OneBossFight\Data\Sevarog\DA_Boss_Sevarog_Draft.uasset'
$config = Join-Path $root 'Config\DefaultGame.ini'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\SevarogDependencyReadback\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0,8))
$log = Join-Path $run 'editor.log'
$receipt = Join-Path $run 'dependency_readback.json'
$statusPath = Join-Path $run 'status.json'
$created = [System.Collections.Generic.List[string]]::new()
$temps = [System.Collections.Generic.List[string]]::new()
$editorProcess = $null
$stage = 'preflight'
$reason = ''
$assetHashBefore = ''
$assetHashAfter = ''
$configHashBefore = ''
$configHashAfter = ''
$receiptData = $null
$editorExit = 'not-run'

function Test-UnrealRunning {
    return [bool](@(Get-Process -Name UnrealEditor, UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count -gt 0)
}
function Write-AtomicLock([string]$Path) {
    $temp = $Path + '.' + $token + '.tmp'
    $temps.Add($temp)
    $record = [ordered]@{agent='Codex';party='X';task='BT-17 Sevarog dependency readback';command_id='BT17.sevarog-dependency-readback';owner_token=$token;pid=$PID;start_utc=[DateTime]::UtcNow.ToString('o');policy='C-1155';scope='Read-only saved definition skeleton/animation reference readback; no PIE/build/config/assets'} | ConvertTo-Json -Compress
    $stream = [IO.File]::Open($temp,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $bytes=[Text.UTF8Encoding]::new($false).GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) }
    finally { $stream.Dispose() }
    [IO.File]::Move($temp,$Path)
    $temps.Remove($temp)
    $created.Add($Path)
    $back=Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ($back.owner_token -cne $token -or $back.policy -cne 'C-1155') { throw "ABORT: lock readback mismatch: $Path" }
}

try {
    if (Test-UnrealRunning) { throw 'ABORT: close UnrealEditor before C-1155 readback' }
    foreach ($path in @($editor,$project,$driver,$assetPackage,$config)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "ABORT: required file missing: $path" }
    }
    foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: existing C-1155 lock: $lock" } }
    New-Item -ItemType Directory -Path $run | Out-Null
    $assetHashBefore = (Get-FileHash -LiteralPath $assetPackage -Algorithm SHA256).Hash
    $configHashBefore = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
    foreach ($lock in $locks) { Write-AtomicLock $lock }
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor appeared after C-1155 lock acquisition' }

    $env:SEVAROG_DEPENDENCY_READBACK_RECEIPT = $receipt
    $stage = 'editor_readback'
    $editorProcess = Start-Process -FilePath $editor -ArgumentList @($project,"-ExecutePythonScript=$driver",'-nosplash','-nosound',"-abslog=$log") -WorkingDirectory $root -PassThru -WindowStyle Normal
    $deadline = [DateTime]::UtcNow.AddSeconds(240)
    while ($true) {
        $editorProcess.Refresh()
        if ($editorProcess.HasExited -or (Test-Path -LiteralPath $receipt -PathType Leaf)) { break }
        if ([DateTime]::UtcNow -ge $deadline) { throw 'TIMEOUT: dependency readback produced no receipt within 240 seconds' }
        Start-Sleep -Milliseconds 250
    }
    if (Test-Path -LiteralPath $receipt -PathType Leaf) { $receiptData = Get-Content -Raw -LiteralPath $receipt | ConvertFrom-Json }
    if (-not $receiptData -or $receiptData.readback_complete -ne $true) { throw 'FAIL: Editor did not produce a complete dependency readback' }
    $editorProcess.Refresh()
    if (-not $editorProcess.HasExited) {
        [void]$editorProcess.CloseMainWindow()
        if (-not $editorProcess.WaitForExit(30000)) { throw 'TIMEOUT: diagnostic Editor did not close' }
    }
    $editorProcess.Refresh()
    $editorExit = $editorProcess.ExitCode
    if ($editorExit -ne 0) { throw "FAIL: diagnostic Editor exited with code $editorExit" }
    $assetHashAfter = (Get-FileHash -LiteralPath $assetPackage -Algorithm SHA256).Hash
    if ($assetHashAfter -cne $assetHashBefore) { throw 'FAIL: Sevarog definition package changed during readback' }
    $configHashAfter = (Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash
    if ($configHashAfter -cne $configHashBefore) { throw 'FAIL: DefaultGame.ini changed during readback' }
    $stage = 'done'
} catch {
    $reason = $_.Exception.Message
    throw
} finally {
    foreach ($temp in $temps) { try { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } } catch {} }
    if ($editorProcess) {
        try { $editorProcess.Refresh(); if (-not $editorProcess.HasExited) { [void]$editorProcess.CloseMainWindow(); [void]$editorProcess.WaitForExit(30000) } } catch {}
    }
    $ownedId = if ($editorProcess) { $editorProcess.Id } else { -1 }
    $editorStillRunning = [bool](@(Get-Process -Name UnrealEditor, UnrealEditor-Cmd -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne $ownedId }).Count -gt 0)
    if ($editorProcess) { try { $editorProcess.Refresh(); $editorStillRunning = $editorStillRunning -or (-not $editorProcess.HasExited) } catch { $editorStillRunning = $true } }
    if (-not $assetHashAfter -and (Test-Path -LiteralPath $assetPackage -PathType Leaf)) { try { $assetHashAfter=(Get-FileHash -LiteralPath $assetPackage -Algorithm SHA256).Hash } catch {} }
    $assetUnchanged = [bool]($assetHashBefore -and $assetHashAfter -ceq $assetHashBefore)
    if (-not $configHashAfter -and (Test-Path -LiteralPath $config -PathType Leaf)) { try { $configHashAfter=(Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash } catch {} }
    $configUnchanged = [bool]($configHashBefore -and $configHashAfter -ceq $configHashBefore)
    $released = 0; $kept = [System.Collections.Generic.List[string]]::new()
    if (-not $editorStillRunning -and $assetUnchanged) {
        foreach ($lock in $created) {
            try {
                if (Test-Path -LiteralPath $lock) {
                    $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                    if ($current.owner_token -ceq $token) { Remove-Item -LiteralPath $lock -Force; $released++ }
                    else { $kept.Add($lock+' owner token mismatch') }
                }
            } catch { $kept.Add($lock+' release failure: '+$_.Exception.Message) }
        }
    } elseif ($editorStillRunning) { $kept.Add('Editor still running; owned locks retained') }
    else { $kept.Add('asset hash unchanged could not be verified; owned locks retained') }
    $passed = ($stage -eq 'done' -and -not $editorStillRunning -and $assetUnchanged -and $configUnchanged -and $released -eq $locks.Count -and $kept.Count -eq 0)
    $status = [ordered]@{result=$(if ($passed) {'PASS'} else {'FAIL'});stage=$stage;reason=$reason;task='BT-17 Sevarog dependency readback';editor_exit=$editorExit;editor_still_running=$editorStillRunning;asset_sha256_before=$assetHashBefore;asset_sha256_after=$assetHashAfter;asset_unchanged=$assetUnchanged;config_sha256_before=$configHashBefore;config_sha256_after=$configHashAfter;config_unchanged=$configUnchanged;readback_receipt=$receipt;locks_created=$created.Count;locks_released=$released;locks_kept=@($kept);no_pie=$true;no_build=$true;no_config_change=$true;no_asset_save=$true}
    try { $status | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statusPath -Encoding UTF8; $status | ConvertTo-Json -Depth 6 } catch { Write-Warning ('Could not write readback status: '+$_.Exception.Message) }
    Remove-Item Env:\SEVAROG_DEPENDENCY_READBACK_RECEIPT -ErrorAction SilentlyContinue
}
if (-not $passed) { throw 'BT-17 readback did not pass' }
