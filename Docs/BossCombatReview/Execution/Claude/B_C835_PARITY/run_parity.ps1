# C-835 live A5 parity (lead, Claude, 2026-11-05): P10 (A4 pair) then P11/P12 (five A5 driver pairs).
# Each arm = a fresh windowed editor process (run_editor_script.ps1, -nosound), legacy arm first, selected arm second.
# Per pair: identity JSON (same for both arms), receipts from the closed raw logs, comparator with --verify-source-logs.
param([string[]]$Only = @(), [string]$BuildId = 'BUILD-218', [string]$Suffix = '')
$ErrorActionPreference = 'Continue'
$repo = 'C:\UnrealProject\OneBossFight'
$here = "$repo\Docs\BossCombatReview\Execution\Claude\B_C835_PARITY"
$runner = "$repo\Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1"
$definition = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
Set-Location $repo

function Sha256Text([string]$text) {
    $sha = [Security.Cryptography.SHA256]::Create()
    -join ($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($text)) | ForEach-Object { $_.ToString('x2') })
}

# Shared run identity: same build, content state, config and driver file for both arms of a pair.
$head = (git rev-parse HEAD).Trim()
$contentState = Sha256Text ($head + "`n" + ((git status --porcelain -- Content) -join "`n"))
$settings = Sha256Text ((Get-ChildItem "$repo\Config" -Filter *.ini | Sort-Object Name | ForEach-Object { Get-Content $_.FullName -Raw }) -join "`n")

function Write-Identity([string]$driver, [string]$path) {
    $driverFile = "$repo\Scripts\Editor\$driver.py"
    [ordered]@{
        map = '/Game/OneBossFight/Levels/L_SevarogArena'
        build_id = $BuildId
        content_sha256 = $contentState
        settings_sha256 = $settings
        seed = 'none'
        driver = $driver
        driver_args = @('fresh-process', 'run_editor_script', 'NullRhi=0')  # validator: ordered string array
        input_sha256 = (Get-FileHash $driverFile -Algorithm SHA256).Hash.ToLower()
    } | ConvertTo-Json | Set-Content -Path $path -Encoding ascii
}

function Invoke-Pair([string]$driver, [string]$wrapper, [int]$timeout) {
    $pair = "$here\$driver$Suffix"
    if (Test-Path $pair) { "SKIP $driver (evidence exists)"; return }
    New-Item -ItemType Directory -Path $pair | Out-Null
    Write-Identity $driver "$pair\identity.json"
    foreach ($route in 'legacy', 'data') {
        $env:A5_PARITY_DRIVER = $driver
        if ($route -eq 'data') { $env:H019_ENCOUNTER_DEFINITION = $definition } else { Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue }
        & $runner -Script "$repo\Scripts\Editor\$wrapper" -OutDir "$pair\$route" -Task "C835-$driver$Suffix-$route" -NullRhi 0 -PyCmd 1 -TimeoutSeconds $timeout
        "$driver $route runner exit=$LASTEXITCODE"
        Remove-Item Env:H019_ENCOUNTER_DEFINITION, Env:A5_PARITY_DRIVER -ErrorAction SilentlyContinue
        & python "$repo\Scripts\Tools\write_a4_parity_receipt.py" --log "$pair\$route\editor_raw.log" --identity "$pair\identity.json" --run-id "C835-$driver$Suffix-$route" --out "$pair\receipt_$route.json" 2>&1 | ForEach-Object { "$driver $route receipt: $_" }
    }
    & python "$repo\Scripts\Tools\compare_encounter_parity.py" "$pair\receipt_legacy.json" "$pair\receipt_data.json" --verify-source-logs --report-json "$pair\parity_report.json" 2>&1 | Tee-Object "$pair\compare.txt" | ForEach-Object { "$driver compare: $_" }
    "$driver compare exit=$LASTEXITCODE"
}

if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running'; exit 2 }
$pairs = @(
    @('pie_a4_low_sweep', 'run_a4_parity_and_quit.py', 900),
    @('pie_dormant_wake', 'run_a5_parity_driver_and_quit.py', 1000),
    @('pie_damage_path', 'run_a5_parity_driver_and_quit.py', 1300),
    @('pie_player_death_reset', 'run_a5_parity_driver_and_quit.py', 1500),
    @('pie_telegraph', 'run_a5_parity_driver_and_quit.py', 1000),
    @('pie_boss_hud', 'run_a5_parity_driver_and_quit.py', 1300),
    # Queue R1 (C-849, Codex X-1226): driver allowance from run_a5_parity_driver_and_quit.py ALLOWED + 300 s warm-up margin
    @('pie_phase_reset', 'run_a5_parity_driver_and_quit.py', 720),
    @('pie_boss_death', 'run_a5_parity_driver_and_quit.py', 600),
    @('pie_boss_death_states', 'run_a5_parity_driver_and_quit.py', 900),
    @('pie_victory_lock', 'run_a5_parity_driver_and_quit.py', 720),
    @('pie_transition_rules', 'run_a5_parity_driver_and_quit.py', 1200),
    # Queue R2-R5 (C-849, Codex X-1227..X-1230): ALLOWED + 300 s
    @('pie_a5_heal_punish', 'run_a5_parity_driver_and_quit.py', 720),
    @('pie_bleed', 'run_a5_parity_driver_and_quit.py', 1200),
    @('pie_leap_wave', 'run_a5_parity_driver_and_quit.py', 720),
    @('pie_posture_hits', 'run_a5_parity_driver_and_quit.py', 1400),
    @('pie_hyperarmor', 'run_a5_parity_driver_and_quit.py', 1200),
    @('pie_close_attacks', 'run_a5_parity_driver_and_quit.py', 720),
    @('pie_authored_close_clips', 'run_a5_parity_driver_and_quit.py', 900),
    @('pie_boss_clips', 'run_a5_parity_driver_and_quit.py', 900),
    @('pie_attack_rules', 'run_a5_parity_driver_and_quit.py', 720),
    @('pie_boss_look', 'run_a5_parity_driver_and_quit.py', 600),
    @('pie_riposte', 'run_a5_parity_driver_and_quit.py', 720),
    @('pie_riposte_exec', 'run_a5_parity_driver_and_quit.py', 1000),
    @('pie_riposte_lethal', 'run_a5_parity_driver_and_quit.py', 600),
    @('pie_trace_audit', 'run_a5_parity_driver_and_quit.py', 1800),
    @('pie_hit_intake', 'run_a5_parity_driver_and_quit.py', 900),
    @('pie_iframes', 'run_a5_parity_driver_and_quit.py', 1800),
    @('pie_fog_gate', 'run_a5_parity_driver_and_quit.py', 720),
    @('pie_remains', 'run_a5_parity_driver_and_quit.py', 900),
    @('pie_soak', 'run_a5_parity_driver_and_quit.py', 1200),
    @('pie_legend', 'run_a5_parity_driver_and_quit.py', 1200)
)
foreach ($p in $pairs) { if ($Only.Count -eq 0 -or $Only -contains $p[0]) { Invoke-Pair $p[0] $p[1] $p[2] } }
Get-ChildItem $here -Recurse -File | Where-Object { $_.Name -ne 'evidence_sha256.txt' -and $_.Extension -ne '.txt' -or $_.Name -eq 'compare.txt' } | Get-FileHash -Algorithm SHA256 |
    ForEach-Object { "$($_.Hash)  $($_.Path.Substring($here.Length + 1))" } | Set-Content "$here\evidence_sha256.txt" -Encoding ascii
'ALL PAIRS DONE'
