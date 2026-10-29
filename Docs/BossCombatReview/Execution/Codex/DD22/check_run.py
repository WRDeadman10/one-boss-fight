"""C268 raw automation gate. Reads evidence only; no engine execution."""
from pathlib import Path
import sys,json,re
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import summarize_automation,parse_job_record
tag=sys.argv[1]
run=here/'run_2026-10-29'
p=run/f'automation_{tag}.log'
r=summarize_automation(p,root)
r['job']=parse_job_record(run/f'automation_{tag}_job_record.txt',root)
t=p.read_text(encoding='utf-8')
r['discovered']=re.findall(r"LogAutomationCommandLine: Display: Found (\d+) automation tests based on '([^']+)'",t)
r['fatal_ensure_unsupported']=[s for s in t.splitlines() if re.search(r'\b(?:fatal|ensure|unsupported)\b',s,re.I)]
suffixes=['Assign','Validation','Isolation','Rejections','Compile','Authoring']
shock={'OneBossFight.Binding.Shockwave.'+s for s in suffixes}
heal={'OneBossFight.Binding.HealPunish.'+s for s in suffixes}
if tag in {'focused_shockwave','focused_healpunish'}:
    expected=shock if tag=='focused_shockwave' else heal
    n=6
    filter='OneBossFight.Binding.'+('Shockwave' if tag=='focused_shockwave' else 'HealPunish')
    r['membership_exact']=set(r['paths'])==expected
else:
    assert tag=='full_dd21_dd22'
    prior=summarize_automation(here.parent/'DD20/run_2026-10-29/automation_full_dd20.log',root)
    r['missing_prior']=sorted(set(prior['paths'])-set(r['paths']))
    r['new_paths']=sorted(set(r['paths'])-set(prior['paths']))
    r['membership_exact']=not r['missing_prior'] and set(r['new_paths'])==shock|heal
    r['cook_coverage_success']=any('CookCoverage' in s and 'Result={Success}' in s for s in t.splitlines())
    n=153
    filter='OneBossFight'
r['pass']=(r['membership_exact'] and r['unique']==n and r['completed']==n
    and not r['failures'] and not r['duplicate_completions'] and r['job']['exit_code']==0
    and r['error_severity_lines']==0 and not r['fatal_ensure_unsupported']
    and 'GIsCriticalError=0' in t and r['discovered']==[(str(n),filter)]
    and r.get('cook_coverage_success',True))
(run/f'{tag}_gate.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k!='paths'},indent=2))
if not r['pass']:raise SystemExit(1)
