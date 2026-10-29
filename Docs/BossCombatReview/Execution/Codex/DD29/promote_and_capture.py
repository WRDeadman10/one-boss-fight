"""C319 one-use promotion. Validate all prerequisites before creating Source files."""
from pathlib import Path
import hashlib,json,subprocess,sys,datetime
H=Path(__file__).resolve().parent;ROOT=H.parents[4];R=H/'run_2026-10-29';S=H/'Staging'
sys.path.insert(0,str(H.parent/'EvidenceTools'))
from verify_bundle import verify_receipt
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest():return {p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
R.mkdir(exist_ok=False)
old=H.parent/'DD28/run_2026-10-29'
expected={s.split(' *',1)[1]:s.split(' *',1)[0] for s in (old/'final_source_manifest_sha256.txt').read_text().splitlines() if ' *' in s}
proc=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress"],text=True).strip()
state={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'processes':json.loads(proc) if proc else [],'head':git('rev-parse','HEAD'),'tracked_status':git('status','--short','--','Source','Content','Config'),'source_count':0,'pins':[]}
assert not state['processes'],'Engine/compiler present; STOP'
actual=manifest();state['source_count']=len(actual)
assert actual==expected and len(actual)==213,'DD28 Source drift; STOP'
assert state['head']=='bc3fe6a49335f0a68bf5df9d895b8a46f6633aeb','HEAD drift'
assert not git('status','--short','--','Content','Config'),'Tracked Content/Config dirty'
prior=json.loads((old/'final_verification.json').read_text())
for row in prior['pin_checks']:
    assert row['equal']
    key=row['path'];current=sha(ROOT/key);assert current==row['final_sha256'],f'Accepted dependency/asset/native pin drift: {key}'
    state['pins'].append({'path':key,'actual_sha256':current,'accepted_DD28_final_sha256':row['final_sha256']})
binary=verify_receipt(old/'final_binary_sha256.txt',ROOT,ROOT);assert binary['all_verified'],'DD28 binary drift'
state['binaries']=binary
stage=json.loads((S/'staged_manifest.json').read_text(encoding='utf-8'))
assert stage['release']=='C-316' and len(stage['files'])==3
mapping={'RPGBossActivation.h':'Source/OneBossFight/Player/RPGBossActivation.h','RPGBossActivation.cpp':'Source/OneBossFight/Player/RPGBossActivation.cpp','RPGBossActivationWorldTests.cpp':'Source/OneBossFight/Tests/RPGBossActivationWorldTests.cpp'}
pre=R/'Preimages';pre.mkdir()
for rel in ('Source/OneBossFight/Player/RPGBossHydrationPreparation.h','Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp','Source/OneBossFight/Player/RPGBossWorldPreparation.h','Source/OneBossFight/Player/RPGBossPreparationRegistry.h'):
    (pre/Path(rel).name).write_bytes((ROOT/rel).read_bytes())
for row in stage['files']:
    assert row['path'] in mapping and sha(S/row['path'])==row['sha256'],'Staged pin drift'
    assert not (ROOT/mapping[row['path']]).exists(),'New Source target already exists; STOP'
state['stage_manifest_sha256']=sha(S/'staged_manifest.json');state['passed']=True
(R/'pre_promotion_safety.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
(R/'pre_source_manifest_sha256.txt').write_text(''.join(f'{v} *{k}\n' for k,v in sorted(actual.items())),encoding='utf-8')
(R/'pre_binary_sha256.txt').write_bytes((old/'final_binary_sha256.txt').read_bytes())
for name,rel in mapping.items():(ROOT/rel).write_bytes((S/name).read_bytes())
post=manifest();added=sorted(post.keys()-actual.keys())
assert len(post)==216 and set(added)==set(mapping.values()) and all(post[k]==v for k,v in actual.items())
(H/'post_source_manifest_sha256.txt').write_text(''.join(f'{v} *{k}\n' for k,v in sorted(post.items())),encoding='utf-8')
(R/'post_promotion_source_manifest_sha256.txt').write_bytes((H/'post_source_manifest_sha256.txt').read_bytes())
(R/'promotion_result.json').write_text(json.dumps({'source_count':216,'prior_unchanged':213,'added':added,'changed':[],'stage_live_equal':True},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'safety_passed':True,'promoted_only':added,'source_count':216,'old_213_unchanged':True,'rehashed_pins':len(state['pins'])}))
