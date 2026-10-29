from pathlib import Path
import json,sys,hashlib
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import verify_receipt,digest
checks=json.loads((here/'source_checks.json').read_text(encoding='utf-8'))
pins=verify_receipt(here/'live_pins_sha256.txt',root,root)
manifest=verify_receipt(here/'post_source_manifest_sha256.txt',root,root)
for row in checks['files']:
    p=root/row['path']
    assert p.read_bytes()==(here/'Review'/p.name).read_bytes()
text=(root/'Source/OneBossFight/Tests/RPGBossHealPunishAdaptersTests.cpp').read_text(encoding='utf-8')
assert 'AimHfourteen' not in text
assert 'FieldAimHeight' in text
print('Verified five Review/live copies and all203 current Source hashes; six test names unique. File checks only.')
delivery=here/'DELIVERY_TO_CLAUDE.md'
with delivery.open('a',encoding='utf-8') as f:
    f.write('\nFive frozen source pins:\n'+''.join(r['path']+' SHA256 '+r['sha256']+'\n' for r in checks['files']))
rows=[]
for p in sorted(here.rglob('*')):
    if p.is_file() and p.name not in {'evidence_sha256.txt','MESSAGE_TO_CLAUDE.txt'}:
        rows.append(f'{digest(p)} *{p.relative_to(here).as_posix()}\n')
receipt=here/'evidence_sha256.txt'
receipt.write_text(''.join(rows),encoding='utf-8')
verify_receipt(receipt,here,root)
body=delivery.read_text(encoding='utf-8')+'\nEvidence: Docs/BossCombatReview/Execution/Codex/DD22/evidence_sha256.txt; '+str(len(rows))+' receipts; SHA256 '+digest(receipt)+'.\n'
(here/'MESSAGE_TO_CLAUDE.txt').write_text(body,encoding='utf-8')
print('Frozen',len(rows),'receipts; SHA256',digest(receipt))
