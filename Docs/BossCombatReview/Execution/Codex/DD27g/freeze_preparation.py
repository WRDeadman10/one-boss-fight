"""Offline preparation checks only; not a pre-launch safety capture or UE test."""
from pathlib import Path
import ast,hashlib,json,difflib,datetime
R=Path(__file__).resolve().parent;ROOT=R.parents[4];F=R.parent/'DD27f'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old_receipt={s.split(' *',1)[1]:s.split(' *',1)[0] for s in (F/'receipt_sha256.txt').read_text(encoding='utf-8').splitlines() if ' *' in s}
copies=[];diff=[]
for name in ('capture_state.py','preflight.py','engine_lock.py','run_once.ps1'):
    a=F/name;b=R/name
    assert old_receipt[name]==sha(a),'Original DD27f evidence drift'
    if name.endswith('.py'):ast.parse(b.read_text(encoding='utf-8'))
    copies.append({'original':a.relative_to(ROOT).as_posix(),'original_sha256':sha(a),'prepared_copy':name,'prepared_sha256':sha(b)})
    diff.extend(difflib.unified_diff(a.read_text(encoding='utf-8').splitlines(True),b.read_text(encoding='utf-8').splitlines(True),fromfile='DD27f/'+name,tofile='DD27g/'+name))
(R/'wrapper_preparation.diff').write_text(''.join(diff),encoding='utf-8')
assert not (R/'release_to_run.json').exists(),'Unexpected run authorization; inspect lead release before continuing'
assert not any((R/n).exists() for n in ('command.json','pre_state.json','job_record.json','editor_raw.log','engine_lock_record.json'))
wrapper=(R/'run_once.ps1').read_text(encoding='utf-8')
assert '--classrefs' in wrapper and '--apply' not in wrapper and '--save' not in wrapper
expected_path=R.parent/'DD29/run_2026-10-29/final_source_manifest_sha256.txt'
expected={s.split(' *',1)[1]:s.split(' *',1)[0] for s in expected_path.read_text(encoding='utf-8').splitlines() if ' *' in s}
live={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
assert live==expected and len(live)==216,'Source drift; report before any engine launch'
manifest={'order':'C-325 PREPARATION ONLY','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run_released':False,'run_performed':False,'no_fresh_prelaunch_snapshot':True,'python_ast_parsed':True,'source_216_DD29_unchanged_offline_check':True,'copies':copies,'scope':'Preparation file checks, not UE tests or runtime/engine-liveness proof'}
(R/'preparation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
exclude={'preparation_receipt_sha256.txt','MESSAGE_PREPARED.txt'}
files=[p for p in sorted(R.iterdir()) if p.is_file() and p.name not in exclude]
(R/'preparation_receipt_sha256.txt').write_text(''.join(f'{sha(p)} *{p.name}\n' for p in files),encoding='utf-8')
print(json.dumps({'prepared_files':len(files),'source_unchanged':216,'run_released':False,'receipt_sha256':sha(R/'preparation_receipt_sha256.txt')}))
