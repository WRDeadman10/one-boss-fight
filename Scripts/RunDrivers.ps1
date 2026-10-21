# Runs the PIE regression drivers one after the other in the open editor (the project is open, the bridge on port 3000 is up) and prints a table.
# A driver passes when its final log line shows no failure and at least the expected number of checks ran (a driver that silently runs fewer checks fails).
# Usage: powershell -ExecutionPolicy Bypass -File Scripts\RunDrivers.ps1 [-Only pie_a4_low_sweep,pie_a5_heal_punish]  (the whole list takes about 100 minutes: run it in chunks with -Only, -SkipWarmup after the first) [-Full] [-SkipWarmup] [-TimeoutSeconds 420]
#   -Full adds the long drivers (the 180 trial dodge scan).
# Resumable: the script keeps no state; run it again after an interruption (use -Only for the drivers not yet run). If a driver times out its tick callback stays registered
# until the editor restarts: restart the editor (Scripts\Rebuild.ps1) before running anything else.
param([string[]]$Only, [switch]$Full, [switch]$SkipWarmup, [int]$TimeoutSeconds = 420)
if ($Only) { $Only = @($Only | ForEach-Object { $_ -split ',' }) }  # powershell -File passes a comma list as one string

$root = Split-Path $PSScriptRoot -Parent
$logPath = Join-Path $root "Saved\Logs\OneBossFight.log"
$runner = Join-Path $root "Scripts\run_in_editor.py"
$editorScripts = Join-Path $root "Scripts\Editor"

# Kind R: final line "RESULT <passed>/<total> passed". Kind S: final line "SUMMARY <total> checks, <failed> failed". Min = the number of checks the driver is expected to run.
$drivers = @(
    @{ N = 'pie_a4_low_sweep';        K = 'R'; Min = 14 },
    @{ N = 'pie_a5_heal_punish';      K = 'R'; Min = 31 },
    @{ N = 'pie_player_death_reset';  K = 'R'; Min = 25 },
    @{ N = 'pie_damage_path';         K = 'R'; Min = 17; T = 900 },
    @{ N = 'pie_iframes';             K = 'R'; Min = 19; T = 1500 },
    @{ N = 'pie_trace_audit';         K = 'R'; Min = 30; T = 1500 },
    @{ N = 'pie_legend';              K = 'R'; Min = 22; T = 900 },
    @{ N = 'pie_close_attacks';       K = 'R'; Min = 43 },
    @{ N = 'pie_leap_wave';           K = 'R'; Min = 17 },
    @{ N = 'pie_attack_rules';        K = 'R'; Min = 13 },
    @{ N = 'pie_boss_hud';            K = 'R'; Min = 29 },
    @{ N = 'pie_victory_lock';        K = 'R'; Min = 9 },
    @{ N = 'pie_camera_scenarios';    K = 'R'; Min = 6 },
    @{ N = 'pie_phase_reset';         K = 'S'; Min = 14 },
    @{ N = 'pie_riposte';             K = 'S'; Min = 5 },
    @{ N = 'pie_fog_gate';            K = 'S'; Min = 6 },
    @{ N = 'pie_transition_rules';    K = 'R'; Min = 28; T = 900 }   # mode from Saved\transition_mode.txt: quick (3 trials, about 6 min) for the gate, main (spec trial counts, about 20 min) before a release
)
if ($Only) { $drivers = @($drivers | Where-Object { $Only -contains $_.N }) }

function Read-LogFrom([int]$skip) {
    # The editor keeps the log open for writing: open it with sharing and return the lines after the first $skip lines.
    $fs = [System.IO.File]::Open($logPath, 'Open', 'Read', 'ReadWrite')
    $sr = New-Object System.IO.StreamReader($fs)
    $lines = New-Object System.Collections.Generic.List[string]
    $i = 0
    while (-not $sr.EndOfStream) { $l = $sr.ReadLine(); if ($i -ge $skip) { $lines.Add($l) }; $i++ }
    $sr.Close(); $fs.Close()
    return $lines
}

function Count-Log() { return (Read-LogFrom 0).Count }

function Invoke-Editor([string]$scriptName) {
    & python -I $runner (Join-Path $editorScripts $scriptName) | Out-Null
}

function Test-Bridge() {
    try { Invoke-WebRequest -Uri 'http://localhost:3000/' -UseBasicParsing -TimeoutSec 3 | Out-Null; return $true }
    catch { return ($_.Exception.Response -ne $null) }  # a 404 from the route handler still means the bridge is up
}

# The editor may still be starting (a rebuild relaunches it): wait for the bridge up to 4 minutes.
$waited = 0
while (-not (Test-Bridge) -and $waited -lt 240) { Start-Sleep -Seconds 5; $waited += 5 }
if (-not (Test-Bridge)) { 'The editor bridge (http://localhost:3000) is not reachable after 4 minutes: open the project with -nosound (Scripts\Rebuild.ps1 does it).'; exit 2 }
if ($waited -gt 0) { Start-Sleep -Seconds 30 }  # the bridge is up before the map is loaded

if (-not $SkipWarmup) {
    # The first PIE after an editor start has broken player attributes (health 0): run the overlay driver once, with the editor throttle off.
    Invoke-Editor 'no_throttle.py'
    Invoke-Editor 'legend_off.py'  # the legend pass (hit stop, slow motion, camera shake) would change the timings the older drivers measure; pie_legend.py switches it on itself
    Invoke-Editor 'pie_debug_overlay.py'
    Start-Sleep -Seconds 40
}

$rows = @()
foreach ($d in $drivers) {
    $name = $d.N
    $start = Count-Log
    Invoke-Editor "$name.py"
    $limit = if ($d.T) { [int]$d.T } else { $TimeoutSeconds }  # a driver may carry its own limit (T)
    $deadline = (Get-Date).AddSeconds($limit)
    $final = $null
    $lines = @()
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 4
        $lines = Read-LogFrom $start
        if ($d.K -eq 'R') { $final = $lines | Where-Object { $_ -match 'LogPython: \[[^\]]+\] RESULT (\d+)/(\d+) passed' } | Select-Object -Last 1 }
        else { $final = $lines | Where-Object { $_ -match 'LogPython: \[[^\]]+\] SUMMARY (\d+) checks, (\d+) failed' } | Select-Object -Last 1 }
        if ($final) { break }
    }
    if (-not $final) {
        Invoke-Editor 'pie_stop.py'
        $rows += [pscustomobject]@{ Driver = $name; Result = 'TIMEOUT'; Detail = "no final line in $limit s: restart the editor before going on (a stale tick callback survives)" }
        break
    }
    if ($d.K -eq 'R') {
        $null = $final -match 'RESULT (\d+)/(\d+) passed'
        $pass = [int]$Matches[1]; $total = [int]$Matches[2]; $failed = $total - $pass
    } else {
        $null = $final -match 'SUMMARY (\d+) checks, (\d+) failed'
        $total = [int]$Matches[1]; $failed = [int]$Matches[2]; $pass = $total - $failed
    }
    $ok = ($failed -eq 0) -and ($total -ge $d.Min)
    $detail = "$pass/$total passed (expected at least $($d.Min) checks)"
    if (-not $ok) {
        $fails = @($lines | Where-Object { $_ -match 'LogPython: \[[^\]]+\] FAIL' } | ForEach-Object { ($_ -replace '^.*LogPython: ', '') } | Select-Object -First 3)
        if ($fails.Count -gt 0) { $detail += ' | ' + ($fails -join ' | ') }
    }
    $rows += [pscustomobject]@{ Driver = $name; Result = $(if ($ok) { 'PASS' } else { 'FAIL' }); Detail = $detail }
    Start-Sleep -Seconds 6
}

if ($Full -and -not ($rows | Where-Object { $_.Result -eq 'TIMEOUT' })) {
    # pie_dodge_trials: 180 trials, several minutes; its final line is a SUMMARY with pass and fail counts.
    $start = Count-Log
    Invoke-Editor 'pie_dodge_trials.py'
    $deadline = (Get-Date).AddSeconds(1500)
    $final = $null
    while ((Get-Date) -lt $deadline -and -not $final) {
        Start-Sleep -Seconds 6
        $final = (Read-LogFrom $start) | Where-Object { $_ -match 'LogPython: \[[^\]]+\] SUMMARY pass (\d+) fail (\d+)' } | Select-Object -Last 1
    }
    if ($final) { $null = $final -match 'SUMMARY pass (\d+) fail (\d+)'; $p = [int]$Matches[1]; $f = [int]$Matches[2]; $rows += [pscustomobject]@{ Driver = 'pie_dodge_trials'; Result = $(if ($f -eq 0 -and $p -ge 180) { 'PASS' } else { 'FAIL' }); Detail = "pass $p fail $f (expected 180 trials)" } }
    else { Invoke-Editor 'pie_stop.py'; $rows += [pscustomobject]@{ Driver = 'pie_dodge_trials'; Result = 'TIMEOUT'; Detail = 'restart the editor' } }
}

$rows | Format-Table -AutoSize -Wrap | Out-String -Width 220
$bad = @($rows | Where-Object { $_.Result -ne 'PASS' })
"$($rows.Count - $bad.Count)/$($rows.Count) drivers passed"
if ($bad.Count -gt 0) { exit 1 }
