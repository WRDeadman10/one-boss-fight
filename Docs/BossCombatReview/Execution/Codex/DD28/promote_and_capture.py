"""C315 one-use promotion; all safety checks finish before any Source write."""
from pathlib import Path
import hashlib,json,subprocess,sys,datetime
H=Path(__file__).resolve().parent;ROOT=H.parents[4];R=H/'run_2026-10-29'
sys.path.insert(0,str(H.parent/'EvidenceTools'))
from verify_bundle import verify_receipt
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def manifest():return {p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
R.mkdir(exist_ok=False)
old=H.parent/'DD26';S=H/'Staging'
expected={s.split(' *',1)[1]:s.split(' *',1)[0] for s in (old/'post_source_manifest_sha256.txt').read_text().splitlines() if ' *' in s}
process_cmd="Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress"
proc=subprocess.check_output(['powershell','-NoProfile','-Command',process_cmd],text=True).strip()
state={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'processes':json.loads(proc) if proc else [],'head':git('rev-parse','HEAD'),'tracked_status':git('status','--short','--','Source','Content','Config'),'source_count':0,'pins':[]}
assert not state['processes'],'Engine/compiler present; STOP'
actual=manifest();state['source_count']=len(actual)
assert actual==expected and len(actual)==212,'DD26 Source drift; STOP'
assert state['head']=='bc3fe6a49335f0a68bf5df9d895b8a46f6633aeb','HEAD drift; STOP'
assert not state['tracked_status'],'Tracked Source/Content/Config dirty before promotion; STOP'
# Rehash every dependency/candidate/catalog/current Source pin captured in the accepted DD26 safety record.
prior=json.loads((old/'run_2026-10-29/pre_safety.json').read_text())
for receipt,bundle in prior['pins'].items():
    if receipt=='binaries':continue
    assert bundle['all_verified'],receipt
    for row in bundle['checks']:
        p=ROOT/row['path'];current=sha(p)
        assert current==row['actual_sha256'],f'DD26 accepted pin drift: {p}; STOP'
        state['pins'].append({'receipt':receipt,'path':p.relative_to(ROOT).as_posix(),'expected_accepted_sha256':row['actual_sha256'],'actual_sha256':current,'historical_status':row['status']})
binary=verify_receipt(old/'run_2026-10-29/final_binary_sha256.txt',ROOT,ROOT)
assert binary['all_verified'],'DD26 binary drift; STOP'
state['binaries']=binary
stage_manifest=json.loads((S/'staged_manifest.json').read_text())
assert stage_manifest['release']=='C-313' and len(stage_manifest['files'])==3
mapping={'RPGBossHydrationPreparation.h':'Source/OneBossFight/Player/RPGBossHydrationPreparation.h','RPGBossHydrationPreparation.cpp':'Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp','RPGBossActivationTests.cpp':'Source/OneBossFight/Tests/RPGBossActivationTests.cpp'}
for row in stage_manifest['files']:
    name=row['path'];assert sha(S/name)==row['sha256'],f'Stage drift {name}'
    live=ROOT/mapping[name]
    if live.exists():assert (S/'Preimages'/name).read_bytes()==live.read_bytes(),'Preimage drift'
    else:assert name=='RPGBossActivationTests.cpp'
state['staged_manifest_sha256']=sha(S/'staged_manifest.json');state['passed']=True
(R/'pre_promotion_safety.json').write_text(json.dumps(state,indent=2)+'\n')
(R/'pre_source_manifest_sha256.txt').write_text(''.join(f'{v} *{k}\n' for k,v in sorted(actual.items())))
(R/'pre_binary_sha256.txt').write_bytes((old/'run_2026-10-29/final_binary_sha256.txt').read_bytes())
# Only these exact three C315-authorized promotions, after every prerequisite above passed.
for name,rel in mapping.items():(ROOT/rel).write_bytes((S/name).read_bytes())
post=manifest();changed=[k for k in actual if actual[k]!=post.get(k)];added=sorted(post.keys()-actual.keys())
assert len(post)==213 and set(changed)==set(list(mapping.values())[:2]) and added==[mapping['RPGBossActivationTests.cpp']]
(H/'post_source_manifest_sha256.txt').write_text(''.join(f'{v} *{k}\n' for k,v in sorted(post.items())))
(R/'post_promotion_source_manifest_sha256.txt').write_bytes((H/'post_source_manifest_sha256.txt').read_bytes())
(R/'promotion_result.json').write_text(json.dumps({'source_count':213,'changed':changed,'added':added,'prior_unchanged':210,'stage_live_equal':True},indent=2)+'\n')
# Disclose blank-line counting convention with exact evidence.
count={}
for name in list(mapping)[:2]:
    rows=(S/(name+'.diff')).read_text().splitlines();adds=[s[1:] for s in rows if s.startswith('+') and not s.startswith('+++')]
    count[name]={'added_including_blank':len(adds),'added_nonblank':sum(bool(s.strip()) for s in adds),'added_blank':sum(not s.strip() for s in adds),'removed':sum(s.startswith('-') and not s.startswith('---') for s in rows)}
(R/'diff_count_convention.json').write_text(json.dumps(count,indent=2)+'\n')
print(json.dumps({'safety_passed':True,'source_count':213,'accepted_pins_rehashed':len(state['pins']),'promotion':'only3 accepted files','diff_count_convention':count}))
