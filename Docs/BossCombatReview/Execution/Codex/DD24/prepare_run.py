"""Prepare exact C283 verification commands; no engine execution."""
from pathlib import Path
here=Path(__file__).resolve().parent
prior=here.parent/'DD23'
run=here/'run_2026-10-29'
run.mkdir(exist_ok=False)
s=(prior/'capture_safety.py').read_text(encoding='utf-8').replace('C275','C283').replace('DD23_Binding','DD24_Binding').replace('len(actual)==206','len(actual)==209').replace('Fresh206','Fresh209').replace('Codex/DD22/run_2026-10-29/final_binary_sha256.txt','Codex/DD23/attempt2_2026-10-29/final_binary_sha256.txt')
s=s.replace('r["head"]=subprocess.run', '''c=verify_receipt(here.parent/"DD23/Revision1/live_pins_sha256.txt",root,root)
for row in c["checks"]:
    key=Path(row["path"]).as_posix()
    if row["status"]=="mismatch" and key in {"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"} and row["actual_sha256"]==expected[key]:
        row["status"]="C283_reviewed_DD24_Binding_supersedes_DD23"
c["all_verified"]=all(row["status"] in {"verified","C283_reviewed_DD24_Binding_supersedes_DD23"} for row in c["checks"])
r["pins"]["DD23_five"]=c
r["head"]=subprocess.run''')
(here/'capture_safety.py').write_text(s,encoding='utf-8')
s=(prior/'check_run.py').read_text(encoding='utf-8').replace('Look','CloseClipSwap').replace('focused_look','focused_closeclipswap').replace('Codex/DD22/run_2026-10-29/automation_full_dd21_dd22.log','Codex/DD23/attempt2_2026-10-29/automation_full_dd23.log').replace('n=159','n=165')
# Count assertions/critical markers as failures even without the word fatal.
s=s.replace('fatal|ensure|unsupported','fatal|ensure|unsupported|assertion|critical error')
(here/'check_run.py').write_text(s,encoding='utf-8')
s=(prior/'finish_capture.py').read_text(encoding='utf-8').replace('==206','==209').replace('Source206','Source209').replace('DD23_Binding','DD24_Binding').replace('build_dd23','build_dd24').replace('full_dd23','full_dd24').replace('focused_look','focused_closeclipswap').replace('Codex/DD22/run_2026-10-29/automation_full_dd21_dd22.log','Codex/DD23/attempt2_2026-10-29/automation_full_dd23.log').replace('warning_delta_vs_DD22','warning_delta_vs_DD23_attempt2')
(here/'finish_capture.py').write_text(s,encoding='utf-8')
for n in ['run_build.ps1','run_focused.ps1','build_dd23.cmd']:
    s=(prior/'attempt2_2026-10-29'/n).read_text(encoding='utf-8').replace('DD23\\attempt2_2026-10-29','DD24\\run_2026-10-29').replace('build_dd23','build_dd24')
    (run/n.replace('build_dd23','build_dd24')).write_text(s,encoding='utf-8')
print('C283 commands prepared; no engine execution.')
