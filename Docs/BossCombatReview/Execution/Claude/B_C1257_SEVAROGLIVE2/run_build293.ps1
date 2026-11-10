# Lead acceptance build+suite (Claude, 2026-11-09, X-1800 C-1256a SpawnFrameworkBossForTest bridge): BUILD-293.
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$project = 'C:\UnrealProject\OneBossFight\OneBossFight.uproject'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
Set-Location 'C:\UnrealProject\OneBossFight'

if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running' | Tee-Object "$dir\status.txt"; exit 2 }
if (Test-Path 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json') { 'ABORT: engine lock present' | Tee-Object "$dir\status.txt"; exit 2 }
$lockJson = @{owner='C';purpose='BUILD-293 C-1257 acceptance';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID} | ConvertTo-Json
Set-Content 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json' $lockJson; Set-Content 'ENGINE_LOCK.json' $lockJson
try {
git status --porcelain -- Source | Out-File "$dir\pre_state.txt" -Encoding utf8

& "$engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *>&1 | Out-File "$dir\build.log" -Encoding utf8
$buildExit = $LASTEXITCODE
if ($buildExit -ne 0) { "BUILD FAILED exit $buildExit" | Tee-Object "$dir\status.txt"; exit 1 }

& "$engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project -ExecCmds="Automation RunTests OneBossFight; Quit" -DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$dir\suite.log" | Out-Null
$suiteExit = $LASTEXITCODE
$pass = (Select-String "$dir\suite.log" -Pattern 'Result=\{Success\}').Count
$fail = (Select-String "$dir\suite.log" -Pattern 'Result=\{(Fail|Error)').Count
git status --porcelain -- Source | Out-File "$dir\post_state.txt" -Encoding utf8
Get-ChildItem $dir -File | Where-Object Name -ne 'evidence_sha256.txt' | Get-FileHash -Algorithm SHA256 | ForEach-Object { "$($_.Hash)  $(Split-Path $_.Path -Leaf)" } | Out-File "$dir\evidence_sha256.txt" -Encoding utf8
"BUILD exit $buildExit; SUITE exit $suiteExit; success=$pass fail=$fail" | Tee-Object "$dir\status.txt"
} finally { Remove-Item 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json','ENGINE_LOCK.json' -ErrorAction SilentlyContinue }



