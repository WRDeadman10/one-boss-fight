from pathlib import Path
import json,sys,datetime,os
R=Path(__file__).resolve().parent;lock=R.parents[1]/'ENGINE_LOCK.json';mode=sys.argv[1]
if mode=='acquire':
    record={'agent':'Codex','party':'X','task':'C-320/DD27f','command_id':'DD27f.apply.no-save','start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy':'C-321'}
    try:
        with lock.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    except FileExistsError:
        print('STOP existing engine lock: '+lock.read_text(encoding='utf-8',errors='replace'));raise SystemExit(2)
    (R/'engine_lock_record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('C321 exclusive DD27f engine lock acquired')
elif mode=='release':
    v=json.loads(lock.read_text(encoding='utf-8'));assert v['agent']=='Codex' and v['task']=='C-320/DD27f' and v['command_id']=='DD27f.apply.no-save'
    lock.unlink();print('C321 own DD27f lock released after evidence frozen / STOP')
else:raise SystemExit('Unknown mode')
