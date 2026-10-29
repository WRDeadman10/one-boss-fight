"""C291 exact scoped run helper setup. Does not launch engine or build."""
from pathlib import Path
here=Path(__file__).resolve().parent
prior=here.parent/'DD25'
run=here/'run_2026-10-29'
run.mkdir(exist_ok=False)
s=(prior/'capture_safety.py').read_text(encoding='utf-8').replace('C286','C291').replace('DD25_Binding','DD26_Binding').replace('Codex/DD24/run_2026-10-29/final_binary_sha256.txt','Codex/DD25/run_2026-10-29/final_binary_sha256.txt')
s=s.replace('here/"native_pins_sha256.txt"','here.parent/"DD25/native_pins_sha256.txt"')
# Historical source pins may name any C291-reviewed changed file; only the exact
# accepted post-manifest bytes may supersede them. Everything else remains frozen.
oldset='{"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"}'
newset='({"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"} | set(json.loads((here/"scope_files.json").read_text(encoding="utf-8"))))'
s=s.replace(oldset,newset)
s=s.replace('r["head"]=subprocess.run', '''for package, receipt_name in [("DD19","live_pins_sha256.txt"),("DD20","live_pins_sha256.txt"),("DD25","live_pins_sha256.txt")]:
    c=verify_receipt(here.parent/package/receipt_name,root,root)
    for row in c["checks"]:
        key=Path(row["path"]).as_posix()
        if row["status"]=="mismatch" and key in {"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"} and row["actual_sha256"]==expected[key]:
            row["status"]="C291_frozen_DD25_Binding_supersedes_historical"
    c["all_verified"]=all(row["status"] in {"verified","C291_frozen_DD25_Binding_supersedes_historical"} for row in c["checks"])
    r["pins"][package+"_five"]=c
r["head"]=subprocess.run''')
(here/'capture_safety.py').write_text(s,encoding='utf-8')
for name in ['run_build.ps1','run_focused.ps1','build_dd25.cmd']:
    s=(prior/'run_2026-10-29'/name).read_text(encoding='utf-8').replace('DD25\\run_2026-10-29','DD26\\run_2026-10-29').replace('build_dd25','build_dd26')
    (run/name.replace('build_dd25','build_dd26')).write_text(s,encoding='utf-8')
print('C291 run commands prepared; no engine execution.')
