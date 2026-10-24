<#
.SYNOPSIS
  Starts a staged One Boss Fight build briefly and checks its packaged log.

.DESCRIPTION
  This is a smoke check, not a benchmark. It starts the packaged launcher with
  -nosound -log, waits, requires the process to remain alive, stops it, then
  delegates log validation to CheckPackagedLog.ps1.
#>
param(
    [ValidateRange(1, 3600)]
    [int]$Seconds = 20,

    [string]$ExePath = ''
)

$ErrorActionPreference = 'Stop'

# $PSScriptRoot is empty when the script is started some ways (a sandboxed shell): fall back to the script's own path, then to the working directory (the repository root).
$scriptDir = $PSScriptRoot
if (-not $scriptDir -and $MyInvocation.MyCommand.Path) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Join-Path (Get-Location).Path 'Scripts' }
if (-not $ExePath) { $ExePath = Join-Path $scriptDir '..\Saved\StagedBuilds\Windows\OneBossFight.exe' }

function Find-RuntimeLog {
    param([string]$Executable)

    $folder = Split-Path -Parent $Executable
    for ($level = 0; $level -lt 5 -and $folder; ++$level) {
        $candidate = Join-Path $folder 'OneBossFight\Saved\Logs\OneBossFight.log'
        if (Test-Path -LiteralPath $candidate) {
            return (Get-Item -LiteralPath $candidate).FullName
        }
        $candidate = Join-Path $folder 'Saved\Logs\OneBossFight.log'
        if (Test-Path -LiteralPath $candidate) {
            return (Get-Item -LiteralPath $candidate).FullName
        }
        $parent = Split-Path -Parent $folder
        if ($parent -eq $folder) { break }
        $folder = $parent
    }
    return $null
}

$resolvedExe = (Resolve-Path -LiteralPath $ExePath -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath $resolvedExe -PathType Leaf)) {
    throw "Packaged executable is not a file: $resolvedExe"
}

$checker = Join-Path $scriptDir 'CheckPackagedLog.ps1'
if (-not (Test-Path -LiteralPath $checker -PathType Leaf)) {
    throw "Packaged log checker is missing: $checker"
}

$process = $null
$alive = $false
$launchTime = Get-Date
try {
    Write-Host ("[Smoke] launching {0} for {1} s" -f $resolvedExe, $Seconds)
    $process = Start-Process -FilePath $resolvedExe -ArgumentList '-nosound', '-log' -PassThru
    Start-Sleep -Seconds $Seconds
    $process.Refresh()
    $alive = -not $process.HasExited
    if ($alive) {
        Write-Host ("[Smoke] PASS process {0} remained alive for {1} s" -f $process.Id, $Seconds)
    }
    else {
        Write-Host ("[Smoke] FAIL process {0} exited before {1} s" -f $process.Id, $Seconds)
    }
}
finally {
    # The staged OneBossFight.exe is a launcher: the game itself is its child (OneBossFight-Win64-*.exe). Stopping only the launcher leaves the game running and locks the staging folder (found 2026-10-24), so the whole process tree is stopped and any game process started since the launch.
    if ($process) {
        if (-not $process.HasExited) {
            & taskkill.exe /PID $process.Id /T /F | Out-Null
            Write-Host ("[Smoke] stopped process tree {0}" -f $process.Id)
        }
        Get-Process -Name 'OneBossFight-Win64-*' -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -ge $launchTime.AddSeconds(-2) } | ForEach-Object {
            Write-Host ("[Smoke] stopped game process {0}" -f $_.Id)
            Stop-Process -Id $_.Id -Force
        }
    }
}

# The log is looked for AFTER the run (a first run has none before it) and must have been written by this run.
# A Shipping build writes no log (logging is compiled out, found 2026-10-24): for it the log step is skipped and the debug-off proof is Scripts/CheckShippingBinary.py (no rpg.Debug, no LogRPGDebug in the executable).
$runtimeLog = Find-RuntimeLog -Executable $resolvedExe
$shippingBinary = Join-Path (Split-Path -Parent $resolvedExe) 'OneBossFight\Binaries\Win64\OneBossFight-Win64-Shipping.exe'
if (-not $runtimeLog -or (Get-Item -LiteralPath $runtimeLog).LastWriteTime -lt $launchTime) {
    if (Test-Path -LiteralPath $shippingBinary -PathType Leaf) {
        Write-Host '[Smoke] NOTE a Shipping build writes no runtime log: the log step is skipped, the binary is checked instead'
        $binaryChecker = Join-Path $scriptDir 'CheckShippingBinary.py'
        & python.exe -I $binaryChecker $shippingBinary
        $binaryExit = $LASTEXITCODE
        if ($binaryExit -eq 0) { Write-Host '[Smoke] PASS Shipping binary check' } else { Write-Host ("[Smoke] FAIL Shipping binary check exit {0}" -f $binaryExit) }
        if ($alive -and $binaryExit -eq 0) { Write-Host '[Smoke] VERDICT PASS (Shipping: alive and no debug names)'; exit 0 }
        Write-Host '[Smoke] VERDICT FAIL'
        exit 1
    }
    Write-Host ("[Smoke] FAIL no runtime log written by this run beside {0}" -f $resolvedExe)
    Write-Host '[Smoke] VERDICT FAIL'
    exit 1
}
& $checker -RuntimeLog $runtimeLog
$checkerExit = $LASTEXITCODE
if ($checkerExit -eq 0) {
    Write-Host '[Smoke] PASS packaged log checker'
}
else {
    Write-Host ("[Smoke] FAIL packaged log checker exit {0}" -f $checkerExit)
}

if ($alive -and $checkerExit -eq 0) {
    Write-Host '[Smoke] VERDICT PASS'
    exit 0
}

Write-Host '[Smoke] VERDICT FAIL'
exit 1
