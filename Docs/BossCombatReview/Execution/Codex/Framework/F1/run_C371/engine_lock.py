from pathlib import Path
import json,datetime,sys,os
R=Path(__file__).resolve().parent
p=R.parents[3]/'ENGINE_LOCK.json'
if sys.argv[1]=='acquire':
 record={'agent':'Codex','party':'X','task':'C-371/F1','command_id':'DD27k.build-and-one-focused','start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy':'C-321'}
 try:
  with p.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 except FileExistsError:
  print('STOP existing lock '+p.read_text());raise SystemExit(2)
 (R/'engine_lock_record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 print('C321 exclusive DD27k lock acquired')
elif sys.argv[1]=='release':
 v=json.loads(p.read_text());assert v['agent']=='Codex' and v['task']=='C-371/F1' and v['command_id']=='DD27k.build-and-one-focused'
 p.unlink();print('Own DD27k lock released after evidence freeze')
else:raise SystemExit(2)
