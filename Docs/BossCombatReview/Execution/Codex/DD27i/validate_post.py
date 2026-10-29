from pathlib import Path
import json
R=Path(__file__).resolve().parent
x=json.loads((R/'state_diff.json').read_text());want=json.loads((R/'expected_new_content.json').read_text())
assert sorted(x['content']['added'])==sorted(want),'Expected EXACTLY three new assets; STOP'
assert not x['content']['changed'] and not x['content']['removed'],'Existing Content inventory changed; STOP'
for k in ('config','source','toolkit','binary'):assert not any(x[k].values()),f'{k} drift; STOP'
post=json.loads((R/'post_state.json').read_text());assert not post['processes']
print('Exact three new Content paths; no other captured drift outside Saved. Existing Content minimum evidence: path/size + Data hashes, not every Content byte.')
