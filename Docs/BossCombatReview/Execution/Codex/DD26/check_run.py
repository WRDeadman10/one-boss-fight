"""C291 raw gates. File-only; no UE launch."""
from pathlib import Path
import sys,json,re
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import summarize_automation,parse_job_record
tag=sys.argv[1]
run=here/'run_2026-10-29'
mapping={'preflight':'Preflight','preparation':'Preparation','registry':'PreparationRegistry','production_preflight':'ProductionPreflight','production_preparation':'ProductionPreparation','world_input':'WorldInput','world_preparation':'WorldPreparation'}
source=json.loads((here/'focused_suite_expectations.json').read_text(encoding='utf-8'))
p=run/f'automation_{tag}.log'
r=summarize_automation(p,root)
r['job']=parse_job_record(run/f'automation_{tag}_job_record.txt',root)
t=p.read_text(encoding='utf-8')
r['discovered']=re.findall(r"LogAutomationCommandLine: Display: Found (\d+) automation tests based on '([^']+)'",t)
r['fatal_ensure_assertion_unsupported']=[line for line in t.splitlines() if re.search(r'\b(?:fatal|ensure|assertion|critical error|unsupported)\b',line,re.I)]
if tag in mapping:
    prefix='OneBossFight.Binding.'+mapping[tag]
    expected=set(source[prefix]);n=len(expected);filter=prefix+'.'
    r['membership_exact']=set(r['paths'])==expected
    r['filter_note']='Trailing dot separates Preparation. from PreparationRegistry.; each gate requires its own exact source-name set.'
else:
    assert tag=='full_dd26'
    prior=summarize_automation(here.parent/'DD25/run_2026-10-29/automation_full_dd25.log',root)
    r['missing_prior']=sorted(set(prior['paths'])-set(r['paths']))
    r['new_paths']=sorted(set(r['paths'])-set(prior['paths']))
    r['membership_exact']=not r['missing_prior'] and not r['new_paths']
    r['cook_coverage_success']=any('CookCoverage' in s and 'Result={Success}' in s for s in t.splitlines())
    n=171;filter='OneBossFight'
r['pass']=(r['membership_exact'] and r['unique']==n and r['completed']==n and not r['failures'] and not r['duplicate_completions']
    and r['job']['exit_code']==0 and r['error_severity_lines']==0 and not r['fatal_ensure_assertion_unsupported']
    and r.get('cook_coverage_success',True) and 'GIsCriticalError=0' in t and r['discovered']==[(str(n),filter)])
(run/f'{tag}_gate.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps(r,indent=2))
if not r['pass']:raise SystemExit(1)
