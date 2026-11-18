param(
    [Parameter(Mandatory=$true)][string]$BuildId,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.5',
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$StageRoot = '',
    [string]$ReflectionDumpExecutable = '',
    [string[]]$ReflectionDumpArguments = @(),
    [switch]$Execute
)
$ErrorActionPreference = 'Stop'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Assert-Under([string]$Base, [string]$Candidate, [string]$Label) {
    $baseFull = [System.IO.Path]::GetFullPath($Base).TrimEnd('\') + '\'
    $candidateFull = [System.IO.Path]::GetFullPath($Candidate)
    if (!$candidateFull.StartsWith($baseFull, [StringComparison]::OrdinalIgnoreCase)) { throw "$Label must remain under $baseFull" }
    return $candidateFull
}

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$uproject = Join-Path $ProjectRoot 'OneBossFight.uproject'
$uat = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$python = (Get-Command python -ErrorAction Stop).Source
$binaryChecker = Join-Path $ProjectRoot 'Scripts\CheckShippingBinary.py'
$featureChecker = Join-Path $ProjectRoot 'Scripts\CheckShippingFeatureSymbols.py'
$sourceGuard = Join-Path $ProjectRoot 'Scripts\Tools\check_shipping_guards.py'
$locks = @(
    (Join-Path $ProjectRoot 'ENGINE_LOCK.json'),
    (Join-Path $ProjectRoot 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json')
)
if ([string]::IsNullOrWhiteSpace($BuildId) -or $BuildId -notmatch '^[A-Za-z0-9._-]{1,80}$') { throw 'BuildId must be a non-empty safe token.' }
if (!(Test-Path -LiteralPath $uproject -PathType Leaf) -or !(Test-Path -LiteralPath $uat -PathType Leaf)) { throw 'Project or Unreal Automation Tool is missing.' }
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count -gt 0) { throw 'ABORT: UnrealEditor is running; close it before the Shipping build.' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: C-1155 engine lock exists: $lock" } }
if ([string]::IsNullOrWhiteSpace($StageRoot)) {
    $StageRoot = Join-Path $ProjectRoot ('Saved\StagedBuilds_Shipping\BK7\' + $BuildId)
}
if (![System.IO.Path]::IsPathRooted($StageRoot)) { $StageRoot = Join-Path $ProjectRoot $StageRoot }
$stageBase = Join-Path $ProjectRoot 'Saved\StagedBuilds_Shipping\BK7'
$StageRoot = Assert-Under $stageBase $StageRoot 'StageRoot'
if (Test-Path -LiteralPath $StageRoot) { throw "ABORT: task stage already exists; refusing overwrite: $StageRoot" }
$evidenceBase = Join-Path $ProjectRoot 'Docs\BossCombatReview\Execution\Codex\BK7_SHIPPING'
$evidence = Join-Path $evidenceBase ($BuildId + '_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss'))
if (Test-Path -LiteralPath $evidence) { throw "ABORT: evidence directory already exists: $evidence" }
if ([string]::IsNullOrWhiteSpace($ReflectionDumpExecutable) -or !(Test-Path -LiteralPath $ReflectionDumpExecutable -PathType Leaf)) {
    throw 'Provide the approved Shipping UHT/reflection dump executable; no reflection command is guessed by this runner.'
}

$preflight = [ordered]@{
    result='PREFLIGHT_PASS'; build_id=$BuildId; engine_root=$EngineRoot; project=$uproject
    stage_root=$StageRoot; reflection_dump_executable=(Resolve-Path -LiteralPath $ReflectionDumpExecutable).Path
    reflection_dump_arguments=$ReflectionDumpArguments; lock_paths=$locks
    editor_processes=0; shipping_smoke='NOT_RUN'; binary_provenance='NOT_ESTABLISHED'
}
if (!$Execute) { $preflight | ConvertTo-Json -Depth 5; exit 0 }

New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; task='BK-36..40 Shipping pipeline'; command_id='BK7-SHIPPING'; owner_token=$token; pid=$PID; build_id=$BuildId; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Win64 Shipping cook/stage, UHT/reflection dump, source and binary guards; no smoke claim' } | ConvertTo-Json -Compress
$temps = [System.Collections.Generic.List[string]]::new()
$created = [System.Collections.Generic.List[string]]::new()
$outcomes = [ordered]@{ buildcookrun_exit=$null; reflection_dump_exit=$null; shipping_binary_guard_exit=$null; feature_symbol_guard_exit=$null; source_guard_exit=$null }
try {
    foreach ($lock in $locks) {
        $parent = Split-Path -Parent $lock
        if (!(Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        $temp = $lock + '.' + $token + '.tmp'
        $temps.Add($temp)
        $stream = [System.IO.File]::Open($temp, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        try { $bytes=[Text.Encoding]::UTF8.GetBytes($record + [Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) }
        finally { $stream.Dispose() }
        [System.IO.File]::Move($temp, $lock)
        $created.Add($lock)
    }
    if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count -gt 0) { throw 'ABORT: UnrealEditor started during lock acquisition.' }
    New-Item -ItemType Directory -Path (Split-Path -Parent $StageRoot) -Force | Out-Null
    $uatLog = Join-Path $evidence 'buildcookrun.log'
    & $uat BuildCookRun "-project=$uproject" -noP4 -platform=Win64 -clientconfig=Shipping -build -cook -stage -pak -archive "-archivedirectory=$StageRoot" -utf8output *> $uatLog
    $outcomes.buildcookrun_exit = $LASTEXITCODE
    if ($outcomes.buildcookrun_exit -ne 0) { throw "BuildCookRun failed with exit $($outcomes.buildcookrun_exit)." }

    $shippingExe = Get-ChildItem -LiteralPath $StageRoot -Filter 'OneBossFight-Win64-Shipping.exe' -File -Recurse | Select-Object -First 1
    if (!$shippingExe) { throw 'Staged Shipping executable was not found.' }
    $exeHash = Get-Sha256 $shippingExe.FullName
    $reflectionLog = Join-Path $evidence 'uht_reflection_dump.log'
    & $ReflectionDumpExecutable @ReflectionDumpArguments *> $reflectionLog
    $outcomes.reflection_dump_exit = $LASTEXITCODE
    if ($outcomes.reflection_dump_exit -ne 0) { throw "Reflection dump command failed with exit $($outcomes.reflection_dump_exit)." }
    if (!(Test-Path -LiteralPath $reflectionLog -PathType Leaf) -or (Get-Item -LiteralPath $reflectionLog).Length -eq 0) { throw 'Reflection dump command produced no captured output.' }
    $reflectionHash = Get-Sha256 $reflectionLog

    & $python -I $binaryChecker $shippingExe.FullName *> (Join-Path $evidence 'shipping_binary_guard.log')
    $outcomes.shipping_binary_guard_exit = $LASTEXITCODE
    & $python -I $featureChecker $shippingExe.FullName *> (Join-Path $evidence 'shipping_feature_guard.log')
    $outcomes.feature_symbol_guard_exit = $LASTEXITCODE
    & $python -I $sourceGuard --source (Join-Path $ProjectRoot 'Source') *> (Join-Path $evidence 'shipping_source_guard.log')
    $outcomes.source_guard_exit = $LASTEXITCODE
    $ok = ($outcomes.shipping_binary_guard_exit -eq 0 -and $outcomes.feature_symbol_guard_exit -eq 0 -and $outcomes.source_guard_exit -eq 0)
    $sourceHead = (& git -C $ProjectRoot rev-parse HEAD 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { $sourceHead = 'unavailable' }
    $dirtyCount = @(& git -C $ProjectRoot status --porcelain 2>$null).Count
    $receipt = [ordered]@{
        receipt_version=1; build_id=$BuildId; engine_root=$EngineRoot; target='Win64'; configuration='Shipping'
        project=$uproject; stage_root=$StageRoot; source_head=$sourceHead; dirty_file_count=$dirtyCount
        artifacts=[ordered]@{
            uat_log=[ordered]@{build_id=$BuildId; path=$uatLog; sha256=(Get-Sha256 $uatLog)}
            shipping_executable=[ordered]@{build_id=$BuildId; path=$shippingExe.FullName; bytes=$shippingExe.Length; sha256=$exeHash}
            reflection_dump=[ordered]@{build_id=$BuildId; command=$ReflectionDumpExecutable; arguments=$ReflectionDumpArguments; path=$reflectionLog; sha256=$reflectionHash}
        }
        checks=$outcomes; shipping_smoke='NOT_RUN'; verdict=$(if ($ok) {'PASS'} else {'FAIL'})
    }
    $receiptPath = Join-Path $evidence 'shipping_receipt.json'
    [System.IO.File]::WriteAllText($receiptPath, ($receipt | ConvertTo-Json -Depth 8), [System.Text.UTF8Encoding]::new($false))
    if (!$ok) { throw 'One or more Shipping checks failed; receipt records the failure.' }
    Write-Output ("PASS build_id={0} exe_sha256={1} receipt={2} shipping_smoke=NOT_RUN" -f $BuildId, $exeHash, $receiptPath)
} finally {
    foreach ($temp in $temps) { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership before cleanup: ' + $lock) }
        }
    }
}
