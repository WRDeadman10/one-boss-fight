param(
    [Parameter(Mandatory = $true)][ValidateSet('control','block','parry')][string]$Mode,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [Parameter(Mandatory = $true)][string]$Task,
    [double]$ParryOffsetSeconds = 0.0,
    [int]$DurationSeconds = 75
)
$root = 'C:\UnrealProject\OneBossFight'
$taskDir = "$root\Docs\BossCombatReview\Execution\Codex\PACK_ARENA_DRIVER"
$configPath = "$taskDir\current_config.json"
@{
    mode = $Mode
    run_id = $Task
    duration_seconds = $DurationSeconds
    parry_offset_seconds = $ParryOffsetSeconds
    input_hold_seconds = $(if ($Mode -eq 'block') { 0.5 } else { 0.12 })
    sample_interval_seconds = 0.25
    editor_log_path = (Join-Path $OutDir 'editor_raw.log')
} | ConvertTo-Json | Set-Content -Encoding utf8 $configPath
& "$root\Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1" `
    -Script "$taskDir\pack_arena_melee_driver.py" `
    -OutDir $OutDir `
    -Task $Task `
    -PyCmd 1 `
    -NullRhi 0 `
    -TimeoutSeconds 240
