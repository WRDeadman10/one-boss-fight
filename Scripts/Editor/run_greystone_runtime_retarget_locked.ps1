# C-1622: C-1155 build, then author the approved runtime retarget setup.
param([Parameter(Mandatory=$true)][string]$LeadApprovalReceipt)
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$build = Join-Path $engine 'Build\BatchFiles\Build.bat'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor.exe'
$project = Join-Path $root 'OneBossFight.uproject'
$stage = Join-Path $root 'Scripts\Editor\greystone_runtime_retarget_stage.py'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\GreystoneRuntimeRetarget\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0,8))
$created = [System.Collections.Generic.List[string]]::new()
$backups = [System.Collections.Generic.List[object]]::new()
$steps = [System.Collections.Generic.List[object]]::new()
$status = Join-Path $run 'status.json'
$manifest = Join-Path $run 'rollback_manifest.json'
$result = 'PREPARED'; $stageName = 'preflight'; $reason = ''

function Write-Atomic([string]$Path, [object]$Value) {
    $tmp = $Path + '.' + $token + '.tmp'
    $Value | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $tmp -Encoding utf8
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}
function Test-Editor { return [bool](@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) }
function Acquire-Lock([string]$Path) {
    $tmp = $Path + '.' + $token + '.tmp'
    $record = [ordered]@{ agent='Codex'; party='X'; task='C-1622 Greystone runtime retarget authoring'; command_id='run_greystone_runtime_retarget_locked'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Build OneBossFightEditor then author allowlisted Greystone runtime retarget AnimBP and BP component templates; no map save or PIE' }
    $bytes = [Text.Encoding]::UTF8.GetBytes(($record | ConvertTo-Json -Depth 5) + [Environment]::NewLine)
    $stream = [IO.File]::Open($tmp,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    try { [IO.File]::Move($tmp,$Path) } catch { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue; throw "ABORT: atomic lock acquisition failed: $Path" }
    $created.Add($Path)
    $check = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ($check.owner_token -cne $token -or $check.policy -cne 'C-1155') { throw "ABORT: lock owner/policy readback failed: $Path" }
}
function Invoke-Child([string]$Name, [string]$File, [string[]]$Arguments) {
    if (Test-Editor) { throw "ABORT: UnrealEditor active before $Name" }
    $proc = Start-Process -FilePath $File -ArgumentList $Arguments -WorkingDirectory $root -PassThru -WindowStyle Hidden -RedirectStandardOutput (Join-Path $run ($Name + '.stdout.log')) -RedirectStandardError (Join-Path $run ($Name + '.stderr.log'))
    $processHandle = $proc.Handle
    if (-not $proc.WaitForExit(1800000)) { throw "FAIL: $Name timeout; retain locks" }
    $proc.Refresh()
    $entry = [ordered]@{ stage=$Name; pid=$proc.Id; exit_code=$proc.ExitCode; stdout=(Join-Path $run ($Name + '.stdout.log')); stderr=(Join-Path $run ($Name + '.stderr.log')) }
    $steps.Add($entry)
    if ($proc.ExitCode -ne 0) { throw "FAIL: $Name exit=$($proc.ExitCode)" }
}
try {
    if (Test-Editor) { throw 'ABORT: close UnrealEditor before C-1155 build/author run' }
    foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: existing lock $lock" } }
    if (-not (Test-Path -LiteralPath $LeadApprovalReceipt -PathType Leaf)) { throw 'ABORT: Claude C-1622 lead approval receipt required' }
    $approval = Get-Content -Raw -LiteralPath $LeadApprovalReceipt | ConvertFrom-Json
    if ($approval.task -ne 'C-1622' -or $approval.lead -ne 'Claude' -or $approval.approved -ne $true) { throw 'ABORT: invalid C-1622 lead receipt' }
    if (Test-Path -LiteralPath $run) { throw "ABORT: evidence folder already exists: $run" }
    New-Item -ItemType Directory -Path $run | Out-Null
    foreach ($lock in $locks) { Acquire-Lock $lock }
    if (Test-Editor) { throw 'ABORT: UnrealEditor appeared during lock acquisition' }
    foreach ($path in @($build,$editor,$project,$stage,(Join-Path $root 'Source\OneBossFightEditor\Private\RPGGreystoneRuntimeRetargetLibrary.cpp'))) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "ABORT: missing $path" }
    }
    $approvalHash = (Get-FileHash -LiteralPath $LeadApprovalReceipt -Algorithm SHA256).Hash
    $assetDir = Join-Path $root 'Content\OneBossFight\Player\Greystone'
    $backupDir = Join-Path $run 'rollback_files'
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    $targetNames = @('BP_GreystoneERPlayer','ABP_Greystone_RuntimeRetarget')
    foreach ($name in $targetNames) {
        foreach ($file in @(Get-ChildItem -LiteralPath $assetDir -File -ErrorAction SilentlyContinue | Where-Object BaseName -EQ $name)) {
            $dest = Join-Path $backupDir $file.Name
            Copy-Item -LiteralPath $file.FullName -Destination $dest
            $sourceHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
            if ((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash -cne $sourceHash) { throw "ABORT: rollback backup hash mismatch $($file.Name)" }
            $backups.Add([ordered]@{ source=$file.FullName; backup=$dest; sha256=$sourceHash })
        }
    }
    $rollback = [ordered]@{ task='C-1622'; owner_token=$token; approval_receipt=$LeadApprovalReceipt; approval_sha256=$approvalHash; backups=@($backups); possible_created_asset=(Join-Path $assetDir 'ABP_Greystone_RuntimeRetarget.uasset'); restore='After Editor closes and under C-1155 only; restore verified package sidecars after referencer review.'; result='PREPARED' }
    Write-Atomic $manifest $rollback

    $stageName='editor_build'
    $buildLog = Join-Path $run 'editor_build.log'
    & $build OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    $steps.Add([ordered]@{ stage=$stageName; pid=$PID; exit_code=$buildExit; log=$buildLog })
    if ($buildExit -ne 0) { Get-Content -LiteralPath $buildLog -Tail 120; throw "FAIL: build exit=$buildExit" }
    $stageName='author_write'
    $authorLog = Join-Path $run 'author_write.log'
    $editorArgs = @($project,"-ExecutePythonScript=$stage",'-BGreystoneRetargetWrite=1','-nosplash','-nosound',"-abslog=$authorLog")
    Invoke-Child $stageName $editor $editorArgs
    $logText = if (Test-Path -LiteralPath $authorLog) { Get-Content -Raw -LiteralPath $authorLog } else { '' }
    if ($logText -cnotmatch '\[GreystoneRuntimeRetarget\] RESULT=PASS') { throw 'FAIL: Editor author log has no exact success marker' }
    if ($logText -cmatch '\[GreystoneRuntimeRetarget\] RESULT=FAIL') { throw 'FAIL: Editor author log contains failure marker' }
    $result='BUILD_AND_AUTHOR_PASS'
} catch { $reason=$_.Exception.Message; $result='STOPPED_AT_' + $stageName; throw }
finally {
    if (Test-Path -LiteralPath $manifest) { try { $m=Get-Content -Raw $manifest | ConvertFrom-Json; $m.steps=@($steps); $m.result=$result; Write-Atomic $manifest $m } catch {} }
    $release = -not (Test-Editor); $released=0; $kept=@()
    if ($release) { foreach ($lock in $created) { try { $v=Get-Content -Raw $lock | ConvertFrom-Json; if ($v.owner_token -ceq $token) { Remove-Item -LiteralPath $lock -Force; $released++ } else { $kept += "$lock owner_token_mismatch" } } catch { $kept += "$lock release_error=$($_.Exception.Message)" } } }
    else { $kept=@($created) }
    if (Test-Path -LiteralPath $run -PathType Container) {
        try { Write-Atomic $status ([ordered]@{ task='C-1622'; stage=$stageName; result=$result; reason=$reason; approval_sha256=$(if ($approvalHash) {$approvalHash} else {''}); lock_release_allowed=$release; locks_released=$released; locks_kept=$kept; steps=@($steps); utc=[DateTime]::UtcNow.ToString('o') }) }
        catch { Write-Warning ('Could not write C-1622 status receipt: ' + $_.Exception.Message) }
    }
}
