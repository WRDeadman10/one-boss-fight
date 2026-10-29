"""Prepare exact C286 run helpers. Does not execute Unreal."""
from pathlib import Path
here=Path(__file__).resolve().parent
prior=here.parent/'DD24'
run=here/'run_2026-10-29'
run.mkdir(exist_ok=False)
s=(prior/'capture_safety.py').read_text(encoding='utf-8').replace('C283','C286').replace('DD24_Binding','DD25_Binding').replace('len(actual)==209','len(actual)==212').replace('Fresh209','Fresh212').replace('Codex/DD23/attempt2_2026-10-29/final_binary_sha256.txt','Codex/DD24/run_2026-10-29/final_binary_sha256.txt')
s=s.replace('r["head"]=subprocess.run', '''c=verify_receipt(here.parent/"DD24/live_pins_sha256.txt",root,root)
for row in c["checks"]:
    key=Path(row["path"]).as_posix()
    if row["status"]=="mismatch" and key in {"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"} and row["actual_sha256"]==expected[key]:
        row["status"]="C286_reviewed_DD25_Binding_supersedes_DD24"
c["all_verified"]=all(row["status"] in {"verified","C286_reviewed_DD25_Binding_supersedes_DD24"} for row in c["checks"])
r["pins"]["DD24_five"]=c
r["pins"]["native_Death"]=verify_receipt(here/"native_pins_sha256.txt",root,root)
r["head"]=subprocess.run''')
(here/'capture_safety.py').write_text(s,encoding='utf-8')
s=(prior/'check_run.py').read_text(encoding='utf-8').replace('CloseClipSwap','Death').replace('focused_closeclipswap','focused_death').replace('Codex/DD23/attempt2_2026-10-29/automation_full_dd23.log','Codex/DD24/run_2026-10-29/automation_full_dd24.log').replace('n=165','n=171')
(here/'check_run.py').write_text(s,encoding='utf-8')
s=(prior/'finish_capture.py').read_text(encoding='utf-8').replace('==209','==212').replace('Source209','Source212').replace('DD24_Binding','DD25_Binding').replace('build_dd24','build_dd25').replace('full_dd24','full_dd25').replace('focused_closeclipswap','focused_death').replace('Codex/DD23/attempt2_2026-10-29/automation_full_dd23.log','Codex/DD24/run_2026-10-29/automation_full_dd24.log').replace('warning_delta_vs_DD23_attempt2','warning_delta_vs_DD24')
(here/'finish_capture.py').write_text(s,encoding='utf-8')
for n in ['run_build.ps1','run_focused.ps1','build_dd24.cmd']:
    s=(prior/'run_2026-10-29'/n).read_text(encoding='utf-8').replace('DD24\\run_2026-10-29','DD25\\run_2026-10-29').replace('build_dd24','build_dd25')
    (run/n.replace('build_dd24','build_dd25')).write_text(s,encoding='utf-8')
print('C286 command files prepared; no engine execution.')
