<#
.SYNOPSIS
  Runs the packaged benchmark and prints the summary.

.DESCRIPTION
  Launches the staged build on L_SevarogArena with -RPGBenchmark -RPGBenchmarkFight -RPGBenchmarkQuit (the bot fights Sevarog; -Empty orbits an empty arena). The runner removes the
  frame cap, discards the warmup, records raw frame times and writes frames.csv + summary.json under the
  staged project's Saved\Benchmark\<label>_<timestamp>. Close other heavy apps first (browser, editor).

.EXAMPLE
  .\Scripts\RunBenchmark.ps1 -Label baseline_defaults
  .\Scripts\RunBenchmark.ps1 -Label lumen_off -ExtraArgs '-ExecCmds="r.DynamicGlobalIlluminationMethod 0"'
  $env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'; .\Scripts\RunBenchmark.ps1 -Label selected_a
#>
param(
	[string]$Label = 'run',
	[int]$ResX = 1920,
	[int]$ResY = 1080,
	[string]$Map = '/Game/OneBossFight/Levels/L_SevarogArena',
	[switch]$Empty,   # empty-arena orbit camera instead of the full fight
	[string]$ExtraArgs = '',
	[switch]$KeepConfig,
	[string]$StageDir = '',  # a different staged build folder (the one that holds OneBossFight.exe), e.g. the Development stage of the kit
	[ValidateRange(1, 7200)][int]$TimeoutSeconds = 900
)

$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'BenchmarkEncounterSelection.psm1') -Force

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StageRoot = if ($StageDir) { $StageDir } else { Join-Path $ProjectRoot 'Saved\StagedBuilds\Windows' }
$Exe = Join-Path $StageRoot 'OneBossFight.exe'
if (-not (Test-Path $Exe)) { throw "Packaged build not found at $Exe. Run Scripts\Package.ps1 first." }

$LaunchArgs = @(
	$Map,
	'-RPGBenchmark', '-RPGBenchmarkQuit', "-RPGBenchmarkLabel=$Label",
	'-windowed', "-ResX=$ResX", "-ResY=$ResY", '-ForceRes',
	'-nosplash', '-NoSound', '-log'
)
if (-not $Empty) { $LaunchArgs += '-RPGBenchmarkFight' }
$LaunchArgs += @(Get-H019EncounterArgument -EncounterDefinition $env:H019_ENCOUNTER_DEFINITION)
if ($ExtraArgs) { $LaunchArgs += $ExtraArgs }

# Precaution: every run starts from the default graphics settings. A previous run can leave GameUserSettings.ini behind (suspected, not proven: in the round 2 experiments of 2026-10-25 the first ten runs were slow and the later ones fast with no clear cause). Only the staged game's own Saved\Config and the local data copy of a Shipping build are cleaned, never the project.
if (-not $KeepConfig) {
	foreach ($cfg in @((Join-Path $StageRoot 'OneBossFight\Saved\Config'), (Join-Path $env:LOCALAPPDATA 'OneBossFight\Saved\Config'))) {
		if (Test-Path $cfg) { Get-ChildItem $cfg -Recurse -Filter 'GameUserSettings.ini' -ErrorAction SilentlyContinue | Remove-Item -Force }
	}
}
Write-Host "Running benchmark '$Label' at ${ResX}x${ResY} ..."
$Process = Start-Process -FilePath $Exe -ArgumentList $LaunchArgs -PassThru
if (-not $Process.WaitForExit($TimeoutSeconds * 1000)) {
	& taskkill.exe /PID $Process.Id /T /F | Out-Null
	throw "Benchmark process exceeded the $TimeoutSeconds-second deadline; terminated owned PID tree $($Process.Id)."
}
Write-Host "Exit code: $($Process.ExitCode)"
if ($Process.ExitCode -ne 0) {
	throw "Benchmark process failed with exit code $($Process.ExitCode); refusing to report a successful run."
}

# A Development build writes next to the staged game (Saved\StagedBuilds\Windows\OneBossFight\Saved); a SHIPPING build writes to the user's local data folder (%LOCALAPPDATA%\OneBossFight\Saved), found 2026-10-24: both places are searched, the newest run of this label wins.
$BenchmarkDirs = @(
	(Join-Path $StageRoot 'OneBossFight\Saved\Benchmark'),
	(Join-Path $env:LOCALAPPDATA 'OneBossFight\Saved\Benchmark')
)
$Latest = $BenchmarkDirs | ForEach-Object { Get-ChildItem $_ -Directory -Filter "${Label}_*" -ErrorAction SilentlyContinue } |
	Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $Latest) { throw "No results found under: $($BenchmarkDirs -join '; ')" }

# Keep this run's game log next to its results (2026-11-05, Round 5): the engine rotates OneBossFight.log on every launch, so after a
# long experiment plan the early runs' logs (and their DLSS active-mode lines) would otherwise be gone. Copy only; nothing is deleted.
foreach ($logDir in @((Join-Path $StageRoot 'OneBossFight\Saved\Logs'), (Join-Path $env:LOCALAPPDATA 'OneBossFight\Saved\Logs'))) {
	$gameLog = Join-Path $logDir 'OneBossFight.log'
	if ((Test-Path $gameLog) -and ((Get-Item $gameLog).LastWriteTime -ge $Process.StartTime)) {
		Copy-Item $gameLog (Join-Path $Latest.FullName 'game.log') -Force
		break
	}
}

$Summary = Get-Content (Join-Path $Latest.FullName 'summary.json') -Raw | ConvertFrom-Json
Write-Host "Results: $($Latest.FullName)"
$Summary | Format-List
