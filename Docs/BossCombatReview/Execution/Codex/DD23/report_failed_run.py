"""Preserve C275 failure. No fix, retry or Source write."""
from pathlib import Path
import sys,json,subprocess,re
here=Path(__file__).resolve().parent
root=here.parents[4]
run=here/'run_2026-10-29'
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt,parse_job_record
manifest=verify_receipt(here/'post_source_manifest_sha256.txt',root,root)
assert manifest['all_verified'] and manifest['entries']==206
pins=verify_receipt(here/'live_pins_sha256.txt',root,root)
assert pins['all_verified']
pre=json.loads((run/'pre_safety.json').read_text(encoding='utf-8'))
dep={}
for name in ['pre_pins.txt','dependency_pins_after_c245_followup_sha256.txt','candidate_assets_sha256.txt','default_catalog_assets_sha256.txt']:
    c=verify_receipt(root/'Docs/BossCombatReview/Execution/Claude/DD18'/name,root,root)
    # Only previously reviewed Binding replacements may differ from historical receipts.
    for row in c['checks']:
        key=Path(row['path']).as_posix()
        if row['status']=='mismatch' and key in {'Source/OneBossFight/Player/RPGEncounterBinding.h','Source/OneBossFight/Player/RPGEncounterBinding.cpp'}:
            accepted=next(x for x in pins['checks'] if Path(x['path']).as_posix()==key)
            assert row['actual_sha256']==accepted['actual_sha256']
            row['status']='C275_reviewed_DD23_Binding'
    c['all_verified']=all(x['status'] in {'verified','C275_reviewed_DD23_Binding'} for x in c['checks'])
    assert c['all_verified']
    dep[name]=c
head=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
assert head==pre['head']
binary={n:digest(root/n) for n in ['Binaries/Win64/UnrealEditor-OneBossFight.dll','Binaries/Win64/OneBossFight.exe']}
(run/'final_source_manifest_sha256.txt').write_bytes((here/'post_source_manifest_sha256.txt').read_bytes())
(run/'final_binary_sha256.txt').write_text(''.join(v+' *'+k+'\n' for k,v in binary.items()),encoding='utf-8')
build=(run/'build_dd23.log').read_text(encoding='utf-8')
focus=(run/'automation_focused_look.log').read_text(encoding='utf-8')
r={'status':'FAILED focused run, STOPPED without fix/retry/full suite','source':manifest,'five_pins':pins,'dependencies':dep,'head':head,'binary':binary,
   'build_job':parse_job_record(run/'build_dd23_job_record.txt',root),'focused_job':parse_job_record(run/'automation_focused_look_job_record.txt',root),
   'build_sha256':digest(run/'build_dd23.log'),'focused_sha256':digest(run/'automation_focused_look.log'),
   'uht_lines':[s for s in build.splitlines() if 'UnrealHeaderTool' in s or 'Reflection code generated' in s],
   'build_warnings':[s for s in build.splitlines() if re.search(r'^\s*Warning:|\bwarning C\d+',s,re.I)],
   'focused_gate':json.loads((run/'focused_look_gate.json').read_text(encoding='utf-8')),
   'assertion_lines':[s for s in focus.splitlines() if 'Assertion failed:' in s or 'already comes from the container' in s or 'RPGBossLookAdaptersTests.cpp:' in s],
   'full_suite_run':False,'no_source_fix':True,'dd24':'four staged files only, no tests yet, no promotion/handoff'}
(run/'failure_verification.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
body='''# C275 DD23 verification FAILED — STOPPED, no fix or retry

Fresh safety passed:206 Source files matched accepted DD23 manifest, DD23/DD21/DD22 pins with explicitly accepted Binding replacements, dependencies/candidates/catalog, DD22 binary baseline, HEAD79d55906 and no engine/build process. ONE editor Development build/UHT succeeded. No Source changed during this run.

Focused OneBossFight.Binding.Look discovered6, but engine crashed during Compile after ONLY Assign and Authoring completed Success. Engine/job exit3; outer command tool reported nonzero1. Completed2, not a passing focused suite.23 Error-severity lines,14 Warning lines; assertion/critical error and StaticShutdownAfterError present; no clean GIsCriticalError=0 completion. Full suite NOT RUN, CookCoverage NOT RUN. No warning-multiset comparison/full159 result exists for this binary.

Cause confirmed by raw callstack and source: RPGBossLookAdaptersTests.cpp:165 constructs the duplicate-piece negative fixture with R.Pieces.Add(R.Pieces[0]). UE TArray::CheckAddress (Array.h:1661) rejects an Add argument referencing an element in the same array, even before this fixture reaches ValidateLook. Callstack points to BadCases lambda at:165 from CompileTest:398. This is my regression-fixture bug, not a demonstrated production-adapter failure. The same self-alias pattern also exists in unexecuted validation-order cases at:290 and:292.

Proposed bounded correction, NOT applied: at all THREE fixture sites copy the selected TSoftObjectPtr<USkeletalMesh> into a local value first, then Add that independent local. Preserve identical duplicate identity and indexed Duplicate expectations/order. Update generator correspondingly, preserve original failed source bytes and this attempt. No validator/domain/default/control change. Please review/release exact source-only correction before any build/retry; this report does not assume retry authority.

DD24: four staged files (adapter.h/.cpp plus Binding.h/.cpp drafts) prepared ONLY under Codex/DD24/Staging while focused run was in progress. No staged tests yet, no live Source promotion or handoff. Staging paused on this failure; no DD24 source completion/acceptance claim.

Post-failure206 Source manifest/five pins/dependencies/HEAD unchanged, no engine/build/compiler process remains at capture. Current DLL is the DD23-built binary, NOT the last accepted DD22 binary; prior153 driver/automation acceptance is not inherited. No fix, retry, other engine action, asset edit, git or history write. Failed raw logs, jobs and commands preserved in Codex/DD23/run_2026-10-29.

'''
body+=f"BUILD exit{r['build_job']['exit_code']}/{r['build_job']['seconds']}s; UHT {r['uht_lines']}; {len(r['build_warnings'])} known Warning lines; raw SHA256 {r['build_sha256']}.\n\n"
body+=f"FOCUSED exit{r['focused_job']['exit_code']}/{r['focused_job']['seconds']}s; raw SHA256 {r['focused_sha256']}.\n\n"
body+='Current binaries: '+json.dumps(binary)+'.\n'
(here/'RUN_REPORT_TO_CLAUDE.md').write_text(body,encoding='utf-8')
summary='DD23 C275 failed attempt (2026-10-29): ONE build/UHT exit0; focusedLook exit3 assertion in duplicate negative fixture self-alias TArray::Add at test:165,2completed/6discovered. Full/CookCoverage NOT RUN. Source206 unchanged, no fix/retry. Codex/DD23/RUN_REPORT_TO_CLAUDE.md; await exact lead correction/retry order. DD24 four files staged only, paused.'
for name in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/name).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
with (root/'Documentation/KNOWN_ISSUES.md').open('a',encoding='utf-8') as f:
    f.write('\n\nKI-131 C275 FAILED ATTEMPT: Look Compile regression fixture Add(R.Pieces[0]) at Tests/RPGBossLookAdaptersTests.cpp:165 triggers TArray CheckAddress assertion Array.h:1661; same unexecuted pattern:290/:292. Engine exit3 after2completed/6discovered; no full or CookCoverage result. No production failure inferred; no fix or retry applied, exact lead delta required. Failure evidence Codex/DD23/run_2026-10-29.\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER STOP C275: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
rows=[(p,p.relative_to(run).as_posix()) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='evidence_sha256.txt']
for name in ['RUN_REPORT_TO_CLAUDE.md','capture_safety.py','check_run.py','finish_capture.py','prepare_run.py','report_failed_run.py']:
    rows.append((here/name,'../'+name))
receipt=run/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+n+'\n' for p,n in rows),encoding='utf-8')
assert verify_receipt(receipt,run,root)['all_verified']
(here/'MESSAGE_RUN_DELIVERY.txt').write_text(body+'\nReceipt Codex/DD23/run_2026-10-29/evidence_sha256.txt: '+str(len(rows))+' files; SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('Failure frozen:',len(rows),digest(receipt));print('binaries',binary)
