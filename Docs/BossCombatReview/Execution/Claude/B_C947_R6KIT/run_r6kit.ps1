# R6b bench kit (lead, Claude, 2026-11-06; owner "Yes, package it"). The R6 kit of 2026-11-05 18:38 predates BUILD-229 (P2a telemetry), so the benchmark PC
# refused Round 6. This packages Shipping and Development from the current tree (commit 21dbcb18 + BUILD-240 green), verifies the telemetry string in the staged
# Development exe, and writes the kit and zip to D:\BenchTransfer\R6b (owner: kits on D: only). Evidence: logs, status.txt, sha256 in this folder.
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$root = 'C:\UnrealProject\OneBossFight'
Set-Location $root
function Status($m) { $m | Tee-Object "$dir\status.txt" }
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { Status 'ABORT: editor running'; exit 2 }
if (Test-Path 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json') { Status 'ABORT: engine lock present'; exit 2 }
git rev-parse HEAD | Out-File "$dir\head.txt" -Encoding ascii
git status --porcelain -- Source Config Content | Out-File "$dir\pre_state.txt" -Encoding utf8

# 1. Shipping, then keep its stage aside (both configurations stage into Saved\StagedBuilds\Windows)
& powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\Package.ps1 -Configuration Shipping *>&1 | Out-File "$dir\package_shipping.log" -Encoding utf8
if ($LASTEXITCODE -ne 0) { Status "SHIPPING PACKAGE FAILED exit $LASTEXITCODE"; exit 1 }
$ship = Join-Path $root 'Saved\StagedBuilds_Shipping\Windows'
if (Test-Path $ship) { Remove-Item $ship -Recurse -Force }
New-Item -ItemType Directory -Force -Path $ship | Out-Null
$null = robocopy (Join-Path $root 'Saved\StagedBuilds\Windows') $ship /E /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { Status "ROBOCOPY SHIPPING FAILED $LASTEXITCODE"; exit 1 }

# 2. Development
& powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\Package.ps1 -Configuration Development *>&1 | Out-File "$dir\package_development.log" -Encoding utf8
if ($LASTEXITCODE -ne 0) { Status "DEVELOPMENT PACKAGE FAILED exit $LASTEXITCODE"; exit 1 }

# 3. The staged Development exe must carry the P2a telemetry log line (BUILD-229)
$devExe = Get-ChildItem (Join-Path $root 'Saved\StagedBuilds\Windows') -Recurse -Filter 'OneBossFight*.exe' | Where-Object { $_.Length -gt 10MB } | Select-Object -First 1
$text = [Text.Encoding]::Unicode.GetString([IO.File]::ReadAllBytes($devExe.FullName))
$hasTelemetry = $text.Contains('effective_primary_screen_percentage')
"dev exe $($devExe.FullName) $($devExe.Length) bytes $($devExe.LastWriteTime.ToString('o')) telemetry=$hasTelemetry" | Out-File "$dir\telemetry_check.txt" -Encoding utf8
if (-not $hasTelemetry) { Status 'TELEMETRY MISSING in the staged Development exe'; exit 1 }

# 4. Kit and zip on D:
New-Item -ItemType Directory -Force -Path 'D:\BenchTransfer\R6b' | Out-Null
& powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MakeBenchKit.ps1 -OutDir 'D:\BenchTransfer\R6b' -IncludeDevelopment -Zip *>&1 | Out-File "$dir\makekit.log" -Encoding utf8
if ($LASTEXITCODE -ne 0) { Status "MAKEKIT FAILED exit $LASTEXITCODE"; exit 1 }
$zip = Get-ChildItem 'D:\BenchTransfer\R6b' -Filter '*.zip' | Select-Object -First 1
"zip $($zip.FullName) $($zip.Length) bytes" | Out-File "$dir\kit.txt" -Encoding utf8
(Get-FileHash $zip.FullName -Algorithm SHA256).Hash | Out-File "$dir\kit_zip_sha256.txt" -Encoding ascii
git status --porcelain -- Source Config Content | Out-File "$dir\post_state.txt" -Encoding utf8
Get-ChildItem $dir -File | Where-Object Name -ne 'evidence_sha256.txt' | Get-FileHash -Algorithm SHA256 | ForEach-Object { "$($_.Hash)  $(Split-Path $_.Path -Leaf)" } | Out-File "$dir\evidence_sha256.txt" -Encoding utf8
Status "R6B KIT OK telemetry=True zip=$($zip.FullName) bytes=$($zip.Length)"
