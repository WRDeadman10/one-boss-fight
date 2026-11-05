[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$OutRoot,
    [switch]$Execute
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

if (-not $Execute) {
    Write-Output 'DRY RUN - 31 A5 parity pairs; each calls RunA5ParityPair.ps1, which launches fresh Editor processes for legacy and data arms.'
    foreach ($driver in $drivers) {
        $pairOut = Join-Path $OutRoot $driver
        Write-Output ("powershell -NoProfile -ExecutionPolicy Bypass -File '{0}' -Driver {1} -OutRoot '{2}'" -f $pairRunner, $driver, $pairOut)
    }
    Write-Output ('Summary after execution: {0}' -f (Join-Path $OutRoot 'summary.md'))
    exit 0
}

if (Test-Path -LiteralPath $OutRoot) { throw ('Refusing existing nightly evidence directory: {0}' -f $OutRoot) }
if (-not (Test-Path -LiteralPath $pairRunner)) { throw ('Missing pair runner: {0}' -f $pairRunner) }
New-Item -ItemType Directory -Path $OutRoot | Out-Null
$rows = [System.Collections.Generic.List[object]]::new()

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

foreach ($driver in $drivers) {
    $legacy = '-'; $data = '-'; $result = 'FAIL'; $detail = ''
    try {
        $pairOut = Join-Path $OutRoot $driver
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
    $rows.Add([pscustomobject]@{ Driver = $driver; Legacy = $legacy; Data = $data; Result = $result; Detail = $detail })
    Write-Summary
    Write-Output ('{0} {1} legacy={2} data={3}' -f $result, $driver, $legacy, $data)
}

$failed = @($rows | Where-Object Result -ne 'PASS')
Write-Output ('SUMMARY {0} pairs; {1} passed; {2} failed; report={3}' -f $rows.Count, ($rows.Count - $failed.Count), $failed.Count, (Join-Path $OutRoot 'summary.md'))
if ($failed.Count -gt 0) { exit 1 }
