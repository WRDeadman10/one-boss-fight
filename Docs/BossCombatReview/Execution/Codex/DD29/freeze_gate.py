from pathlib import Path
import hashlib,sys
R=Path(__file__).resolve().parent/'run_2026-10-29';tag=sys.argv[1]
names=[f'automation_{tag}.log',f'automation_{tag}_job_record.txt',f'{tag}_gate.json',f'engine_lock_{tag}.json']
assert all((R/n).is_file() for n in names)
(R/f'{tag}_sealed_receipt_sha256.txt').write_text(''.join(hashlib.sha256((R/n).read_bytes()).hexdigest()+' *'+n+'\n' for n in names),encoding='utf-8')
print('Raw/job/gate/lock evidence frozen for '+tag)
