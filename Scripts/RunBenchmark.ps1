<#
.SYNOPSIS
  Runs the packaged benchmark and prints the summary.

.DESCRIPTION
  Launches the staged build on L_Benchmark with -RPGBenchmark -RPGBenchmarkQuit. The runner removes the
  frame cap, discards the warmup, records raw frame times and writes frames.csv + summary.json under the
  staged project's Saved\Benchmark\<label>_<timestamp>. Close other heavy apps first (browser, editor).

.EXAMPLE
  .\Scripts\RunBenchmark.ps1 -Label baseline_defaults
  .\Scripts\RunBenchmark.ps1 -Label lumen_off -ExtraArgs '-ExecCmds="r.DynamicGlobalIlluminationMethod 0"'
#>
param(
	[string]$Label = 'run',
	[int]$ResX = 1920,
	[int]$ResY = 1080,
	[string]$Map = '/Game/OneBossFight/Levels/L_Benchmark',
	[string]$ExtraArgs = ''
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StageRoot = Join-Path $ProjectRoot 'Saved\StagedBuilds\Windows'
$Exe = Join-Path $StageRoot 'OneBossFight.exe'
if (-not (Test-Path $Exe)) { throw "Packaged build not found at $Exe. Run Scripts\Package.ps1 first." }

$LaunchArgs = @(
	$Map,
	'-RPGBenchmark', '-RPGBenchmarkQuit', "-RPGBenchmarkLabel=$Label",
	'-windowed', "-ResX=$ResX", "-ResY=$ResY", '-ForceRes',
	'-nosplash', '-NoSound', '-log'
)
if ($ExtraArgs) { $LaunchArgs += $ExtraArgs }

Write-Host "Running benchmark '$Label' at ${ResX}x${ResY} ..."
$Process = Start-Process -FilePath $Exe -ArgumentList $LaunchArgs -PassThru -Wait
Write-Host "Exit code: $($Process.ExitCode)"

$BenchmarkDir = Join-Path $StageRoot 'OneBossFight\Saved\Benchmark'
$Latest = Get-ChildItem $BenchmarkDir -Directory -Filter "${Label}_*" -ErrorAction SilentlyContinue |
	Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $Latest) { throw "No results found under $BenchmarkDir" }

$Summary = Get-Content (Join-Path $Latest.FullName 'summary.json') -Raw | ConvertFrom-Json
Write-Host "Results: $($Latest.FullName)"
$Summary | Format-List
