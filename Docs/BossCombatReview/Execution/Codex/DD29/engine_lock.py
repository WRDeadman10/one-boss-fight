"""C321 exclusive engine ownership. Never remove another operator's lock."""
from pathlib import Path
import json,sys,datetime,os
H=Path(__file__).resolve().parent;E=H.parents[1];R=H/'run_2026-10-29'
lock=E/'ENGINE_LOCK.json';mode,command=sys.argv[1:3]
if mode=='acquire':
    record={'agent':'Codex','party':'X','task':'C-319/DD29','command_id':command,'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy':'C-321'}
    try:
        with lock.open('x',encoding='utf-8') as f:
            json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    except FileExistsError:
        print('STOP: existing ENGINE_LOCK.json: '+lock.read_text(encoding='utf-8',errors='replace'));raise SystemExit(2)
    (R/f'engine_lock_{command}.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('C321 exclusive engine lock acquired for '+command)
elif mode=='release':
    record=json.loads(lock.read_text(encoding='utf-8'))
    assert record['agent']=='Codex' and record['task']=='C-319/DD29' and record['command_id']==command,'Different lock owner; STOP'
    lock.unlink();print('C321 own engine lock released after evidence capture: '+command)
else:raise SystemExit('Unknown mode')
