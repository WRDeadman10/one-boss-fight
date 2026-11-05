<#
.SYNOPSIS
  Shipping package + benchmark smoke + Development-only feature string scan.
.DESCRIPTION
  Defaults to a printed dry run. Pass -Execute only from the Lead's packaging
  session; the benchmark uses the existing RunBenchmark.ps1 wrapper.
#>
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.5',
    [ValidateRange(30, 1800)][int]$TimeoutSeconds = 900,
    [switch]$Execute
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Package = Join-Path $PSScriptRoot 'Package.ps1'
$Benchmark = Join-Path $PSScriptRoot 'RunBenchmark.ps1'
$Stage = Join-Path $Root 'Saved\StagedBuilds\Windows'
$Exe = Join-Path $Stage 'OneBossFight.exe'
$Binary = Join-Path $Stage 'OneBossFight\Binaries\Win64\OneBossFight-Win64-Shipping.exe'
$Features = Join-Path $PSScriptRoot 'CheckShippingFeatureSymbols.py'
$Plan = @(
    "& `"$Package`" -Configuration Shipping -EngineRoot `"$EngineRoot`"",
    "& `"$Benchmark`" -Label shipping_smoke -StageDir `"$Stage`" -TimeoutSeconds $TimeoutSeconds",
    "& python.exe -I `"$Features`" `"$Binary`""
)
if (-not $Execute) {
    $Plan | ForEach-Object { Write-Output ("[DRY-RUN] {0}" -f $_) }
    exit 0
}

& $Package -Configuration Shipping -EngineRoot $EngineRoot
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Shipping package failed: $LASTEXITCODE" }
if (-not (Test-Path -LiteralPath $Exe -PathType Leaf)) { throw "Packaged launcher missing: $Exe" }
& $Benchmark -Label shipping_smoke -StageDir $Stage -TimeoutSeconds $TimeoutSeconds
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Shipping benchmark smoke failed: $LASTEXITCODE" }
& python.exe -I $Features $Binary
if ($LASTEXITCODE -ne 0) { throw "Shipping feature-symbol scan failed: $LASTEXITCODE" }
