"""Capture post-run files and warning delta without running Unreal."""
from pathlib import Path
from collections import Counter
import sys,json,re,subprocess,hashlib
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/"EvidenceTools"))
from verify_bundle import digest,parse_receipt,verify_receipt,parse_job_record
run=here/"run_2026-10-29"
actual={p.relative_to(root).as_posix():digest(p) for p in (root/"Source").rglob("*") if p.is_file()}
initial={r["relative_path"]:r["expected_sha256"] for r in parse_receipt((run/"pre_source_manifest_sha256.txt").read_text(encoding="utf-8-sig"))}
(run/"final_source_manifest_sha256.txt").write_text("".join(f"{v} *{k}\n" for k,v in sorted(actual.items())),encoding="utf-8")
binary={n:digest(root/n) for n in ["Binaries/Win64/UnrealEditor-OneBossFight.dll","Binaries/Win64/OneBossFight.exe"]}
(run/"final_binary_sha256.txt").write_text("".join(f"{v} *{k}\n" for k,v in binary.items()),encoding="utf-8")
r={"source_unchanged":actual==initial,"source_count":len(actual),"binary":binary}
prebin={x["relative_path"]:x["expected_sha256"] for x in parse_receipt((run/"pre_binary_sha256.txt").read_text(encoding="utf-8-sig"))}
r["exe_unchanged"]=binary["Binaries/Win64/OneBossFight.exe"]==prebin["Binaries/Win64/OneBossFight.exe"]
dd18=root/"Docs/BossCombatReview/Execution/Claude/DD18"
r["pin_checks"]={}
for name in ["pre_pins.txt","dependency_pins_after_c245_followup_sha256.txt","candidate_assets_sha256.txt","default_catalog_assets_sha256.txt"]:
    c=verify_receipt(dd18/name,root,root)
    for row in c["checks"]:
        key=Path(row["path"]).as_posix()
        if row["status"]=="mismatch" and key in {"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"} and row["actual_sha256"]==initial[key]:
            row["status"]="reviewed_DD19_Binding_replacement"
    c["all_verified"]=all(x["status"] in {"verified","reviewed_DD19_Binding_replacement"} for x in c["checks"])
    r["pin_checks"][name]=c
r["head"]=subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
r["dirty"]=subprocess.run(["git","status","--porcelain","--","Source","Config","Content"],cwd=root,capture_output=True,text=True,check=True).stdout
r["head_unchanged"]=r["head"]==json.loads((run/"pre_safety.json").read_text(encoding="utf-8"))["head"]
r["build_job"]=parse_job_record(run/"build_dd19_job_record.txt",root)
build=(run/"build_dd19.log").read_text(encoding="utf-8")
r["build_sha256"]=digest(run/"build_dd19.log")
r["uht_lines"]=[x for x in build.splitlines() if "UnrealHeaderTool" in x or "Reflection code generated" in x]
r["build_warnings"]=[x for x in build.splitlines() if re.search(r"^\s*Warning:|\bwarning C\d+",x,re.I)]
r["build_errors"]=[x for x in build.splitlines() if re.search(r"\berror(?: C\d+| LNK\d+|:)",x,re.I)]
def warnings(p):
    lines=[re.sub(r"^\[[^]]*\]\[\s*\d+\]","",x) for x in p.read_text(encoding="utf-8").splitlines() if ": Warning:" in x]
    return Counter(re.sub(r"(?i)(sponsor(?:process)?(?:id|pid)?[ =:]+)\d+",r"\1<PID>",re.sub(r"(?i)(epoch=)[a-f0-9]{32}\b",r"\1<EPOCH>",x)) for x in lines)
a=warnings(run/"automation_full_dd19.log")
b=warnings(dd18/"run_2026-10-28/automation_full_dd18.log")
r["warning_delta_vs_DD18"]={"added":dict(a-b),"removed":dict(b-a)}
for tag in ["focused_bleed","full_dd19"]:
    r[tag]=json.loads((run/f"{tag}_gate.json").read_text(encoding="utf-8"))
(run/"final_verification.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
assert r["source_unchanged"] and r["source_count"]==194 and r["exe_unchanged"] and r["head_unchanged"]
assert all(c["all_verified"] for c in r["pin_checks"].values())
assert r["build_job"]["exit_code"]==0 and not r["build_errors"] and r["focused_bleed"]["pass"] and r["full_dd19"]["pass"]
print("Source194 unchanged; final pins/assets/HEAD verified; EXE unchanged.")
print("binaries",binary)
print("build",r["build_job"],r["build_sha256"],"warnings",len(r["build_warnings"]),"UHT",r["uht_lines"])
print("warnings",r["warning_delta_vs_DD18"])
print("full log",r["full_dd19"]["sha256"],"warnings",r["full_dd19"]["warning_severity_lines"])
print("File/evidence verification completed; lead acceptance pending.")
