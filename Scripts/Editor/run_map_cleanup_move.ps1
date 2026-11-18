$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor.exe'
$script = Join-Path $root 'Scripts\Editor\move_arena_to_maps.py'
$source = Join-Path $root 'Content\OneBossFight\Levels\L_SevarogArena.umap'
$destination = Join-Path $root 'Content\OneBossFight\Maps\L_SevarogArena.umap'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$run = Join-Path $root ('Saved\MapCleanup\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss'))
if (!(Test-Path -LiteralPath $project -PathType Leaf) -or !(Test-Path -LiteralPath $editor -PathType Leaf)) { throw 'ABORT: project or UE 5.5 editor missing.' }
if (!(Test-Path -LiteralPath $script -PathType Leaf) -or !(Test-Path -LiteralPath $source -PathType Leaf)) { throw 'ABORT: move script or source map missing.' }
if (Test-Path -LiteralPath $destination) { throw 'ABORT: destination map already exists.' }
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor is running.' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: C-1155 lock exists: $lock" } }
New-Item -ItemType Directory -Path $run -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='X-2429/2430 playable arena map organization'; command_id='map_cleanup.move_arena_to_maps'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Unreal-supported move of L_SevarogArena to Maps with redirector; preserve all proof maps' } | ConvertTo-Json -Compress
$created = [System.Collections.Generic.List[string]]::new()
$proc = $null
try {
    foreach ($lock in $locks) {
        $temp = $lock + '.' + $token + '.tmp'
        $stream = [System.IO.File]::Open($temp,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
        [System.IO.File]::Move($temp,$lock)
        $created.Add($lock)
    }
    if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor started during lock acquisition.' }
    $fso = New-Object -ComObject Scripting.FileSystemObject
    $short = $fso.GetFile($script).ShortPath.ToLowerInvariant() -replace '\\','/'
    $log = Join-Path $run 'editor.log'
    # This task is completed through Unreal's interactive Content Browser so
    # the operator can accept the asset rename warning and inspect the result.
    $args = @($project,'-nosound','-nosplash',("-abslog=$log"))
    $proc = Start-Process -FilePath $editor -PassThru -ArgumentList $args
    Set-Content -LiteralPath (Join-Path $run 'process.txt') -Value ("PID=$($proc.Id)`nLOG=$log`nSTATUS=WAITING_FOR_NORMAL_EDITOR_CLOSE_AFTER_PYTHON_SCRIPT")
    while (!$proc.HasExited) { Start-Sleep -Seconds 2; $proc.Refresh() }
    $text = if (Test-Path -LiteralPath $log) { Get-Content -Raw -LiteralPath $log } else { '' }
    if (!(Test-Path -LiteralPath $destination)) { throw "Unreal Content Browser move did not complete; see $log" }
    if (!(Test-Path -LiteralPath $source)) { throw 'Source package/redirector is missing after move.' }
    Set-Content -LiteralPath (Join-Path $run 'status.txt') -Value "STATUS=MOVED`nSOURCE=$source`nDESTINATION=$destination`nSOURCE_REDIRECTOR_PACKAGE_PRESENT=True"
} finally {
    if ($proc -and !$proc.HasExited) { [void]$proc.CloseMainWindow(); Start-Sleep -Seconds 5; $proc.Refresh(); if (!$proc.HasExited) { throw 'Editor still active; locks retained for safe manual recovery.' } }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -ceq $token) { [System.IO.File]::Delete($lock) } }
            catch { Write-Warning ('Could not verify lock ownership; retained: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $run 'lock_result.txt')
}
