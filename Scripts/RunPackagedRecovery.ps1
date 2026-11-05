<#
.SYNOPSIS
  Lead-side execution helper for the two G044 packaged recovery arms.
.DESCRIPTION
  Prints both commands by default. With -Execute, launches each arm and keeps
  its per-run log; visual-state screenshots remain a manual capture step.
#>
param(
    [string]$ExePath = '',
    [ValidateRange(10, 600)][int]$Seconds = 60,
    [switch]$Execute
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
if (-not $ExePath) { $ExePath = Join-Path $Root 'Saved\StagedBuilds\Windows\OneBossFight.exe' }
$resolved = (Resolve-Path -LiteralPath $ExePath -ErrorAction SilentlyContinue).Path
if (-not $resolved) { $resolved = [IO.Path]::GetFullPath($ExePath) }
$arms = @(
    @{ Name = 'missing_asset'; Definition = '/Game/OneBossFight/Data/DoesNotExist_C062' },
    @{ Name = 'wrong_class'; Definition = '/Game/OneBossFight/VFX/NS_Boss_ShockwaveRing.NS_Boss_ShockwaveRing' }
)
foreach ($arm in $arms) {
    $args = @('/Game/OneBossFight/Levels/L_SevarogArena', '-nosound', '-log', '-RPGBenchmark', "-H019EncounterDefinition=$($arm.Definition)")
    if (-not $Execute) {
        Write-Output ("[DRY-RUN] {0} `"{1}`" {2}" -f $arm.Name, $resolved, ($args -join ' '))
        continue
    }
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) { throw "Packaged launcher missing: $resolved" }
    Import-Module (Join-Path $PSScriptRoot 'PackagedRunLog.psm1') -Force
    $runLog = New-PackagedRunLogPath -StageRoot (Split-Path -Parent $resolved) -Label ("recovery_{0}" -f $arm.Name)
    $args += "-abslog=$runLog"
    $process = Start-Process -FilePath $resolved -ArgumentList $args -PassThru
    if (-not $process.WaitForExit($Seconds * 1000)) {
        & taskkill.exe /PID $process.Id /T /F | Out-Null
        Write-Output ("[{0}] timed out after {1}s; owned process tree stopped; log={2}" -f $arm.Name, $Seconds, $runLog)
    }
    else {
        Write-Output ("[{0}] exit={1}; log={2}" -f $arm.Name, $process.ExitCode, $runLog)
    }
}
