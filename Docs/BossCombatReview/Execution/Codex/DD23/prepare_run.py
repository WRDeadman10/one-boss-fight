"""Prepare C275 run helpers; no engine operation."""
from pathlib import Path
here=Path(__file__).resolve().parent
prior=here.parent/'DD22'
run=here/'run_2026-10-29'
run.mkdir(exist_ok=False)
s=(prior/'capture_safety.py').read_text(encoding='utf-8').replace('C268','C275').replace('DD22_Binding','DD23_Binding').replace('len(actual)==203','len(actual)==206').replace('Fresh203','Fresh206').replace('Codex/DD20/run_','Codex/DD22/run_')
s=s.replace('r["head"]=subprocess.run', '''c=verify_receipt(here.parent/"DD22/live_pins_sha256.txt",root,root)
for row in c["checks"]:
    key=Path(row["path"]).as_posix()
    if row["status"]=="mismatch" and key in {"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"} and row["actual_sha256"]==expected[key]:
        row["status"]="C275_reviewed_DD23_Binding_supersedes_DD22"
c["all_verified"]=all(row["status"] in {"verified","C275_reviewed_DD23_Binding_supersedes_DD22"} for row in c["checks"])
r["pins"]["DD22_five"]=c
r["head"]=subprocess.run''')
(here/'capture_safety.py').write_text(s,encoding='utf-8')
s=(prior/'finish_capture.py').read_text(encoding='utf-8').replace('==203','==206').replace('Source203','Source206').replace('DD22_Binding','DD23_Binding').replace('build_dd21_dd22','build_dd23').replace('full_dd21_dd22','full_dd23').replace('Codex/DD20/run_','Codex/DD22/run_').replace('automation_full_dd20','automation_full_dd21_dd22').replace('warning_delta_vs_DD20','warning_delta_vs_DD22')
s=s.replace('["focused_shockwave","focused_healpunish","full_dd23"]','["focused_look","full_dd23"]').replace('r["focused_shockwave"]["pass"] and r["focused_healpunish"]["pass"]','r["focused_look"]["pass"]')
(here/'finish_capture.py').write_text(s,encoding='utf-8')
s=(here.parent/'DD20/check_run.py').read_text(encoding='utf-8').replace('LowSweep','Look').replace('focused_lowsweep','focused_look').replace('Codex/DD19/run_','Codex/DD22/run_').replace('automation_full_dd19','automation_full_dd21_dd22').replace('n=141','n=159')
s=s.replace('r["membership_exact"]=not r["missing_prior"] and set(r["new_paths"])==expected','r["membership_exact"]=not r["missing_prior"] and set(r["new_paths"])==expected\n    r["cook_coverage_success"]=any("CookCoverage" in line and "Result={Success}" in line for line in t.splitlines())')
s=s.replace('and "GIsCriticalError=0" in t','and r.get("cook_coverage_success",True) and "GIsCriticalError=0" in t')
(here/'check_run.py').write_text(s,encoding='utf-8')
for n in ['run_build.ps1','run_focused.ps1','build_dd21_dd22.cmd']:
    s=(prior/'run_2026-10-29'/n).read_text(encoding='utf-8').replace('Codex\\DD22\\','Codex\\DD23\\').replace('build_dd21_dd22','build_dd23')
    (run/n.replace('build_dd21_dd22','build_dd23')).write_text(s,encoding='utf-8')
print('C275 run files prepared; no engine execution.')
