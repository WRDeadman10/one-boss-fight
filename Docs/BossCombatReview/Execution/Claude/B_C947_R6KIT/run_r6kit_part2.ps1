# R6b kit, part 2 (lead, Claude, 2026-11-06). Part 1 packaged Shipping (12:04) and Development (12:07, telemetry=True, telemetry_check.txt) but MakeBenchKit
# failed: the Shipping stage had no BuildStamp.txt and the Development stamp used OBF-DEV-, while check_bench_kit.py requires OBF-SHIPPING-/OBF-DEVELOPMENT-.
# Package.ps1 is fixed for future packages; here both EXISTING stages get the same stamp Package.ps1 now writes (no repackage, the binaries are unchanged),
# then the kit and zip are built on D:.
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$root = 'C:\UnrealProject\OneBossFight'
Set-Location $root
function Status($m) { $m | Tee-Object "$dir\status.txt" }
function Stamp($stage, $config) {
    $d = Join-Path $stage 'OneBossFight\Saved'
    New-Item -ItemType Directory -Path $d -Force | Out-Null
    $id = 'OBF-' + $config + '-' + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    Set-Content -LiteralPath (Join-Path $d 'BuildStamp.txt') -Value $id -Encoding ascii
    "$config $id $stage" | Out-File "$dir\stamps.txt" -Append -Encoding utf8
}
try {
    Stamp (Join-Path $root 'Saved\StagedBuilds_Shipping\Windows') 'SHIPPING'
    Stamp (Join-Path $root 'Saved\StagedBuilds\Windows') 'DEVELOPMENT'
    & powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MakeBenchKit.ps1 -OutDir 'D:\BenchTransfer\R6b' -IncludeDevelopment -Zip *>&1 | Out-File "$dir\makekit2.log" -Encoding utf8
    if ($LASTEXITCODE -ne 0) { Status "MAKEKIT FAILED exit $LASTEXITCODE (makekit2.log)"; exit 1 }
    $zip = Get-Item 'D:\BenchTransfer\R6b\OneBossFight_BenchKit.zip'
    "zip $($zip.FullName) $($zip.Length) bytes" | Out-File "$dir\kit.txt" -Encoding utf8
    (Get-FileHash $zip.FullName -Algorithm SHA256).Hash | Out-File "$dir\kit_zip_sha256.txt" -Encoding ascii
    Copy-Item 'D:\BenchTransfer\R6b\OneBossFight_BenchKit\BUILD_INFO.txt' "$dir\BUILD_INFO.txt"
    git status --porcelain -- Source Config Content | Out-File "$dir\post_state.txt" -Encoding utf8
    Get-ChildItem $dir -File | Where-Object Name -ne 'evidence_sha256.txt' | Get-FileHash -Algorithm SHA256 | ForEach-Object { "$($_.Hash)  $(Split-Path $_.Path -Leaf)" } | Out-File "$dir\evidence_sha256.txt" -Encoding utf8
    Status "R6B KIT OK telemetry=True zip=$($zip.FullName) bytes=$($zip.Length)"
} catch {
    Status "PART2 ERROR: $($_.Exception.Message)"
    exit 1
}
