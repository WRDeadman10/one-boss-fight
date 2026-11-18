$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root 'Scripts\Editor\author_greystone_player.py'
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1257A_GREYSTONE_WRITE'
$log = Join-Path $evidence 'editor_raw.log'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Claude'; party='C'; task='C-1265a'; command_id='C1265A.greystone-author-write'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Lead-run authoring of 4 Greystone montage wrappers and child BP under /Game/OneBossFight/Player/Greystone only; saved-package readback; rollback only assets created by this invocation' } | ConvertTo-Json
$created = [System.Collections.Generic.List[string]]::new()
$proc = $null
try {
    foreach ($lock in $locks) {
        $stream = [System.IO.File]::Open($lock,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[System.Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
        $created.Add($lock)
    }
    $fso = New-Object -ComObject Scripting.FileSystemObject
    $short = $fso.GetFile($script).ShortPath.ToLower() -replace '\\','/'
    $execCmd = '-ExecCmds="py ' + $short + ' --write"'
    $proc = Start-Process -FilePath $engine -PassThru -WindowStyle Hidden -ArgumentList @($project,$execCmd,'-nosound','-nosplash','-unattended',"-abslog=$log")
    $deadline = [DateTime]::UtcNow.AddMinutes(15)
    while ([DateTime]::UtcNow -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Seconds 2
        if ((Test-Path -LiteralPath $log) -and (Select-String -Path $log -Pattern '\[GreystoneER\] ERROR|ROLLBACK_REMAINS|ROLLBACK_DELETE_FAILED|ROLLBACK_FATAL' -Quiet)) { break }
    }
    if (-not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    $logText = if (Test-Path -LiteralPath $log) { Get-Content -Raw -LiteralPath $log } else { '' }
    $expected = @(
        'MODE=WRITE',
        'NOTIFY_READBACK AM_ER_Backstep_Mixamo_V2_Fit_Greystone',
        'NOTIFY_READBACK AM_ER_Attack_Air_Light_Fit_Greystone',
        'NOTIFY_READBACK AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone',
        'NOTIFY_READBACK AM_ER_Attack_GuardCounter_Fit_Greystone',
        'CHILD_BP_SAVED=/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer.BP_GreystoneERPlayer',
        'PACKAGE_RELOADED path=/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer class=Blueprint',
        'CHILD_READBACK field=QuickMontage',
        'SAVED_COUNT=5; PACKAGE_COUNT=5; PACK_PATH_WRITES=0; DEFAULT_PLAYER_UNCHANGED=1'
    )
    $checks = foreach ($item in $expected) { "$($item -replace '[^A-Za-z0-9]+','_')=$($logText.Contains($item))" }
    $status = @('EDITOR_EXITED=' + $proc.HasExited,'EDITOR_EXIT_CODE=' + $proc.ExitCode) + $checks + @(
        'ERROR=' + $logText.Contains('[GreystoneER] ERROR'),
        'ROLLBACK=' + $logText.Contains('ROLLBACK_RECEIPT'),
        'ASSET_ALLOWLIST=/Game/OneBossFight/Player/Greystone/')
    $status -join [Environment]::NewLine | Set-Content -LiteralPath (Join-Path $evidence 'status.txt')
    $status
    if ($logText.Contains('[GreystoneER] ERROR') -or $logText.Contains('ROLLBACK_REMAINS') -or $logText.Contains('ROLLBACK_DELETE_FAILED') -or $logText.Contains('ROLLBACK_FATAL') -or -not $logText.Contains('SAVED_COUNT=5; PACKAGE_COUNT=5; PACK_PATH_WRITES=0; DEFAULT_PLAYER_UNCHANGED=1')) { Get-Content $log -Tail 120; throw 'C-1257a authoring/readback failed or incomplete; inspect the script rollback receipt' }
} finally {
    if ($proc -and -not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'lock_result.txt')
}
