$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$project = Join-Path $root 'OneBossFight.uproject'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$script = Join-Path $root 'Scripts\Editor\dryrun_sevarog_s6_ultimate.py'
$evidence = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\C1274_S6_DRYRUN'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'),(Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor process is running' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='BB-X11'; command_id='C1274.S6.transient-validation'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Transient-only S6 candidate card validation; no packages saved' } | ConvertTo-Json
$created = [System.Collections.Generic.List[string]]::new()
$proc = $null
try {
    foreach ($lock in $locks) {
        $stream = [System.IO.File]::Open($lock,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[System.Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length) } finally { $stream.Dispose() }
        $created.Add($lock)
    }
    $log = Join-Path $evidence 's6_dryrun.log'
    $stdout = Join-Path $evidence 's6_dryrun_stdout.log'
    $args = @($project,"-ExecutePythonScript=$script",'-unattended','-nopause','-nosplash','-nosound','-NullRHI',"-abslog=$log")
    $proc = Start-Process -FilePath (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') -ArgumentList $args -PassThru -Wait -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError (Join-Path $evidence 's6_dryrun_stderr.log')
    $pass = Select-String -Path $log -Pattern '\[SevarogS6DryRun\] PASS .*saved=0' -Quiet -ErrorAction SilentlyContinue
    $status = "EDITOR_EXIT=$($proc.ExitCode)`nS6_PASS=$pass`nNO_PACKAGES_SAVED=1`nLOCKED=1"
    Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status
    Write-Output $status
    if ($proc.ExitCode -ne 0 -or !$pass) { Get-Content $log -Tail 70; throw 'S6 transient dry-run failed.' }
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
