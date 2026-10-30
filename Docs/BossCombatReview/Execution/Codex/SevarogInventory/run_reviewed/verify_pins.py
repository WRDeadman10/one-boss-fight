from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[5]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((R/'baseline.json').read_text());pre=json.loads((R/'pre_state.json').read_text())
assert len(pre['source'])==219 and len(pre['content'])==11756 and sum('sha256' in x for x in pre['content'])==20
assert all(sha(ROOT/p)==h for p,h in b['binary'].items()),'Binary drift; STOP'
assert sha(R.parent/'probe_sevarog_inventory.py')==b['probe_sha256'] and sha(R.parent/'run_inventory_review_only.ps1')==b['wrapper_sha256'],'Script drift; STOP'
print('C361 inventory fresh Source219/4assets/Content11756/Data20/HEAD+allowed-delta/binary/probe pins verified')
