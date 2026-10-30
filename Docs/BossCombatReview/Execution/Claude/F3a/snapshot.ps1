# Writes a path|size|mtime(UTC ticks) listing of Content, Config, Source, Binaries plus a summary hash; usage: snapshot.ps1 -Out <file>
param([Parameter(Mandatory=$true)][string]$Out)
$root = 'C:\UnrealProject\OneBossFight'
$rows = foreach ($d in 'Content','Config','Source','Binaries') {
    $p = Join-Path $root $d
    if (Test-Path $p) { Get-ChildItem -LiteralPath $p -Recurse -File -Force | ForEach-Object { '{0}|{1}|{2}' -f $_.FullName.Substring($root.Length + 1).Replace('\','/'), $_.Length, $_.LastWriteTimeUtc.Ticks } }
}
$rows | Sort-Object | Set-Content -LiteralPath $Out -Encoding utf8
$h = (Get-FileHash -LiteralPath $Out -Algorithm SHA256).Hash.ToLower()
"snapshot rows=$($rows.Count) sha256=$h out=$Out"
