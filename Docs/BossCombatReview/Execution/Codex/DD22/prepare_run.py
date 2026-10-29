"""Prepare the exact C268 run commands and read-only capture helpers."""
from pathlib import Path
here=Path(__file__).resolve().parent
prior=here.parent/'DD20'
run=here/'run_2026-10-29'
run.mkdir(exist_ok=False)
s=(prior/'capture_safety.py').read_text(encoding='utf-8').replace('C253/C254','C268').replace('len(actual)==197','len(actual)==203').replace('Fresh197','Fresh203').replace('DD20_Binding','DD22_Binding').replace('Codex/DD19/run_','Codex/DD20/run_')
s=s.replace('r["pins"]["five_live"]=verify_receipt(here/"live_pins_sha256.txt",root,root)', '''r["pins"]["five_live"]=verify_receipt(here/"live_pins_sha256.txt",root,root)
c=verify_receipt(here.parent/"DD21/live_pins_sha256.txt",root,root)
for row in c["checks"]:
    key=Path(row["path"]).as_posix()
    if row["status"]=="mismatch" and key in {"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"} and row["actual_sha256"]==expected[key]:
        row["status"]="C268_reviewed_DD22_Binding_supersedes_DD21"
c["all_verified"]=all(row["status"] in {"verified","C268_reviewed_DD22_Binding_supersedes_DD21"} for row in c["checks"])
r["pins"]["DD21_five"]=c''')
(here/'capture_safety.py').write_text(s,encoding='utf-8')
s=(prior/'finish_capture.py').read_text(encoding='utf-8').replace('==197','==203').replace('Source197','Source203').replace('build_dd20','build_dd21_dd22').replace('automation_full_dd20','automation_full_dd21_dd22').replace('Codex/DD19/run_','Codex/DD20/run_').replace('automation_full_dd19','automation_full_dd20').replace('warning_delta_vs_DD19','warning_delta_vs_DD20').replace('DD19_Binding','DD22_Binding')
s=s.replace('["focused_lowsweep","full_dd20"]','["focused_shockwave","focused_healpunish","full_dd21_dd22"]')
s=s.replace('r["focused_lowsweep"]["pass"] and r["full_dd20"]["pass"]','r["focused_shockwave"]["pass"] and r["focused_healpunish"]["pass"] and r["full_dd21_dd22"]["pass"]')
s=s.replace('r["full_dd20"]','r["full_dd21_dd22"]')
(here/'finish_capture.py').write_text(s,encoding='utf-8')
for name in ['run_build.ps1','run_focused.ps1','build_dd20.cmd']:
    s=(prior/'run_2026-10-29'/name).read_text(encoding='utf-8').replace('Codex\\DD20\\','Codex\\DD22\\').replace('build_dd20','build_dd21_dd22')
    (run/name.replace('build_dd20','build_dd21_dd22')).write_text(s,encoding='utf-8')
print('C268 run commands prepared. No engine execution.')
