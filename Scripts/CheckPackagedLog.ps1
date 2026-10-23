<#
.SYNOPSIS
  Read-only checks for packaged cook and runtime log failures.

.DESCRIPTION
  Uses the newest UAT text log and staged runtime log by default. Each input may
  be either a log file or a folder. Findings print their file, line, and text.
  Exit 0 only when asset, error/cook/shader, and fatal categories are empty.
#>
param(
    [string]$CookLog,
    [string]$RuntimeLog
)

$ErrorActionPreference = 'Stop'

function Resolve-LogInput {
    param(
        [string]$InputPath,
        [string]$DefaultFolder,
        [string[]]$Patterns,
        [string]$Label
    )

    $Candidate = $InputPath
    if ([string]::IsNullOrWhiteSpace($Candidate)) {
        $Candidate = $DefaultFolder
    }

    if (-not (Test-Path -LiteralPath $Candidate)) {
        throw "$Label log path does not exist: $Candidate"
    }

    if (-not (Get-Item -LiteralPath $Candidate).PSIsContainer) {
        return (Get-Item -LiteralPath $Candidate).FullName
    }

    $Files = Get-ChildItem -LiteralPath $Candidate -File -Recurse |
        Where-Object {
            $extension = $_.Extension
            $Patterns -contains $extension
        } |
        Sort-Object LastWriteTime -Descending

    if ($null -eq $Files -or $Files.Count -eq 0) {
        throw "No $Label log matching $($Patterns -join ', ') under $Candidate"
    }

    return $Files[0].FullName
}

function Read-LogRecords {
    param([string]$Path)

    $number = 0
    foreach ($line in Get-Content -LiteralPath $Path -ErrorAction Stop) {
        $number++
        [pscustomobject]@{
            File = $Path
            Line = $number
            Text = $line
        }
    }
}

function Show-Findings {
    param(
        [string]$Name,
        [object[]]$Findings
    )

    Write-Host ("[{0}] {1}" -f $Name, $Findings.Count)
    if ($Findings.Count -eq 0) {
        Write-Host '  (none)'
        return
    }

    $Findings | Select-Object -First 10 | ForEach-Object {
        Write-Host ("  {0}:{1}: {2}" -f $_.File, $_.Line, $_.Text)
    }
    if ($Findings.Count -gt 10) {
        Write-Host ("  ... {0} additional finding(s) omitted" -f ($Findings.Count - 10))
    }
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$UatLogs = Join-Path $env:APPDATA 'Unreal Engine\AutomationTool\Logs'
$RuntimeLogs = Join-Path $ProjectRoot 'Saved\StagedBuilds\Windows\OneBossFight\Saved\Logs'
$CookPath = Resolve-LogInput -InputPath $CookLog -DefaultFolder $UatLogs -Patterns @('.txt', '.log') -Label 'cook/UAT'
$RuntimePath = Resolve-LogInput -InputPath $RuntimeLog -DefaultFolder $RuntimeLogs -Patterns @('.log', '.txt') -Label 'runtime'

$records = @((Read-LogRecords -Path $CookPath)) + @((Read-LogRecords -Path $RuntimePath))

# Keep generic optional profiler-DLL loader noise out of KI-084. Asset failures
# require an asset/package context or an explicit /Game path.
$assetFindings = @($records | Where-Object {
    $_.Text -match '(?i)(/Game/.*(?:failed to (?:load|find)|unable to load|could not load|can''t find)|(?:failed to (?:load|find)|unable to load|could not load|can''t find).*(?:/Game/|\.uasset|asset|package|object)|LogLinker:.*(?:failed|unable|could not|can''t).*(?:load|find))'
})

$errorFindings = @($records | Where-Object {
    $_.Text -match '(?i)(\bError:|LogShaderCompilers:\s*Error|(?:Cook|ShaderCompileWorker|Shader).*\b(?:error|failed|failure)\b)'
})

$rpgWarnings = @($records | Where-Object {
    $_.Text -match '(?i)\bLogRPG\w*:\s*Warning:'
})

# These identify output that should be impossible in Shipping: RPGCombatDebug
# owns LogRPGDebug/rpg.Debug and RPGBossShockwave owns DrawDebugCircle.
$shippingDebug = @($records | Where-Object {
    $_.Text -match '(?i)(\bLogRPGDebug:|\brpg\.Debug\b|\bDrawDebugCircle\b)'
})

# Do not use CrashGUID here: Unreal writes a Session CrashGUID at normal startup.
$fatalFindings = @($records | Where-Object {
    $_.Text -match '(?i)(Fatal error:|Critical error:|LowLevelFatalError|Unhandled Exception|Ensure condition failed)'
})

Write-Host 'Packaged log check (read-only)'
Write-Host ("Cook/UAT log: {0}" -f $CookPath)
Write-Host ("Runtime log:  {0}" -f $RuntimePath)
Show-Findings -Name 'missing/unloadable assets (KI-084)' -Findings $assetFindings
Show-Findings -Name 'Error / shader / cook' -Findings $errorFindings
Show-Findings -Name 'LogRPG warnings' -Findings $rpgWarnings
Show-Findings -Name 'Shipping debug text' -Findings $shippingDebug
Show-Findings -Name 'crash / fatal' -Findings $fatalFindings

if ($assetFindings.Count -eq 0 -and $errorFindings.Count -eq 0 -and $fatalFindings.Count -eq 0) {
    Write-Host 'Result: PASS (blocking categories empty)'
    exit 0
}

Write-Host 'Result: FAIL (blocking findings present)'
exit 1
