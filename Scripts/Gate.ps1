<#
.SYNOPSIS
  Runs the local engineering gate in a fixed order and records one JSON receipt.
.DESCRIPTION
  Refuses to start while this project's editor is open. The build/native test step
  delegates to Rebuild.ps1 -Tests -NoRelaunch; offline checks and release guards
  follow. -DryRun prints the commands without executing them or writing a receipt.
#>
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Project = Join-Path $Root 'OneBossFight.uproject'
$Engine = 'C:\Program Files\Epic Games\UE_5.5'
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$ReceiptPath = Join-Path $Root "Saved\LocalGate\gate_$Stamp.json"
$Steps = @(
    [pscustomobject]@{ Name = 'build_and_native_tests'; File = 'powershell'; Args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $PSScriptRoot 'Rebuild.ps1'),'-Tests','-NoRelaunch') },
    [pscustomobject]@{ Name = 'offline_tool_suite'; File = 'python'; Args = @('-m','unittest','discover','-s','Scripts/Tools') },
    [pscustomobject]@{ Name = 'make_bench_kit_dependency_test'; File = 'python'; Args = @('-m','unittest','discover','-s','Scripts/Tools','-p','test_make_bench_kit_dependencies.py') },
    [pscustomobject]@{ Name = 'shipping_debug_guard'; File = 'python'; Args = @('-I','Scripts/CheckShippingBinary.py',(Join-Path $Root 'Saved\StagedBuilds_Shipping\Windows\OneBossFight\Binaries\Win64\OneBossFight-Win64-Shipping.exe')) },
    [pscustomobject]@{ Name = 'documentation_line_count_guard'; File = 'powershell'; Args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $PSScriptRoot 'Tools\CheckDocLineCounts.ps1')) }
)

function Get-ProjectEditorProcesses {
    $full = [System.IO.Path]::GetFullPath($Project)
    Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" -ErrorAction Stop |
        Where-Object { $_.CommandLine -and $_.CommandLine.IndexOf($full, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 }
}

try { $editors = @(Get-ProjectEditorProcesses) }
catch { throw "Cannot safely determine whether this project's editor is open; gate refused: $_" }
if ($editors.Count -gt 0) { throw "Gate refused because this project's UnrealEditor is open (PID $($editors.ProcessId -join ', ')). Close it and rerun." }

if ($DryRun) {
    foreach ($step in $Steps) { Write-Output ("DRY RUN {0}: {1} {2}" -f $step.Name, $step.File, ($step.Args -join ' ')) }
    Write-Output 'DRY RUN complete; no gate commands ran and no receipt was written.'
    exit 0
}

$results = [System.Collections.Generic.List[object]]::new()
foreach ($step in $Steps) {
    $started = Get-Date
    Write-Host "=== $($step.Name) ==="
    $invokeArgs = $step.Args
    & $step.File @invokeArgs
    $exitCode = $LASTEXITCODE
    if ($null -eq $exitCode) { $exitCode = 0 }
    $results.Add([pscustomobject]@{ name = $step.Name; exit_code = $exitCode; started = $started.ToString('o'); finished = (Get-Date).ToString('o') })
    if ($exitCode -ne 0) { break }
}
$passed = $results.Count -eq $Steps.Count -and @($results | Where-Object exit_code -ne 0).Count -eq 0
$receipt = [pscustomobject]@{ schema = 1; project = $Project; started = $Stamp; passed = $passed; steps = @($results) }
New-Item -ItemType Directory -Force -Path (Split-Path $ReceiptPath) | Out-Null
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ReceiptPath -Encoding utf8
Write-Host "GATE $($(if ($passed) { 'PASS' } else { 'FAIL' })); receipt: $ReceiptPath"
if (-not $passed) { exit 1 }
