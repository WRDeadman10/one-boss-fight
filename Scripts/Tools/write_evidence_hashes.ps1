function Write-EvidenceHashes {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$EvidenceRoot)

    $root = [IO.Path]::GetFullPath($EvidenceRoot).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw "Evidence directory does not exist: $root" }
    $manifest = Join-Path $root 'evidence_sha256.txt'
    $rows = @(Get-ChildItem -LiteralPath $root -File -Recurse |
        Where-Object { [IO.Path]::GetFullPath($_.FullName) -ne $manifest } |
        Sort-Object FullName |
        ForEach-Object {
            $relative = $_.FullName.Substring($root.Length).TrimStart([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar).Replace('\', '/')
            $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            "$hash  $relative"
        })
    [IO.File]::WriteAllLines($manifest, $rows, [Text.UTF8Encoding]::new($false))
    return $manifest
}
