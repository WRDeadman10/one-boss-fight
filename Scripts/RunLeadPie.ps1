<#
Lead-only PIE probe runner. DryRun prints commands and does not touch the lock,
environment, editor, or output files. Example:
  ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_er_guard_counter.py `
    -Routes legacy,data -Env ER_GC_SYNTHETIC=1,ER_GC_ASSIGN=1 `
    -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1006_GUARDCOUNTER -DryRun
The legacy arm sets RPG_LEGACY_STARTUP=1; both route arms fail closed unless
the raw editor log contains exactly the requested [EncounterActivation] route.
#>
param(
    [Parameter(Mandatory = $true)][string]$Script,
    [ValidateSet('legacy', 'data')][string[]]$Routes = @('legacy', 'data'),
    [string[]]$Env = @(),
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [int]$TimeoutSeconds = 480,
    [string]$StopMarker = '',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$scriptInput = if ([System.IO.Path]::IsPathRooted($Script)) { $Script } else { Join-Path $projectRoot $Script }
$scriptPath = (Resolve-Path -LiteralPath $scriptInput).Path
$projectFile = Join-Path $projectRoot 'OneBossFight.uproject'
$lockPath = Join-Path $projectRoot 'Docs/BossCombatReview/Execution/ENGINE_LOCK.json'
$editorExe = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe'
$outInput = if ([System.IO.Path]::IsPathRooted($OutputDir)) { $OutputDir } else { Join-Path $projectRoot $OutputDir }
$outPath = [System.IO.Path]::GetFullPath($outInput)
$routeAsset = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
if ($TimeoutSeconds -lt 10) { throw 'TimeoutSeconds must be at least 10' }

$extraEnv = @{}
foreach ($entry in $Env) {
    $pair = $entry.Split('=', 2)
    if ($pair.Count -ne 2 -or $pair[0] -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') {
        throw "Invalid -Env entry: $entry (expected NAME=value)"
    }
    if ($pair[0] -in @('H019_ENCOUNTER_DEFINITION', 'RPG_LEGACY_STARTUP')) {
        throw "$($pair[0]) is selected by -Routes"
    }
    $extraEnv[$pair[0]] = $pair[1]
}
$prefixMatch = [regex]::Match([System.IO.File]::ReadAllText($scriptPath), '(?m)^LOG\s*=\s*"(\[[^\]]+\])')
if (-not $StopMarker) {
    if (-not $prefixMatch.Success) { throw 'Probe must declare LOG = "[Prefix] " or supply -StopMarker' }
    $StopMarker = $prefixMatch.Groups[1].Value + ' SUMMARY'
}
$prefix = if ($prefixMatch.Success) { $prefixMatch.Groups[1].Value } else { '' }
$statusLines = [System.Collections.Generic.List[string]]::new()
$hadFailure = $false

if (-not $DryRun) {
    if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { throw 'Editor already running' }
    if (Test-Path -LiteralPath $lockPath) { throw "ENGINE_LOCK already present: $lockPath" }
    if (-not (Test-Path -LiteralPath $editorExe)) { throw "Editor missing: $editorExe" }
    New-Item -ItemType Directory -Path $outPath -Force | Out-Null
    $lockStream = [System.IO.File]::Open($lockPath, [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes((@{
            purpose = 'Lead PIE probe'; owner = 'C'; startTime = (Get-Date).ToString('o')
        } | ConvertTo-Json -Compress))
        $lockStream.Write($bytes, 0, $bytes.Length)
    } finally { $lockStream.Dispose() }
}

try {
    foreach ($route in $Routes) {
        $routeValue = if ($route -eq 'data') { $routeAsset } else { '' }
        $logPath = Join-Path $outPath "${route}.log"
        $linesPath = Join-Path $outPath "${route}_lines.txt"
        # UE's ExecCmds Python command cannot safely contain a spaced path.
        # The 8.3 path is used only for the editor launch; the source remains untouched.
        $pythonPath = if ($DryRun) { $scriptPath } else {
            (New-Object -ComObject Scripting.FileSystemObject).GetFile($scriptPath).ShortPath
        }
        $pythonPath = $pythonPath.Replace([char]92, [char]47)
        if (-not $DryRun -and $pythonPath -match '\s') {
            throw "UE py command requires a path without spaces; 8.3 ShortPath unavailable: $scriptPath"
        }
        $arguments = @(
            "`"$projectFile`"", "-ExecCmds=`"py $pythonPath`"",
            '-unattended', '-nosplash', '-nosound', "-abslog=`"$logPath`""
        )
        if ($DryRun) {
            $legacyStartupValue = if ($route -eq 'legacy') { '1' } else { '(unset)' }
            Write-Output "DRY RUN route=$route H019_ENCOUNTER_DEFINITION=$routeValue RPG_LEGACY_STARTUP=$legacyStartupValue"
            foreach ($name in ($extraEnv.Keys | Sort-Object)) { Write-Output "DRY RUN env $name=$($extraEnv[$name])" }
            if ($pythonPath -match '\s') { Write-Output 'DRY RUN note: live launch requires an available 8.3 ShortPath for this spaced script path' }
            Write-Output "DRY RUN command: `"$editorExe`" $($arguments -join ' ')"
            Write-Output "DRY RUN stop marker: $StopMarker"
            Write-Output "DRY RUN lines file: $linesPath"
            continue
        }
        $savedEnv = @{}
        $allNames = @($extraEnv.Keys) + @('H019_ENCOUNTER_DEFINITION', 'RPG_LEGACY_STARTUP')
        foreach ($name in $allNames) {
            $savedEnv[$name] = [System.Environment]::GetEnvironmentVariable($name, 'Process')
        }
        $process = $null
        try {
            foreach ($name in $extraEnv.Keys) {
                [System.Environment]::SetEnvironmentVariable($name, $extraEnv[$name], 'Process')
            }
            [System.Environment]::SetEnvironmentVariable('H019_ENCOUNTER_DEFINITION', $routeValue, 'Process')
            [System.Environment]::SetEnvironmentVariable('RPG_LEGACY_STARTUP', $(if ($route -eq 'legacy') { '1' } else { '' }), 'Process')
            $process = Start-Process -FilePath $editorExe -ArgumentList $arguments -PassThru
            $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
            $seenMarker = $false
            while (-not $process.HasExited -and (Get-Date) -lt $deadline) {
                Start-Sleep -Seconds 2
                if ((Test-Path -LiteralPath $logPath) -and
                    (Select-String -LiteralPath $logPath -Pattern $StopMarker -SimpleMatch -Quiet)) {
                    $seenMarker = $true
                    Start-Sleep -Seconds 3
                    break
                }
            }
            if (-not $seenMarker -and (Test-Path -LiteralPath $logPath)) {
                $seenMarker = Select-String -LiteralPath $logPath -Pattern $StopMarker -SimpleMatch -Quiet
            }
            if (-not $process.HasExited) { $process.Kill(); $process.WaitForExit() }
            $activationRoutes = @(
                Select-String -LiteralPath $logPath -Pattern '\[EncounterActivation\] route=(legacy|data)\b' |
                    ForEach-Object { [regex]::Match($_.Line, '\[EncounterActivation\] route=(legacy|data)\b').Groups[1].Value } |
                    Sort-Object -Unique
            )
            $routeVerified = ($activationRoutes.Count -eq 1 -and $activationRoutes[0] -eq $route)
            $result = "${route}: finished=$seenMarker route_verified=$routeVerified"
            $statusLines.Add($result)
            if (-not $seenMarker -or -not $routeVerified) { $hadFailure = $true }
            if (Test-Path -LiteralPath $logPath) {
                Get-Content -LiteralPath $logPath | Where-Object {
                    ($prefix -and $_.Contains($prefix)) -or $_.Contains('[EncounterActivation]') -or $_.Contains('Fatal error')
                } | Set-Content -LiteralPath $linesPath -Encoding utf8
            } else {
                "MISSING LOG: $logPath" | Set-Content -LiteralPath $linesPath -Encoding utf8
            }
            Write-Output $result
        } finally {
            if ($process -and -not $process.HasExited) { $process.Kill(); $process.WaitForExit() }
            foreach ($name in $allNames) {
                [System.Environment]::SetEnvironmentVariable($name, $savedEnv[$name], 'Process')
            }
        }
    }
    if (-not $DryRun) {
        $statusLines | Set-Content -LiteralPath (Join-Path $outPath 'status.txt') -Encoding utf8
        if ($hadFailure) { throw 'One or more PIE routes ended without the stop marker; see status.txt' }
    }
} finally {
    if (-not $DryRun) { Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue }
}
