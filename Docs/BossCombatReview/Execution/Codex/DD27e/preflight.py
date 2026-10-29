from pathlib import Path
import hashlib,json,subprocess,sys,datetime
R=Path(__file__).resolve().parent;ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=ROOT/'Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/evidence_sha256.txt'
probe=receipt.parent/'probe_unreal_api.py'
rel=probe.relative_to(ROOT).as_posix()
rows=[s for s in receipt.read_text().splitlines() if s.split()[-1].replace('\\','/')==rel]
assert len(rows)==1,'Probe receipt entry missing or ambiguous'
expected=rows[0].split()[0].lower();actual=sha(probe)
assert len(expected)==64 and expected.startswith('5feae7df'),'Not the C317 probe revision; STOP'
assert actual==expected,'Probe receipt mismatch; STOP'
baseline_path=R.parent/'CURRENT_ENGINE_BASELINE.json';base=json.loads(baseline_path.read_text())
assert base['source_count']==213 and base['release']=='C-315 item6'
for item in ('source','binary'):
    assert sha(ROOT/base[item+'_manifest'])==base[item+'_manifest_sha256'],'DD28 baseline receipt drift'
for path,want in base['binary'].items():assert sha(ROOT/path)==want,'DD28 binary drift; STOP'
subprocess.run([sys.executable,'-I',str(R/'capture_state.py'),'pre'],cwd=ROOT,check=True)
pre=json.loads((R/'pre_state.json').read_text());assert len(pre['content'])==11752 and sum('sha256' in s for s in pre['content'])==16,'Content/Data inventory changed'
assert pre['head']==base['head']
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
content_config=subprocess.check_output(['git','status','--short','--','Content','Config'],cwd=ROOT,text=True)
assert not content_config.strip(),'Content/Config tracked drift; STOP'
data={'release':'C-317','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'probe_receipt_sha256':sha(receipt),'probe_expected_sha256':expected,'probe_actual_sha256':actual,'pre_state_sha256':sha(R/'pre_state.json'),'current_engine_baseline_sha256':sha(baseline_path),'binary':base['binary'],'git_status_Content_Config_Source':status,'passed':True}
(R/'preflight_verified.json').write_text(json.dumps(data,indent=2)+'\n')
print('PREFLIGHT VERIFIED: C317 receipt probe pin and DD28 Source213/binary baseline with fresh snapshots')
