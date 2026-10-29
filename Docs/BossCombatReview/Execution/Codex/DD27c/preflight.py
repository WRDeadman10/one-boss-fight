from pathlib import Path
import hashlib,json,subprocess,sys,datetime
R=Path(__file__).resolve().parent
ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=ROOT/'Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/evidence_sha256.txt'
probe=receipt.parent/'probe_unreal_api.py'
rows=[s for s in receipt.read_text().splitlines() if s.split()[-1].replace('\\','/').endswith('/probe_unreal_api.py')]
assert len(rows)==1,'Probe receipt entry missing or ambiguous'
expected=rows[0].split()[0].lower()
assert len(expected)==64 and expected.startswith('c74c4835'),'Receipt is not the C307 probe revision; STOP'
actual=sha(probe)
assert actual==expected,f'Probe receipt mismatch: {actual} != {expected}; STOP'
subprocess.run([sys.executable,'-I',str(R/'capture_state.py'),'pre'],cwd=ROOT,check=True)
git_status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
assert not git_status.strip(),'Tracked Content/Config/Source dirty; STOP'
data={'release':'C-307','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'probe_receipt_sha256':sha(receipt),'probe_expected_sha256':expected,'probe_actual_sha256':actual,'pre_state_sha256':sha(R/'pre_state.json'),'git_status_Content_Config_Source':git_status,'passed':True}
(R/'preflight_verified.json').write_text(json.dumps(data,indent=2)+'\n')
print('PREFLIGHT VERIFIED; fresh snapshot captured and receipt pin matched')
