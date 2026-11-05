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

    [ValidateSet('Development', 'Shipping')]
    [string]$Configuration = 'Development',

    [string]$ExePath = ''
)

$ErrorActionPreference = 'Stop'

# $PSScriptRoot is empty when the script is started some ways (a sandboxed shell): fall back to the script's own path, then to the working directory (the repository root).
$scriptDir = $PSScriptRoot
if (-not $scriptDir -and $MyInvocation.MyCommand.Path) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Join-Path (Get-Location).Path 'Scripts' }
if (-not $ExePath) { $ExePath = Join-Path $scriptDir '..\Saved\StagedBuilds\Windows\OneBossFight.exe' }

$resolvedExe = (Resolve-Path -LiteralPath $ExePath -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath $resolvedExe -PathType Leaf)) {
    throw "Packaged executable is not a file: $resolvedExe"
}

$checker = Join-Path $scriptDir 'CheckPackagedLog.ps1'
if (-not (Test-Path -LiteralPath $checker -PathType Leaf)) {
    throw "Packaged log checker is missing: $checker"
}

Import-Module (Join-Path $scriptDir 'PackagedRunLog.psm1') -Force
$StageRoot = Split-Path -Parent $resolvedExe
$RunLog = New-PackagedRunLogPath -StageRoot $StageRoot -Label 'smoke'

$process = $null
$alive = $false
$launchTime = Get-Date
try {
    Write-Host ("[Smoke] launching {0} for {1} s" -f $resolvedExe, $Seconds)
    $process = Start-Process -FilePath $resolvedExe -ArgumentList '-nosound', '-log', "-abslog=$RunLog" -PassThru
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
    # The staged OneBossFight.exe is a launcher: stop only its PID tree so the game child cannot keep the staging folder locked. Avoid image-name sweeps that can stop an unrelated game.
    if ($process) {
        $descendants = @()
        try {
            $allProcesses = @(Get-CimInstance Win32_Process -ErrorAction Stop)
            $treeIds = @([int]$process.Id)
            do {
                $children = @($allProcesses | Where-Object {
                    ([int]$_.ParentProcessId) -in $treeIds -and
                    ([int]$_.ProcessId) -notin $treeIds -and
                    $_.CreationDate -ge $launchTime
                })
                foreach ($child in $children) { $treeIds += [int]$child.ProcessId }
            } while ($children.Count -gt 0)
            $descendants = @($allProcesses | Where-Object { ([int]$_.ProcessId) -in @($treeIds | Select-Object -Skip 1) })
        }
        catch {
            Write-Warning ("[Smoke] could not snapshot launcher descendants; will attempt PID-tree cleanup only: {0}" -f $_)
        }
        if (-not $process.HasExited) {
            & taskkill.exe /PID $process.Id /T /F | Out-Null
            Write-Host ("[Smoke] stopped process tree {0}" -f $process.Id)
        }
        foreach ($descendant in $descendants) {
            $current = Get-CimInstance Win32_Process -Filter ("ProcessId={0}" -f $descendant.ProcessId) -ErrorAction SilentlyContinue
            if ($current -and [string]$current.CreationDate -eq [string]$descendant.CreationDate -and $current.ParentProcessId -eq $descendant.ParentProcessId) {
                Write-Host ("[Smoke] stopping snapshotted child process {0}" -f $descendant.ProcessId)
                & taskkill.exe /PID $descendant.ProcessId /T /F | Out-Null
            }
        }
    }
}

# The log path is unique to this invocation. Shipping compiles runtime logging out,
# so its debug-off proof remains the binary checker.
# A Shipping build writes no log (logging is compiled out, found 2026-10-24): for it the log step is skipped and the debug-off proof is Scripts/CheckShippingBinary.py (no rpg.Debug, no LogRPGDebug in the executable).
$runtimeLog = $RunLog
$shippingBinary = Join-Path (Split-Path -Parent $resolvedExe) 'OneBossFight\Binaries\Win64\OneBossFight-Win64-Shipping.exe'
if ($Configuration -eq 'Shipping') {
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
    Write-Host ("[Smoke] FAIL Shipping binary not found: {0}" -f $shippingBinary)
    Write-Host '[Smoke] VERDICT FAIL'
    exit 1
}
if (-not (Test-Path -LiteralPath $runtimeLog -PathType Leaf)) {
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
