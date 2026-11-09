param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('probe_aura_niagara_python_api.py','author_aura_boostlite_graph_copy.py')]
    [string]$ScriptName
)

$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$lockPaths = @(
    (Join-Path $root 'ENGINE_LOCK.json'),
    (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json')
)
$editor = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$uproject = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root "Scripts\Editor\$ScriptName"
$token = [guid]::NewGuid().ToString('N')
$created = [System.Collections.Generic.List[string]]::new()

if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) {
    throw 'Refusing to start: an UnrealEditor process is already active.'
}
foreach ($path in $lockPaths) {
    if (Test-Path -LiteralPath $path) { throw "Refusing to start: existing lock $path" }
}
if (!(Test-Path -LiteralPath $editor) -or !(Test-Path -LiteralPath $uproject) -or !(Test-Path -LiteralPath $script)) {
    throw 'Required editor, project, or script path is missing.'
}

try {
    foreach ($path in $lockPaths) {
        $record = @{ owner='Codex'; task='C-1202'; command_id=$token; pid=$PID; purpose="C-1202 $ScriptName"; start_utc=[DateTime]::UtcNow.ToString('o') } | ConvertTo-Json
        New-Item -Path $path -ItemType File -Value $record -ErrorAction Stop | Out-Null
        $created.Add($path)
    }
    & $editor $uproject "-ExecutePythonScript=$script" -nosound -stdout -FullStdOutLogOutput -unattended -NoSplash "-abslog=$(Join-Path $root 'Saved\Logs\c1202_aura_graph_authoring.log')"
    if ($LASTEXITCODE -ne 0) { throw "UnrealEditor-Cmd exited with $LASTEXITCODE" }
} finally {
    foreach ($path in @($created.ToArray())) {
        if (Test-Path -LiteralPath $path) {
            $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
            if ($record.command_id -eq $token -and $record.task -eq 'C-1202') {
                Remove-Item -LiteralPath $path -Force
            } else {
                Write-Error "Lock ownership changed; preserving $path"
            }
        }
    }
}
