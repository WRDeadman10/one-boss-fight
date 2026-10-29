"""C285 source-only promotion, following amended C281/C284 contract."""
from pathlib import Path
import sys,re,json,subprocess
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import verify_receipt
baseline=here.parent/'DD24/run_2026-10-29/final_source_manifest_sha256.txt'
assert verify_receipt(baseline,root,root)['all_verified']
assert verify_receipt(here/'binding_base_sha256.txt',root,root)['all_verified']
(here/'pre_source_manifest_sha256.txt').write_bytes(baseline.read_bytes())
(here/'Preimages').mkdir(exist_ok=False)
for n in ['RPGEncounterBinding.h','RPGEncounterBinding.cpp']:(here/'Preimages'/n).write_bytes((root/'Source/OneBossFight/Player'/n).read_bytes())
stage=here/'Staging'
test=stage/'RPGBossDeathAdaptersTests.cpp'
inventory=[f'{i}:{s}' for i,s in enumerate(test.read_text(encoding='utf-8').splitlines(),1) if re.search(r'\.(?:Add|AddUnique|Insert|Append|Emplace|SetNum)\w*\(',s)]
(here/'array_mutation_inventory.txt').write_text('\n'.join(inventory)+'\n',encoding='utf-8')
(here/'ARRAY_MUTATION_AUDIT.md').write_text('''# DD25 source-only collection-mutation review

Every Add/AddUnique/Insert/Append/Emplace/SetNum site is listed in array_mutation_inventory.txt.
Owned Result.Add(C) reads the distinct owner component collection.
Cases.Add constructs new FBad records with no reference to Cases or its elements.
The two malformed-path Cases.Add sites capture a copied external FSoftObjectPath and assign scalar soft references, not a container element.
Definition D->Fields.Add(Field) copies a distinct stack FRPGParityField.
Seven Valid.Add(R) sites copy separate scoped stack records before iteration begins. Neither the validator/configure loop nor callbacks mutate Valid.
FRuntime Counters is initializer-built from getter return values and never appended to.
There is no Insert/Append/Emplace/SetNum, Add(R.Array[index]), Add(array reference local), MoveTemp(array element), or self-array source argument in the test source. No runtime/UE proof is claimed by this manual provenance audit.
''',encoding='utf-8')
assert not re.search(r'\b(\w+)\.(?:Add|AddUnique|Insert|Append|Emplace)\(\1\[',test.read_text(encoding='utf-8'))
for p in sorted(stage.iterdir()):
    target=root/'Source/OneBossFight'/('Tests' if p.name.endswith('Tests.cpp') else 'Player')/p.name
    if p.name.startswith('RPGBossDeathAdapters'):assert not target.exists()
    data=p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
    p.write_bytes(data)
    target.write_bytes(data)
s=(here.parent/'DD24/prepare_source.py').read_text(encoding='utf-8').replace('DD24','DD25').replace('CloseClipSwap','Death').replace('len(baseline)==206 and len(current)==209','len(baseline)==209 and len(current)==212').replace('"baseline":206,"current":209','"baseline":209,"current":212').replace('"old_files_unchanged":204','"old_files_unchanged":207')
(here/'prepare_source.py').write_text(s,encoding='utf-8')
r=subprocess.run([sys.executable,str(here/'prepare_source.py')],cwd=root,capture_output=True,text=True)
(here/'source_capture_output.txt').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
assert r.returncode==0,r.stdout+r.stderr
(here/'STAGING_STATUS.md').write_text('C285: five staged files promoted source-only against accepted DD24 Binding.212Source/207prior unchanged; six tests UNRUN, actual diff/freeze follows. No build/UE/native edit.\n',encoding='utf-8')
print('C285 promoted five-file source package;212 Source,207 prior unchanged; all tests UNRUN.')
