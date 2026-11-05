param([Parameter(Mandatory = $true)][string]$Runner)
$temp = Join-Path ([IO.Path]::GetTempPath()) ("onebossfight-evidence-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null
try {
    $output = & $Runner -Script 'unused.py' -OutDir $temp -Task 'offline-guard-test' 2>&1
    if ($LASTEXITCODE -ne 2 -or ($output -join "`n") -notmatch 'evidence folder already exists') {
        throw "existing evidence folder was not refused (exit=$LASTEXITCODE): $output"
    }
    if ((Get-ChildItem -LiteralPath $temp -Force | Measure-Object).Count -ne 0) {
        throw 'guard wrote into the existing evidence folder'
    }
    'PASS existing evidence folder refused without mutation'
}
finally { Remove-Item -LiteralPath $temp -Force -Recurse }
