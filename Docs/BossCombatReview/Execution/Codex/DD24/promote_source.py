"""C281 promotion SOURCE ONLY, no build/UHT/engine/git operation."""
from pathlib import Path
import sys,json,re,subprocess
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
stage=here/'Staging'
baseline=here.parent/'DD23/attempt2_2026-10-29/final_source_manifest_sha256.txt'
assert verify_receipt(baseline,root,root)['all_verified']
assert verify_receipt(here/'binding_base_sha256.txt',root,root)['all_verified']
(here/'pre_source_manifest_sha256.txt').write_bytes(baseline.read_bytes())
(here/'Preimages').mkdir(exist_ok=True)
for n in ['RPGEncounterBinding.h','RPGEncounterBinding.cpp']:
    (here/'Preimages'/n).write_bytes((root/'Source/OneBossFight/Player'/n).read_bytes())
# Mutation audit inventory before promotion; no collection argument is an element
# of the destination. Repeated montage test copies between scalar fields only.
test=stage/'RPGBossCloseClipSwapAdaptersTests.cpp'
mutations=[f'{i}:{s}' for i,s in enumerate(test.read_text(encoding='utf-8').splitlines(),1) if re.search(r'\.(?:Add|AddUnique|Insert|Append|Emplace|SetNum)\w*\(',s)]
(here/'array_mutation_inventory.txt').write_text('\n'.join(mutations)+'\n',encoding='utf-8')
assert len(mutations)==19,len(mutations)
(here/'ARRAY_MUTATION_AUDIT.md').write_text('''# DD24 C281 test collection mutation review

Exhaustive Add/AddUnique/Insert/Append/Emplace/SetNum scan:19 call sites (array_mutation_inventory.txt).
Owned Result.Add(C): C comes from owner component set, not Result.
Cases.Add at148-160:13 newly constructed FBad records, lambdas capture no Cases/array element reference.
Cases.Add at178-180:3 new FBad records; each captures a by-value copied external FSoftObjectPath, then assigns a scalar montage field. No container mutation in those lambdas.
Definition D->Fields.Add(Field) at202: Field is an independent stack record, not from D->Fields.
Valid.Add(Repeated) at261: Repeated is a separate stack config. The three equal montage pointers are scalar fields, not array elements; sharing the asset identity is intentionally legal.
No Insert/Append/Emplace/SetNum or same-array source-element argument exists in this test file. No Add(R.Array[index]) or reference local or MoveTemp array element. No changed fixture can reproduce the DD23 self-alias operation.
This is source reasoning, not a compiler/Unreal test. Native components are never begun/ticked/applied; plain begun owner receives component afterwards.
''',encoding='utf-8')
for p in stage.iterdir():
    assert p.is_file()
    target=root/'Source/OneBossFight'/('Tests' if p.name.endswith('Tests.cpp') else 'Player')/p.name
    if p.name.startswith('RPGBossCloseClipSwap'):assert not target.exists()
    target.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
s=(here.parent/'DD23/prepare_source.py').read_text(encoding='utf-8').replace('DD23','DD24').replace('Look','CloseClipSwap').replace('len(baseline)==203 and len(current)==206','len(baseline)==206 and len(current)==209').replace('"baseline":203,"current":206','"baseline":206,"current":209').replace('"old_files_unchanged":201','"old_files_unchanged":204')
(here/'prepare_source.py').write_text(s,encoding='utf-8')
r=subprocess.run([sys.executable,str(here/'prepare_source.py')],cwd=root,capture_output=True,text=True)
(here/'source_capture_output.txt').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
assert r.returncode==0,r.stdout+r.stderr
print('C281 source promotion complete:209 Source files,204 old unchanged. No build or Unreal operation.')
