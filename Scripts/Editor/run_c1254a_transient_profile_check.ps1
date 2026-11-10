$ErrorActionPreference = 'Stop'
$project = 'C:\UnrealProject\OneBossFight\OneBossFight.uproject'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$scriptPath = 'C:\UnrealProject\OneBossFight\Scripts\Editor\pie_sevarog_framework_live.py'
$evidence = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\C1254A_LIVE_PROFILE_CHECK'
$locks = @(
    'C:\UnrealProject\OneBossFight\ENGINE_LOCK.json',
    'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\ENGINE_LOCK.json'
)
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: engine lock exists: $lock" } }
$owned = @(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($owned.Count -gt 0) { throw 'ABORT: project UnrealEditor process is running' }
if (-not (Test-Path -LiteralPath 'C:\UnrealProject\OneBossFight\Content\OneBossFight\Data\Sevarog\DA_Boss_Sevarog_FrameworkProfile_Draft.uasset')) {
    throw 'ABORT: Lead-authored framework profile asset is missing'
}
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='C-1254a'; command_id='C1254A.transient-profile-check'; owner_token=$token; start_utc=(Get-Date).ToUniversalTime().ToString('o'); policy='C-1155' } | ConvertTo-Json
$createdLocks = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($lock in $locks) {
        $stream = [System.IO.File]::Open($lock, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try {
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($record + [Environment]::NewLine)
            $stream.Write($bytes, 0, $bytes.Length)
        } finally { $stream.Dispose() }
        $createdLocks.Add($lock)
    }

    $env:SEVAROG_LIVE_TRANSIENT_CHECK = '1'
    try {
        $log = Join-Path $evidence 'profile-check.log'
        & "$engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project "-ExecutePythonScript=$scriptPath" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$log" *> (Join-Path $evidence 'stdout.log')
        $exitCode = $LASTEXITCODE
    } finally { Remove-Item Env:\SEVAROG_LIVE_TRANSIENT_CHECK -ErrorAction SilentlyContinue }

    $profilePass = (Select-String -Path $log,(Join-Path $evidence 'stdout.log') -Pattern '\[SevarogLive\] PROFILE PASS' -ErrorAction SilentlyContinue).Count
    $bridge = (Select-String -Path $log,(Join-Path $evidence 'stdout.log') -Pattern '\[SevarogLive\] LIVE_API PASS initialize_with_profile_for_test=1 start_card_for_test=1' -ErrorAction SilentlyContinue).Count
    $finished = (Select-String -Path $log,(Join-Path $evidence 'stdout.log') -Pattern '\[SevarogLive\] finished: transient profile and bridge reflection check only' -ErrorAction SilentlyContinue).Count
    $status = "EXIT=$exitCode`nPROFILE_PASS=$profilePass`nBRIDGE_PASS=$bridge`nTRANSIENT_FINISHED=$finished`nFULL_PIE=0`nSPAWNED=0`nMAP_SAVED=0"
    Set-Content (Join-Path $evidence 'status.txt') $status
    Write-Output $status
    if ($exitCode -ne 0 -or $profilePass -eq 0 -or $bridge -eq 0 -or $finished -eq 0) {
        Get-Content (Join-Path $evidence 'stdout.log') -Tail 80
        Get-Content $log -Tail 80
        throw 'C-1254a transient profile/bridge reflection check failed'
    }
} finally {
    foreach ($lock in $createdLocks) {
        if (Test-Path -LiteralPath $lock) {
            try {
                $existing = Get-Content -LiteralPath $lock -Raw | ConvertFrom-Json
                if ($existing.owner_token -eq $token) { Remove-Item -LiteralPath $lock }
            } catch { Write-Warning "Could not verify lock ownership before cleanup: $lock" }
        }
    }
}
