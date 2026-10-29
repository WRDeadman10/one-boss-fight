from pathlib import Path
import hashlib,json,subprocess,sys,datetime
R=Path(__file__).resolve().parent;ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
release_path=R/'release_to_run.json'
assert release_path.exists(),'C333 preparation only: explicit owner save approval AND Claude DD27i release REQUIRED; STOP'
release=json.loads(release_path.read_text(encoding='utf-8'))
assert release['task']=='DD27i' and release['mode']=='--apply --save' and release['operator']=='Codex','Wrong release scope'
approval_path=R/'owner_approval.json'
assert approval_path.exists(),'Owner explicit SAVE approval absent; STOP'
approval=json.loads(approval_path.read_text(encoding='utf-8'))
assert approval['approved'] is True and approval['scope']=='three new draft assets only' and approval['evidence_path'] and approval['quote'],'Owner approval evidence required'
evidence=ROOT/approval['evidence_path']
assert evidence.is_file() and sha(evidence)==approval['evidence_sha256'],'Owner approval evidence missing/drift'
assert approval['quote'] in evidence.read_text(encoding='utf-8',errors='replace'),'Owner approval quote absent'
expected_new=json.loads((R/'expected_new_content.json').read_text())
assert len(expected_new)==3 and all(not (ROOT/p).exists() for p in expected_new),'Existing output package; STOP'
posted=R.parent/'DD29/run_2026-10-29/report_posted.json'
marker=json.loads(posted.read_text(encoding='utf-8-sig'))
mail=(ROOT/'Documentation/TEAM_MAILBOX.md').read_text(encoding='utf-8',errors='replace')
assert marker['release']=='C-319' and '### ['+marker['message_id']+']' in mail,'DD29 report must be posted BEFORE DD27i'
assert '### ['+release['message_id']+'] Claude ->' in mail,'Run-release header absent'
baseline=R.parent/'CURRENT_ENGINE_BASELINE.json';base=json.loads(baseline.read_text(encoding='utf-8'))
assert base['source_count']==216 and base['release']=='C-319 item6','Wrong engine baseline'
for kind in ('source','binary'):assert sha(ROOT/base[kind+'_manifest'])==base[kind+'_manifest_sha256'],'DD29 baseline manifest drift'
for rel,want in base['binary'].items():assert sha(ROOT/rel)==want,'DD29 binary drift; STOP'
receipt=ROOT/'Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/evidence_sha256.txt'
pins=[]
for name in ('draft_boss_profiles.py','authoring_core.py','inspect_authored_assets.py','examples/boss_draft_profiles.json'):
    p=receipt.parent/name;rel=p.relative_to(ROOT).as_posix()
    rows=[s for s in receipt.read_text(encoding='utf-8').splitlines() if s.split()[-1].replace('\\','/')==rel]
    assert len(rows)==1,f'Receipt entry missing/ambiguous {name}'
    want=rows[0].split()[0].lower();actual=sha(p)
    assert len(want)==64 and actual==want,f'Toolkit receipt mismatch {name}; STOP'
    pins.append({'path':rel,'expected_sha256':want,'actual_sha256':actual})
subprocess.run([sys.executable,'-I',str(R/'capture_state.py'),'pre'],cwd=ROOT,check=True)
state=json.loads((R/'pre_state.json').read_text());assert len(state['content'])==11752 and sum('sha256' in x for x in state['content'])==16
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
assert not subprocess.check_output(['git','status','--short','--','Content','Config'],cwd=ROOT,text=True).strip(),'Tracked Content/Config drift'
v={'preparation_order':'C-333','release':release['message_id'],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'DD29_report_id':marker['message_id'],'receipt_sha256':sha(receipt),'pins':pins,'binary':base['binary'],'baseline_sha256':sha(baseline),'pre_state_sha256':sha(R/'pre_state.json'),'git_status_Content_Config_Source':status,'passed':True}
(R/'preflight_verified.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
print('DD27i fresh216Source/DD29binary/four receipt pins/content/process checks passed AFTER posted DD29 report')
