# C-1619 route source build and DD27j-pinned suite. No PIE, package, cook, or asset authoring.
# A pre-build lead receipt authorizes only this source build and must match the current subsystem hashes.
# On success, this runner emits the post-build receipt consumed by run_sevarog_arena_route_acceptance.ps1.
param([Parameter(Mandatory=$true)][string]$LeadApprovalReceipt)
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$project = Join-Path $root 'OneBossFight.uproject'
$sourceCpp = Join-Path $root 'Source\OneBossFight\Player\RPGPlayerMovesSubsystem.cpp'
$sourceH = Join-Path $root 'Source\OneBossFight\Player\RPGPlayerMovesSubsystem.h'
$bossCpp = Join-Path $root 'Source\OneBossFight\Boss\RPGFrameworkBossCharacter.cpp'
$bossH = Join-Path $root 'Source\OneBossFight\Boss\RPGFrameworkBossCharacter.h'
$blueprintCallH = Join-Path $root 'Source\OneBossFight\Pack\RPGBlueprintCall.h'
$frameworkProfileCpp = Join-Path $root 'Source\OneBossFight\Player\RPGBossFrameworkProfile.cpp'
$frameworkRuntimeTestsCpp = Join-Path $root 'Source\OneBossFight\Tests\RPGFrameworkRuntimeTests.cpp'
$acceptanceRunner = Join-Path $root 'Scripts\Editor\run_sevarog_arena_route_acceptance.ps1'
$acceptanceDriver = Join-Path $root 'Scripts\Editor\pie_sevarog_arena_route_acceptance.py'
$locks = @((Join-Path $root 'ENGINE_LOCK.json'), (Join-Path $root 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$manifest = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
$token = [guid]::NewGuid().ToString('N')
$run = Join-Path $root ('Saved\C1619RouteBuild\Run_' + [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss') + '_' + $token.Substring(0,8))
$created = [System.Collections.Generic.List[string]]::new()
$temps = [System.Collections.Generic.List[string]]::new()
$stage = 'preflight'; $reason = ''; $buildExit = 'not-run'; $suiteExit = 'not-run'
$started = @(); $passed = @(); $failed = @(); $complete = $null

function Test-UnrealRunning { return [bool](@(Get-Process -Name UnrealEditor, UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count -gt 0) }
function Get-SourceHashes {
    return @{
        subsystem_cpp=(Get-FileHash -LiteralPath $sourceCpp -Algorithm SHA256).Hash
        subsystem_h=(Get-FileHash -LiteralPath $sourceH -Algorithm SHA256).Hash
        boss_cpp=(Get-FileHash -LiteralPath $bossCpp -Algorithm SHA256).Hash
        boss_h=(Get-FileHash -LiteralPath $bossH -Algorithm SHA256).Hash
        blueprint_call_h=(Get-FileHash -LiteralPath $blueprintCallH -Algorithm SHA256).Hash
        framework_profile_cpp=(Get-FileHash -LiteralPath $frameworkProfileCpp -Algorithm SHA256).Hash
        framework_runtime_tests_cpp=(Get-FileHash -LiteralPath $frameworkRuntimeTestsCpp -Algorithm SHA256).Hash
        acceptance_runner=(Get-FileHash -LiteralPath $acceptanceRunner -Algorithm SHA256).Hash
        acceptance_driver=(Get-FileHash -LiteralPath $acceptanceDriver -Algorithm SHA256).Hash
    }
}
function Write-AtomicLock([string]$Path, [string]$Record) {
    $temp = $Path + '.' + $token + '.tmp'
    $stream = [IO.File]::Open($temp,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    $temps.Add($temp)
    try { $bytes=[Text.UTF8Encoding]::new($false).GetBytes($Record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) }
    finally { $stream.Dispose() }
    [IO.File]::Move($temp,$Path)
    $temps.Remove($temp)
    $created.Add($Path)
    $readback=Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ($readback.owner_token -cne $token) { throw "ABORT: acquired lock owner token mismatch: $Path" }
}

# Refuse before creating evidence or taking a lock.
if (Test-UnrealRunning) { throw 'ABORT: close UnrealEditor before C-1155 route build' }
foreach ($path in @($project,$sourceCpp,$sourceH,$bossCpp,$bossH,$blueprintCallH,$frameworkProfileCpp,$frameworkRuntimeTestsCpp,$acceptanceRunner,$acceptanceDriver,$LeadApprovalReceipt,(Join-Path $engine 'Build\BatchFiles\Build.bat'),(Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe'))) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "ABORT: required file missing: $path" }
}
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: existing engine lock: $lock" } }
$hashes = Get-SourceHashes
$approval = Get-Content -Raw -LiteralPath $LeadApprovalReceipt | ConvertFrom-Json
if ($approval.task -cne 'C-1619 route source build' -or $approval.lead -cne 'Codex' -or $approval.approved -cne $true -or
    $approval.subsystem_cpp_sha256 -cne $hashes.subsystem_cpp -or $approval.subsystem_h_sha256 -cne $hashes.subsystem_h -or
    $approval.boss_cpp_sha256 -cne $hashes.boss_cpp -or $approval.boss_h_sha256 -cne $hashes.boss_h -or
    $approval.blueprint_call_h_sha256 -cne $hashes.blueprint_call_h -or
    $approval.framework_profile_cpp_sha256 -cne $hashes.framework_profile_cpp -or
    $approval.framework_runtime_tests_cpp_sha256 -cne $hashes.framework_runtime_tests_cpp -or
    $approval.acceptance_runner_sha256 -cne $hashes.acceptance_runner -or
    $approval.acceptance_driver_sha256 -cne $hashes.acceptance_driver) {
    throw 'ABORT: current Codex lead source-build approval receipt is missing, invalid, or bound to different source hashes'
}
if (Test-Path -LiteralPath $run) { throw "ABORT: evidence directory already exists: $run" }
New-Item -ItemType Directory -Path $run | Out-Null
$record = [ordered]@{agent='Codex';party='X';task='C-1619 route source build';command_id='C1619.route-build-suite';owner_token=$token;pid=$PID;start_utc=[DateTime]::UtcNow.ToString('o');policy='C-1155';scope='Development editor build and complete DD27j-pinned suite; no PIE, package, cook, or asset authoring'} | ConvertTo-Json -Compress
try {
    foreach ($lock in $locks) { Write-AtomicLock $lock $record }
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor appeared after lock acquisition' }
    $hashes = Get-SourceHashes
    if ($approval.subsystem_cpp_sha256 -cne $hashes.subsystem_cpp -or $approval.subsystem_h_sha256 -cne $hashes.subsystem_h -or
        $approval.boss_cpp_sha256 -cne $hashes.boss_cpp -or $approval.boss_h_sha256 -cne $hashes.boss_h -or
        $approval.blueprint_call_h_sha256 -cne $hashes.blueprint_call_h -or
        $approval.framework_profile_cpp_sha256 -cne $hashes.framework_profile_cpp -or
        $approval.framework_runtime_tests_cpp_sha256 -cne $hashes.framework_runtime_tests_cpp -or
        $approval.acceptance_runner_sha256 -cne $hashes.acceptance_runner -or
        $approval.acceptance_driver_sha256 -cne $hashes.acceptance_driver) { throw 'ABORT: source changed after approval preflight' }

    $stage='build'
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor appeared before build' }
    $buildLog=Join-Path $run 'build.log'
    & (Join-Path $engine 'Build\BatchFiles\Build.bat') OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReload *> $buildLog
    $buildExit=$LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 120; throw 'C-1619 Development build failed' }

    $stage='suite'
    if (Test-UnrealRunning) { throw 'ABORT: UnrealEditor appeared before pinned suite' }
    $suiteLog=Join-Path $run 'suite.log'; $suiteStdout=Join-Path $run 'suite_stdout.log'
    & (Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe') $project '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$manifest" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$suiteLog" *> $suiteStdout
    $suiteExit=$LASTEXITCODE
    $started=@(Select-String -LiteralPath $suiteLog -Pattern 'Test Started\. Name=' -ErrorAction SilentlyContinue)
    $passed=@(Select-String -LiteralPath $suiteLog -Pattern 'Test Completed\. Result=\{Success\}' -ErrorAction SilentlyContinue)
    $failed=@(Select-String -LiteralPath $suiteLog -Pattern 'Test Completed\. Result=\{(Fail|Error)\}' -ErrorAction SilentlyContinue)
    $complete=Select-String -LiteralPath $suiteLog -Pattern 'TEST COMPLETE\. EXIT CODE: 0' -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($suiteExit -ne 0 -or !$complete -or $started.Count -eq 0 -or $started.Count -ne $passed.Count -or $failed.Count -gt 0) {
        Get-Content $suiteLog -Tail 120; throw 'C-1619 DD27j-pinned suite failed or incomplete'
    }
    $afterHashes = Get-SourceHashes
    if ($afterHashes.subsystem_cpp -cne $hashes.subsystem_cpp -or $afterHashes.subsystem_h -cne $hashes.subsystem_h -or
        $afterHashes.boss_cpp -cne $hashes.boss_cpp -or $afterHashes.boss_h -cne $hashes.boss_h -or
        $afterHashes.blueprint_call_h -cne $hashes.blueprint_call_h -or
        $afterHashes.framework_profile_cpp -cne $hashes.framework_profile_cpp -or
        $afterHashes.framework_runtime_tests_cpp -cne $hashes.framework_runtime_tests_cpp -or
        $afterHashes.acceptance_runner -cne $hashes.acceptance_runner -or
        $afterHashes.acceptance_driver -cne $hashes.acceptance_driver) { throw 'C-1619 source hashes changed during build/suite' }
    $stage='done'
} catch {
    $reason=$_.Exception.Message
    throw
} finally {
    foreach ($temp in $temps) { try { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } } catch {} }
    $released=0; $kept=[System.Collections.Generic.List[string]]::new()
    foreach ($lock in $created) {
        try {
            if (Test-Path -LiteralPath $lock) {
                $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json
                if ($current.owner_token -ceq $token) { Remove-Item -LiteralPath $lock -Force; $released++ }
                else { $kept.Add($lock+' (owner token changed; retained)') }
            }
        } catch { $kept.Add($lock+' (ownership could not be verified or removed)') }
    }
    $result=if ($stage -eq 'done' -and $kept.Count -eq 0 -and $released -eq $locks.Count) {'PASS'} else {'FAIL'}
    $status=[ordered]@{result=$result;stage=$stage;reason=$reason;task='C-1619 route source build';lead='Codex';approved=($result -eq 'PASS');source_build_exit=$buildExit;suite_result=$(if ($result -eq 'PASS') {'PASS'} else {'FAIL'});suite_exit=$suiteExit;started=$started.Count;passed=$passed.Count;failed=$failed.Count;suite_complete=[bool]$complete;dd27j_manifest_hash=$manifest;subsystem_cpp_sha256=$hashes.subsystem_cpp;subsystem_h_sha256=$hashes.subsystem_h;boss_cpp_sha256=$hashes.boss_cpp;boss_h_sha256=$hashes.boss_h;blueprint_call_h_sha256=$hashes.blueprint_call_h;framework_profile_cpp_sha256=$hashes.framework_profile_cpp;framework_runtime_tests_cpp_sha256=$hashes.framework_runtime_tests_cpp;acceptance_runner_sha256=$hashes.acceptance_runner;acceptance_driver_sha256=$hashes.acceptance_driver;owner_token=$token;locks_created=$created.Count;locks_released=$released;locks_kept=@($kept);no_pie=$true;no_package=$true;no_assets=$true}
    try {
        $status | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $run 'status.json') -Encoding UTF8
        if ($result -eq 'PASS') {
            $routeReceipt=[ordered]@{task='C-1619 route acceptance';lead='Codex';approved=$true;source_build_exit=$buildExit;suite_result='PASS';subsystem_cpp_sha256=$hashes.subsystem_cpp;subsystem_h_sha256=$hashes.subsystem_h;boss_cpp_sha256=$hashes.boss_cpp;boss_h_sha256=$hashes.boss_h;blueprint_call_h_sha256=$hashes.blueprint_call_h;framework_profile_cpp_sha256=$hashes.framework_profile_cpp;framework_runtime_tests_cpp_sha256=$hashes.framework_runtime_tests_cpp;acceptance_runner_sha256=$hashes.acceptance_runner;acceptance_driver_sha256=$hashes.acceptance_driver;build_suite_run=$run;dd27j_manifest_hash=$manifest;locks_released=$released}
            $routeReceipt | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $run 'route_lead_approval.json') -Encoding UTF8
        }
        $status | ConvertTo-Json -Depth 5
    } catch { Write-Warning ('Could not write C-1619 build status/receipt: '+$_.Exception.Message) }
}
if ($result -ne 'PASS') { throw 'C-1619 route build/suite result is not PASS' }
if (-not (Test-Path -LiteralPath (Join-Path $run 'route_lead_approval.json') -PathType Leaf)) {
    throw 'C-1619 build/suite passed but the route lead receipt could not be written; do not proceed to PIE'
}
