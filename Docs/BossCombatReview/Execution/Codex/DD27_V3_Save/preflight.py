from pathlib import Path
import hashlib,json,subprocess,sys,datetime
R=Path(__file__).resolve().parent;ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
release_path=R/'release_to_run.json'
assert release_path.exists(),'C343 preparation only: Claude acceptance of A226 and explicit DD27_V3_Save run release REQUIRED; STOP'
release=json.loads(release_path.read_text(encoding='utf-8'))
assert release['task']=='DD27_V3_Save' and release['mode']=='--apply --only DA_Player_Hero_Draft_V3 --save' and release['operator']=='Codex','Wrong release scope'
approval_path=R/'owner_approval.json'
assert approval_path.exists(),'Owner explicit fourth-asset SAVE approval absent; STOP'
approval=json.loads(approval_path.read_text(encoding='utf-8'))
assert approval['approved'] is True and approval['scope']=='one new Hero V3 asset only' and approval['quote'],'Wrong approval scope'
evidence=ROOT/approval['evidence_path']
assert evidence.is_file() and sha(evidence)==approval['evidence_sha256'],'Owner evidence absent/drift'
assert approval['quote'] in evidence.read_text(encoding='utf-8',errors='replace'),'Owner quote absent'
acceptance_path=R/'accepted_in_memory.json'
assert acceptance_path.exists(),'Lead acceptance of measured V3 in-memory run required; STOP'
acceptance=json.loads(acceptance_path.read_text(encoding='utf-8'))
assert acceptance['message_id'] and acceptance['report_path'] and sha(ROOT/acceptance['report_path'])==acceptance['report_sha256'],'Missing/drifted in-memory evidence'
posted=R.parent/'DD29/run_2026-10-29/report_posted.json'
marker=json.loads(posted.read_text(encoding='utf-8-sig'))
mail=(ROOT/'Documentation/TEAM_MAILBOX.md').read_text(encoding='utf-8',errors='replace')
assert marker['release']=='C-319' and '### ['+marker['message_id']+']' in mail,'DD29 report must be posted BEFORE DD27_V3_Save'
assert '### ['+release['message_id']+'] Claude ->' in mail,'Run-release header absent'
baseline=R.parent/'C364_V3_AUTHORING_BASELINE.json';base=json.loads(baseline.read_text(encoding='utf-8'))
assert base['source_count']==219 and base['release']=='C-364 preparation','Wrong engine baseline'
for kind in ('source','binary'):assert sha(ROOT/base[kind+'_manifest'])==base[kind+'_manifest_sha256'],'DD29 baseline manifest drift'
for rel,want in base['binary'].items():assert sha(ROOT/rel)==want,'DD29 binary drift; STOP'
receipt=ROOT/'Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/evidence_sha256.txt'
pins=[]
for name in ('draft_boss_profiles.py','authoring_core.py','inspect_authored_assets.py','examples/boss_draft_profiles.json','examples/hero_target_source.json','emit_fields_manifest.py'):
    p=receipt.parent/name;rel=p.relative_to(ROOT).as_posix()
    rows=[s for s in receipt.read_text(encoding='utf-8').splitlines() if s.strip() and s.split()[-1].replace('\\','/')==rel]
    assert len(rows)==1,f'Receipt entry missing/ambiguous {name}'
    want=rows[0].split()[0].lower();actual=sha(p)
    assert len(want)==64 and actual==want,f'Toolkit receipt mismatch {name}; STOP'
    pins.append({'path':rel,'expected_sha256':want,'actual_sha256':actual})
subprocess.run([sys.executable,'-I',str(R/'capture_state.py'),'pre'],cwd=ROOT,check=True)
state=json.loads((R/'pre_state.json').read_text());assert len(state['content'])==11756 and sum('sha256' in x for x in state['content'])==20
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
assert not subprocess.check_output(['git','diff','--name-only','HEAD','--','Content','Config'],cwd=ROOT,text=True).strip(),'Tracked Content/Config drift'
reference=json.loads((R.parent/'SevarogInventory/run_reviewed/post_state.json').read_text())
for kind in ('content','config'):
    view=lambda rows:{x['path']:(x.get('size'),x.get('sha256')) for x in rows}
    assert view(state[kind])==view(reference[kind]),f'Accepted {kind} baseline drift; STOP'
assets=base['assets']
assert all(sha(ROOT/a['path'])==a['sha256'] for a in assets),'Saved3asset drift; STOP'
assert not (ROOT/'Content/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3.uasset').exists(),'V2 already exists; no overwrite'
v={'preparation_order':'C-364','release':release['message_id'],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'DD29_report_id':marker['message_id'],'receipt_sha256':sha(receipt),'pins':pins,'binary':base['binary'],'baseline_sha256':sha(baseline),'pre_state_sha256':sha(R/'pre_state.json'),'git_status_Content_Config_Source':status,'passed':True}
(R/'preflight_verified.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
print('DD27_V3_Save fresh219Source/DD27k432fbbinary/six receipt pins/content/process checks passed AFTER posted DD29 report')
