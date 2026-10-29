from pathlib import Path
import hashlib,json,re,difflib
R=Path(__file__).resolve().parent;ROOT=R.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=('RPGBossHydrationPreparation.h','RPGBossHydrationPreparation.cpp','RPGBossActivationTests.cpp')
for name in names:
    p=R/name;p.write_bytes(p.read_text().replace('\n','\r\n').encode())
old=(R/'Preimages/RPGBossHydrationPreparation.cpp').read_text();new=(R/'RPGBossHydrationPreparation.cpp').read_text()
cut=new.index('\nnamespace\n{\n#if WITH_DEV_AUTOMATION_TESTS\n\tint32 GRegistrationFailAfter')
prefix=new[:cut]
start=prefix.index('\t// DD28: unregister only registrations owned')
end=prefix.index('\tbAborted = true;',start)
assert prefix[:start]+prefix[end:]==old,'Existing cpp changed outside allowed Abort addition'
old_h=(R/'Preimages/RPGBossHydrationPreparation.h').read_text();new_h=(R/'RPGBossHydrationPreparation.h').read_text()
diffs={}
for name in names[:2]:
    a=(R/'Preimages'/name).read_text();b=(R/name).read_text()
    changes=list(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (R/(name+'.diff')).write_text(''.join(changes))
    diffs[name]={'added':sum(s.startswith('+') and not s.startswith('+++') for s in changes),'removed':sum(s.startswith('-') and not s.startswith('---') for s in changes)}
assert all(c['removed']==0 for c in diffs.values()),'Non-additive accepted-file delta'
baseline=ROOT/'Docs/BossCombatReview/Execution/Codex/DD26/post_source_manifest_sha256.txt'
expected={s.split(' *',1)[1]:s.split(' *',1)[0] for s in baseline.read_text().splitlines() if ' *' in s}
live={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
assert expected==live and len(live)==212,'Live Source drift'
test=(R/names[2]).read_text()
test_names=re.findall(r'"(OneBossFight.Binding.Activation\.[^"]+)"',test)
assert len(set(test_names))==len(test_names)==6
assert 'Ordinal <= 24' in test and 'const TCHAR* Expected[]' in test
assert 'const_cast' not in test+new
mutations=[]
for filename in (names[1],names[2]):
    for line,s in enumerate((R/filename).read_text().splitlines(),1):
        if re.search(r'\.(Add(?:Unique)?|Emplace|Append|Insert|Reset|Sort)\(',s):mutations.append({'file':filename,'line':line,'text':s.strip()})
(R/'array_mutations.json').write_text(json.dumps(mutations,indent=2)+'\n')
audit='''# DD28 array mutations / arithmetic / limits

The machine-readable array_mutations.json enumerates every matching Add/AddUnique/Emplace/Append/Insert/Reset/Sort site in the staged implementation and test file, including inherited code. Manual review: no new Add takes a reference to an element of its destination. RegisteredThisCall.Add(Component) stores a local pointer as a weak handle; OutReport.Registered.Add(Info) copies a separate local value; Errors.Add uses literal/local strings; Errors.Append(Cleanup.Errors) uses two separate arrays. No mutation is performed while holding an element reference into the same destination array.

The test-local fixture is copied into a distinct ActivationTests namespace from the accepted preparation fixture: Plans.Add takes fresh factory values; Paths.AddUnique reads a different plan.RequiredFields array; Fields.Add takes a fresh MakeField return; config Phases.Add copies a local; Requests.Add takes fresh request values; snapshot Actors.Add takes fresh CaptureActor values; component snapshot arrays store external pointers and flags, then Sort before iteration. No repeated in-place element alias was introduced. Test assertions and independent Expected[] are read-only; the ordinal sweep re-prepares after destroying the prior artifact, never retains a raw destroyed component for name reuse.

No authored numeric field, arithmetic/timing policy or tuning is introduced. Loops use bounded TArray int32 counts, checked member/plan indexes and reverse count-minus-one cleanup; empty reverse loops start at -1 and do not execute. Test arithmetic is fixed two-boss/twelve-plan indexing within24 registrations. All24 post-registration fault ordinals1..24 are source-covered; no runtime execution yet. No synthetic failure is called an organically reproduced native failure.

Limits: no compile or UE test has run; these are source/static checks only. Registration does not decide BeginPlay chronology, ticking, bindings, reservations, Ready or legacy suppression. If an external actor/component lifecycle transition invalidates ownership or begins play, cleanup can report the existing contract violation rather than claim to reverse external gameplay. With batch-owned registration flag false the original Abort implementation body is byte-identical; the destructor is byte-identical. Existing accepted tests stay untouched.
'''
(R/'ARRAY_MUTATION_AND_LIMITS_AUDIT.md').write_text(audit)
design='''# DD28 staged registration — C313 / REVIEW PENDING

`FRPGPreparedBatch::RegisterOwnedComponents(FRPGRegistrationReport&)` encapsulates the private owned lease list. No production accessor, friend, const_cast or actor/name lookup. The game-thread check happens before UObject access; thread/state refusals return named errors and leave any earlier success intact. The whole batch (including target-only owner) is checked for valid, never-begun world/owners, exact component identities/classes/names/ownership and unregistered/not-begun state before registration. Each boss then registers in plan order, with checks immediately before and after every call. Report records actual order and member/plan/class failure coordinates.

On execution/prevalidation failure, this call's registered weak handles are unregistered in reverse, then existing Abort destroys the owned unregistered components; cleanup errors remain in the report. On success, a private bRegisteredByBatch flag is set. Abort checks that flag and unregisters its still-valid, still-owned, never-begun components in reverse before entering the historical cleanup. Externally registered components with flag false still take the original ContractViolation branch. If external changes have begun/reparented an owned component, existing contract-violation safety wins; no claim to undo external BeginPlay. IsRegistered reports the batch's successful transition, not a continuously monitored engine state.

Destructor unchanged: it already calls Abort on the game thread and reports off-thread destruction. Therefore successful registration is now cleaned by that EXISTING path; no new implicit abort operation was added. Plan/config/leasing/PrepareBatch/existing fault injection/dev accessor remain unchanged. Registration fault injection uses an independent dev-only FRegistrationFaultScope in RPGBossActivation; it fires after actual registration, no production knob/callback.

Six new UNRUN Activation suites: Success (24 ordered registrations/no component begun), NotGameThread, OwnerBegun (late member; zero registrations), StateRefusals (repeat/aborted), InjectedFaults (all1..24, reverse rollback+all managed classes absent), Lifetime (clean Abort, repeat, existing destructor). Existing preparation/world-preparation/registry/production-preparation tests are not edited. Expected total177 is only171+six source declarations, not an observed discovery/result.

Does not decide BeginPlay order, component ticking, binding, reservation, readiness or suppression. No live caller/startup hook. All files remain staged; source promotion and any build/run require Claude's acceptance and explicit release. DD27 diagnostics/corrections remain priority. Source212 remains DD26-pinned. Historical C311 stop is resolved by C313; PREWRITE_STOP_C311.md is preserved as the earlier finding, not the active scope.
'''
(R/'DESIGN_REVIEW_PENDING.md').write_text(design)
manifest={'release':'C-313','review':'PENDING','source_count':212,'source_matches_DD26':True,'diff_line_counts':diffs,'new_test_names':test_names,'tests_run':False,'mutation_sites':len(mutations),'files':[{'path':n,'size':(R/n).stat().st_size,'sha256':sha(R/n)} for n in names]}
(R/'staged_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'static_checks.json').write_text(json.dumps({'old_cpp_unchanged_except_abort_addition_and_new_function':True,'accepted_file_removed_lines':0,'live_source_212_unchanged':True,'unique_new_test_declarations':6,'is_UE_result':False},indent=2)+'\n')
message=f'''C313 DD28 STAGED SOURCE HANDOFF / REVIEW PENDING. Full preparation.h/.cpp staged copies plus NEW RPGBossActivationTests.cpp in Codex/DD28/Staging. Encapsulated RegisterOwnedComponents, private batch-owned flag/query, whole-batch never-begun checks, ordered registration, reverse rollback then Abort, and batch-owned Abort unregister path. No public pointer accessor/friend/name lookup or const_cast. Existing destructor/PrepareBatch/leases/old fault hook/dev accessor unchanged; external registration with flag false retains byte-identical historical Abort behaviour.
Six UNRUN suites: Success/NotGameThread/OwnerBegun/StateRefusals/InjectedFaults/Lifetime. All24 registration-fault ordinals; independent12-class order; managed-class cleanup across all3actors; clean/repeated/destructor Abort. Expected177 is not discovered/measured. Header delta+{diffs[names[0]]['added']}/-0; cpp+{diffs[names[1]]['added']}/-0. Exact diffs/preimages/full212Source manifest/pins/staged_manifest/static checks/design/array-mutation and arithmetic-limits audit supplied. Live Source212 matches DD26; no promotion/build/engine/git for DD28.
Please review staged accepted-file delta line by line. No BeginPlay/tick/binding/reservation/Ready/suppression/startup/runtime release implied. DD27 rerun failed and was reported X323; A213 softref probe/correction remains priority. KI-137 records DD28 staging/verification limits in KNOWN_ISSUES. Await your promotion and separately scoped verification release.'''
(R/'MESSAGE_DELIVERY.txt').write_text(message)
print(json.dumps(manifest))
