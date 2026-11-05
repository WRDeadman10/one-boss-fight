function New-PackagedRunLogPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$StageRoot,
        [Parameter(Mandatory = $true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Label
    )

    $savedRoot = Join-Path $StageRoot 'OneBossFight\Saved'
    $stampPath = Join-Path $savedRoot 'BuildStamp.txt'
    $buildId = 'UNSTAMPED'
    if (Test-Path -LiteralPath $stampPath -PathType Leaf) {
        $candidate = (Get-Content -LiteralPath $stampPath -Raw -ErrorAction Stop).Trim()
        if ($candidate -match '^[A-Za-z0-9_-]{1,80}$') { $buildId = $candidate }
    }

    $runId = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    $runDirectory = Join-Path (Join-Path $savedRoot 'PackagedRuns') (Join-Path $buildId "$Label-$runId")
    New-Item -ItemType Directory -Path $runDirectory -Force | Out-Null
    return (Join-Path $runDirectory 'game.log')
}

Export-ModuleMember -Function New-PackagedRunLogPath
