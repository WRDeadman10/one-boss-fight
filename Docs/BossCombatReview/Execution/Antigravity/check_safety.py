import os, hashlib, subprocess, json
from pathlib import Path

ROOT = Path('.').resolve()
print('ROOT:', ROOT)

# 1. Process check
proc_cmd = "Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress"
proc_out = subprocess.check_output(['powershell', '-NoProfile', '-Command', proc_cmd], text=True).strip()
print('Running engine/compiler processes:', proc_out if proc_out else 'NONE')
assert not proc_out, f'Processes running: {proc_out}'

# 2. Lock check
lock_path = ROOT / 'ENGINE_LOCK.json'
lock_path_exec = ROOT / 'Docs/BossCombatReview/Execution/ENGINE_LOCK.json'
print('ENGINE_LOCK exists:', lock_path.exists() or lock_path_exec.exists())
assert not lock_path.exists() and not lock_path_exec.exists()

# 3. Git HEAD check
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
print('HEAD:', head)
assert head == '605c2dd81d4092e8f84aa7608651ed19d566423a'

# 4. Source files count and preimage comparison
source_files = list(ROOT.glob('Source/**/*.*'))
source_files = [p for p in source_files if p.is_file()]
print('Live Source files count:', len(source_files))
assert len(source_files) == 219

# Verify preimages match live Source files
targets = [
    ('Source/OneBossFight/Player/RPGBossEncounter.cpp', 'Docs/BossCombatReview/Execution/Antigravity/DD30ChronologyFix/preimages/RPGBossEncounter.cpp'),
    ('Source/OneBossFight/Player/RPGDodgeTiming.cpp', 'Docs/BossCombatReview/Execution/Antigravity/DD30ChronologyFix/preimages/RPGDodgeTiming.cpp'),
    ('Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp', 'Docs/BossCombatReview/Execution/Antigravity/DD30ChronologyFix/preimages/RPGPlayerMovesSubsystem.cpp'),
]
for src, pre in targets:
    with open(src, 'rb') as f1, open(pre, 'rb') as f2:
        b1 = f1.read()
        b2 = f2.read()
    assert b1 == b2, f'Preimage mismatch for {src}'
    print(f'PASS: Live {src} is byte-identical to preimage')

# 5. Saved drafts & V2 pins check
saved_check = json.loads(Path('Docs/BossCombatReview/Execution/Codex/DD30Chronology/run_C346/saved_assets_unchanged.json').read_text(encoding='utf-8'))
for item in saved_check:
    asset_rel = item['path']
    expected_hash = item['sha256']
    with open(asset_rel, 'rb') as fp:
        cur_hash = hashlib.sha256(fp.read()).hexdigest()
    assert cur_hash == expected_hash, f'Asset hash mismatch for {asset_rel}'
    print(f'PASS: Saved draft pin {asset_rel} unchanged ({cur_hash[:16]}...)')

# 6. DLL baseline check
with open('Binaries/Win64/UnrealEditor-OneBossFight.dll', 'rb') as fp:
    dll_sha = hashlib.sha256(fp.read()).hexdigest()
assert dll_sha == '99baecdb4fb324e07f4ad488a34f76c798ec991c47f5cd73d05a66b0bdd5e875'
print(f'PASS: DLL baseline matches ({dll_sha[:16]}...)')

print('\nALL PRE-RUN SAFETY CHECKS PASSED PERFECTLY!')
