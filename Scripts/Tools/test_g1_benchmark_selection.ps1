$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$scriptPath = Join-Path $root 'Scripts\RunBenchmark.ps1'
$modulePath = Join-Path $root 'Scripts\BenchmarkEncounterSelection.psm1'
$tokens = $null
$parseErrors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw "RunBenchmark.ps1 parse failed: $($parseErrors -join '; ')" }
Import-Module $modulePath -Force

$baseline = @('/Game/OneBossFight/Levels/L_SevarogArena', '-RPGBenchmark', '-RPGBenchmarkFight', '-NoSound')
$unset = @($baseline + @(Get-H019EncounterArgument -EncounterDefinition ''))
if (($unset -join "`0") -cne ($baseline -join "`0")) { throw 'Unset selection changed the benchmark launch argument vector.' }

$selected = @(Get-H019EncounterArgument -EncounterDefinition '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter')
if ($selected.Count -ne 1 -or $selected[0] -cne '-H019EncounterDefinition=/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter') {
    throw 'Selected path did not produce exactly one H019 benchmark argument.'
}

$refused = $false
try { [void](Get-H019EncounterArgument -EncounterDefinition '/Game/Boss Bad;quit') } catch { $refused = $true }
if (-not $refused) { throw 'Unsafe selection argument was not refused.' }

$source = Get-Content $scriptPath -Raw
if ($source -notmatch "Get-H019EncounterArgument -EncounterDefinition \`$env:H019_ENCOUNTER_DEFINITION") {
    throw 'RunBenchmark.ps1 does not route the H019 environment variable through the tested argument builder.'
}
Write-Output 'G1 benchmark selection helper: PASS (unset identity, selected argument, unsafe path refusal, PowerShell parse)'
