from pathlib import Path
import json
R=Path(__file__).resolve().parent
x=json.loads((R/'state_diff.json').read_text());expected=json.loads((R/'expected_new_content.json').read_text())
assert sorted(x['content']['added'])==sorted(expected),'Unexpected Content additions; STOP'
assert not x['content']['changed'] and not x['content']['removed'],'Existing Content drift; STOP'
for k in ('config','source','toolkit','binary'):assert not any(x[k].values()),f'{k} drift; STOP'
post=json.loads((R/'post_state.json').read_text());assert not post['processes']
print('Expected Content delta only; captured baseline unchanged outside Saved')
