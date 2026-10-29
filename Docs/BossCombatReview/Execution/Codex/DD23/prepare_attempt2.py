"""C277 exact new run setup. Preserves all attempt1 artifacts."""
from pathlib import Path
here=Path(__file__).resolve().parent
run=here/'attempt2_2026-10-29'
run.mkdir(exist_ok=False)
for old,new in [('capture_safety.py','capture_safety_attempt2.py'),('check_run.py','check_run_attempt2.py'),('finish_capture.py','finish_capture_attempt2.py')]:
    s=(here/old).read_text(encoding='utf-8').replace('run=here/"run_2026-10-29"','run=here/"attempt2_2026-10-29"')
    if old=='capture_safety.py':
        s=s.replace('C275','C277').replace('here/"post_source_manifest_sha256.txt"','here/"Revision1/post_source_manifest_sha256.txt"').replace('here/"live_pins_sha256.txt"','here/"Revision1/live_pins_sha256.txt"').replace('Codex/DD22/run_2026-10-29/final_binary_sha256.txt','Codex/DD23/run_2026-10-29/final_binary_sha256.txt')
    (here/new).write_text(s,encoding='utf-8')
for name in ['run_build.ps1','run_focused.ps1','build_dd23.cmd']:
    s=(here/'run_2026-10-29'/name).read_text(encoding='utf-8').replace('DD23\\run_2026-10-29','DD23\\attempt2_2026-10-29')
    (run/name).write_text(s,encoding='utf-8')
print('Attempt2 setup only. Original run untouched.')
