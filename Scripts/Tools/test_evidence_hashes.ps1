$ErrorActionPreference = 'Stop'
$helper = Join-Path $PSScriptRoot 'write_evidence_hashes.ps1'
. $helper
$temp = Join-Path ([IO.Path]::GetTempPath()) ("onebossfight-hash-test-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $temp 'nested') -Force | Out-Null
try {
    $inputPath = Join-Path $temp 'nested\sample.log'
    [IO.File]::WriteAllText($inputPath, "fixture`n")
    $manifest = Write-EvidenceHashes -EvidenceRoot $temp
    $line = @(Get-Content -LiteralPath $manifest)
    $expected = (Get-FileHash -LiteralPath $inputPath -Algorithm SHA256).Hash.ToLowerInvariant() + '  nested/sample.log'
    if ($line.Count -ne 1 -or $line[0] -notmatch '^([0-9a-f]{64})  nested/sample\.log$' -or $Matches[1] -ne (Get-FileHash -LiteralPath $inputPath -Algorithm SHA256).Hash.ToLowerInvariant()) {
        throw "unexpected manifest: $($line -join ' | ')"
    }
    'PASS relative path and SHA-256 match'
}
finally { Remove-Item -LiteralPath $temp -Force -Recurse }
