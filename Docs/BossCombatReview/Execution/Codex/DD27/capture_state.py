"""C300 bounded snapshots: all Content file names/sizes; Data subtree hashes."""
from pathlib import Path
import hashlib, json, subprocess, sys, datetime
ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()
def snapshot(folder, hashes=False, data_hash=False):
    rows=[]
    for p in sorted((ROOT/folder).rglob('*')):
        if not p.is_file(): continue
        s=p.stat(); rel=p.relative_to(ROOT).as_posix()
        row={'path':rel,'size':s.st_size,'mtime_ns':s.st_mtime_ns}
        if hashes or (data_hash and rel.startswith('Content/OneBossFight/Data/')): row['sha256']=sha(p)
        rows.append(row)
    return rows
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
stage=sys.argv[1]
assert stage in ('pre','post')
process_cmd="Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress"
proc=subprocess.check_output(['powershell','-NoProfile','-Command',process_cmd],text=True).strip()
source=snapshot('Source',hashes=True)
expected={line.split(' *',1)[1]:line.split(' *',1)[0] for line in (OUT.parent/'DD26/post_source_manifest_sha256.txt').read_text().splitlines() if ' *' in line}
drift=[r['path'] for r in source if expected.get(r['path'])!=r['sha256']]
assert len(source)==len(expected)==212 and not drift, f'Source drift {drift}'
head=git('rev-parse','HEAD')
assert head=='bc3fe6a49335f0a68bf5df9d895b8a46f6633aeb',head
toolkit=ROOT/'Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit'
pins=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted(toolkit.glob('*.py'))]
input_json=toolkit/'examples/boss_draft_profiles.json'
pins.append({'path':input_json.relative_to(ROOT).as_posix(),'sha256':sha(input_json)})
data={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'processes':json.loads(proc) if proc else [],'head':head,'source':source,'content':snapshot('Content',data_hash=True),'config':snapshot('Config',hashes=True),'saved':snapshot('Saved'),'toolkit':pins,'input_fields_counts':{p['asset_name']:len(p.get('fields',[])) for p in json.loads(input_json.read_text())['profiles']},'content_git_status':git('status','--short','--','Content'),'binary':[]}
for name in ('UnrealEditor-OneBossFight.dll','UnrealEditor-OneBossFight.pdb','OneBossFight.exe'):
    p=ROOT/'Binaries/Win64'/name
    if p.exists(): data['binary'].append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'size':p.stat().st_size})
target=OUT/f'{stage}_state.json'
assert not target.exists(),target
target.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'stage':stage,'processes':data['processes'],'source_count':len(source),'content_files':len(data['content']),'content_data_hashes':sum('sha256' in r for r in data['content']),'input_fields_counts':data['input_fields_counts'],'snapshot_sha256':sha(target)}))
if data['processes']: raise SystemExit('STOP: engine/compiler present')
if stage=='post':
    pre=json.loads((OUT/'pre_state.json').read_text())
    result={}
    for kind in ('content','config','saved','source','toolkit','binary'):
        a={r['path']:r for r in pre[kind]}; b={r['path']:r for r in data[kind]}
        keys=('size','sha256') if kind=='content' else ('size','sha256','mtime_ns')
        result[kind]={'added':sorted(b.keys()-a.keys()),'removed':sorted(a.keys()-b.keys()),'changed':[k for k in sorted(a.keys()&b.keys()) if any(a[k].get(v)!=b[k].get(v) for v in keys)]}
    (OUT/'state_diff.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
