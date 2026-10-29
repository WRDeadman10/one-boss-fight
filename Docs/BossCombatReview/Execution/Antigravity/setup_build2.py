import os, hashlib, difflib
from pathlib import Path

SRC_DIR = Path('Docs/BossCombatReview/Execution/Codex/DD30Chronology/run_C346')
DST_DIR = Path('Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyBuild2')
DST_DIR.mkdir(parents=True, exist_ok=True)

wrapper_files = ['run_build.ps1', 'build_once.cmd', 'capture_state.py', 'engine_lock.py']

orig_hashes = {}
for f in wrapper_files:
    with open(SRC_DIR / f, 'rb') as fp:
        raw = fp.read()
    orig_hashes[f] = hashlib.sha256(raw).hexdigest()

print('ORIGINAL HASHES (run_C346):')
for k, v in orig_hashes.items():
    print(f'  {k}: {v}')

# 1. build_once.cmd: change ONLY the run root path
# "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD30Chronology\run_C346\build_raw.log"
# -> "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\EngineRuns\DD30ChronologyBuild2\build_raw.log"
with open(SRC_DIR / 'build_once.cmd', 'r', encoding='utf-8') as fp:
    b_cmd = fp.read()
b_cmd_new = b_cmd.replace(
    r'Docs\BossCombatReview\Execution\Codex\DD30Chronology\run_C346',
    r'Docs\BossCombatReview\Execution\Antigravity\EngineRuns\DD30ChronologyBuild2'
)
assert b_cmd_new != b_cmd
with open(DST_DIR / 'build_once.cmd', 'w', encoding='utf-8', newline='\r\n') as fp:
    fp.write(b_cmd_new)

# 2. run_build.ps1: change ONLY run root path and release id (C-350)
with open(SRC_DIR / 'run_build.ps1', 'r', encoding='utf-8') as fp:
    r_ps1 = fp.read()
r_ps1_new = r_ps1.replace(
    r'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\DD30Chronology\run_C346',
    r'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\EngineRuns\DD30ChronologyBuild2'
).replace("release='C-346'", "release='C-350'")
assert r_ps1_new != r_ps1
with open(DST_DIR / 'run_build.ps1', 'w', encoding='utf-8', newline='\r\n') as fp:
    fp.write(r_ps1_new)

# 3. engine_lock.py: change ONLY run root path / release id / agent (Antigravity, C-350)
with open(SRC_DIR / 'engine_lock.py', 'r', encoding='utf-8') as fp:
    e_lock = fp.read()
e_lock_new = (e_lock
    .replace("'agent':'Codex'", "'agent':'Antigravity'")
    .replace("v['agent']=='Codex'", "v['agent']=='Antigravity'")
    .replace("'party':'X'", "'party':'A'")
    .replace("C-346/DD30Chronology", "C-350/DD30ChronologyBuild2")
)
assert e_lock_new != e_lock
with open(DST_DIR / 'engine_lock.py', 'w', encoding='utf-8', newline='\r\n') as fp:
    fp.write(e_lock_new)

# 4. capture_state.py:
# Note: delta = json.loads((OUT.parent.parent/'C331_HEAD_BASELINE_DELTA.json').read_text(encoding='utf-8'))
# In run_C346, OUT.parent.parent was Codex. For DD30ChronologyBuild2, OUT.parent.parent is Antigravity.
# We also copy C331_HEAD_BASELINE_DELTA.json into Antigravity/ so capture_state.py finds it with ZERO code changes!
# But wait, does capture_state.py need ANY changes?
# Let's inspect capture_state.py lines.
with open(SRC_DIR / 'capture_state.py', 'r', encoding='utf-8') as fp:
    c_state = fp.read()
# In capture_state.py: ROOT = Path(__file__).resolve().parents[6]. As verified, parents[6] is C:\UnrealProject\OneBossFight.
# All paths relative to ROOT or OUT work identically!
# So capture_state.py is 100% IDENTICAL!
with open(DST_DIR / 'capture_state.py', 'w', encoding='utf-8', newline='\r\n') as fp:
    fp.write(c_state)

# Copy C331_HEAD_BASELINE_DELTA.json to Antigravity/ so OUT.parent.parent/'C331_HEAD_BASELINE_DELTA.json' works!
import shutil
shutil.copy2('Docs/BossCombatReview/Execution/Codex/C331_HEAD_BASELINE_DELTA.json', 'Docs/BossCombatReview/Execution/Antigravity/C331_HEAD_BASELINE_DELTA.json')

# Record diffs
diffs = {}
for f in wrapper_files:
    t_orig = (SRC_DIR / f).read_text(encoding='utf-8').splitlines(keepends=True)
    t_new = (DST_DIR / f).read_text(encoding='utf-8').splitlines(keepends=True)
    d = list(difflib.unified_diff(t_orig, t_new, fromfile=f'a/{f}', tofile=f'b/{f}'))
    diffs[f] = ''.join(d)

print('\nDIFFS:')
for f in wrapper_files:
    print(f'=== {f} ===')
    print(diffs[f] if diffs[f] else '<IDENTICAL>')

# Write wrapper_diffs.txt
with open(DST_DIR / 'wrapper_diffs.txt', 'w', encoding='utf-8', newline='\r\n') as fp:
    for f in wrapper_files:
        fp.write(f'=== {f} ===\r\n')
        fp.write(diffs[f] + '\r\n\r\n')

print('\nSetup completed successfully.')
