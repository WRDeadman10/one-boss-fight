"""Raw-log gate for a released run; never launches anything."""
from pathlib import Path
import sys,json,re
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/"EvidenceTools"))
from verify_bundle import summarize_automation,parse_job_record
tag=sys.argv[1]
run=here/"run_2026-10-29"
p=run/f"automation_{tag}.log"
r=summarize_automation(p,root)
r["job"]=parse_job_record(run/f"automation_{tag}_job_record.txt",root)
t=p.read_text(encoding="utf-8")
r["discovered"]=re.findall(r"LogAutomationCommandLine: Display: Found (\d+) automation tests based on '([^']+)'",t)
r["fatal_ensure_unsupported"]=[x for x in t.splitlines() if re.search(r"\b(?:fatal|ensure|unsupported)\b",x,re.I)]
expected={"OneBossFight.Binding.Look."+s for s in ["Assign","Validation","Isolation","Rejections","Compile","Authoring"]}
if tag=="focused_look":
    r["membership_exact"]=set(r["paths"])==expected
    n=6
else:
    prior=summarize_automation(root/"Docs/BossCombatReview/Execution/Codex/DD22/run_2026-10-29/automation_full_dd21_dd22.log",root)
    r["missing_prior"]=sorted(set(prior["paths"])-set(r["paths"]))
    r["new_paths"]=sorted(set(r["paths"])-set(prior["paths"]))
    r["membership_exact"]=not r["missing_prior"] and set(r["new_paths"])==expected
    r["cook_coverage_success"]=any("CookCoverage" in line and "Result={Success}" in line for line in t.splitlines())
    n=159
r["pass"]=(r["membership_exact"] and r["unique"]==n and r["completed"]==n
    and not r["failures"] and not r["duplicate_completions"] and r["job"]["exit_code"]==0
    and r["error_severity_lines"]==0 and not r["fatal_ensure_unsupported"]
    and r.get("cook_coverage_success",True) and "GIsCriticalError=0" in t and r["discovered"]==[(str(n),"OneBossFight.Binding.Look" if tag=="focused_look" else "OneBossFight")])
(run/f"{tag}_gate.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in r.items() if k not in {"paths"}},indent=2))
if not r["pass"]:raise SystemExit(1)
