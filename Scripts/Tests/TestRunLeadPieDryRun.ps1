$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runner = Join-Path $root 'Scripts/RunLeadPie.ps1'
$lock = Join-Path $root 'Docs/BossCombatReview/Execution/ENGINE_LOCK.json'
$out = "Docs/BossCombatReview/Execution/Claude/__dry_run_$([guid]::NewGuid().ToString('N'))"
$hadLock = Test-Path -LiteralPath $lock
$lines = @(& $runner -Script Scripts/Editor/pie_er_guard_counter.py `
    -Routes @('legacy', 'data') -Env @('ER_GC_SYNTHETIC=1', 'ER_GC_ASSIGN=1') `
    -OutputDir $out -DryRun)
$text = $lines -join "`n"
foreach ($expected in @('route=legacy', 'route=data', 'ER_GC_SYNTHETIC=1',
                       'ER_GC_ASSIGN=1', '-nosound', '-abslog=',
                       '[ERGuardCounter] SUMMARY', 'legacy_lines.txt', 'data_lines.txt')) {
    if (-not $text.Contains($expected)) { throw "Dry-run output missing $expected" }
}
if ((Test-Path -LiteralPath $lock) -ne $hadLock) { throw 'Dry-run changed ENGINE_LOCK state' }
if (Test-Path -LiteralPath (Join-Path $root $out)) { throw 'Dry-run created output folder' }

function Assert-RunnerRefuses([scriptblock]$Call, [string]$Expected) {
    $errorText = ''
    try { & $Call | Out-Null } catch { $errorText = $_.ToString() }
    if (-not $errorText.Contains($Expected)) { throw "Expected refusal '$Expected'; got '$errorText'" }
}
Assert-RunnerRefuses {
    & $runner -Script Scripts/Editor/pie_er_guard_counter.py -Routes invalid `
        -OutputDir $out -DryRun
} 'ValidateSet'
Assert-RunnerRefuses {
    & $runner -Script Scripts/Editor/pie_er_guard_counter.py -Routes legacy `
        -Env 'bad-name=1' -OutputDir $out -DryRun
} 'Invalid -Env entry'
Assert-RunnerRefuses {
    & $runner -Script Scripts/Editor/pie_er_guard_counter.py -Routes legacy `
        -Env 'H019_ENCOUNTER_DEFINITION=wrong' -OutputDir $out -DryRun
} 'selected by -Routes'
Assert-RunnerRefuses {
    & $runner -Script Scripts/Editor/pie_er_guard_counter.py -Routes legacy `
        -OutputDir $out -TimeoutSeconds 0 -DryRun
} 'at least 10'

$absoluteOutput = Join-Path $root $out
$absoluteLines = @(& $runner -Script (Join-Path $root 'Scripts/Editor/pie_er_guard_counter.py') `
    -Routes data -OutputDir $absoluteOutput -DryRun)
if (-not (($absoluteLines -join "`n").Contains($absoluteOutput))) {
    throw 'Absolute script/output paths were not preserved in dry-run command'
}

$previous = [System.Environment]::GetEnvironmentVariable('ER_GC_ASSIGN', 'Process')
try {
    [System.Environment]::SetEnvironmentVariable('ER_GC_ASSIGN', 'original', 'Process')
    & $runner -Script Scripts/Editor/pie_er_guard_counter.py -Routes legacy `
        -Env ER_GC_ASSIGN=1 -OutputDir $out -DryRun | Out-Null
    if ([System.Environment]::GetEnvironmentVariable('ER_GC_ASSIGN', 'Process') -ne 'original') {
        throw 'Dry-run changed a pre-existing environment value'
    }
} finally {
    [System.Environment]::SetEnvironmentVariable('ER_GC_ASSIGN', $previous, 'Process')
}
if ((Test-Path -LiteralPath $lock) -ne $hadLock) { throw 'Negative dry-runs changed ENGINE_LOCK state' }
if (Test-Path -LiteralPath (Join-Path $root $out)) { throw 'Negative dry-runs created output folder' }
Write-Output 'RunLeadPie dry-run contract OK (routes, env, arguments, refusals, marker, no side effects)'
