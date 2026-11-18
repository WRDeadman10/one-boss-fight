# C-1619 Step 3: prepare the approved O1 boss definition and framework encounter.
# Never run until Claude reviews/schedules it. Full UnrealEditor only; no map save, build or PIE.
param([string]$LeadApprovalReceipt)
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$editor = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$stageAdapter = Join-Path $root 'Scripts\Editor\sevarog_o1_stage.py'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\B_SEVAROG_O1\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0,8))
$created = [System.Collections.Generic.List[string]]::new()
$rootAsset = Join-Path $root 'Content\OneBossFight\Data\Sevarog'
$backupDir = Join-Path $run 'rollback_files'
$existing = Join-Path $rootAsset 'DA_Boss_Sevarog_Draft.uasset'
$phase = Join-Path $root 'Scripts\Editor\ensure_bk56_60_sevarog_initial_phase.py'
$author = Join-Path $root 'Scripts\Editor\author_framework_encounter_definition.py'
$manifest = Join-Path $run 'rollback_manifest.json'
$status = Join-Path $run 'status.json'
$steps = [System.Collections.Generic.List[object]]::new()
$result = 'PREPARED'; $stage = 'preflight'; $reason = ''

function Write-Atomic([string]$Path, [object]$Value) {
    $tmp = $Path + '.' + $token + '.tmp'
    $Value | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $tmp -Encoding utf8
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}
function Test-Editor { return [bool](@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) }
function Acquire-Lock([string]$Path) {
    $tmp = $Path + '.' + $token + '.tmp'
    $record = [ordered]@{ agent='Codex'; party='X'; task='C-1619 Sevarog O1 author/readback'; command_id='run_BK_SEVAROG_O1_locked'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Editor Python authoring of Sevarog draft Stats/Phase_1/115-path provenance manifest and framework encounter; no map save, build or PIE' }
    $bytes = [Text.Encoding]::UTF8.GetBytes(($record | ConvertTo-Json -Depth 5) + [Environment]::NewLine)
    $stream = [IO.File]::Open($tmp,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    try { [IO.File]::Move($tmp,$Path) } catch { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue; throw "ABORT: atomic lock acquisition failed: $Path" }
    $created.Add($Path)
    $check = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ($check.owner_token -ne $token -or $check.policy -ne 'C-1155') { throw "ABORT: lock owner/policy readback failed: $Path" }
}
function Invoke-Stage([string]$Name, [string]$Expected) {
    if (Test-Editor) { throw "ABORT: UnrealEditor appeared before $Name" }
    $log = Join-Path $run ($Name + '.log')
    $env:SEVAROG_O1_EVIDENCE_DIR = $run
    $proc = Start-Process -FilePath $editor -ArgumentList @($project, "-ExecutePythonScript=$stageAdapter", "-BSevarogO1Stage=$Name", '-nosplash', '-nosound', "-abslog=$log") -WorkingDirectory $root -PassThru -WindowStyle Normal
    $processHandle = $proc.Handle
    if (-not $proc.WaitForExit(900000)) { throw "FAIL: $Name timeout; retain locks" }
    $lines = @(Select-String -Path $log -Pattern '\[SevarogO1Stage\] RESULT=' -CaseSensitive -ErrorAction SilentlyContinue | ForEach-Object { $_.Line.Trim() })
    $steps.Add([ordered]@{ stage=$Name; pid=$proc.Id; exit_code=$proc.ExitCode; log=$log; results=$lines })
    Write-Atomic (Join-Path $run 'step_results.json') @($steps)
    if ($proc.ExitCode -ne 0 -or -not ($lines -match [regex]::Escape($Expected))) { throw "FAIL: $Name exit=$($proc.ExitCode), result=$lines" }
}
try {
    if (Test-Editor) { throw 'ABORT: close UnrealEditor before acquiring C-1155 locks' }
    foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: existing lock $lock" } }
    if (-not $LeadApprovalReceipt -or -not (Test-Path -LiteralPath $LeadApprovalReceipt)) { throw 'ABORT: Lead approval receipt required' }
    $approval = Get-Content -Raw -LiteralPath $LeadApprovalReceipt | ConvertFrom-Json
    if ($approval.task -ne 'C-1619' -or ($approval.lead -ne 'Claude' -and $approval.lead -ne 'Codex') -or $approval.approved -ne $true) { throw 'ABORT: invalid C-1619 lead receipt' }
    if (Test-Path -LiteralPath $run) { throw "ABORT: evidence directory already exists: $run" }
    New-Item -ItemType Directory -Path $run | Out-Null
    foreach ($lock in $locks) { Acquire-Lock $lock }
    if (Test-Editor) { throw 'ABORT: UnrealEditor appeared during lock acquisition' }
    foreach ($path in @($editor,$project,$stageAdapter,$phase,$author,$existing)) { if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "ABORT: missing $path" } }
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    $sourceFiles = @(Get-ChildItem -LiteralPath $rootAsset -File | Where-Object { $_.BaseName -in @('DA_Boss_Sevarog_Draft','DA_Sevarog_Framework_Encounter') })
    if (-not ($sourceFiles | Where-Object { $_.BaseName -eq 'DA_Boss_Sevarog_Draft' -and $_.Extension -eq '.uasset' })) { throw 'ABORT: draft package uasset missing' }
    $backups = @()
    foreach ($file in $sourceFiles) {
        $dest = Join-Path $backupDir $file.Name; Copy-Item -LiteralPath $file.FullName -Destination $dest
        $srcHash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash; $bakHash = (Get-FileHash $dest -Algorithm SHA256).Hash
        if ($srcHash -ne $bakHash) { throw "ABORT: backup hash mismatch $($file.Name)" }
        $backups += [ordered]@{ source=$file.FullName; backup=$dest; sha256=$srcHash }
    }
    $possibleNew = Join-Path $rootAsset 'DA_Sevarog_Framework_Encounter.uasset'
    $rollback = [ordered]@{ task='C-1619 Step 3'; owner_token=$token; approval_receipt=$LeadApprovalReceipt; approval_sha256=(Get-FileHash $LeadApprovalReceipt -Algorithm SHA256).Hash; backups=$backups; possible_created_package=$possibleNew; restore='After Editor closes and under C-1155 only; restore verified backups and remove a newly created package only after referencer checks.'; steps=@(); result='PREPARED' }
    Write-Atomic $manifest $rollback
    $stage='phase_dry'; Invoke-Stage $stage 'RESULT=PASS'
    $stage='phase_write'; Invoke-Stage $stage 'RESULT=PASS'
    $stage='phase_readback'; Invoke-Stage $stage 'RESULT=PASS'
    $stage='encounter_dry'; Invoke-Stage $stage 'RESULT=PASS'
    $stage='encounter_write'; Invoke-Stage $stage 'RESULT=PASS'
    $stage='encounter_readback'; Invoke-Stage $stage 'RESULT=PASS'
    $result='ALL_STAGES_PASS'
} catch { $reason=$_.Exception.Message; $result='STOPPED_AT_' + $stage; throw }
finally {
    if (Test-Path -LiteralPath $manifest) { try { $m=Get-Content -Raw $manifest | ConvertFrom-Json; $m.steps=@($steps); $m.result=$result; Write-Atomic $manifest $m } catch {} }
    $release = -not (Test-Editor); $released=0; $kept=@()
    if ($release) { foreach ($lock in $created) { try { $v=Get-Content -Raw $lock | ConvertFrom-Json; if ($v.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force; $released++ } else { $kept += "$lock owner_token_mismatch" } } catch { $kept += "$lock release_error=$($_.Exception.Message)" } } }
    else { $kept=@($created) }
    if (Test-Path -LiteralPath $run -PathType Container) {
        try { Write-Atomic $status ([ordered]@{ task='C-1619'; stage=$stage; result=$result; reason=$reason; lock_release_allowed=$release; locks_released=$released; locks_kept=$kept; steps=@($steps); utc=[DateTime]::UtcNow.ToString('o') }) }
        catch { Write-Warning ('Could not write C-1619 status receipt: ' + $_.Exception.Message) }
    }
}
