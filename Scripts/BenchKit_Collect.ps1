<#
.SYNOPSIS
  Runs on the BENCHMARK PC (the one with the target-class GPU): collects the benchmark results and the facts that make them valid into one zip.

.DESCRIPTION
  Run it AFTER the four benchmark runs (RunBenchmark.ps1 warm-up + three). It does not run the game. It writes bench_results_<computer>_<timestamp>.zip next to the kit folder containing:
   - every benchmark run folder found (frames.csv and summary.json) from the staged build and from %LOCALAPPDATA%\OneBossFight\Saved\Benchmark;
   - system_info.txt: the session type (console or rdp), Windows version, CPU, RAM, GPU name and driver, monitor mode, power plan, nvidia-smi output;
   - summary_table.txt: the output of SummarizeBenchmark.py;
   - the newest game log (Saved\Logs) when there is one.
  The session must be the CONSOLE session of the physical PC (query user shows SESSIONNAME console); a Remote Desktop session reports a virtual GPU and its numbers are invalid.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\BenchKit_Collect.ps1
#>
$ErrorActionPreference = 'Continue'
$Kit = Split-Path -Parent $PSScriptRoot
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Work = Join-Path $env:TEMP "bench_collect_$Stamp"
New-Item -ItemType Directory -Force -Path $Work | Out-Null

# 1. the facts
$info = @()
$info += "Collected: $(Get-Date -Format o)"
$info += "Computer: $env:COMPUTERNAME  User: $env:USERNAME"
$info += "--- query user (the benchmark user's SESSIONNAME must be 'console', not rdp-tcp#...)"
$info += (query user 2>&1 | Out-String)
$info += "--- OS"
$info += ((Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber | Format-List | Out-String))
$info += "--- CPU and RAM"
$info += ((Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | Format-List | Out-String))
$info += ((Get-CimInstance Win32_ComputerSystem | Select-Object @{n = 'RAM_GB'; e = { [math]::Round($_.TotalPhysicalMemory / 1GB, 1) } } | Format-List | Out-String))
$info += "--- GPU(s) and monitor mode"
$info += ((Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, DriverDate, CurrentHorizontalResolution, CurrentVerticalResolution, CurrentRefreshRate, VideoProcessor | Format-List | Out-String))
$info += "--- nvidia-smi"
$info += ((& nvidia-smi 2>&1 | Out-String))
$info += ((& nvidia-smi --query-gpu=name,driver_version,clocks.max.graphics,power.limit,pcie.link.gen.current --format=csv 2>&1 | Out-String))
$info += "--- power plan"
$info += ((powercfg /getactivescheme 2>&1 | Out-String))
$info | Out-File -FilePath (Join-Path $Work 'system_info.txt') -Encoding utf8

# 2. the runs
$roots = @(
    (Join-Path $Kit 'Saved\StagedBuilds\Windows\OneBossFight\Saved\Benchmark'),
    (Join-Path $Kit 'Saved\StagedBuilds_Development\Windows\OneBossFight\Saved\Benchmark'),
    (Join-Path $env:LOCALAPPDATA 'OneBossFight\Saved\Benchmark')
)
$n = 0
foreach ($root in $roots) {
    if (Test-Path $root) {
        foreach ($dir in Get-ChildItem $root -Directory) {
            $target = Join-Path $Work (Join-Path 'runs' $dir.Name)
            Copy-Item $dir.FullName $target -Recurse -Force
            $n++
        }
    }
}
"run folders copied: $n" | Out-File (Join-Path $Work 'runs_count.txt')

# 3. the table
$py = Join-Path $Kit 'Scripts\SummarizeBenchmark.py'
if (Test-Path $py) {
    $rootArgs = @()
    foreach ($root in $roots) { if (Test-Path $root) { $rootArgs += @('--root', $root) } }
    (& python -I $py @rootArgs 2>&1 | Out-String) | Out-File (Join-Path $Work 'summary_table.txt') -Encoding utf8
}

# 4. the newest game log
$logDirs = @((Join-Path $Kit 'Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs'), (Join-Path $Kit 'Saved\StagedBuilds_Development\Windows\OneBossFight\Saved\Logs'), (Join-Path $env:LOCALAPPDATA 'OneBossFight\Saved\Logs'))
$li = 0
foreach ($ld in $logDirs) {
    if (Test-Path $ld) {
        # all logs of the Development stage (they carry the ProfileGPU tables), the newest of the others
        $logs = Get-ChildItem $ld -Filter '*.log' | Sort-Object LastWriteTime -Descending
        if ($ld -notlike '*Development*') { $logs = $logs | Select-Object -First 1 }
        foreach ($log in $logs) { Copy-Item $log.FullName (Join-Path $Work ("game${li}_" + $log.Name)) -Force }
    }
    $li++
}
# the experiment tables of RunPerfExperiments.ps1
Get-ChildItem (Join-Path $Kit 'Saved') -Filter 'smi_*.csv' -ErrorAction SilentlyContinue | ForEach-Object { Copy-Item $_.FullName $Work -Force }
Get-ChildItem (Join-Path $Kit 'Saved') -Filter 'perf_experiments_*.txt' -ErrorAction SilentlyContinue | ForEach-Object { Copy-Item $_.FullName $Work -Force }

$zip = Join-Path (Split-Path -Parent $Kit) "bench_results_${env:COMPUTERNAME}_$Stamp.zip"
Compress-Archive -Path (Join-Path $Work '*') -DestinationPath $zip -Force
Write-Host "Results written to: $zip"
Write-Host "Run folders: $n. Look at system_info.txt first: the session must be 'console' and the GPU must name the NVIDIA card."
