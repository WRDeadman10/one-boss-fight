<#
.SYNOPSIS
  Lead's build/native gate followed by the five BUILD-232 default-off parity pairs.
.DESCRIPTION
  Prints a dry run by default. -Execute invokes Gate.ps1 and, after it passes,
  runs the five archived pair harnesses and summarizes their comparator reports.
#>
param([Parameter(Mandatory = $true)][string]$BuildId, [switch]$Execute)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Gate = Join-Path $PSScriptRoot 'Gate.ps1'
$Parity = Join-Path $Root 'Docs\BossCombatReview\Execution\Claude\B_C835_PARITY\run_parity.ps1'
$Summary = Join-Path $Root 'Scripts\Tools\summarize_parity_set.py'
$ParityRoot = Join-Path $Root 'Docs\BossCombatReview\Execution\Claude\B_C835_PARITY'
$Pairs = @('pie_phase_reset','pie_boss_death','pie_authored_close_clips','pie_legend','pie_iframes')
$Suffix = '_gate_' + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')

if (-not $Execute) {
    & $Gate -DryRun
    Write-Output ("DRY RUN parity: powershell -NoProfile -ExecutionPolicy Bypass -File `"{0}`" -Only {1} -BuildId {2} -Suffix {3}" -f $Parity, ($Pairs -join ','), $BuildId, $Suffix)
    Write-Output ("DRY RUN summary: python -I `"{0}`" --root `"{1}`" --suffix {2}" -f $Summary, $ParityRoot, $Suffix)
    exit 0
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Gate
if ($LASTEXITCODE -ne 0) { throw "Local gate failed with exit code $LASTEXITCODE" }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Parity -Only $Pairs -BuildId $BuildId -Suffix $Suffix
if ($LASTEXITCODE -ne 0) { throw "Parity pair runner failed with exit code $LASTEXITCODE" }
& python.exe -I $Summary --root $ParityRoot --suffix $Suffix
if ($LASTEXITCODE -ne 0) { throw "One or more selected parity comparators failed" }
