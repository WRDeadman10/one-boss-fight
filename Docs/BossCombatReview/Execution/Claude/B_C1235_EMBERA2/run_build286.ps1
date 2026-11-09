# Lead acceptance (Claude, 2026-11-10): BUILD-286 (A-715 A2 annotation + idempotent rerun of A1/A3a/A3b).
# X-1743 strict audit + A-712 author_ember_move_timing.py (A1/A3a/A3b URPGANS_BossMoveTiming, timing-identical, setting stays off).
# Order: build -> author 3 montages (saves only those) -> strict audit -> full suite. Rollback: git checkout of the 3 montages.
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$project = 'C:\UnrealProject\OneBossFight\OneBossFight.uproject'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$cmd = "$engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$hash = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
Set-Location 'C:\UnrealProject\OneBossFight'

if (Get-Process UnrealEditor* -ErrorAction SilentlyContinue) { 'ABORT: editor running' | Tee-Object "$dir\status.txt"; exit 2 }
if ((Test-Path 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json') -or (Test-Path 'ENGINE_LOCK.json')) { 'ABORT: engine lock present' | Tee-Object "$dir\status.txt"; exit 2 }
$lockJson = @{owner='C';purpose='BUILD-286 C-1235 Ember annotations + strict audit';startedUtc=[DateTime]::UtcNow.ToString('o');pid=$PID} | ConvertTo-Json
Set-Content 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json' $lockJson; Set-Content 'ENGINE_LOCK.json' $lockJson
try {
    git status --porcelain -- Source Content | Out-File "$dir\pre_state.txt" -Encoding utf8

    & "$engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *>&1 | Out-File "$dir\build.log" -Encoding utf8
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { "BUILD FAILED exit $buildExit" | Tee-Object "$dir\status.txt"; exit 1 }

    # Strict audit BEFORE authoring (expect MISSING only).
    & $cmd $project '-run=EmberMontageTimingAudit' '-Strict' "-DD27jManifestHash=$hash" -unattended -nosound -nosplash -nullrhi "-abslog=$dir\audit_before.log" | Out-Null
    $auditBefore = $LASTEXITCODE

    # Author the annotations (A-712 script; saves only the 3 Ember montages).
    $script = (Resolve-Path 'Scripts\Editor\author_ember_move_timing.py').Path
    & $cmd $project '-run=pythonscript' "-script=$script" -unattended -nosound -nosplash -nullrhi "-abslog=$dir\author.log" | Out-Null
    $authorExit = $LASTEXITCODE
    $authorDone = (Select-String "$dir\author.log" -Pattern 'EMBER MOVE TIMING AUTHORING COMPLETE' -SimpleMatch).Count
    git status --porcelain -- Content | Out-File "$dir\content_after_author.txt" -Encoding utf8

    # Strict audit AFTER authoring (expect A1/A3a/A3b present, 0 mismatch/duplicate/invalid).
    & $cmd $project '-run=EmberMontageTimingAudit' '-Strict' "-DD27jManifestHash=$hash" -unattended -nosound -nosplash -nullrhi "-abslog=$dir\audit_after.log" | Out-Null
    $auditAfter = $LASTEXITCODE

    & $cmd $project -ExecCmds="Automation RunTests OneBossFight; Quit" "-DD27jManifestHash=$hash" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$dir\suite.log" | Out-Null
    $suiteExit = $LASTEXITCODE
    $pass = (Select-String "$dir\suite.log" -Pattern 'Result=\{Success\}').Count
    $fail = (Select-String "$dir\suite.log" -Pattern 'Result=\{(Fail|Error)').Count
    git status --porcelain -- Source Content | Out-File "$dir\post_state.txt" -Encoding utf8
    Get-ChildItem $dir -File | Where-Object Name -ne 'evidence_sha256.txt' | Get-FileHash -Algorithm SHA256 | ForEach-Object { "$($_.Hash)  $(Split-Path $_.Path -Leaf)" } | Out-File "$dir\evidence_sha256.txt" -Encoding utf8
    "BUILD exit $buildExit; AUDIT_BEFORE exit $auditBefore; AUTHOR exit $authorExit complete=$authorDone; AUDIT_AFTER exit $auditAfter; SUITE exit $suiteExit; success=$pass fail=$fail" | Tee-Object "$dir\status.txt"
} finally {
    Remove-Item 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json','ENGINE_LOCK.json' -ErrorAction SilentlyContinue
}

