[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$OutRoot,
    [switch]$Execute,
    [switch]$Resume
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$pairRunner = Join-Path $PSScriptRoot 'RunA5ParityPair.ps1'
$drivers = @(
    'pie_a4_low_sweep', 'pie_dormant_wake', 'pie_damage_path', 'pie_player_death_reset',
    'pie_telegraph', 'pie_boss_hud', 'pie_phase_reset', 'pie_boss_death',
    'pie_boss_death_states', 'pie_victory_lock', 'pie_transition_rules',
    'pie_a5_heal_punish', 'pie_bleed', 'pie_leap_wave', 'pie_posture_hits',
    'pie_hyperarmor', 'pie_close_attacks', 'pie_authored_close_clips', 'pie_boss_clips',
    'pie_attack_rules', 'pie_boss_look', 'pie_riposte', 'pie_riposte_exec',
    'pie_riposte_lethal', 'pie_trace_audit', 'pie_hit_intake', 'pie_iframes',
    'pie_fog_gate', 'pie_remains', 'pie_soak', 'pie_legend'
)

$resumePath = Join-Path $OutRoot 'resume.json'
$priorRows = @()
if ($Resume) {
    if (-not (Test-Path -LiteralPath $resumePath -PathType Leaf)) { throw "Resume file is missing: $resumePath" }
    $resumeState = Get-Content -LiteralPath $resumePath -Raw | ConvertFrom-Json
    if ($resumeState.schema -ne 1 -or (($resumeState.drivers -join '|') -ne ($drivers -join '|'))) {
        throw 'Resume file schema or registered driver list does not match this runner.'
    }
    $priorRows = @($resumeState.rows)
    if (@($priorRows | ForEach-Object Driver | Sort-Object -Unique).Count -ne @($priorRows).Count) {
        throw 'Resume file contains duplicate driver rows.'
    }
}
elseif (Test-Path -LiteralPath $OutRoot) {
    throw ('Refusing existing nightly evidence directory: {0}' -f $OutRoot)
}

if (-not $Execute) {
    $completed = @($priorRows | Where-Object Result -eq 'PASS' | ForEach-Object Driver)
    Write-Output ("DRY RUN - 31 A5 parity pairs; each calls RunA5ParityPair.ps1 ({0} already PASS and {1} pending). Each pair uses fresh legacy/data Editor processes." -f $completed.Count, ($drivers.Count - $completed.Count))
    foreach ($driver in $drivers) {
        if ($driver -in $completed) { Write-Output ("SKIP {0} (checkpoint PASS)" -f $driver); continue }
        $pairOut = Join-Path $OutRoot $driver
        Write-Output ("powershell -NoProfile -ExecutionPolicy Bypass -File '{0}' -Driver {1} -OutRoot '{2}'" -f $pairRunner, $driver, $pairOut)
    }
    Write-Output ('Summary after execution: {0}' -f (Join-Path $OutRoot 'summary.md'))
    exit 0
}

if (-not (Test-Path -LiteralPath $pairRunner)) { throw ('Missing pair runner: {0}' -f $pairRunner) }
if (-not $Resume) { New-Item -ItemType Directory -Path $OutRoot | Out-Null }
$rows = [System.Collections.Generic.List[object]]::new()
foreach ($row in $priorRows) { $rows.Add($row) }

function Write-Summary {
    $lines = @(
        '# A5 parity nightly summary',
        '',
        '| Driver | Legacy checks | Data checks | Result | Detail |',
        '|---|---:|---:|---|---|'
    )
    foreach ($row in $rows) {
        $detail = ([string]$row.Detail) -replace '[|]', ' '
        $lines += ('| {0} | {1} | {2} | {3} | {4} |' -f $row.Driver, $row.Legacy, $row.Data, $row.Result, $detail)
    }
    Set-Content -LiteralPath (Join-Path $OutRoot 'summary.md') -Value $lines -Encoding UTF8
}

function Save-Checkpoint {
    $tempPath = $resumePath + '.tmp'
    [pscustomobject]@{ schema = 1; drivers = $drivers; rows = @($rows) } |
        ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $tempPath -Encoding utf8
    Move-Item -LiteralPath $tempPath -Destination $resumePath -Force
}

if (-not $Resume) {
    Save-Checkpoint
}

foreach ($driver in $drivers) {
    $oldRow = @($rows | Where-Object Driver -eq $driver | Select-Object -Last 1)
    if ($oldRow.Count -gt 0 -and $oldRow[0].Result -eq 'PASS') { continue }
    $legacy = '-'; $data = '-'; $result = 'FAIL'; $detail = ''
    try {
        $pairOut = Join-Path $OutRoot $driver
        if (Test-Path -LiteralPath $pairOut) {
            $attempt = 2
            do { $pairOut = Join-Path $OutRoot ("{0}_attempt{1:D2}" -f $driver, $attempt); $attempt++ }
            while (Test-Path -LiteralPath $pairOut)
        }
        $output = & $pairRunner -Driver $driver -OutRoot $pairOut 2>&1
        $armResults = @{}
        $resultPattern = '^PASS ' + [regex]::Escape($driver) + ' (legacy|data) (\d+)/(\d+)'
        foreach ($line in $output) {
            if ([string]$line -match $resultPattern) {
                $armResults[$Matches[1]] = ('{0}/{1}' -f $Matches[2], $Matches[3])
            }
        }
        if (-not $armResults.ContainsKey('legacy') -or -not $armResults.ContainsKey('data')) {
            throw 'Pair harness did not report both arm results.'
        }
        $legacy = $armResults['legacy']; $data = $armResults['data']; $result = 'PASS'
        $detail = 'both fresh-process arms met registered minimum'
    } catch {
        $detail = $_.Exception.Message
    }
    if ($oldRow.Count -gt 0) { $rows.Remove($oldRow[0]) }
    $rows.Add([pscustomobject]@{ Driver = $driver; Legacy = $legacy; Data = $data; Result = $result; Detail = $detail; PairOut = $pairOut })
    Write-Summary
    Save-Checkpoint
    Write-Output ('{0} {1} legacy={2} data={3}' -f $result, $driver, $legacy, $data)
}

$failed = @($rows | Where-Object Result -ne 'PASS')
Write-Output ('SUMMARY {0} pairs; {1} passed; {2} failed; report={3}' -f $rows.Count, ($rows.Count - $failed.Count), $failed.Count, (Join-Path $OutRoot 'summary.md'))
if ($failed.Count -gt 0) { exit 1 }
