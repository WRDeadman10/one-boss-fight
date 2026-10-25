<#
.SYNOPSIS
  Assembles the benchmark kit for another PC: the packaged Shipping build (and optionally the Development build for GPU profiling) and the benchmark scripts, in one folder (and optionally one zip).

.DESCRIPTION
  Run it on the development PC after Scripts\Package.ps1 -Configuration Shipping (stage kept in Saved\StagedBuilds_Shipping\Windows) and -Configuration Development (stage in Saved\StagedBuilds\Windows). The kit folder has the same shape as the project root where it matters (Saved\StagedBuilds\Windows = Shipping, Saved\StagedBuilds_Development\Windows = Development, Scripts), so Scripts\RunBenchmark.ps1 works unchanged on the other PC (-StageDir picks the Development stage).
  Output: <OutDir>\OneBossFight_BenchKit\ (about 3 GB with Shipping only, about 6.5 GB with both). Copy the folder (or the zip) to the other PC, any local drive path without spaces.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MakeBenchKit.ps1 -OutDir C:/BenchTransfer -IncludeDevelopment -Zip
#>
param([Parameter(Mandatory = $true)][string]$OutDir, [switch]$IncludeDevelopment, [switch]$DevelopmentOnly, [switch]$Zip,
      [string]$ShippingStage = '', [string]$DevelopmentStage = '')
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
if (-not $ShippingStage) {
    $ShippingStage = Join-Path $Root 'Saved\StagedBuilds_Shipping\Windows'
    if (-not (Test-Path (Join-Path $ShippingStage 'OneBossFight.exe'))) { $ShippingStage = Join-Path $Root 'Saved\StagedBuilds\Windows' }
}
if (-not $DevelopmentStage) { $DevelopmentStage = Join-Path $Root 'Saved\StagedBuilds\Windows' }
if ($DevelopmentOnly) { $IncludeDevelopment = $true }
if (-not $DevelopmentOnly -and -not (Test-Path (Join-Path $ShippingStage 'OneBossFight.exe'))) { throw "No staged Shipping build at ${ShippingStage}: run Scripts\Package.ps1 -Configuration Shipping first." }
$Kit = Join-Path $OutDir 'OneBossFight_BenchKit'
if (Test-Path $Kit) { Remove-Item $Kit -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $Kit 'Scripts') | Out-Null

function Copy-Stage($From, $To) {
    # robocopy skips the .pdb symbol files (not needed to run, several hundred MB); exit codes below 8 mean success
    $null = robocopy $From $To /E /XF *.pdb /NFL /NDL /NJH /NJS /NP
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed with exit code $LASTEXITCODE" }
}
if (-not $DevelopmentOnly) {
    Write-Host "Copying the Shipping stage (about 3 GB) ..."
    Copy-Stage $ShippingStage (Join-Path $Kit 'Saved\StagedBuilds\Windows')
}
if ($IncludeDevelopment) {
    if (-not (Test-Path (Join-Path $DevelopmentStage 'OneBossFight.exe'))) { throw "No staged Development build at ${DevelopmentStage}" }
    Write-Host "Copying the Development stage (about 3.5 GB) ..."
    Copy-Stage $DevelopmentStage (Join-Path $Kit 'Saved\StagedBuilds_Development\Windows')
}
foreach ($f in 'RunBenchmark.ps1', 'SummarizeBenchmark.py', 'BenchKit_Collect.ps1', 'PackagedSmoke.ps1', 'RunPerfExperiments.ps1') {
    Copy-Item (Join-Path $Root "Scripts\$f") (Join-Path $Kit "Scripts\$f") -Force
}
Copy-Item (Join-Path $Root 'Documentation\BENCHKIT_README.md') (Join-Path $Kit 'BENCHKIT_README.md') -Force
$exePath = if ($DevelopmentOnly) { Join-Path $Kit 'Saved\StagedBuilds_Development\Windows\OneBossFight\Binaries\Win64\OneBossFight.exe' } else { Join-Path $Kit 'Saved\StagedBuilds\Windows\OneBossFight\Binaries\Win64\OneBossFight-Win64-Shipping.exe' }
$exe = Get-Item $exePath
"Executable time: $($exe.LastWriteTime.ToString('o')); size $($exe.Length)`r`nShipping stage included: $(-not $DevelopmentOnly); Development stage included: $IncludeDevelopment" | Out-File (Join-Path $Kit 'BUILD_INFO.txt') -Encoding utf8
Write-Host "Kit: $Kit"
if ($Zip) {
    $z = Join-Path $OutDir 'OneBossFight_BenchKit.zip'
    Write-Host "Zipping to $z (several minutes) ..."
    # Compress-Archive of Windows PowerShell 5.1 fails above 2 GB: tar.exe (bsdtar, part of Windows 10/11) writes the zip
    if (Test-Path $z) { Remove-Item $z -Force }
    & "$env:SystemRoot/System32/tar.exe" -a -c -f $z -C $OutDir OneBossFight_BenchKit
    if ($LASTEXITCODE -ne 0) { throw "tar failed with exit code $LASTEXITCODE" }
    Write-Host "Zip: $z"
}
