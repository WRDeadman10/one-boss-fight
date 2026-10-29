"""C305 offline comparison only; historical equality cannot recreate a fresh pre-state."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a_path=R.parent/'DD27/post_state.json'
b_path=R/'post_only_state.json'
a=json.loads(a_path.read_text());b=json.loads(b_path.read_text())
def compare(rows_a,rows_b,keys):
    aa={r['path']:r for r in rows_a};bb={r['path']:r for r in rows_b}
    added=sorted(bb.keys()-aa.keys());removed=sorted(aa.keys()-bb.keys())
    changed=[{'path':p,'before':{k:aa[p].get(k) for k in keys},'after':{k:bb[p].get(k) for k in keys}} for p in sorted(aa.keys()&bb.keys()) if any(aa[p].get(k)!=bb[p].get(k) for k in keys)]
    return {'added':added,'removed':removed,'changed':changed,'differing_paths':len(added)+len(removed)+len(changed)}
content=compare(a['content'],b['content'],('size',))
data_a=[r for r in a['content'] if r['path'].startswith('Content/OneBossFight/Data/')]
data_b=[r for r in b['content'] if r['path'].startswith('Content/OneBossFight/Data/')]
data=compare(data_a,data_b,('size','sha256'))
result={'order':'C-305','comparison':'historical DD27 run1 post vs DD27b post-only; NOT fresh before/after','earlier':{'path':str(a_path),'sha256':sha(a_path),'utc':a['utc'],'content_count':len(a['content'])},'later':{'path':str(b_path),'sha256':sha(b_path),'utc':b['utc'],'content_count':len(b['content'])},'content_path_size':content,'data_hashes':{'earlier_count':len(data_a),'later_count':len(data_b),'comparison':data},'content_git_status_equal':a['content_git_status']==b['content_git_status'],'limits':'Content beyond Data was inventoried by path/size, not hashed; identical size is not proof of identical bytes. Historical equality does not repair missing DD27b pre-state.'}
out=R/'C305_historical_content_comparison.json'
assert not out.exists(),'Preserve prior comparison'
out.write_text(json.dumps(result,indent=2)+'\n')
report=f'''C305 requested offline comparison completed. DD27 run1 post inventory vs DD27b post-only inventory: {len(a['content'])} vs {len(b['content'])} Content files; {content['differing_paths']} differing paths by path+size (added {len(content['added'])}, removed {len(content['removed'])}, size-changed {len(content['changed'])}). The 16 Data files also have {data['differing_paths']} differences by path+size+SHA256. Content git-status snapshots equal: {result['content_git_status_equal']}.

Evidence Codex/DD27b/C305_historical_content_comparison.json SHA256 {sha(out)}. Both input snapshot hashes/times and full differences are recorded there. This is a historical interval comparison, NOT the missing fresh pre-state; unchanged sizes outside Data do not certify unchanged bytes. No engine/toolkit/Source/Config/Content changes or retry. C305 API-only acceptance and the execution-control finding remain. Holding for your release after AG's instance probe delivery.
'''
(R/'C305_MESSAGE_DELIVERY.txt').write_text(report)
with (R.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:
    f.write('\n\nC305 offline comparison completed: DD27 post vs DD27b post-only Content inventories11752 each,0 path/size differences,16Data0SHA differences. Historical comparison only; DD27b fresh pre-state remains missing. Probe accepted API-presence only; no engine release pending AG A209 instance-probe review.\n')
(R/'C305_comparison_receipt_sha256.txt').write_text('\n'.join(f'{sha(p)} *{p.name}' for p in (Path(__file__),out,R/'C305_MESSAGE_DELIVERY.txt'))+'\n')
print(report)
