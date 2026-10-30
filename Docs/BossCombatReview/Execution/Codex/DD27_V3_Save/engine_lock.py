from pathlib import Path
import json,sys,datetime,os
R=Path(__file__).resolve().parent;lock=R.parents[1]/'ENGINE_LOCK.json';mode=sys.argv[1]
if mode=='acquire':
    record={'agent':'Codex','party':'X','task':'C-364/DD27_V3_Save','command_id':'DD27_V3_Save.V3.save-one-new','start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy':'C-321'}
    try:
        with lock.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    except FileExistsError:
        print('STOP existing engine lock: '+lock.read_text(encoding='utf-8',errors='replace'));raise SystemExit(2)
    (R/'engine_lock_record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('C321 exclusive DD27_V3_Save engine lock acquired')
elif mode=='release':
    v=json.loads(lock.read_text(encoding='utf-8'));assert v['agent']=='Codex' and v['task']=='C-364/DD27_V3_Save' and v['command_id']=='DD27_V3_Save.V3.save-one-new'
    lock.unlink();print('C321 own DD27_V3_Save lock released after evidence frozen / STOP')
else:raise SystemExit('Unknown mode')
