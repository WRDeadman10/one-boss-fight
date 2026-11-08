<#
.SYNOPSIS
  Cooks and stages a packaged Windows build of One Boss Fight.

.DESCRIPTION
  Wraps UAT BuildCookRun. Development defaults to Saved\StagedBuilds\Windows;
  Shipping defaults to Saved\StagedBuilds_Shipping\Windows (git-ignored).
  -StageDir can explicitly override the UAT staging root.

.EXAMPLE
  .\Scripts\Package.ps1
  .\Scripts\Package.ps1 -Configuration Shipping
#>
param(
	[ValidateSet('Development', 'Shipping')]
	[string]$Configuration = 'Development',

	[string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.5',

	# Optional UAT staging root (the UAT parent of Windows). Relative paths are project-root-relative.
	[string]$StageDir = '',

	# Optional post-cook G044 + project VFX closure check. Supply a Lead-reviewed
	# closure export and a normalized manifest captured from this exact package.
	[string]$G044RequiredFile = '',
	[string]$G044CookManifest = ''
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Project = Join-Path $ProjectRoot 'OneBossFight.uproject'
$Uat = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$DefaultStageRelative = if ($Configuration -eq 'Shipping') {
	'Saved\StagedBuilds_Shipping'
} else {
	'Saved\StagedBuilds'
}
$StageWasOverridden = -not [string]::IsNullOrWhiteSpace($StageDir)
if (-not $StageWasOverridden) {
	$StageDir = Join-Path $ProjectRoot $DefaultStageRelative
} elseif (-not [IO.Path]::IsPathRooted($StageDir)) {
	$StageDir = Join-Path $ProjectRoot $StageDir
}
$StageDir = [IO.Path]::GetFullPath($StageDir)

# Keep the built-in configuration destinations distinct. An explicit custom
# root remains available for Lead workflows and is reported verbatim below.
$OtherDefaultRelative = if ($Configuration -eq 'Shipping') {
	'Saved\StagedBuilds'
} else {
	'Saved\StagedBuilds_Shipping'
}
$OtherDefaultStage = [IO.Path]::GetFullPath((Join-Path $ProjectRoot $OtherDefaultRelative))
if (-not $StageWasOverridden -and $StageDir -eq $OtherDefaultStage) {
	throw "Default $Configuration stage root collides with the other configuration: $StageDir"
}

if (-not (Test-Path $Uat)) { throw "RunUAT.bat not found at $Uat" }

if ([string]::IsNullOrWhiteSpace($G044RequiredFile) -ne [string]::IsNullOrWhiteSpace($G044CookManifest)) {
	throw 'G044 cook verification requires both -G044RequiredFile and -G044CookManifest.'
}

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

# Every configuration gets a build ID (lead fix 2026-11-06: only Development was stamped, as OBF-DEV-..., while Scripts\Tools\check_bench_kit.py requires
# OBF-SHIPPING-... or OBF-DEVELOPMENT-... for the kit's selected stage, so MakeBenchKit failed for every kit). The game shows the stamp only in non-Shipping builds.
if ($true) {
	$StampDirectory = Join-Path $StageDir 'Windows\OneBossFight\Saved'
	New-Item -ItemType Directory -Path $StampDirectory -Force | Out-Null
	$BuildId = 'OBF-' + $Configuration.ToUpperInvariant() + '-' + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
	$StampPath = Join-Path $StampDirectory 'BuildStamp.txt'
	Set-Content -LiteralPath $StampPath -Value $BuildId -Encoding ascii
	Write-Host ("[PACKAGE_BUILD_ID] {0}" -f $BuildId)
}

if ($G044RequiredFile) {
	$G044Checker = Join-Path $PSScriptRoot 'Tools\check_packaged_g044_cook.py'
	if (-not (Test-Path -LiteralPath $G044RequiredFile -PathType Leaf)) { throw "G044 required closure file not found: $G044RequiredFile" }
	if (-not (Test-Path -LiteralPath $G044CookManifest -PathType Leaf)) { throw "G044 normalized cook manifest not found: $G044CookManifest" }
	& python.exe -I $G044Checker --required $G044RequiredFile --manifest $G044CookManifest --configuration $Configuration --content-root (Join-Path $ProjectRoot 'Content')
	if ($LASTEXITCODE -ne 0) { throw "G044/VFX cook-manifest verification failed with exit code $LASTEXITCODE" }
}

Write-Host "Done. Run it with Scripts\RunBenchmark.ps1"
