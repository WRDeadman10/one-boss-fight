param(
    [Parameter(Mandatory = $true)][ValidateSet('pie_a4_low_sweep','pie_dormant_wake','pie_damage_path','pie_player_death_reset','pie_telegraph','pie_boss_hud','pie_phase_reset','pie_boss_death','pie_boss_death_states','pie_victory_lock','pie_transition_rules','pie_a5_heal_punish','pie_bleed','pie_leap_wave','pie_posture_hits','pie_hyperarmor','pie_close_attacks','pie_authored_close_clips','pie_boss_clips','pie_attack_rules','pie_boss_look','pie_riposte','pie_riposte_exec','pie_riposte_lethal','pie_trace_audit','pie_hit_intake','pie_iframes','pie_fog_gate','pie_remains','pie_soak','pie_legend')][string]$Driver,
    [Parameter(Mandatory = $true)][string]$OutRoot,
    [ValidateSet(1,3)][int]$DeathResetRepetitions = 1
)
$ErrorActionPreference = 'Stop'
if ($Driver -ne 'pie_player_death_reset' -and $DeathResetRepetitions -ne 1) {
    throw 'DeathResetRepetitions applies only to pie_player_death_reset'
}
$root = 'C:\UnrealProject\OneBossFight'
$runner = Join-Path $root 'Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1'
$driverScript = Join-Path $root 'Scripts\Editor\run_a5_parity_driver_and_quit.py'
if ($Driver -eq 'pie_a4_low_sweep') { $driverScript = Join-Path $root 'Scripts\Editor\run_a4_parity_and_quit.py' }
$definition = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
$prefix = @{ pie_a4_low_sweep = 'A4'; pie_dormant_wake = 'DormantWake'; pie_damage_path = 'Dmg'; pie_player_death_reset = 'DeathReset'; pie_telegraph = 'Telegraph'; pie_boss_hud = 'BossHud'; pie_phase_reset = 'PhaseReset'; pie_boss_death = 'BossDeath'; pie_boss_death_states = 'DeathStates'; pie_victory_lock = 'VictoryLock'; pie_transition_rules = 'Transition'; pie_a5_heal_punish = 'A5'; pie_bleed = 'Bleed'; pie_leap_wave = 'Leap'; pie_posture_hits = 'Posture'; pie_hyperarmor = 'HyperArmor'; pie_close_attacks = 'Close'; pie_authored_close_clips = 'AuthoredClose'; pie_boss_clips = 'BossClips'; pie_attack_rules = 'Rules'; pie_boss_look = 'BossLook'; pie_riposte = 'Riposte'; pie_riposte_exec = 'RipostExec'; pie_riposte_lethal = 'RipostLethal'; pie_trace_audit = 'Trace'; pie_hit_intake = 'Intake'; pie_iframes = 'IFrame'; pie_fog_gate = 'FogGate'; pie_remains = 'Remains'; pie_soak = 'Soak'; pie_legend = 'Legend' }[$Driver]
$minimum = @{ pie_a4_low_sweep = 14; pie_dormant_wake = 11; pie_damage_path = 17; pie_player_death_reset = 25; pie_telegraph = 25; pie_boss_hud = 29; pie_phase_reset = 14; pie_boss_death = 11; pie_boss_death_states = 28; pie_victory_lock = 9; pie_transition_rules = 28; pie_a5_heal_punish = 31; pie_bleed = 19; pie_leap_wave = 17; pie_posture_hits = 25; pie_hyperarmor = 23; pie_close_attacks = 55; pie_authored_close_clips = 14; pie_boss_clips = 14; pie_attack_rules = 13; pie_boss_look = 14; pie_riposte = 5; pie_riposte_exec = 15; pie_riposte_lethal = 3; pie_trace_audit = 30; pie_hit_intake = 36; pie_iframes = 19; pie_fog_gate = 6; pie_remains = 4; pie_soak = 213; pie_legend = 25 }[$Driver]
if (Test-Path -LiteralPath $OutRoot) { throw "Refusing existing pair evidence directory: $OutRoot" }
New-Item -ItemType Directory -Path $OutRoot | Out-Null

function Invoke-Arm([string]$Route) {
    $out = Join-Path $OutRoot $Route
    if (Test-Path -LiteralPath $out) { throw "Refusing existing arm evidence directory: $out" }
    $env:A5_PARITY_DRIVER = $Driver
    $env:A5_DEATH_RESET_REPETITIONS = [string]$DeathResetRepetitions
    if ($Route -eq 'data') { $env:H019_ENCOUNTER_DEFINITION = $definition; Remove-Item Env:RPG_LEGACY_STARTUP -ErrorAction SilentlyContinue }
    else { Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue; $env:RPG_LEGACY_STARTUP = '1' } # the data route is the game default since 2026-11-06
    & $runner -Script $driverScript -OutDir $out -Task "A5-$Driver-$Route" -NullRhi 0 -PyCmd 1 -TimeoutSeconds 1500
    if ($LASTEXITCODE -ne 0) { throw "Editor runner failed for $Route arm with exit $LASTEXITCODE" }
    $rawLog = Join-Path $out 'editor_raw.log'
    $final = Select-String -LiteralPath $rawLog -Pattern "\[$prefix\] (RESULT (\d+)/(\d+) passed|SUMMARY (\d+) checks, (\d+) failed)" | Select-Object -Last 1
    if (-not $final) { throw "Missing terminal result for $Driver $Route" }
    if ($final.Line -match 'RESULT (\d+)/(\d+) passed') { $passed = [int]$Matches[1]; $total = [int]$Matches[2] }
    elseif ($final.Line -match 'SUMMARY (\d+) checks, (\d+) failed') { $total = [int]$Matches[1]; $passed = $total - [int]$Matches[2] }
    else { throw "Malformed terminal result for $Driver $Route" }
    if ($passed -ne $total -or $total -lt $minimum) { throw "$Driver $Route failed acceptance count: $passed/$total, minimum $minimum" }
    "PASS $Driver $Route $passed/$total log=$rawLog"
}

try {
    Invoke-Arm 'legacy'
    Invoke-Arm 'data'
}
finally {
    Remove-Item Env:A5_PARITY_DRIVER -ErrorAction SilentlyContinue
    Remove-Item Env:H019_ENCOUNTER_DEFINITION, Env:RPG_LEGACY_STARTUP -ErrorAction SilentlyContinue
    Remove-Item Env:A5_DEATH_RESET_REPETITIONS -ErrorAction SilentlyContinue
}
