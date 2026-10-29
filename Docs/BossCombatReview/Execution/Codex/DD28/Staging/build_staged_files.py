"""C313 staging only. Never writes Source. One-use frozen preimages and additive delta."""
from pathlib import Path
import hashlib,difflib,json
R=Path(__file__).resolve().parent; ROOT=R.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=ROOT/'Docs/BossCombatReview/Execution/Codex/DD26/post_source_manifest_sha256.txt'
expected={s.split(' *',1)[1]:s.split(' *',1)[0] for s in baseline.read_text().splitlines() if ' *' in s}
actual={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
assert actual==expected and len(actual)==212,'Frozen Source drift; stop'
pre=R/'Preimages';pre.mkdir(exist_ok=False)
paths=['Source/OneBossFight/Player/RPGBossHydrationPreparation.h','Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp','Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp']
for rel in paths:(pre/Path(rel).name).write_bytes((ROOT/rel).read_bytes())
header=(ROOT/paths[0]).read_text();cpp=(ROOT/paths[1]).read_text()
new_header=header.replace('/** The owned, unregistered prepared subset.',(R/'registration_additions.h.txt').read_text()+'/** The owned, unregistered prepared subset.',1)
anchor='\tbool IsPrepared() const { return bPrepared && !bAborted; }'
assert new_header.count(anchor)==1
new_header=new_header.replace(anchor,anchor+'''\n\n\t/** DD28 additive step: game-thread only, never-begun owners/world only. No binding, Ready or suppression.\n\t *  Own registrations are undone by Abort (and thus by the existing destructor's Abort). External registrations retain the old contract-violation behaviour.\n\t *  Thread/state refusals do not touch an earlier success; execution/prevalidation failure unregisters this call in reverse, then Abort. */
\tbool RegisterOwnedComponents(FRPGRegistrationReport& OutReport);
\tbool IsRegistered() const { return bRegisteredByBatch; }''',1)
new_header=new_header.replace('\tbool bAborted = false;','\tbool bAborted = false;\n\tbool bRegisteredByBatch = false;',1)
abort_insert='''\t// DD28: unregister only registrations owned by a successful call of this batch.
\t// With this flag false, the historical Abort branch below is unchanged.
\tif (bRegisteredByBatch)
\t{
\t\tfor (int32 MemberIndex = Members.Num() - 1; MemberIndex >= 0; --MemberIndex)
\t\t{
\t\t\tAActor* Owner = Plan->Participants[MemberIndex].Actor.Get();
\t\t\tfor (int32 Index = Members[MemberIndex].Owned.Num() - 1; Index >= 0; --Index)
\t\t\t{
\t\t\t\tUActorComponent* Component = Members[MemberIndex].Owned[Index].Component.Get();
\t\t\t\tif (IsValid(Owner) && IsValid(Component) && !Component->IsBeingDestroyed()
\t\t\t\t\t&& Component->GetOwner() == Owner && !Component->HasBegunPlay() && Component->IsRegistered())
\t\t\t\t{
\t\t\t\t\tComponent->UnregisterComponent();
\t\t\t\t}
\t\t\t}
\t\t}
\t\tbRegisteredByBatch = false;
\t}
'''
assert cpp.count('\tbAborted = true;')==1
new_cpp=cpp.replace('\tbAborted = true;',abort_insert+'\tbAborted = true;',1)+(R/'registration_additions.cpp.txt').read_text()
for name,content,old in [('RPGBossHydrationPreparation.h',new_header,header),('RPGBossHydrationPreparation.cpp',new_cpp,cpp)]:
    (R/name).write_bytes(content.replace('\n','\r\n').encode())
    (R/(name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),content.splitlines(True),fromfile='a/'+name,tofile='b/'+name)))
test=(ROOT/paths[2]).read_text()
includes=test[:test.index('// These tests prove')]
helpers=test[test.index('namespace\n{'):test.index('\tstruct FExpectedComponent')].replace('PreparationTests','ActivationTests')
new_test=includes+'// DD28 staged tests: transient never-begun fixtures; synthetic config/epoch, no authored asset or gameplay proof.\n'+helpers+'}\n}\nusing namespace ActivationTests;\n'+(R/'activation_tests_body.cpp.txt').read_text()
(R/'RPGBossActivationTests.cpp').write_bytes(new_test.replace('\n','\r\n').encode())
manifest={'release':'C-313','source_count':212,'source_frozen':True,'new_test_names':__import__('re').findall(r'"(OneBossFight.Binding.Activation\.[^"]+)"',new_test),'files':[]}
assert len(manifest['new_test_names'])==6
for name in ('RPGBossHydrationPreparation.h','RPGBossHydrationPreparation.cpp','RPGBossActivationTests.cpp'):
    p=R/name;manifest['files'].append({'path':name,'size':p.stat().st_size,'sha256':sha(p)})
(R/'staged_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'source_full_manifest_sha256.txt').write_bytes(baseline.read_bytes())
print(json.dumps(manifest))
