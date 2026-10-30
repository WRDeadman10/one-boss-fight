# One-shot headless editor script run with evidence (lead, Claude). Usage:
#   run_editor_script.ps1 -Script <py> -OutDir <dir> -Task <name> [-ExtraArgs <string[]>] [-TimeoutSeconds 240] [-NullRhi $true]
# Refuses to start when an engine process or ENGINE_LOCK.json exists. Writes ENGINE_LOCK.json, pre/post snapshots, raw log, result.json; releases the lock last.
param(
    [Parameter(Mandatory = $true)][string]$Script,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [Parameter(Mandatory = $true)][string]$Task,
    [string[]]$ExtraArgs = @(),
    [int]$TimeoutSeconds = 240,
    [bool]$NullRhi = $true
)
$root = 'C:\UnrealProject\OneBossFight'
$lock = "$root\Docs\BossCombatReview\Execution\ENGINE_LOCK.json"
$snap = "$root\Docs\BossCombatReview\Execution\Claude\F3a\snapshot.ps1"
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
if (@(Get-Process | Where-Object { $_.ProcessName -match 'UnrealEditor|UnrealBuildTool' }).Count -gt 0) { 'STOP: engine process running' | Set-Content "$OutDir\STOP.txt"; exit 2 }
if (Test-Path $lock) { 'STOP: engine lock present' | Set-Content "$OutDir\STOP.txt"; exit 2 }
@{ agent = 'Claude'; party = 'C'; task = $Task; start_utc = (Get-Date).ToUniversalTime().ToString('o'); policy = 'C-321' } | ConvertTo-Json | Set-Content $lock
try {
    & $snap -Out "$OutDir\pre_state.txt" | Set-Content "$OutDir\pre_state_summary.txt"
    $args = @("$root\OneBossFight.uproject", "-ExecutePythonScript=`"$Script`"", '-unattended', '-nosound', '-nosplash', "-abslog=$OutDir\editor_raw.log") + $ExtraArgs
    if ($NullRhi) { $args += '-nullrhi' }
    $args | ConvertTo-Json | Set-Content "$OutDir\command.json"
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $p = Start-Process -FilePath $engine -ArgumentList $args -PassThru -WindowStyle Hidden
    $timedOut = $false
    if (-not $p.WaitForExit($TimeoutSeconds * 1000)) { $timedOut = $true; $p.Kill(); $p.WaitForExit() }
    $sw.Stop()
    & $snap -Out "$OutDir\post_state.txt" | Set-Content "$OutDir\post_state_summary.txt"
    $rawHash = (Get-FileHash "$OutDir\editor_raw.log" -Algorithm SHA256).Hash.ToLower()
    @{ task = $Task; exit_code = $p.ExitCode; timed_out = $timedOut; seconds = [int]$sw.Elapsed.TotalSeconds; raw_sha256 = $rawHash } | ConvertTo-Json | Set-Content "$OutDir\result.json"
    "exit=$($p.ExitCode) timedOut=$timedOut seconds=$([int]$sw.Elapsed.TotalSeconds) raw=$rawHash"
}
finally { Remove-Item $lock -Force -ErrorAction SilentlyContinue }
