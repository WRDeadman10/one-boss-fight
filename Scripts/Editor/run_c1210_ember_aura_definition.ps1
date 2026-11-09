$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$uproject = Join-Path $root 'OneBossFight.uproject'
$script = Join-Path $root 'Scripts\Editor\apply_c1210_ember_aura_definition.py'
$log = Join-Path $root 'Saved\Logs\c1210_ember_aura_definition.log'
$locks = @(
    (Join-Path $root 'ENGINE_LOCK.json'),
    (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json')
)
if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { throw 'UnrealEditor is running.' }
foreach ($path in $locks) { if (Test-Path -LiteralPath $path) { throw "Lock exists: $path" } }
$token = [guid]::NewGuid().ToString('N')
$created = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($path in $locks) {
        $record = @{ owner='Codex'; task='C-1210'; command_id=$token; pid=$PID; purpose='C-1210 Ember aura typed-data and G044 receipt update'; start_utc=[DateTime]::UtcNow.ToString('o') } | ConvertTo-Json
        New-Item -Path $path -ItemType File -Value $record -ErrorAction Stop | Out-Null
        $created.Add($path)
    }
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $uproject "-ExecutePythonScript=$script" -nosound -stdout -FullStdOutLogOutput -unattended -NoSplash "-abslog=$log"
    if ($LASTEXITCODE -ne 0) { throw "Editor script exit $LASTEXITCODE; see $log" }
    $pass = Select-String -Path $log -Pattern '\[C1210EmberAura\] PASS'
    if (!$pass) { throw "Editor script did not record its PASS receipt; see $log" }
    Write-Output $pass.Line
} finally {
    foreach ($path in $created.ToArray()) {
        if (Test-Path -LiteralPath $path) {
            $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
            if ($record.command_id -eq $token -and $record.task -eq 'C-1210') { Remove-Item -LiteralPath $path -Force }
            else { Write-Error "Lock ownership changed; preserving $path" }
        }
    }
}
