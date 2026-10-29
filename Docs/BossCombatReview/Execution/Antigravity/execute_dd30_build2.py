import os, sys, shutil, hashlib, json, subprocess, time
from pathlib import Path

ROOT = Path('.').resolve()
RUN_DIR = ROOT / 'Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyBuild2'
FIX_DIR = ROOT / 'Docs/BossCombatReview/Execution/Antigravity/DD30ChronologyFix'

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

# Source count and preimages
source_files = [p for p in ROOT.glob('Source/**/*.*') if p.is_file()]
assert len(source_files) == 219, f'Source count: {len(source_files)}'

targets = [
    ('Source/OneBossFight/Player/RPGBossEncounter.cpp', 'RPGBossEncounter.cpp'),
    ('Source/OneBossFight/Player/RPGDodgeTiming.cpp', 'RPGDodgeTiming.cpp'),
    ('Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp', 'RPGPlayerMovesSubsystem.cpp'),
]
for src_rel, fname in targets:
    pre = FIX_DIR / 'preimages' / fname
    assert sha256_file(ROOT / src_rel) == sha256_file(pre), f'Preimage mismatch on {src_rel}'

# Saved drafts check
saved_check = json.loads(Path('Docs/BossCombatReview/Execution/Codex/DD30Chronology/run_C346/saved_assets_unchanged.json').read_text(encoding='utf-8'))
for item in saved_check:
    assert sha256_file(ROOT / item['path']) == item['sha256'], f"Asset modified: {item['path']}"

# DLL baseline check
dll_base = sha256_file(ROOT / 'Binaries/Win64/UnrealEditor-OneBossFight.dll')
assert dll_base == '99baecdb4fb324e07f4ad488a34f76c798ec991c47f5cd73d05a66b0bdd5e875', f'DLL base mismatch: {dll_base}'

print('Safety checks PASSED.')

print('\n=== STEP 2: ACQUIRE ENGINE LOCK ===')
subprocess.check_call(['python', '-B', str(RUN_DIR / 'engine_lock.py'), 'acquire'], cwd=ROOT)
assert lock_path.exists(), 'Lock file not created'
print('Acquired ENGINE_LOCK.json')

try:
    print('\n=== STEP 3: PROMOTE 3 STAGED CPP FILES ===')
    promotion_record = []
    for src_rel, fname in targets:
        src_path = ROOT / src_rel
        staged_path = FIX_DIR / 'staged' / fname
        before_hash = sha256_file(src_path)
        with open(staged_path, 'rb') as f_in, open(src_path, 'wb') as f_out:
            staged_bytes = f_in.read()
            f_out.write(staged_bytes)
        after_hash = sha256_file(src_path)
        assert after_hash == sha256_file(staged_path)
        promotion_record.append({
            'path': src_rel,
            'before': before_hash,
            'after': after_hash
        })
        print(f'Promoted {src_rel}: {before_hash[:12]} -> {after_hash[:12]}')
        
    (RUN_DIR / 'promotion.json').write_text(json.dumps(promotion_record, indent=2) + '\n', encoding='utf-8')

    print('\n=== STEP 4: GENERATE NEW PROMOTED SOURCE MANIFEST (219 FILES) ===')
    source_files = sorted([p for p in ROOT.glob('Source/**/*.*') if p.is_file()])
    assert len(source_files) == 219
    manifest_lines = []
    for p in source_files:
        rel = p.relative_to(ROOT).as_posix()
        manifest_lines.append(f'{sha256_file(p)} *{rel}')
    manifest_text = '\n'.join(manifest_lines) + '\n'
    (RUN_DIR / 'promoted_source_manifest_sha256.txt').write_text(manifest_text, encoding='utf-8')
    print(f'Wrote promoted_source_manifest_sha256.txt ({len(manifest_lines)} files)')

    print('\n=== STEP 5: RUN BUILD VIA RUN_BUILD.PS1 ===')
    ps1_cmd = f"powershell -NoProfile -ExecutionPolicy Bypass -File \"{RUN_DIR / 'run_build.ps1'}\""
    print(f'Executing: {ps1_cmd}')
    res = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(RUN_DIR / 'run_build.ps1')], cwd=ROOT, capture_output=True, text=True)
    print('run_build stdout:\n', res.stdout)
    if res.stderr:
        print('run_build stderr:\n', res.stderr)
    print(f'run_build exit code: {res.returncode}')

    print('\n=== STEP 6: CAPTURE POST STATE ===')
    subprocess.check_call(['python', '-B', str(RUN_DIR / 'capture_state.py'), 'post'], cwd=ROOT)

    print('\n=== STEP 7: PARSE BUILD_RAW.LOG ERRORS & WARNINGS ===')
    raw_log = (RUN_DIR / 'build_raw.log').read_text(encoding='utf-8', errors='ignore')
    err_lines = []
    warn_lines = []
    for line in raw_log.splitlines():
        if ': error' in line or ' error:' in line or line.startswith('Error:'):
            err_lines.append(line)
        if ': warning' in line or ' warning:' in line or line.startswith('Warning:'):
            warn_lines.append(line)

    (RUN_DIR / 'build_error_lines_verbatim.txt').write_text('\n'.join(err_lines) + ('\n' if err_lines else ''), encoding='utf-8')
    (RUN_DIR / 'build_warning_lines_verbatim.txt').write_text('\n'.join(warn_lines) + ('\n' if warn_lines else ''), encoding='utf-8')

    print(f'Errors found ({len(err_lines)}):')
    for l in err_lines:
        print('  ' + l)
    print(f'Warnings found ({len(warn_lines)}):')
    for l in warn_lines:
        print('  ' + l)

    # Save final binary hashes
    binaries = {}
    for name in ('Binaries/Win64/UnrealEditor-OneBossFight.dll', 'Binaries/Win64/UnrealEditor-OneBossFight.pdb', 'Binaries/Win64/OneBossFight.exe'):
        p = ROOT / name
        if p.exists():
            binaries[name] = sha256_file(p)
    (RUN_DIR / 'final_binary_sha256.json').write_text(json.dumps(binaries, indent=2) + '\n', encoding='utf-8')
    print('Final binaries:', binaries)

    # Saved assets unchanged check
    saved_unchanged = []
    for item in saved_check:
        saved_unchanged.append({
            'path': item['path'],
            'size': (ROOT / item['path']).stat().st_size,
            'sha256': sha256_file(ROOT / item['path'])
        })
    (RUN_DIR / 'saved_assets_unchanged.json').write_text(json.dumps(saved_unchanged, indent=2) + '\n', encoding='utf-8')

    print('\n=== STEP 8: FREEZE EVIDENCE (RECEIPT) ===')
    receipt_lines = []
    for p in sorted(RUN_DIR.glob('*')):
        if p.is_file() and p.name != 'receipt_sha256.txt':
            receipt_lines.append(f'{sha256_file(p)} *{p.name}')
    (RUN_DIR / 'receipt_sha256.txt').write_text('\n'.join(receipt_lines) + '\n', encoding='utf-8')
    print(f'Wrote receipt_sha256.txt ({len(receipt_lines)} items)')

finally:
    print('\n=== STEP 9: RELEASE ENGINE LOCK ===')
    subprocess.check_call(['python', '-B', str(RUN_DIR / 'engine_lock.py'), 'release'], cwd=ROOT)
    assert not lock_path.exists(), 'Lock file not removed'
    print('Released ENGINE_LOCK.json successfully.')

print('\nALL STEPS COMPLETED.')
