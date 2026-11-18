$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor.exe'
$script = Join-Path $root 'Scripts\Editor\delete_orphan_framework_maps.py'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$run = Join-Path $root ('Saved\MapCleanup\DeleteRun_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss'))
if (!(Test-Path -LiteralPath $project -PathType Leaf) -or !(Test-Path -LiteralPath $editor -PathType Leaf)) { throw 'ABORT: project or UE 5.5 editor missing.' }
if (!(Test-Path -LiteralPath $script -PathType Leaf)) { throw 'ABORT: batch deletion script missing.' }
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor is running.' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: C-1155 lock exists: $lock" } }
New-Item -ItemType Directory -Path $run -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='X-2429/2430 delete 20 unreferenced proof maps'; command_id='map_cleanup.delete_orphan_framework_maps'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Delete exactly 20 tracked FrameworkProof maps from four batches of five after manifest/hash/backup/referencer checks; preserve L_AssetProof and cited maps' } | ConvertTo-Json -Compress
$created = [System.Collections.Generic.List[string]]::new()
$proc = $null
$oldRunDir = $env:MAP_CLEANUP_RUN_DIR
try {
    foreach ($lock in $locks) {
        $temp = $lock + '.' + $token + '.tmp'
        $stream = [System.IO.File]::Open($temp,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
        [System.IO.File]::Move($temp,$lock)
        $created.Add($lock)
    }
    if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor started during lock acquisition.' }
    $env:MAP_CLEANUP_RUN_DIR = $run
    $log = Join-Path $run 'editor.log'
    $args = @($project,('-ExecutePythonScript=' + $script),'-nosound','-nosplash',("-abslog=$log"))
    $proc = Start-Process -FilePath $editor -PassThru -ArgumentList $args
    Set-Content -LiteralPath (Join-Path $run 'process.txt') -Value ("PID=$($proc.Id)`nLOG=$log`nSCRIPT=$script`nSTATUS=RUNNING_FOUR_FIVE_MAP_BATCHES")
    $deadline = [DateTime]::UtcNow.AddMinutes(25)
    while (!$proc.HasExited) {
        if ([DateTime]::UtcNow -gt $deadline) { throw 'ABORT: Unreal deletion run exceeded 25 minutes.' }
        Start-Sleep -Seconds 2
        $proc.Refresh()
    }
    $text = if (Test-Path -LiteralPath $log) { Get-Content -Raw -LiteralPath $log } else { '' }
    if (!$text.Contains('[MAP_CLEANUP_DELETE] COMPLETE deleted=20 batches=4')) { throw "Unreal deletion run did not complete; see $log" }
    $summary = Get-Content -Raw -LiteralPath (Join-Path $run 'summary.json') | ConvertFrom-Json
    if ($summary.status -cne 'COMPLETE' -or $summary.deleted_count -ne 20) { throw 'Unreal completion receipt is invalid.' }
    foreach ($batch in 1..4) {
        $receipt = Get-Content -Raw -LiteralPath (Join-Path $run ('batch_{0:D2}.json' -f $batch)) | ConvertFrom-Json
        if ($receipt.status -cne 'COMPLETE' -or $receipt.deleted.Count -ne 5) { throw "Batch $batch receipt is incomplete." }
    }
    Set-Content -LiteralPath (Join-Path $run 'status.txt') -Value "STATUS=COMPLETE`nDELETED=20`nBATCHES=4`nPRESERVED_PLAY_MAP=/Game/OneBossFight/Maps/L_SevarogArena`nBACKUPS=Saved/MapCleanupBackup_20261113"
} finally {
    if ($oldRunDir) { $env:MAP_CLEANUP_RUN_DIR = $oldRunDir } else { Remove-Item Env:MAP_CLEANUP_RUN_DIR -ErrorAction SilentlyContinue }
    if ($proc -and !$proc.HasExited) { [void]$proc.CloseMainWindow(); Start-Sleep -Seconds 5; $proc.Refresh(); if (!$proc.HasExited) { throw 'Editor still active; locks retained for safe manual recovery.' } }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -ceq $token) { [System.IO.File]::Delete($lock) } }
            catch { Write-Warning ('Could not verify lock ownership; retained: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $run 'lock_result.txt')
}
