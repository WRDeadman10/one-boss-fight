"""C291 post-run raw evidence and pin verification; never launches UE."""
from pathlib import Path
from collections import Counter
import sys,json,re,subprocess
here=Path(__file__).resolve().parent
root=here.parents[4]
run=here/'run_2026-10-29'
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,parse_receipt,parse_job_record
pre=json.loads((run/'pre_safety.json').read_text(encoding='utf-8'))
original={r['relative_path']:r['expected_sha256'] for r in parse_receipt((run/'pre_source_manifest_sha256.txt').read_text(encoding='utf-8'))}
current={p.relative_to(root).as_posix():digest(p) for p in (root/'Source').rglob('*') if p.is_file()}
(run/'final_source_manifest_sha256.txt').write_text(''.join(v+' *'+k+'\n' for k,v in sorted(current.items())),encoding='utf-8')
binary={p:digest(root/p) for p in ['Binaries/Win64/UnrealEditor-OneBossFight.dll','Binaries/Win64/OneBossFight.exe']}
(run/'final_binary_sha256.txt').write_text(''.join(v+' *'+k+'\n' for k,v in binary.items()),encoding='utf-8')
prebin={r['relative_path']:r['expected_sha256'] for r in parse_receipt((run/'pre_binary_sha256.txt').read_text(encoding='utf-8'))}
r={'source_unchanged':original==current,'source_count':len(current),'binary':binary,'exe_unchanged':binary['Binaries/Win64/OneBossFight.exe']==prebin['Binaries/Win64/OneBossFight.exe'],'pin_checks':{}}
# Compare every source/dependency/candidate/catalog pin against its VERIFIED fresh
# pre-run bytes (including explicitly reviewed historical manifest replacements).
for group,result in pre['pins'].items():
    if group=='binaries':continue
    checks=[]
    assert result['all_verified']
    for row in result['checks']:
        path=root/row['path']
        actual=digest(path)
        checks.append({'path':row['path'],'pre_verified_sha256':row['actual_sha256'],'post_sha256':actual,'equal':actual==row['actual_sha256']})
    r['pin_checks'][group]={'all_verified':all(c['equal'] for c in checks),'checks':checks}
r['head']=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
r['head_unchanged']=r['head']==pre['head']
r['dirty']=subprocess.run(['git','status','--porcelain','--','Source','Config','Content'],cwd=root,capture_output=True,text=True,check=True).stdout
r['build_job']=parse_job_record(run/'build_dd26_job_record.txt',root)
build=(run/'build_dd26.log').read_text(encoding='utf-8')
r['build_sha256']=digest(run/'build_dd26.log')
r['uht_lines']=[s for s in build.splitlines() if 'UnrealHeaderTool' in s or 'Reflection code generated' in s]
r['build_warnings']=[s for s in build.splitlines() if re.search(r'^\s*Warning:|\bwarning C\d+',s,re.I)]
r['build_errors']=[s for s in build.splitlines() if re.search(r'\berror(?: C\d+| LNK\d+|:)',s,re.I)]
tags=['preflight','preparation','registry','production_preflight','production_preparation','world_input','world_preparation']
observed=[]
for tag in tags+['full_dd26']:
    r[tag]=json.loads((run/f'{tag}_gate.json').read_text(encoding='utf-8'))
    if tag!='full_dd26':observed+=r[tag]['paths']
r['focused_disjoint']=len(observed)==len(set(observed))==30
source=json.loads((here/'focused_suite_expectations.json').read_text(encoding='utf-8'))
r['focused_union_exact']=set(observed)=={name for names in source.values() for name in names}
def warnings(p):
    lines=[re.sub(r'^\[[^]]*\]\[\s*\d+\]','',s) for s in p.read_text(encoding='utf-8').splitlines() if ': Warning:' in s]
    return Counter(re.sub(r'(?i)(sponsor(?:process)?(?:id|pid)?[ =:]+)\d+',r'\1<PID>',re.sub(r'(?i)(epoch=)[a-f0-9]{32}\b',r'\1<EPOCH>',s)) for s in lines)
a=warnings(run/'automation_full_dd26.log');b=warnings(here.parent/'DD25/run_2026-10-29/automation_full_dd25.log')
r['warning_delta_vs_DD25']={'added':dict(a-b),'removed':dict(b-a),'current_count':sum(a.values()),'prior_count':sum(b.values())}
(run/'final_verification.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
assert r['source_unchanged'] and r['source_count']==212 and r['exe_unchanged'] and r['head_unchanged']
assert all(c['all_verified'] for c in r['pin_checks'].values())
assert r['build_job']['exit_code']==0 and not r['build_errors']
assert all(r[tag]['pass'] for tag in tags+['full_dd26']) and r['focused_disjoint'] and r['focused_union_exact']
print('Final212 Source/frozen pins/dependencies/assets/HEAD unchanged; disjoint30focused names, full171 exact.')
print('binary',binary);print('build',r['build_job'],'UHT',r['uht_lines'],'warnings',len(r['build_warnings']));print('warning delta',r['warning_delta_vs_DD25'])
