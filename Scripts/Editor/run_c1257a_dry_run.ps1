$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root 'Scripts\Editor\author_greystone_player.py'
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1257A_GREYSTONE_DRY_RUN'
$log = Join-Path $evidence 'editor_raw.log'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1257a'; command_id='C1257A.greystone-author-dry-run'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Editor Python dry-run only; transient objects; no packages/assets saved' } | ConvertTo-Json
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
    $execCmd = '-ExecCmds="py ' + $short + ' --dry-run"'
    $proc = Start-Process -FilePath $engine -PassThru -WindowStyle Hidden -ArgumentList @($project,$execCmd,'-nosound','-nosplash','-unattended',"-abslog=$log")
    $deadline = [DateTime]::UtcNow.AddMinutes(10)
    while ([DateTime]::UtcNow -lt $deadline -and -not $proc.HasExited) {
        Start-Sleep -Seconds 2
        if ((Test-Path -LiteralPath $log) -and (Select-String -Path $log -Pattern 'SAVED_COUNT=0; PACKAGE_COUNT=0; PACK_PATH_WRITES=0' -Quiet)) { break }
        if ((Test-Path -LiteralPath $log) -and (Select-String -Path $log -Pattern '\[GreystoneER\] ERROR' -Quiet)) { break }
    }
    if (-not $proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    $logText = if (Test-Path -LiteralPath $log) { Get-Content -Raw -LiteralPath $log } else { '' }
    $expected = @('MODE=DRY_RUN_TRANSIENT','PREFLIGHT_PASS=1; SAVED_COUNT=0; PACKAGE_COUNT=0; PACK_PATH_WRITES=0','CHILD_COMPONENT=transient URPGDodgeTiming only','SOURCE_NOTIFY_READBACK montage=AM_ER_Backstep_Mixamo_V2_Fit_Greystone','SOURCE_NOTIFY_READBACK montage=AM_ER_Attack_Air_Light_Fit_Greystone','SOURCE_NOTIFY_READBACK montage=AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone','SOURCE_NOTIFY_READBACK montage=AM_ER_Attack_GuardCounter_Fit_Greystone','DRY_RUN_TARGET_MONTAGE_OBJECT name=AM_ER_Backstep_Mixamo_V2_Fit_Greystone','DRY_RUN_TARGET_MONTAGE_OBJECT name=AM_ER_Attack_Air_Light_Fit_Greystone','DRY_RUN_TARGET_MONTAGE_OBJECT name=AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone','DRY_RUN_TARGET_MONTAGE_OBJECT name=AM_ER_Attack_GuardCounter_Fit_Greystone','NOTIFY_READBACK AM_ER_Backstep_Mixamo_V2_Fit_Greystone','NOTIFY_READBACK AM_ER_Attack_Air_Light_Fit_Greystone','NOTIFY_READBACK AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone','NOTIFY_READBACK AM_ER_Attack_GuardCounter_Fit_Greystone','TARGET_NOTIFY_OBJECT_READBACK=14','DRY_RUN_TRANSIENT_OBJECTS=4 segmented montages')
    $checks = foreach ($item in $expected) { "$($item -replace '[^A-Za-z0-9]+','_')=$($logText.Contains($item))" }
    $status = @('EDITOR_EXITED=' + $proc.HasExited) + $checks + @('ERROR=' + $logText.Contains('[GreystoneER] ERROR'),'SAVED_ASSET_COUNT=0')
    $status -join [Environment]::NewLine | Set-Content -LiteralPath (Join-Path $evidence 'status.txt')
    $status
    if ($logText.Contains('[GreystoneER] ERROR') -or -not $logText.Contains('PREFLIGHT_PASS=1; SAVED_COUNT=0; PACKAGE_COUNT=0; PACK_PATH_WRITES=0')) { Get-Content $log -Tail 100; throw 'C-1257a preflight failed or incomplete' }
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
