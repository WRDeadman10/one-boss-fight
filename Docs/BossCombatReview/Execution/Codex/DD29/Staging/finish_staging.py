"""C316 offline staging; no Source/engine operation."""
from pathlib import Path
import hashlib,json,re,os
R=Path(__file__).resolve().parent;ROOT=R.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=ROOT/'Docs/BossCombatReview/Execution/Codex/DD28/run_2026-10-29/final_source_manifest_sha256.txt'
expected={s.split(' *',1)[1]:s.split(' *',1)[0] for s in base.read_text().splitlines() if ' *' in s}
current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
assert current==expected and len(current)==213,'Frozen DD28 Source drift; STOP'
refs=['Player/RPGBossWorldPreparation.h','Player/RPGBossWorldPreparation.cpp','Player/RPGBossPreparationRegistry.h','Player/RPGBossPreparationRegistry.cpp','Player/RPGBossHydrationPreparation.h','Player/RPGBossHydrationPreparation.cpp','Player/RPGBossWorldInputCompiler.h','Player/RPGBossWorldInputCompiler.cpp','Tests/RPGBossWorldPreparationTests.cpp']
pre=R/'ReferencePreimages';pre.mkdir(exist_ok=False)
for rel in refs:(pre/Path(rel).name).write_bytes((ROOT/'Source/OneBossFight'/rel).read_bytes())
original=(ROOT/'Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp').read_text()
includes=original[:original.index('// DD18 part C')]
fixture=original[original.index('namespace\n{'):original.index('\tTArray<TWeakObjectPtr<UActorComponent>> WeakOwned')]
fixture=fixture.replace('WorldPreparationTests','ActivationWorldTests')
# Remove unused legacy StaticFindObject helper (and its const_cast); retain NoConsumers and snapshot helpers.
a=fixture.index('\t\t/** No object, not even a destroyed one, carries a planned')
b=fixture.index('\t\tbool NoConsumers()',a)
fixture=fixture[:a]+fixture[b:]
test=includes+'#include "Player/RPGBossActivation.h"\n\n// C316 new staged tests; fixture setup copied from accepted WorldPreparation tests, not modified in Source.\n'+fixture+'}\n}\nusing namespace ActivationWorldTests;\n'+(R/'activation_world_tests_body.cpp.txt').read_text()
names=('RPGBossActivation.h','RPGBossActivation.cpp','RPGBossActivationWorldTests.cpp')
(R/names[2]).write_text(test)
for name in names:
    p=R/name;p.write_bytes(p.read_text().replace('\n','\r\n').encode())
prod=(R/names[0]).read_text()+(R/names[1]).read_text()
assert len(re.findall(r'PrepareWorldBatch\(',prod))==1
assert 'const_cast' not in prod+test and 'TryPrepareAndReserve(' not in prod
assert not re.search(r'(?:NewObject|LoadObject|LoadClass|BindEncounter|RegisterComponent|BeginPlay)\s*[<(]',prod)
test_names=re.findall(r'"(OneBossFight\.Binding\.ActivationWorld\.[^"]+)"',test)
assert len(test_names)==len(set(test_names))==5
mutations=[]
for name in names[1:]:
    for number,line in enumerate((R/name).read_text().splitlines(),1):
        if re.search(r'\.(Add(?:Unique)?|Emplace|Append|Insert|Reset|Sort)\(',line):mutations.append({'file':name,'line':number,'text':line.strip()})
(R/'array_mutations.json').write_text(json.dumps(mutations,indent=2)+'\n')
design='''# DD29 world registration composition — C316 / REVIEW PENDING

ActivateWorld(World, Binding, Selections, ManifestHash) calls accepted PrepareWorldBatch then accepted RegisterOwnedComponents. The facade acquires the authoritative epoch/catalog through the world GI; no caller epoch/config is injected and no validator is reimplemented. Chosen over TryPrepareAndReserve because the facade returns a unique batch while the frozen registry stores its batch privately and exposes only release tokens. No accepted API edit is needed. The returned move-only artifact retains the plan/config/content/class leases; it is NOT a registry reservation, global exclusion or a new catalog epoch authority.

Activated denotes registered native subset only. The caller owns a TUniquePtr batch; Release reports the accepted Abort result and resets it after non-refused cleanup. A worker-thread Release refuses and retains ownership for game-thread release. The existing batch destructor provides scope-exit cleanup. Moving the result transfers its only artifact; Outcome is historical while IsHeld reflects the current batch handle. Thread misuse is HardError before UObject work. Ordinary preparation/registration rejection with clean cleanup returns FallBackToLegacy, nested named diagnostics intact and no owned artifact. Registered-prefix failure uses the accepted reverse rollback+Abort, then a defensive idempotent Abort and resets the local artifact. Inherited cleanup/ownership contract violations are HardError, never a falsely clean legacy fallback. Earlier independent artifacts are not touched.

The caller must keep world, actors, binding, definitions and content authority stable through the synchronous call, as required by the accepted stages; arbitrary external mutations are not reversible. The code does not claim to repair invalid external lifecycle changes or guarantee the state of the entire engine. One new log-category Display line per ActivateWorld outcome carries the stage reason; original detailed diagnostics stay in Errors. Does not choose a definition, bind a participant, reserve an encounter, decide BeginPlay/tick order, publish Ready, suppress the legacy bundle, hook a subsystem or edit/load/save assets directly.

Five NEW UNRUN suites reuse a copied real-GI WorldPreparation fixture in a distinct namespace: SuccessAndRelease (24 registered/never begun, epoch lease, clean explicit/repeat/destructor release and move); InvalidInputAndMisuse (invalid manifest fallback, worker misuse hard error); ContentEpochRejection (test-local GI temporarily detached to exercise WorldInput.NoContent, then restored by fixture, no cvar/epoch injection); PreparationFailure (existing dev-only fault after allocation1); RegistrationFailure (existing registration dev-only fault after1/12/13/24 actual registrations). Snapshots compare actor component sets/registration/begun flags/meshes and context bound/ready counts. The fixture loads existing pack assets and uses transient definitions, not authored saved data. No organically reproduced native failure is claimed. Full count182 (177+five) is only an expectation.

No Source change/promotion/build/engine test is released by this delivery. Three files stay in Staging; all213 current Source hashes match DD28. DD27f authoring remains higher priority and requires its own release. Review the hard-error classification and artifact-lease choice before promotion.
'''
(R/'DESIGN_REVIEW_PENDING.md').write_text(design)
audit='''# Array mutations and numeric limits — source review only

array_mutations.json lists every matching mutation site. Production Result.Errors.Add stores new literals; Errors.Append(Cleanup.Errors) reads a separate array; Batch.Reset destroys only an independently owned artifact. MoveTemp transfers between distinct result objects. No container mutation takes a reference to an element of that same container. Diagnostic classifier lambdas are read-only.

Copied test fixture mutation sites: literal required-path arrays, fresh FRPGParityField / phase / binding rows built as local values, Selections.Add of separate aggregate values, snapshot component pointers/flags and Actors.Add of fresh CaptureActor results. Sort occurs before read-only snapshot iteration. Original unused StaticFindObject/const_cast helper was omitted. New registration failure loop uses independent fresh results and scoped hooks at fixed ordinals1/12/13/24; it does not retain raw destroyed component pointers across retries. The test's GI detach/restore is a local missing-content control, not production catalog mutation. Source tests have not run.

No new authored numeric domain, tuning, damage/timer arithmetic or limits are introduced. Counts come from accepted stages; fixed test counts24/two bosses/twelve plans and selected ordinals are fixture bounds only. Array snapshots and expected counts are not runtime gameplay, lease exclusivity, complete world-state or performance proof. No runtime result or compilation is claimed by these static checks.
'''
(R/'ARRAY_MUTATION_AND_LIMITS_AUDIT.md').write_text(audit)
(R/'source_full_manifest_sha256.txt').write_bytes(base.read_bytes())
(R/'reference_pins_sha256.txt').write_text(''.join(f'{sha(ROOT/"Source/OneBossFight"/rel)} *Source/OneBossFight/{rel}\n' for rel in refs))
manifest={'release':'C-316','review':'PENDING','source_frozen_count':213,'accepted_source_edits':0,'new_test_names':test_names,'tests_run':False,'files':[{'path':name,'size':(R/name).stat().st_size,'sha256':sha(R/name)} for name in names]}
(R/'staged_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'static_checks.json').write_text(json.dumps({'source_213_DD28_equal':True,'new_production_api_edits_required':False,'accepted_facade_call_count':1,'new_tests':5,'no_direct_registration_or_asset_operation_in_wrapper':True,'no_UE_execution':True,'mutation_sites':len(mutations)},indent=2)+'\n')
message='''C316 DD29 STAGED SOURCE HANDOFF / REVIEW PENDING: NEW RPGBossActivation.h/.cpp + Tests/RPGBossActivationWorldTests.cpp under Codex/DD29/Staging only. ActivateWorld composes accepted PrepareWorldBatch -> RegisterOwnedComponents; the caller owns the move-only batch artifact and its plan/config/content/class leases. Chosen facade over registry because registry hides the artifact behind release-only tokens. No reservation/global-uniqueness claim, no accepted API or Source edit.
Ordinary clean stage failure returns FallBackToLegacy with stage reason and original nested diagnostics; registration failure uses accepted reverse rollback/Abort plus defensive idempotent cleanup, no artifact held. Worker-thread or inherited cleanup-contract misuse is HardError, not falsely clean fallback. Explicit/repeat/destructor release is delegated to accepted batch Abort. One Display log per outcome. Activated means registered subset only, no gameplay activation.
Five UNRUN suites: SuccessAndRelease/InvalidInputAndMisuse/ContentEpochRejection/PreparationFailure/RegistrationFailure. Real-GI fixture copied into distinct namespace; missing-GI control restores fixture-owned change; failures injected after real allocation1 and registration1/12/13/24; actor/component/mesh/context snapshots and lease transfer/release checked in source. Expected182 is not measured. No new callbacks/cvars/assets/startup/binding/Ready/suppression. No Source/promotion/build/engine/git changes for DD29.
Full files, one-page DESIGN_REVIEW_PENDING.md, static checks, reference preimages/pins, full213Source manifest, staged_manifest.json and array/limits audit supplied. KI138 records staged scope/limits. Please review the artifact-lease choice and hard-error distinction, then release promotion/test only after the DD27-family priority work. DD27e was delivered X326; awaiting your exact further engine release.'''
(R/'MESSAGE_DELIVERY.txt').write_text(message)
print(json.dumps(manifest))
