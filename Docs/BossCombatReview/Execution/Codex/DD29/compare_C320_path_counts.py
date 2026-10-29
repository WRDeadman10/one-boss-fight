"""Read-only reconciliation of C320/A214's JSON path count, not asset-class/load proof."""
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent;ROOT=H.parents[4];R=H/'run_2026-10-29'
p=ROOT/'Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json'
data=json.loads(p.read_text(encoding='utf-8'));uses={}
def walk(v,where='$'):
    if isinstance(v,dict):
        for k,x in v.items():walk(x,where+'.'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v):walk(x,f'{where}[{i}]')
    elif isinstance(v,str) and v.startswith('/Game/'):
        uses.setdefault(v,[]).append(where)
walk(data)
mail=(ROOT/'Documentation/TEAM_MAILBOX.md').read_text(encoding='utf-8',errors='replace')
start=mail.index('### [A-214]');end=mail.find('### [',start+5);text=mail[start:end if end>=0 else len(mail)]
table=set(re.findall(r'^\| (/Game/[^ |]+) \| True',text,re.M))
extra=sorted(set(uses)-table);missing=sorted(table-set(uses))
rows=[]
for value,locations in sorted(uses.items()):
    object_path='.' in value.rsplit('/',1)[-1]
    package=value.split('.',1)[0]
    local=ROOT/'Content'/package.removeprefix('/Game/')
    rows.append({'value':value,'json_locations':locations,'has_object_suffix':object_path,'asset_file_exists':local.with_suffix('.uasset').is_file() if object_path else None,'directory_exists':local.is_dir() if not object_path else None})
result={'all_distinct_JSON_Game_strings':len(uses),'A214_asset_table_distinct':len(table),'JSON_only':extra,'A214_only':missing,'rows':rows,'scope':'Disk path presence and count categories only, not class/skeleton/engine load/cook/authoring proof'}
(R/'C320_profile_path_count_comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'all_JSON_Game_strings':len(uses),'A214_asset_table':len(table),'extra':extra,'missing':missing}))
