import os, hashlib
from pathlib import Path

RUN_DIR = Path('Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1')
SRC_BUILD_DIR = Path('Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyBuild2')

# 1. engine_lock.py
e_lock = '''from pathlib import Path
import json,datetime,sys,os
R=Path(__file__).resolve().parent
p=R.parents[2]/'ENGINE_LOCK.json'
if sys.argv[1]=='acquire':
 record={'agent':'Antigravity','party':'A','task':'C-352/DD30ChronologyRun1','command_id':'DD30Chronology.pie-run','start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy':'C-321'}
 try:
  with p.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\\n');f.flush();os.fsync(f.fileno())
 except FileExistsError:
  print('STOP existing lock '+p.read_text());raise SystemExit(2)
 (R/'engine_lock_record.json').write_text(json.dumps(record,indent=2)+'\\n',encoding='utf-8')
 print('C321 exclusive DD30ChronologyRun1 lock acquired')
elif sys.argv[1]=='release':
 v=json.loads(p.read_text());assert v['agent']=='Antigravity' and v['task']=='C-352/DD30ChronologyRun1' and v['command_id']=='DD30Chronology.pie-run'
 p.unlink();print('Own DD30ChronologyRun1 lock released after evidence freeze')
else:raise SystemExit(2)
'''
with open(RUN_DIR / 'engine_lock.py', 'w', encoding='utf-8', newline='\r\n') as fp:
    fp.write(e_lock)

# 2. capture_state.py (copy from DD30ChronologyBuild2)
with open(SRC_BUILD_DIR / 'capture_state.py', 'r', encoding='utf-8') as fp:
    c_state = fp.read()
with open(RUN_DIR / 'capture_state.py', 'w', encoding='utf-8', newline='\r\n') as fp:
    fp.write(c_state)

# Copy promoted_source_manifest_sha256.txt from DD30ChronologyBuild2 so capture_state pre/post has authoritative 219-file baseline!
with open(SRC_BUILD_DIR / 'promoted_source_manifest_sha256.txt', 'r', encoding='utf-8') as fp:
    manifest = fp.read()
with open(RUN_DIR / 'promoted_source_manifest_sha256.txt', 'w', encoding='utf-8', newline='\r\n') as fp:
    fp.write(manifest)

# 3. run_chronology.ps1
run_ps1 = '''$ErrorActionPreference = 'Stop'
$runDir = 'C:\\UnrealProject\\OneBossFight\\Docs\\BossCombatReview\\Execution\\Antigravity\\EngineRuns\\DD30ChronologyRun1'
$jobFile = Join-Path $runDir 'chronology_job.json'
if (Test-Path $jobFile) { throw 'Already executed chronology run; STOP' }

# Pre-state capture
python -I (Join-Path $runDir 'capture_state.py') pre
if ($LASTEXITCODE -ne 0) { throw 'Pre-state failed; STOP BEFORE RUN' }

$editor = 'C:\\Program Files\\Epic Games\\UE_5.5\\Engine\\Binaries\\Win64\\UnrealEditor.exe'
$uproject = 'C:\\UnrealProject\\OneBossFight\\OneBossFight.uproject'
$map = '/Game/OneBossFight/Levels/L_SevarogArena'
$driver = Join-Path $runDir 'dd30_chronology_pie.py'
$rawLog = Join-Path $runDir 'chronology_raw.log'

$launchArgs = @(
    $uproject,
    $map,
    '-nosound',
    '-nosplash',
    '-unattended',
    '-nullrhi',
    '-DD30Chronology',
    "-ExecutePythonScript=$driver",
    "-abslog=$rawLog"
)

$startUtc = (Get-Date).ToUniversalTime()
$s = Get-Date

Write-Host "Launching UnrealEditor (PID tracking active with 180s hard timeout)..."
$proc = Start-Process -FilePath $editor -ArgumentList $launchArgs -PassThru -NoNewWindow
$editorPid = $proc.Id
Write-Host "Launched UnrealEditor PID: $editorPid"

$timeoutSeconds = 180
$killedDueToTimeout = $false
$completed = $proc.WaitForExit($timeoutSeconds * 1000)

if (-not $completed) {
    Write-Warning "Hard timeout ($timeoutSeconds s) exceeded! Stopping ONLY process ID $editorPid..."
    Stop-Process -Id $editorPid -Force -ErrorAction SilentlyContinue
    $killedDueToTimeout = $true
}

$e = Get-Date
$exitCode = if ($killedDueToTimeout) { -999 } else { $proc.ExitCode }
$outcome = if ($killedDueToTimeout) { 'TIMEOUT_KILL' } elseif ($exitCode -eq 0) { 'SUCCESS' } else { 'EXIT_NONZERO' }

$jobRecord = @{
    release = 'C-352'
    task = 'DD30ChronologyRun1'
    editor_pid = $editorPid
    start = $s.ToString('o')
    end = $e.ToString('o')
    seconds = ($e - $s).TotalSeconds
    exit_code = $exitCode
    outcome = $outcome
    killed_due_to_timeout = $killedDueToTimeout
    nullrhi = $true
}

$jobRecord | ConvertTo-Json -Depth 4 | Set-Content $jobFile
Write-Host "Chronology job completed with outcome: $outcome (exit: $exitCode, seconds: $(($e - $s).TotalSeconds))"
exit $exitCode
'''

with open(RUN_DIR / 'run_chronology.ps1', 'w', encoding='utf-8', newline='\r\n') as fp:
    fp.write(run_ps1)

print('Assembled scripts in DD30ChronologyRun1 successfully.')
