"""Independent DD17/DD18 run review. File/log reads only, no Unreal execution."""
from pathlib import Path
from collections import Counter
import sys,json,re,hashlib
here=Path(__file__).resolve().parent
root=here.parents[3]
sys.path.insert(0,str(here/"EvidenceTools"))
from verify_bundle import verify_receipt,summarize_automation,parse_job_record,digest
package=root/"Docs/BossCombatReview/Execution/Claude/DD18"
run=package/"run_2026-10-28"
out=here/"C250Evidence"
out.mkdir(exist_ok=True)
r={"receipts":verify_receipt(run/"evidence_sha256.txt",run,root)}
for name in ["final_source_manifest_sha256.txt","final_binary_sha256.txt"]:
    r[name]=verify_receipt(run/name,root,root)
for name in ["pre_pins.txt","dependency_pins_after_c245_followup_sha256.txt","candidate_assets_sha256.txt","default_catalog_assets_sha256.txt"]:
    r[name]=verify_receipt(package/name,root,root)
r["source_pre_final_identical"]=(run/"pre_source_manifest_sha256.txt").read_bytes()==(run/"final_source_manifest_sha256.txt").read_bytes()
r["source_matches_reviewed"]=(package/"post_c246_correction_full_tree_manifest_sha256.txt").read_bytes()==(run/"final_source_manifest_sha256.txt").read_bytes()
groups=["world_input","world_preparation","preparation_registry"]
for group in groups+["full_dd18"]:
    stem="automation_"+("focused_"+group if group in groups else group)
    p=run/(stem+".log")
    s=summarize_automation(p,root)
    t=p.read_text(encoding="utf-8")
    s["job"]=parse_job_record(run/(stem+"_job_record.txt"),root)
    s["found"]=re.findall(r"Found (\d+) automation tests",t)
    s["critical_error"]=re.findall(r"GIsCriticalError[^\r\n]*",t)
    s["fatal_ensure_unsupported_lines"]=[line for line in t.splitlines() if re.search(r"\b(?:fatal|ensure|unsupported)\b",line,re.I)]
    r[group]=s
prior=root/"Docs/BossCombatReview/Execution/Claude/DD16/run_2026-10-28/automation_full_dd16.log"
r["prior"]=summarize_automation(prior,root)
full=set(r["full_dd18"]["paths"])
old=set(r["prior"]["paths"])
focused=set().union(*(set(r[g]["paths"]) for g in groups))
r["membership"]={"missing_prior":sorted(old-full),"new":sorted(full-old),"new_equals_focused":full-old==focused,"overlap_old_focused":sorted(old&focused)}
def warnings(p):
    lines=p.read_text(encoding="utf-8").splitlines()
    lines=[re.sub(r"^\[[^]]*\]\[\s*\d+\]","",x) for x in lines if re.search(r": Warning:",x)]
    # Accepted nondeterministic values ONLY; retain every warning body otherwise.
    return Counter(re.sub(r"(?i)(sponsor(?:process)?(?:id|pid)?[ =:]+)\d+",r"\1<PID>",re.sub(r"(?i)(epoch=)[0-9a-f]{32}\b",r"\1<EPOCH>",re.sub(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}","<GUID>",x))) for x in lines)
a,b=warnings(run/"automation_full_dd18.log"),warnings(prior)
r["warning_delta"]={"added":dict(a-b),"removed":dict(b-a)}
build=(run/"build_dd18.log").read_text(encoding="utf-8")
r["build"]={"sha256":digest(run/"build_dd18.log"),"job":parse_job_record(run/"build_dd18_job_record.txt",root),"warnings":[x for x in build.splitlines() if re.search("warning",x,re.I)],"uht_lines":[x for x in build.splitlines() if re.search(r"\b(?:UHT|UnrealHeaderTool)\b",x)]}
r["head_equal"]=(run/"pre_git_head.txt").read_bytes()==(run/"post_git_head.txt").read_bytes()
text=json.dumps(r,indent=2)
(out/"verification.json").write_text(text,encoding="utf-8")
(out/"verification.sha256").write_text(hashlib.sha256(text.encode()).hexdigest()+" *verification.json\n",encoding="utf-8")
print("receipts",r["receipts"]["entries"],r["receipts"]["all_verified"])
for group in groups+["full_dd18"]:
    s=r[group];print(group,s["completed"],s["unique"],s["job"],"warnings/errors",s["warning_severity_lines"],s["error_severity_lines"],"fatal/ensure/unsupported",len(s["fatal_ensure_unsupported_lines"]),s["sha256"])
print("source_pre_final_identical",r["source_pre_final_identical"],"source_matches_reviewed",r["source_matches_reviewed"])
print("membership",r["membership"])
print("warning_delta",r["warning_delta"])
print("build",r["build"])
assert all(x["all_verified"] for x in r.values() if isinstance(x,dict) and "all_verified" in x)
assert r["source_pre_final_identical"] and r["source_matches_reviewed"]
assert r["membership"]["new_equals_focused"] and not r["membership"]["missing_prior"] and not r["membership"]["overlap_old_focused"]
for group,count in zip(groups+["full_dd18"],[3,4,3,129]):
    s=r[group]
    assert s["unique"]==count and s["completed"]==count and not s["failures"] and not s["duplicate_completions"] and s["job"]["exit_code"]==0 and s["error_severity_lines"]==0 and not s["fatal_ensure_unsupported_lines"]
assert r["build"]["job"]["exit_code"]==0 and r["head_equal"]
print("Independent evidence checks completed exit0; acceptance scope remains a lead decision.")
