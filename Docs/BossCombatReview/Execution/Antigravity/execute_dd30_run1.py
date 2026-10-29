import os, sys, shutil, hashlib, json, subprocess, time
from pathlib import Path

ROOT = Path('.').resolve()
RUN_DIR = ROOT / 'Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1'

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fp:
        for b in iter(lambda: fp.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

print('=== STEP 1: PRE-RUN SAFETY CHECK ===')
# Process check
proc_cmd = "Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress"
proc_out = subprocess.check_output(['powershell', '-NoProfile', '-Command', proc_cmd], text=True).strip()
assert not proc_out, f'Engine processes active: {proc_out}'

# Lock check
lock_path = ROOT / 'Docs/BossCombatReview/Execution/ENGINE_LOCK.json'
assert not lock_path.exists(), f'Existing lock: {lock_path}'
assert not (ROOT / 'ENGINE_LOCK.json').exists()

# Git HEAD
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert head == '605c2dd81d4092e8f84aa7608651ed19d566423a', f'HEAD mismatch: {head}'

# Source count
source_files = [p for p in ROOT.glob('Source/**/*.*') if p.is_file()]
assert len(source_files) == 219, f'Source count: {len(source_files)}'

# Saved drafts check
saved_check = json.loads(Path('Docs/BossCombatReview/Execution/Codex/DD30Chronology/run_C346/saved_assets_unchanged.json').read_text(encoding='utf-8'))
for item in saved_check:
    assert sha256_file(ROOT / item['path']) == item['sha256'], f"Asset modified: {item['path']}"

# DLL check (current newly built DLL from C-350)
dll_cur = sha256_file(ROOT / 'Binaries/Win64/UnrealEditor-OneBossFight.dll')
assert dll_cur == '332afd497b68c01b556be9fd73682574e97c31ed868f46a382ee0cb301bdaacf', f'DLL mismatch: {dll_cur}'

print('Safety checks PASSED.')

print('\n=== STEP 2: ACQUIRE ENGINE LOCK ===')
subprocess.check_call(['python', '-B', str(RUN_DIR / 'engine_lock.py'), 'acquire'], cwd=ROOT)
assert lock_path.exists(), 'Lock file not created'
print('Acquired ENGINE_LOCK.json')

try:
    print('\n=== STEP 3: RUN CHRONOLOGY PIE VIA RUN_CHRONOLOGY.PS1 ===')
    res = subprocess.run(
        ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(RUN_DIR / 'run_chronology.ps1')],
        cwd=ROOT,
        capture_output=True,
        text=True
    )
    print('run_chronology stdout:\n', res.stdout)
    if res.stderr:
        print('run_chronology stderr:\n', res.stderr)
    print(f'run_chronology exit code: {res.returncode}')

    print('\n=== STEP 4: CAPTURE POST STATE ===')
    subprocess.check_call(['python', '-B', str(RUN_DIR / 'capture_state.py'), 'post'], cwd=ROOT)

    print('\n=== STEP 5: PARSE LOGS & EXTRACT CHRONO LINES ===')
    raw_log_path = RUN_DIR / 'chronology_raw.log'
    if raw_log_path.exists():
        raw_log = raw_log_path.read_text(encoding='utf-8', errors='ignore')
        raw_log_sha = sha256_file(raw_log_path)
    else:
        raw_log = ''
        raw_log_sha = 'ABSENT'

    chrono_lines = []
    error_lines = []
    warn_lines = []
    for line in raw_log.splitlines():
        if '[DD30_CHRONO' in line:
            chrono_lines.append(line)
        if ': error' in line or ' error:' in line or line.startswith('Error:'):
            error_lines.append(line)
        if ': warning' in line or ' warning:' in line or line.startswith('Warning:'):
            warn_lines.append(line)

    (RUN_DIR / 'chrono_lines_verbatim.txt').write_text('\n'.join(chrono_lines) + ('\n' if chrono_lines else ''), encoding='utf-8')
    (RUN_DIR / 'run_error_lines_verbatim.txt').write_text('\n'.join(error_lines) + ('\n' if error_lines else ''), encoding='utf-8')
    (RUN_DIR / 'run_warning_lines_verbatim.txt').write_text('\n'.join(warn_lines) + ('\n' if warn_lines else ''), encoding='utf-8')

    print(f'Chrono lines found ({len(chrono_lines)}):')
    for l in chrono_lines:
        print('  ' + l)

    print(f'Error lines found ({len(error_lines)}):')
    for l in error_lines[:10]:
        print('  ' + l)

    print(f'Warning lines found ({len(warn_lines)}):')
    for l in warn_lines[:10]:
        print('  ' + l)

    # Saved assets unchanged check
    saved_unchanged = []
    for item in saved_check:
        saved_unchanged.append({
            'path': item['path'],
            'size': (ROOT / item['path']).stat().st_size,
            'sha256': sha256_file(ROOT / item['path'])
        })
    (RUN_DIR / 'saved_assets_unchanged.json').write_text(json.dumps(saved_unchanged, indent=2) + '\n', encoding='utf-8')

    print('\n=== STEP 6: FREEZE EVIDENCE (RECEIPT) ===')
    receipt_lines = []
    for p in sorted(RUN_DIR.glob('*')):
        if p.is_file() and p.name != 'receipt_sha256.txt':
            receipt_lines.append(f'{sha256_file(p)} *{p.name}')
    (RUN_DIR / 'receipt_sha256.txt').write_text('\n'.join(receipt_lines) + '\n', encoding='utf-8')
    print(f'Wrote receipt_sha256.txt ({len(receipt_lines)} items)')

finally:
    print('\n=== STEP 7: RELEASE ENGINE LOCK ===')
    subprocess.check_call(['python', '-B', str(RUN_DIR / 'engine_lock.py'), 'release'], cwd=ROOT)
    assert not lock_path.exists(), 'Lock file not removed'
    print('Released ENGINE_LOCK.json successfully.')

print('\nALL STEPS COMPLETED.')
