"""C276 approved three-fixture correction only. No engine/build/retry."""
from pathlib import Path
import sys,json,difflib,re,shutil
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,parse_receipt,verify_receipt
rev=here/'Revision1'
rev.mkdir(exist_ok=False)
original=rev/'Original_DD23_Source'
original.mkdir()
old_receipt=here/'evidence_sha256.txt'
assert verify_receipt(old_receipt,here,root)['all_verified']
for row in parse_receipt(old_receipt.read_text(encoding='utf-8')):
    src=here/row['relative_path']
    dst=original/row['relative_path']
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(src.read_bytes())
(original/'evidence_sha256.txt').write_bytes(old_receipt.read_bytes())
assert verify_receipt(original/'evidence_sha256.txt',original,root)['all_verified']
baseline=here/'post_source_manifest_sha256.txt'
assert verify_receipt(baseline,root,root)['all_verified']
test=root/'Source/OneBossFight/Tests/RPGBossLookAdaptersTests.cpp'
gen=here/'generate_tests.py'
(rev/'Preimages').mkdir()
for p in [test,gen]:(rev/'Preimages'/p.name).write_bytes(p.read_bytes())
replacements=[
('[](FRPGLookConfig& R) { R.Pieces.Add(R.Pieces[0]); }','[](FRPGLookConfig& R) { const TSoftObjectPtr<USkeletalMesh> Duplicate = R.Pieces[0]; R.Pieces.Add(Duplicate); }'),
('R = RecordA(); R.Pieces[0].Reset(); R.Pieces.Add(R.Pieces[1]); R.Sword.Reset();','R = RecordA(); R.Pieces[0].Reset();\n\tconst TSoftObjectPtr<USkeletalMesh> LaterDuplicate = R.Pieces[1];\n\tR.Pieces.Add(LaterDuplicate); R.Sword.Reset();'),
('R = RecordA(); R.Pieces.Add(R.Pieces[0]); R.Sword.Reset();','R = RecordA();\n\tconst TSoftObjectPtr<USkeletalMesh> FirstDuplicate = R.Pieces[0];\n\tR.Pieces.Add(FirstDuplicate); R.Sword.Reset();')]
for p in [test,gen]:
    s=p.read_text(encoding='utf-8')
    for before,after in replacements:
        assert s.count(before)==1,(p,before)
        s=s.replace(before,after)
    p.write_bytes(s.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
current={p.relative_to(root).as_posix():digest(p) for p in (root/'Source').rglob('*') if p.is_file()}
prior={r['relative_path']:r['expected_sha256'] for r in parse_receipt(baseline.read_text(encoding='utf-8'))}
changed=[k for k in prior if prior[k]!=current[k]]
assert len(current)==206 and current.keys()==prior.keys() and changed==[test.relative_to(root).as_posix()]
(rev/'pre_source_manifest_sha256.txt').write_bytes(baseline.read_bytes())
(rev/'post_source_manifest_sha256.txt').write_text(''.join(v+' *'+k+'\n' for k,v in sorted(current.items())),encoding='utf-8')
(rev/'Review').mkdir()
(rev/'Review'/test.name).write_bytes(test.read_bytes())
before=(rev/'Preimages'/test.name).read_text(encoding='utf-8').splitlines(keepends=True)
after=test.read_text(encoding='utf-8').splitlines(keepends=True)
(rev/'one_file.diff').write_text(''.join(difflib.unified_diff(before,after,fromfile=changed[0],tofile=changed[0])),encoding='utf-8')
(rev/'generator.diff').write_text(''.join(difflib.unified_diff((rev/'Preimages'/gen.name).read_text(encoding='utf-8').splitlines(keepends=True),gen.read_text(encoding='utf-8').splitlines(keepends=True),fromfile=gen.name,tofile=gen.name)),encoding='utf-8')
sourcepins=parse_receipt((here/'live_pins_sha256.txt').read_text(encoding='utf-8'))
for row in sourcepins:
    p=root/row['relative_path']
    if p!=test:assert digest(p)==row['expected_sha256']
(rev/'live_pins_sha256.txt').write_text(''.join(digest(root/r['relative_path'])+' *'+r['relative_path']+'\n' for r in sourcepins),encoding='utf-8')
assert not re.search(r'Pieces\.(?:Add|Insert|Append|Emplace|SetNum)\(R\.Pieces',test.read_text(encoding='utf-8'))
# Save exhaustive lexical inventory for the requested manual mutation review.
inventory=[]
for p in [test,*sorted((here.parent/'DD24/Staging').glob('*'))]:
    if not p.is_file():continue
    for line,s in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
        if re.search(r'\.(?:Add|Insert|Append|Emplace|SetNum)\w*\(',s):inventory.append(f'{p.relative_to(root).as_posix()}:{line}:{s}')
(rev/'array_mutation_inventory.txt').write_text('\n'.join(inventory)+'\n',encoding='utf-8')
audit='''# C276 array mutation audit (read-only; no engine test)

Look test original sites165/290/292 were the only direct same-array source-element arguments. All three now use independent local TSoftObjectPtr values; Duplicate expectation/identity/index/order unchanged. No references or MoveTemp of array elements retained.

Other Look test sites: Owned Result.Add(C) reads owner component set, not Result. Cases.Add builds new FBad values; Path lambdas capture a copied external FSoftObjectPath. Original164 adds a newly constructed empty soft pointer. Original166 constructs Mesh(MakePath(...)) independently, despite the identity intentionally comparing equal. Original190 constructs Mesh(Path) from a by-value captured external Path. Definition Fields.Add copies a local FRPGParityField. Valid.Add copies local Empty and LongSocket records from outside Valid. Original317 changes an element by assignment;318 adds a newly constructed soft pointer, not an element reference. No other Insert/Append/Emplace/SetNum in Look tests. These conclusions trace value provenance, not just the spelling of the call.

DD24 staging currently has FOUR files and NO test file yet, so no DD24 test audit is claimed. Adapter has no collection insertion. Binding draft inherited collection mutations checked: PhaseIds.Add(Phase.PhaseId), Fields.Add(F.FieldPath), Manifest.Add(Field.FieldPath) read different source arrays; Slots.Add(B.Slot), Actors.Add(Actor), Classes.Add(Plan.Class), Names.Add(Plan.InstanceName) read external record/local values; Value->Animations.Emplace(Animation) reads definition leases; Pending.Add(MoveTemp(Record)) moves a separate local, Records.Append(MoveTemp(Pending)) moves a distinct container; ClassLeases.Emplace(Plan.Class), Pending.Emplace(Component) use external plan/local component; Errors.Add(Message) is inherited result diagnostic flow and callers supply separate diagnostic expressions, not Errors elements. No staged new same-array self-alias found. DD24 tests must receive the same review when actually written, before freezing.

Only the Look tests Source file changed; four adapter/Binding pins unchanged. Generator updated at corresponding three sites. Preserved original20-file source bundle and original receipt, failed source preimage, failed run23-file receipt/logs all retained. No retry/Source promotion/engine/build/asset/git action.
'''
(rev/'ARRAY_MUTATION_AUDIT.md').write_text(audit,encoding='utf-8')
result={'scope':'C276 source-only correction, NOT compilation/UE test','source_count':206,'changed':changed,'unchanged':205,'tests_sha256':digest(test),'four_other_pins_unchanged':True,'original_source_receipt_sha256':digest(original/'evidence_sha256.txt'),'failed_run_receipt_sha256':digest(here/'run_2026-10-29/evidence_sha256.txt')}
(rev/'source_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
