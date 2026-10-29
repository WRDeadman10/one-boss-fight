"""C319 fail-closed file gates; never launches engine or modifies Source."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[4];R=H/'run_2026-10-29'
sys.path.insert(0,str(H.parent/'EvidenceTools'))
from verify_bundle import summarize_automation,parse_job_record,verify_receipt
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source_check():
    expected={s.split(' *',1)[1]:s.split(' *',1)[0] for s in (H/'post_source_manifest_sha256.txt').read_text().splitlines() if ' *' in s}
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
    assert expected==current and len(current)==216,'Source drift'
    pre=json.loads((R/'pre_promotion_safety.json').read_text())
    changes=set()
    checks=[]
    for row in pre['pins']:
        key=row['path'];want=expected[key] if key in changes else row['actual_sha256'];actual=sha(ROOT/key)
        checks.append({'path':key,'expected_post_sha256':want,'actual_sha256':actual,'reviewed_promotion_replacement':key in changes,'equal':want==actual})
    assert all(c['equal'] for c in checks),'Dependency/candidate/catalog drift'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==pre['head'],'HEAD drift'
    return checks
tag=sys.argv[1]
checks=source_check()
if tag=='before_build':
    proc=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress"],text=True).strip()
    (R/'pre_build_process_check.txt').write_text(proc+'\n')
    assert not proc,'Engine/compiler present'
    c=verify_receipt(R/'pre_binary_sha256.txt',ROOT,ROOT);assert c['all_verified'],'Pre-build binary drift'
    print('C319 fresh pre-build Source213/pins/HEAD/process/binary checks passed')
elif tag=='build':
    job=parse_job_record(R/'build_dd29_job_record.txt',ROOT);t=(R/'build_dd29.log').read_text(errors='replace')
    result={'job':job,'raw_sha256':sha(R/'build_dd29.log'),'errors':[s for s in t.splitlines() if re.search(r'\berror(?: C\d+| LNK\d+|:)',s,re.I)],'uht_lines':[s for s in t.splitlines() if 'UnrealHeaderTool' in s or 'Reflection code generated' in s],'warnings':[s for s in t.splitlines() if re.search(r'^\s*Warning:|\bwarning C\d+',s,re.I)],'source_unchanged':True}
    result['pass']=job['exit_code']==0 and not result['errors']
    (R/'build_gate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert result['pass'],'Build failed; STOP'
else:
    map_file={'activation_world':('ActivationWorld','RPGBossActivationWorldTests.cpp',5),'activation':('Activation','RPGBossActivationTests.cpp',6),'world_preparation':('WorldPreparation','RPGBossWorldPreparationTests.cpp',4),'registry':('PreparationRegistry','RPGBossPreparationRegistryTests.cpp',3)}
    p=R/f'automation_{tag}.log';r=summarize_automation(p,ROOT);r['job']=parse_job_record(R/f'automation_{tag}_job_record.txt',ROOT)
    t=p.read_text(errors='replace');r['discovered']=re.findall(r"LogAutomationCommandLine: Display: Found (\d+) automation tests based on '([^']+)'",t)
    r['fatal_ensure_assertion_unsupported']=[s for s in t.splitlines() if re.search(r'\b(?:fatal|ensure|assertion|critical error|unsupported)\b',s,re.I)]
    if tag in map_file:
        suite,name,n=map_file[tag];filter='OneBossFight.Binding.'+suite+'.'
        expected=set(re.findall(r'"(OneBossFight\.Binding\.'+suite+r'\.[^"]+)"',(ROOT/'Source/OneBossFight/Tests'/name).read_text()))
        assert len(expected)==n
        r['membership_exact']=set(r['paths'])==expected
    else:
        assert tag=='full_dd29';filter='OneBossFight';n=182
        prior=summarize_automation(H.parent/'DD28/run_2026-10-29/automation_full_dd28.log',ROOT)
        new=set(re.findall(r'"(OneBossFight\.Binding\.ActivationWorld\.[^"]+)"',(ROOT/'Source/OneBossFight/Tests/RPGBossActivationWorldTests.cpp').read_text()))
        r['missing_prior']=sorted(set(prior['paths'])-set(r['paths']));r['new_paths']=sorted(set(r['paths'])-set(prior['paths']))
        r['membership_exact']=not r['missing_prior'] and set(r['new_paths'])==new and len(new)==5
        r['cook_coverage_success']=any('CookCoverage' in s and 'Result={Success}' in s for s in t.splitlines())
    r['pass']=r['membership_exact'] and r['unique']==n and r['completed']==n and not r['failures'] and not r['duplicate_completions'] and r['job']['exit_code']==0 and r['error_severity_lines']==0 and not r['fatal_ensure_assertion_unsupported'] and r.get('cook_coverage_success',True) and 'GIsCriticalError=0' in t and r['discovered']==[(str(n),filter)]
    (R/f'{tag}_gate.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'tag':tag,'pass':r['pass'],'unique':r['unique'],'completed':r['completed'],'errors':r['error_severity_lines'],'failures':r['failures'],'raw_sha256':r['sha256'] if 'sha256' in r else sha(p)}))
    if not r['pass']:raise SystemExit('Gate failed; STOP, no next suite')
