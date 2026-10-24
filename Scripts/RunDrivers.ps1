# Runs the PIE regression drivers one after the other in the open editor (the project is open, the bridge on port 3000 is up) and prints a table.
# A driver passes when its final log line shows no failure and at least the expected number of checks ran (a driver that silently runs fewer checks fails).
# Usage: powershell -ExecutionPolicy Bypass -File Scripts\RunDrivers.ps1 [-Only pie_a4_low_sweep,pie_a5_heal_punish]  (the whole list takes about 100 minutes: run it in chunks with -Only, -SkipWarmup after the first) [-Full] [-SkipWarmup] [-Repeat 3] [-TimeoutSeconds 420]
#   -Full adds the long drivers (the 180 trial dodge scan).
# Resumable: the script keeps no state; run it again after an interruption (use -Only for the drivers not yet run). If a driver times out its tick callback stays registered
# until the editor restarts: restart the editor (Scripts\Rebuild.ps1) before running anything else.
param([string[]]$Only, [switch]$Full, [switch]$SkipWarmup, [ValidateRange(1, 100)][int]$Repeat = 1, [int]$TimeoutSeconds = 420)
if ($Only) { $Only = @($Only | ForEach-Object { $_ -split ',' }) }  # powershell -File passes a comma list as one string

$root = Split-Path $PSScriptRoot -Parent
$logPath = Join-Path $root "Saved\Logs\OneBossFight.log"
$runner = Join-Path $root "Scripts\run_in_editor.py"
$editorScripts = Join-Path $root "Scripts\Editor"

# Kind R: final line "RESULT <passed>/<total> passed". Kind S: final line "SUMMARY <total> checks, <failed> failed". Min = the number of checks the driver is expected to run.
$drivers = @(
    @{ N = 'pie_a4_low_sweep';        K = 'R'; Min = 14 },
    @{ N = 'pie_hit_intake';          K = 'R'; Min = 36; T = 600 },
    @{ N = 'pie_posture_hits';        K = 'R'; Min = 25; T = 1100 },
    @{ N = 'pie_stamina_cost';        K = 'R'; Min = 17; T = 900 },
    @{ N = 'pie_hyperarmor';          K = 'R'; Min = 23; T = 900 },
    @{ N = 'pie_bleed';               K = 'R'; Min = 19; T = 900 },
    @{ N = 'pie_boss_clips';          K = 'R'; Min = 14; T = 600 },
    @{ N = 'pie_riposte_exec';         K = 'R'; Min = 15; T = 700 },
    @{ N = 'pie_riposte_lethal';       K = 'R'; Min = 3; T = 300 },
    @{ N = 'pie_boss_look';            K = 'R'; Min = 14; T = 300 },
    @{ N = 'pie_boss_death';           K = 'R'; Min = 11; T = 300 },
    @{ N = 'pie_boss_death_states';    K = 'R'; Min = 28; T = 600 },
    @{ N = 'pie_remains';              K = 'R'; Min = 4; T = 600 },
    @{ N = 'pie_builds';               K = 'R'; Min = 103; T = 1500 },
    @{ N = 'pie_build_hyperarmor';     K = 'R'; Min = 20; T = 900 },
    @{ N = 'pie_build_hud';            K = 'R'; Min = 8; T = 600 },
    @{ N = 'pie_build_select';         K = 'R'; Min = 18; T = 600 },
    @{ N = 'pie_telegraph';            K = 'R'; Min = 22; T = 600 },
    @{ N = 'pie_soak';                 K = 'R'; Min = 213; T = 900 },
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
# Balance runs (M14): the scripted player bot with each build. Not part of the gate (a fight is not deterministic and takes minutes): run them with -Only pie_build_fight_starter,pie_build_fight_strength,pie_build_fight_dex.
# A row with S runs that script under its own name; Setup = file (relative to the project) and the text written to it first (the build of the run).
$balance = @(
    @{ N = 'pie_build_fight_starter';  S = 'pie_build_fight'; K = 'R'; Min = 10; T = 1000; Setup = @('Saved/build_fight_build.txt', 'Starter') },
    @{ N = 'pie_build_fight_strength'; S = 'pie_build_fight'; K = 'R'; Min = 10; T = 1000; Setup = @('Saved/build_fight_build.txt', 'Strength') },
    @{ N = 'pie_build_fight_dex';      S = 'pie_build_fight'; K = 'R'; Min = 10; T = 1000; Setup = @('Saved/build_fight_build.txt', 'Dex') }
)
if ($Only) { $drivers = @(($drivers + $balance) | Where-Object { $Only -contains $_.N }) }
if ($Only) {
    $unknown = @($Only | Where-Object { $_ -notin $drivers.N })
    if ($unknown.Count -gt 0) { throw "Unknown driver(s): $($unknown -join ', ')" }
}

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
    try { Invoke-WebRequest -Uri 'http://127.0.0.1:3000/mcp/status' -UseBasicParsing -TimeoutSec 3 | Out-Null; return $true }
    catch { return $false }
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
    Invoke-Editor 'build_off.py'  # rpg.Build is process wide: a build left by an aborted pie_builds.py run would change every later PIE
    Invoke-Editor 'pie_debug_overlay.py'
    Start-Sleep -Seconds 40
}

$rows = @()
$expandedDrivers = @()
foreach ($driver in $drivers) {
    $count = if ($driver.S -eq 'pie_build_fight') { $Repeat } else { 1 }
    for ($index = 1; $index -le $count; $index++) {
        $expandedDrivers += [pscustomobject]@{ Definition = $driver; Index = $index; Count = $count }
    }
}
foreach ($entry in $expandedDrivers) {
    $d = $entry.Definition
    $name = if ($entry.Count -gt 1) { "$($d.N) [$($entry.Index)/$($entry.Count)]" } else { $d.N }
    $start = Count-Log
    if ($d.Setup) { Set-Content -Path (Join-Path $root $d.Setup[0]) -Value $d.Setup[1] -Encoding ascii }
    $scriptName = if ($d.S) { $d.S } else { $name }
    Invoke-Editor "$scriptName.py"
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
    if ($d.Setup -and $d.S -eq 'pie_build_fight') {
        $expectedBuild = [regex]::Escape($d.Setup[1])
        $identity = @($lines | Where-Object { $_ -match "\[BuildFight\] METRIC build = $expectedBuild \(" })
        if ($identity.Count -ne 1) {
            $ok = $false
            $detail += " | missing or mismatched build identity: expected $($d.Setup[1])"
        }
    }
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
