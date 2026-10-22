<#
.SYNOPSIS
  Cooks and stages a packaged Windows build of One Boss Fight.

.DESCRIPTION
  Wraps UAT BuildCookRun. Output goes to Saved\StagedBuilds\Windows (git-ignored).
  Use Development for profiling captures and Shipping for final verification.

.EXAMPLE
  .\Scripts\Package.ps1
  .\Scripts\Package.ps1 -Configuration Shipping
#>
param(
	[ValidateSet('Development', 'Shipping')]
	[string]$Configuration = 'Development',

	[string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.5'
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Project = Join-Path $ProjectRoot 'OneBossFight.uproject'
$Uat = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$StageDir = Join-Path $ProjectRoot 'Saved\StagedBuilds'

if (-not (Test-Path $Uat)) { throw "RunUAT.bat not found at $Uat" }

# Only the maps we ship are cooked.
$Maps = '/Game/OneBossFight/Levels/L_SevarogArena'

Write-Host "Packaging $Configuration build -> $StageDir"

& $Uat BuildCookRun `
	"-project=$Project" `
	-platform=Win64 `
	"-clientconfig=$Configuration" `
	-build -cook -stage -pak `
	"-map=$Maps" `
	"-stagingdirectory=$StageDir" `
	-NoP4 -utf8output

if ($LASTEXITCODE -ne 0) { throw "BuildCookRun failed with exit code $LASTEXITCODE" }

Write-Host "Done. Run it with Scripts\RunBenchmark.ps1"
