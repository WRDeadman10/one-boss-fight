from pathlib import Path
import json,datetime,sys,os
R=Path(__file__).resolve().parent
p=R.parents[2]/'ENGINE_LOCK.json'
if sys.argv[1]=='acquire':
 record={'agent':'Antigravity','party':'A','task':'C-352/DD30ChronologyRun1','command_id':'DD30Chronology.pie-run','start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy':'C-321'}
 try:
  with p.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 except FileExistsError:
  print('STOP existing lock '+p.read_text());raise SystemExit(2)
 (R/'engine_lock_record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 print('C321 exclusive DD30ChronologyRun1 lock acquired')
elif sys.argv[1]=='release':
 v=json.loads(p.read_text());assert v['agent']=='Antigravity' and v['task']=='C-352/DD30ChronologyRun1' and v['command_id']=='DD30Chronology.pie-run'
 p.unlink();print('Own DD30ChronologyRun1 lock released after evidence freeze')
else:raise SystemExit(2)
