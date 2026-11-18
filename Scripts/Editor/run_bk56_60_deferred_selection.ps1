param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.5',
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$uproject = Join-Path $ProjectRoot 'OneBossFight.uproject'
$engine = Join-Path $EngineRoot 'Engine'
$buildTool = Join-Path $engine 'Build\BatchFiles\Build.bat'
$editor = Join-Path $engine 'Binaries\Win64\UnrealEditor.exe'
$editorCmd = Join-Path $engine 'Binaries\Win64\UnrealEditor-Cmd.exe'
$driver = Join-Path $ProjectRoot 'Scripts\Editor\pie_sevarog_framework_live.py'
$author = Join-Path $ProjectRoot 'Scripts\Editor\author_framework_encounter_definition.py'
$phaseAuthor = Join-Path $ProjectRoot 'Scripts\Editor\ensure_bk56_60_sevarog_initial_phase.py'
$manifest = 'cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec'
$locks = @((Join-Path $ProjectRoot 'ENGINE_LOCK.json'), (Join-Path $ProjectRoot 'Docs\BossCombatReview\Execution\ENGINE_LOCK.json'))
$stamp = [DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss')
$evidenceRoot = Join-Path $ProjectRoot 'Docs\BossCombatReview\Execution\Codex\BK_56_60'
$evidence = Join-Path $evidenceRoot ('Run_' + $stamp)
if (!(Test-Path -LiteralPath $uproject -PathType Leaf) -or !(Test-Path -LiteralPath $buildTool -PathType Leaf) -or !(Test-Path -LiteralPath $editor -PathType Leaf) -or !(Test-Path -LiteralPath $editorCmd -PathType Leaf)) { throw 'ABORT: project or Unreal 5.5 editor/build executable missing.' }
foreach ($path in @($driver,$author,$phaseAuthor)) { if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw "ABORT: required script missing: $path" } }
if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: an UnrealEditor process is active; close it before C-1155 acquisition.' }
foreach ($lock in $locks) { if (Test-Path -LiteralPath $lock) { throw "ABORT: C-1155 lock already exists: $lock" } }
if (Test-Path -LiteralPath $evidence) { throw "ABORT: evidence path already exists: $evidence" }
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$token = [guid]::NewGuid().ToString('N')
$record = [ordered]@{ agent='Codex'; party='X'; task='BK-56..60 deferred framework selection'; command_id='BK_56_60.build-suite-author-pie'; owner_token=$token; pid=$PID; start_utc=[DateTime]::UtcNow.ToString('o'); policy='C-1155'; scope='Development build, DD27j-pinned full suite, new deferred encounter asset, bounded no-save deferred selected-route PIE' } | ConvertTo-Json -Compress
$created = [System.Collections.Generic.List[string]]::new()
$processes = [System.Collections.Generic.List[System.Diagnostics.Process]]::new()
$savedEnv = @{}
foreach ($name in @('FRAMEWORK_ENCOUNTER_WRITE','FRAMEWORK_ENCOUNTER_READBACK','BK56_AUTHOR_PHASE_WRITE','SEVAROG_LIVE_DEFERRED_SELECTION','SEVAROG_LIVE_AUTONOMOUS','SEVAROG_LIVE_AUTONOMOUS_SECONDS','SEVAROG_LIVE_PHASE2_PROBES','SEVAROG_LIVE_BOSS_HEALTH_FRACTION','SEVAROG_LIVE_SELF_TEST','SEVAROG_LIVE_SELF_TEST_CARDS')) { $savedEnv[$name] = [Environment]::GetEnvironmentVariable($name,'Process') }
$stage = 'lock acquisition'
$pieExit = $null

function Get-ContentAssetState {
    $content = Join-Path $ProjectRoot 'Content'
    $result = [System.Collections.Generic.List[string]]::new()
    if (Test-Path -LiteralPath $content) {
        foreach ($file in Get-ChildItem -LiteralPath $content -Recurse -File | Where-Object { $_.Extension -in @('.uasset','.umap','.uexp','.ubulk','.uptnl') }) {
            $relative = $file.FullName.Substring($ProjectRoot.Length + 1).Replace('\','/')
            $result.Add(('{0}|{1}|{2}' -f $relative,$file.Length,$file.LastWriteTimeUtc.Ticks))
        }
    }
    return @($result | Sort-Object)
}

function Invoke-EditorScript([string]$ScriptPath,[string]$ExtraArgs,[string]$LogPath,[string]$ExpectedMarker,[int]$TimeoutMinutes) {
    $fso = New-Object -ComObject Scripting.FileSystemObject
    $shortPath = $fso.GetFile($ScriptPath).ShortPath.ToLowerInvariant() -replace '\\','/'
    $exec = '-ExecCmds="py ' + $shortPath + ' ' + $ExtraArgs + '; Quit"'
    $proc = Start-Process -FilePath $editor -PassThru -ArgumentList @($uproject,$exec,'-nosound','-nosplash','-unattended',"-abslog=$LogPath") -WindowStyle Hidden
    $processes.Add($proc)
    $deadline = [DateTime]::UtcNow.AddMinutes($TimeoutMinutes)
    try {
        while ([DateTime]::UtcNow -lt $deadline -and !$proc.HasExited) {
            Start-Sleep -Seconds 2
            if (Test-Path -LiteralPath $LogPath) {
                $text = Get-Content -Raw -LiteralPath $LogPath -ErrorAction SilentlyContinue
                if ($text.Contains($ExpectedMarker)) { break }
                if ($text -match 'Fatal error|Assertion failed|Traceback \(most recent call last\)|LogPython: Error:|\[FrameworkEncounterAuthor\] REFUSED|\[SevarogLive\] ERROR') { break }
            }
        }
    } finally {
        if (!$proc.HasExited) { [void]$proc.CloseMainWindow(); Start-Sleep -Seconds 5 }
        if (!$proc.HasExited) { $proc.Kill(); $proc.WaitForExit() }
    }
    $text = if (Test-Path -LiteralPath $LogPath) { Get-Content -Raw -LiteralPath $LogPath } else { '' }
    if (!$text.Contains($ExpectedMarker)) { throw "Editor script did not produce required marker '$ExpectedMarker'; see $LogPath" }
    return $text
}

try {
    foreach ($lock in $locks) {
        $temp = $lock + '.' + $token + '.tmp'
        $stream = [System.IO.File]::Open($temp,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try { $bytes=[Text.Encoding]::UTF8.GetBytes($record+[Environment]::NewLine); $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
        [System.IO.File]::Move($temp,$lock)
        $created.Add($lock)
    }
    if (@(Get-Process UnrealEditor* -ErrorAction SilentlyContinue).Count) { throw 'ABORT: UnrealEditor started during C-1155 lock acquisition.' }
    Set-Location -LiteralPath $ProjectRoot
    $preAssets = Get-ContentAssetState
    Set-Content -LiteralPath (Join-Path $evidence 'content_assets_before.txt') -Value $preAssets

    $stage = 'focused offline contracts'
    $python = (Get-Command python -ErrorAction Stop).Source
    $ErrorActionPreference = 'Continue'
    & $python -m unittest -v Scripts.Tools.test_bk51_bk55_framework_deferred_selection_contract Scripts.Tools.test_bk56_60_deferred_production_tick_contract 2>&1 | Out-File -LiteralPath (Join-Path $evidence 'focused_contracts.log') -Encoding utf8
    $contractExit = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($contractExit -ne 0) { Get-Content (Join-Path $evidence 'focused_contracts.log') -Tail 80; throw 'Focused deferred-selection source contracts failed.' }
    & $python -m py_compile Scripts/Editor/pie_sevarog_framework_live.py Scripts/Editor/author_framework_encounter_definition.py 2>&1 | Out-File -LiteralPath (Join-Path $evidence 'py_compile.log') -Encoding utf8
    $compileExit = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($compileExit -ne 0) { Get-Content (Join-Path $evidence 'py_compile.log') -Tail 80; throw 'Editor Python compilation failed.' }

    $stage = 'Development build'
    $buildLog = Join-Path $evidence 'build.log'
    & $buildTool OneBossFightEditor Win64 Development "-Project=$uproject" -WaitMutex -NoHotReload *> $buildLog
    $buildExit = $LASTEXITCODE
    if ($buildExit -ne 0) { Get-Content $buildLog -Tail 120; throw "Development editor build failed: $buildExit" }

    $stage = 'DD27j-pinned native suite'
    $suiteLog = Join-Path $evidence 'suite.log'
    $suiteOut = Join-Path $evidence 'suite_stdout.log'
    & $editorCmd $uproject '-ExecCmds=Automation RunTests OneBossFight; Quit' "-DD27jManifestHash=$manifest" -unattended -nopause -nosplash -nosound -NullRHI "-abslog=$suiteLog" *> $suiteOut
    $suiteExit = $LASTEXITCODE
    $started = @(Select-String -LiteralPath $suiteLog -Pattern 'Test Started\. Name=' -ErrorAction SilentlyContinue)
    $passed = @(Select-String -LiteralPath $suiteLog -Pattern 'Test Completed\. Result=\{Success\}' -ErrorAction SilentlyContinue)
    $failed = @(Select-String -LiteralPath $suiteLog -Pattern 'Test Completed\. Result=\{(Fail|Error)\}' -ErrorAction SilentlyContinue)
    $complete = Select-String -LiteralPath $suiteLog -Pattern 'TEST COMPLETE\. EXIT CODE: 0' -ErrorAction SilentlyContinue | Select-Object -Last 1
    if ($suiteExit -ne 0 -or !$complete -or !$started.Count -or $started.Count -ne $passed.Count -or $failed.Count) { Get-Content $suiteLog -Tail 120; throw 'DD27j-pinned OneBossFight suite failed or incomplete.' }

    $stage = 'Sevarog Phase_1 prerequisite'
    $bossDraftFile = Join-Path $ProjectRoot 'Content\OneBossFight\Data\Sevarog\DA_Boss_Sevarog_Draft.uasset'
    if (!(Test-Path -LiteralPath $bossDraftFile)) { throw 'Sevarog draft boss asset is missing; refusing phase prerequisite write.' }
    Copy-Item -LiteralPath $bossDraftFile -Destination (Join-Path $evidence 'DA_Boss_Sevarog_Draft.before.uasset')
    $env:BK56_AUTHOR_PHASE_WRITE = '1'
    $phaseLog = Join-Path $evidence 'phase_prerequisite.log'
    $phaseText = Invoke-EditorScript $phaseAuthor '' $phaseLog '[BK56Phase]' 10
    if (!$phaseText.Contains('[BK56Phase] ADDED') -and !$phaseText.Contains('[BK56Phase] PRESENT')) { throw 'Sevarog Phase_1 prerequisite was neither added nor confirmed.' }
    Remove-Item Env:\BK56_AUTHOR_PHASE_WRITE -ErrorAction SilentlyContinue

    $stage = 'encounter author/readback'
    $assetFile = Join-Path $ProjectRoot 'Content\OneBossFight\Data\Sevarog\DA_Sevarog_Framework_Encounter.uasset'
    if (!(Test-Path -LiteralPath $assetFile)) {
        $env:FRAMEWORK_ENCOUNTER_WRITE = '1'
        $authorWriteLog = Join-Path $evidence 'author_write.log'
        $authorWriteText = Invoke-EditorScript $author '--write' $authorWriteLog '[FrameworkEncounterAuthor] CREATED /Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter' 10
        if (!$authorWriteText.Contains('[FrameworkEncounterAuthor] CREATED /Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter')) { throw 'Asset creation marker missing after save.' }
    }
    Remove-Item Env:\FRAMEWORK_ENCOUNTER_WRITE -ErrorAction SilentlyContinue
    $env:FRAMEWORK_ENCOUNTER_READBACK = '1'
    $authorLog = Join-Path $evidence 'author_readback.log'
    $authorText = Invoke-EditorScript $author '--readback' $authorLog '[FrameworkEncounterAuthor] READBACK' 10

    $env:SEVAROG_LIVE_DEFERRED_SELECTION = '1'
    $env:SEVAROG_LIVE_AUTONOMOUS_SECONDS = '45'
    foreach ($name in @('SEVAROG_LIVE_AUTONOMOUS','SEVAROG_LIVE_PHASE2_PROBES','SEVAROG_LIVE_BOSS_HEALTH_FRACTION','SEVAROG_LIVE_SELF_TEST','SEVAROG_LIVE_SELF_TEST_CARDS')) { Remove-Item ("Env:\" + $name) -ErrorAction SilentlyContinue }
    $pieLog = Join-Path $evidence 'deferred_pie.log'
    $fso = New-Object -ComObject Scripting.FileSystemObject
    $driverShort = $fso.GetFile($driver).ShortPath.ToLowerInvariant() -replace '\\','/'
    $pieExec = '-ExecCmds="py ' + $driverShort + '"'
    $stage = 'deferred PIE'
    $pieProc = Start-Process -FilePath $editor -PassThru -ArgumentList @($uproject,$pieExec,'-nosound','-nosplash','-unattended',"-abslog=$pieLog") -WindowStyle Hidden
    $processes.Add($pieProc)
    $pieDeadline = [DateTime]::UtcNow.AddMinutes(12)
    try {
        while ([DateTime]::UtcNow -lt $pieDeadline -and !$pieProc.HasExited) {
            Start-Sleep -Seconds 2
            if (!(Test-Path -LiteralPath $pieLog)) { continue }
            $tail = Get-Content -Raw -LiteralPath $pieLog -ErrorAction SilentlyContinue
            if ($tail.Contains('[SevarogLive] DEFERRED_TICK_RESULT')) { break }
            if ($tail -match 'Fatal error|Assertion failed|\[SevarogLive\] ERROR|\[FrameworkEncounterAuthor\] REFUSED') { break }
        }
    } finally {
        if (!$pieProc.HasExited) { [void]$pieProc.CloseMainWindow(); Start-Sleep -Seconds 5 }
        if (!$pieProc.HasExited) { $pieProc.Kill(); $pieProc.WaitForExit() }
        if ($pieProc.HasExited) {
            $pieExit = $pieProc.ExitCode
            ('PIE_EXIT=' + $pieExit) | Set-Content -LiteralPath (Join-Path $evidence 'pie_exit.txt')
        }
    }
    $pieText = if (Test-Path -LiteralPath $pieLog) { Get-Content -Raw -LiteralPath $pieLog } else { '' }
    $packReady = $pieText.IndexOf('PACK_STYLE_READY')
    $spawn = $pieText.IndexOf('SPAWN PASS')
    $routeInit = $pieText.IndexOf('selected_route_initialized route=data')
    $activation = $pieText.IndexOf('deferred_selected route=data')
    $decision = $pieText.IndexOf('[CARD_DECISION]')
    $monitor = $pieText.IndexOf('DEFERRED_TICK_MONITOR')
    $result = $pieText.IndexOf('DEFERRED_TICK_RESULT')
    $healthBaseline = $pieText -match 'selected_route_initialized route=data profile=\S+ generation=\d+ targetHealthAfterPackStyle=[0-9.]+ testStartApis=0'
    $ordered = $packReady -ge 0 -and $routeInit -gt $packReady -and $activation -gt $routeInit -and $spawn -gt $activation -and $decision -gt $activation -and $decision -lt $result -and $monitor -gt $spawn -and $result -gt $monitor
    $apiCallsAbsent = $pieText -notmatch 'autonomous_test_selection|COMBO_START|\[SevarogLive\] CARD accepted move='
    if (!$ordered -or !$healthBaseline -or !$apiCallsAbsent -or $pieText -notmatch 'saves=0') { Get-Content $pieLog -Tail 160; throw 'Deferred production Tick PIE markers/order/health-baseline/no-test-start/no-save check failed.' }

    $stage = 'Content asset delta verification'
    $postAssets = Get-ContentAssetState
    Set-Content -LiteralPath (Join-Path $evidence 'content_assets_after.txt') -Value $postAssets
    $beforeSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($line in $preAssets) { [void]$beforeSet.Add($line) }
    $afterSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($line in $postAssets) { [void]$afterSet.Add($line) }
    $assetDelta = @($postAssets | Where-Object { !$beforeSet.Contains($_) }) + @($preAssets | Where-Object { !$afterSet.Contains($_) })
    $unexpected = @($assetDelta | Where-Object { $_ -notmatch '(^|/)(DA_Sevarog_Framework_Encounter|DA_Boss_Sevarog_Draft)\.(uasset|uexp|ubulk|uptnl)\|' })
    Set-Content -LiteralPath (Join-Path $evidence 'content_asset_delta.txt') -Value $assetDelta
    if ($unexpected.Count) { throw ('Unexpected Content asset delta: ' + ($unexpected -join '; ')) }
    if (!$assetDelta.Count) { throw 'Expected authored encounter asset is absent from Content asset delta.' }

    $stage = 'success status'
    $status = "BUILD_EXIT=$buildExit`nSUITE_EXIT=$suiteExit`nSUITE_STARTED=$($started.Count)`nSUITE_PASSED=$($passed.Count)`nSUITE_FAILED=$($failed.Count)`nDD27J=$manifest`nFOCUSED_CONTRACTS_EXIT=$contractExit`nPY_COMPILE_EXIT=$compileExit`nPIE_EXIT=$pieExit`nPHASE_PREREQUISITE=PASS`nASSET_READBACK=PASS`nPIE_ORDER_VALID=$ordered`nHEALTH_BASELINE_AFTER_PACK_STYLE_READY=$healthBaseline`nTEST_START_APIS_ABSENT=$apiCallsAbsent`nCONTENT_DELTA_ONLY_EXPECTED_ASSETS=$($unexpected.Count -eq 0)`nDEFERRED_PIE=PASS`nNO_MAP_OR_OTHER_CONTENT_SAVES=1"
    Set-Content -LiteralPath (Join-Path $evidence 'status.txt') -Value $status
    $status
}
catch {
    $failure = $_
    $message = "STAGE=$stage`nERROR=$($failure.Exception.Message)`nPIE_EXIT=$pieExit"
    try { Set-Content -LiteralPath (Join-Path $evidence 'failure_status.txt') -Value $message }
    catch { Write-Warning ('Could not write failure_status.txt: ' + $_.Exception.Message) }
    throw $failure
}
finally {
    foreach ($name in $savedEnv.Keys) { [Environment]::SetEnvironmentVariable($name,$savedEnv[$name],'Process') }
    foreach ($proc in $processes) { if (!$proc.HasExited) { $proc.Kill(); $proc.WaitForExit() } }
    foreach ($lock in $created) {
        if (Test-Path -LiteralPath $lock) {
            try { $current=Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json; if ($current.owner_token -eq $token) { Remove-Item -LiteralPath $lock -Force } }
            catch { Write-Warning ('Could not verify lock ownership; retained lock: ' + $lock) }
        }
    }
    ('LOCKS_RELEASED=' + $created.Count) | Set-Content -LiteralPath (Join-Path $evidence 'lock_result.txt')
}
