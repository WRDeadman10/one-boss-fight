$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path $PSScriptRoot -Parent)
$repoPaths = & git -C $Root diff --name-only -- Documentation
if ($LASTEXITCODE -ne 0) { throw 'git diff could not list changed documentation files.' }
$failures = @()
foreach ($repoPath in $repoPaths) {
    if (-not $repoPath.EndsWith('.md', [System.StringComparison]::OrdinalIgnoreCase)) { continue }
    $currentPath = Join-Path $Root ($repoPath -replace '/', '\')
    if (-not (Test-Path -LiteralPath $currentPath -PathType Leaf)) {
        $failures += "$repoPath is missing from the working tree"
        continue
    }
    $tracked = & git -C $Root ls-files --error-unmatch -- $repoPath 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "SKIP new document (no HEAD baseline): $repoPath"; continue }
    $baseline = @(& git -C $Root show "HEAD:$repoPath")
    if ($LASTEXITCODE -ne 0) { throw "Cannot read HEAD baseline for $repoPath" }
    $current = @(Get-Content -LiteralPath $currentPath)
    if ($current.Count -lt $baseline.Count) {
        $failures += "$repoPath shrank from $($baseline.Count) to $($current.Count) lines"
    } else {
        Write-Host "PASS $repoPath ($($baseline.Count) -> $($current.Count) lines)"
    }
}
if ($failures.Count) { $failures | ForEach-Object { Write-Error $_ }; exit 1 }
Write-Host 'PASS documentation line-count guard'
