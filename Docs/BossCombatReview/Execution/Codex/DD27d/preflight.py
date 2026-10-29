from pathlib import Path
import hashlib,json,subprocess,sys,datetime
R=Path(__file__).resolve().parent;ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=ROOT/'Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/evidence_sha256.txt'
names=('draft_boss_profiles.py','authoring_core.py','inspect_authored_assets.py','examples/boss_draft_profiles.json')
lines=receipt.read_text().splitlines(); pins=[]
for name in names:
    path=receipt.parent/name
    rel=path.relative_to(ROOT).as_posix()
    rows=[s for s in lines if s.split()[-1].replace('\\','/')==rel]
    assert len(rows)==1,f'Missing/ambiguous receipt entry: {name}'
    expected=rows[0].split()[0].lower();actual=sha(path)
    assert len(expected)==64 and actual==expected,f'Receipt mismatch: {name}; STOP'
    pins.append({'path':rel,'expected_sha256':expected,'actual_sha256':actual})
subprocess.run([sys.executable,'-I',str(R/'capture_state.py'),'pre'],cwd=ROOT,check=True)
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
assert not status.strip(),'Tracked Content/Config/Source dirty; STOP'
verified={'release':'C-312','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receipt_sha256':sha(receipt),'pins':pins,'pre_state_sha256':sha(R/'pre_state.json'),'git_status_Content_Config_Source':status,'passed':True}
(R/'preflight_verified.json').write_text(json.dumps(verified,indent=2)+'\n')
print('PREFLIGHT VERIFIED: all four current receipt pins and fresh pre-state')
