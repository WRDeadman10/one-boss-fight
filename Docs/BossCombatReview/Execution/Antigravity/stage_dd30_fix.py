import os
import hashlib
import difflib

base_dir = r'Docs/BossCombatReview/Execution/Antigravity/DD30ChronologyFix'
preimage_dir = os.path.join(base_dir, 'preimages')
staged_dir = os.path.join(base_dir, 'staged')
os.makedirs(preimage_dir, exist_ok=True)
os.makedirs(staged_dir, exist_ok=True)

targets = [
    ('Source/OneBossFight/Player/RPGBossEncounter.cpp', 'RPGBossEncounter.cpp', 'Player/RPGBossEncounter.h'),
    ('Source/OneBossFight/Player/RPGDodgeTiming.cpp', 'RPGDodgeTiming.cpp', 'Player/RPGDodgeTiming.h'),
    ('Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp', 'RPGPlayerMovesSubsystem.cpp', 'Player/RPGPlayerMovesSubsystem.h'),
]

preimage_hashes = {}
staged_hashes = {}
diff_outputs = {}

for src_path, fname, own_hdr in targets:
    # 1. Read preimage exactly
    with open(src_path, 'rb') as f:
        preimage_bytes = f.read()
    
    assert b'\r\n' in preimage_bytes
    assert preimage_bytes.count(b'\r\n') == preimage_bytes.count(b'\n')
    
    preimage_path = os.path.join(preimage_dir, fname)
    with open(preimage_path, 'wb') as f:
        f.write(preimage_bytes)
        
    preimage_sha = hashlib.sha256(preimage_bytes).hexdigest()
    preimage_hashes[fname] = (preimage_sha, len(preimage_bytes))
    
    # 2. Generate staged
    lines = preimage_bytes.decode('utf-8').split('\r\n')
    # Verify line 2 and 3
    # line indices 0-based: 0 is copyright, 1 is empty, 2 is chronology include, 3 is own header include
    assert lines[0] == '// Copyright One Boss Fight. All Rights Reserved.'
    assert lines[1] == ''
    assert lines[2] == '#include "Player/RPGStartupChronology.h"'
    assert lines[3] == f'#include "{own_hdr}"'
    
    # Move line 2 after line 3
    new_lines = list(lines)
    new_lines[2] = f'#include "{own_hdr}"'
    new_lines[3] = '#include "Player/RPGStartupChronology.h"'
    
    staged_bytes = '\r\n'.join(new_lines).encode('utf-8')
    assert staged_bytes.count(b'\r\n') == staged_bytes.count(b'\n')
    assert len(staged_bytes) == len(preimage_bytes) # length should be identical since strings swapped!
    
    staged_path = os.path.join(staged_dir, fname)
    with open(staged_path, 'wb') as f:
        f.write(staged_bytes)
        
    staged_sha = hashlib.sha256(staged_bytes).hexdigest()
    staged_hashes[fname] = (staged_sha, len(staged_bytes))
    
    # 3. Compute unified diff
    pre_text = preimage_bytes.decode('utf-8').splitlines(keepends=True)
    stg_text = staged_bytes.decode('utf-8').splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        pre_text,
        stg_text,
        fromfile=f'a/Source/OneBossFight/Player/{fname}',
        tofile=f'b/Source/OneBossFight/Player/{fname}'
    ))
    diff_outputs[fname] = ''.join(diff)

print('=== PREIMAGES ===')
for k, (sha, sz) in preimage_hashes.items():
    print(f'{k}: {sha} ({sz} bytes)')

print('\n=== STAGED ===')
for k, (sha, sz) in staged_hashes.items():
    print(f'{k}: {sha} ({sz} bytes)')

print('\n=== DIFFS ===')
for k, d in diff_outputs.items():
    print(f'--- DIFF FOR {k} ---')
    print(d)

# 4. Scripted verification
print('\n=== VERIFICATION (Own Header First Include) ===')
for src_path, fname, own_hdr in targets:
    staged_path = os.path.join(staged_dir, fname)
    with open(staged_path, 'r', encoding='utf-8') as f:
        stg_lines = f.readlines()
    
    # Find first include after line 0 (copyright)
    first_inc = None
    first_inc_idx = None
    for idx, l in enumerate(stg_lines):
        l_strip = l.strip()
        if l_strip.startswith('#include'):
            first_inc = l_strip
            first_inc_idx = idx + 1
            break
            
    expected_first = f'#include "{own_hdr}"'
    assert first_inc == expected_first, f'Mismatch in {fname}: expected {expected_first}, got {first_inc}'
    second_inc = stg_lines[first_inc_idx].strip()
    assert second_inc == '#include "Player/RPGStartupChronology.h"', f'Second include mismatch: {second_inc}'
    print(f'PASS: {fname} line {first_inc_idx} is {first_inc}, line {first_inc_idx+1} is {second_inc}')

# Write evidence_sha256.txt
evidence_path = os.path.join(base_dir, 'evidence_sha256.txt')
with open(evidence_path, 'w', encoding='utf-8', newline='\r\n') as f:
    for fname in sorted(preimage_hashes.keys()):
        f.write(f'{preimage_hashes[fname][0]}  preimages/{fname}\r\n')
    for fname in sorted(staged_hashes.keys()):
        f.write(f'{staged_hashes[fname][0]}  staged/{fname}\r\n')
print(f'\nWrote {evidence_path}')
