"""C289 prewrite baseline capture. File-only; no engine or build."""
from pathlib import Path
import sys,re,json
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import verify_receipt
baseline=here.parent/'DD25/run_2026-10-29/final_source_manifest_sha256.txt'
assert verify_receipt(baseline,root,root)['all_verified']
scanfiles=['RPGBossHydrationPreparation.cpp','RPGBossWorldPreparation.cpp','RPGBossPreparationRegistry.cpp','RPGBossWorldInputCompiler.cpp','RPGBossHydrationPreflight.h']
pattern=r'\b(5|10|6|51)\b|Plans\s*\[\s*[0-4]\s*\]|ClassLeases\s*\[\s*[0-4]\s*\]'
hits=[]
for name in scanfiles:
    p=root/'Source/OneBossFight/Player'/name
    hits.extend(f'{name}:{i}:{s}' for i,s in enumerate(p.read_text(encoding='utf-8').splitlines(),1) if re.search(pattern,s))
assert not hits,hits
(here/'C289_PREWRITE_COUNT_SCAN.json').write_text(json.dumps({'pattern':pattern,'files':scanfiles,'hits':hits,'scope':'source-only widened count/index search'},indent=2),encoding='utf-8')
testnames=['RPGBossHydrationPreflightTests.cpp','RPGBossHydrationPreparationTests.cpp','RPGBossProductionPreflightTests.cpp','RPGBossProductionPreparationTests.cpp','RPGBossWorldPreparationTests.cpp','RPGBossWorldInputCompilerTests.cpp','RPGBossPreparationRegistryTests.cpp']
files=[root/'Source/OneBossFight/Player'/n for n in ['RPGBossHydrationPreflight.h','RPGBossHydrationPreflight.cpp']]+[root/'Source/OneBossFight/Tests'/n for n in testnames]
pre=here/'Preimages'
pre.mkdir(exist_ok=False)
for p in files:(pre/p.name).write_bytes(p.read_bytes())
(here/'pre_source_manifest_sha256.txt').write_bytes(baseline.read_bytes())
(here/'scope_files.json').write_text(json.dumps([p.relative_to(root).as_posix() for p in files],indent=2),encoding='utf-8')
refs=[]
for p in (root/'Source').rglob('*'):
    if p.suffix not in {'.h','.cpp'} or 'Tests' in p.parts:continue
    refs.extend(f'{p.relative_to(root).as_posix()}:{i}:{s}' for i,s in enumerate(p.read_text(encoding='utf-8').splitlines(),1) if re.search(r'CompilePreflight\(|PrepareBatch\(|TryPrepareAndReserve\(',s))
(here/'non_test_pipeline_references.txt').write_text('\n'.join(refs)+'\n',encoding='utf-8')
print('C289 widened check zero hits;9 preimages and212-source baseline saved. No Source written.')
