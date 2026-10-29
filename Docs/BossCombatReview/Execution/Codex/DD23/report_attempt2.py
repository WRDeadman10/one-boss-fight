"""C277 measured attempt2 report. Keeps attempt1 report/receipt immutable."""
from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent
root=here.parents[4]
run=here/'attempt2_2026-10-29'
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
r=json.loads((run/'final_verification.json').read_text(encoding='utf-8'))
assert r['source_unchanged'] and r['source_count']==206 and r['exe_unchanged'] and r['head_unchanged']
assert r['build_job']['exit_code']==0 and not r['build_errors'] and r['focused_look']['pass'] and r['full_dd23']['pass']
assert verify_receipt(here/'run_2026-10-29/evidence_sha256.txt',here/'run_2026-10-29',root)['all_verified']
assert verify_receipt(here/'Revision1/evidence_sha256.txt',here/'Revision1',root)['all_verified']
body='''# C277 DD23 ATTEMPT 2 run report — lead acceptance pending

ONE new serialized verification run, in separate attempt2_2026-10-29 folder. Fresh safety matched206 Revision1 Source hashes, new test pin64fc3399 and unchanged adapter/Binding/DD21/DD22 pins with explicit reviewed Binding replacements, dependencies/candidates/catalog, failed-attempt DLL f6eebc60, EXE5495fb88, HEAD79d55906. Immediate process check found no engine/build/compiler.

Attempt1 remains FAILED: build exit0, focused exit3 TArray assertion/two completions, no full/CookCoverage. Original23-file receipt55658b44... still verifies byte-for-byte. Original20-file source bundle preserved in Revision1/Original_DD23_Source; approved three-fixture source correction36-file receipta0aaf564... also still verifies. Successful attempt2 does not erase failure1.

'''
body+=f"BUILD attempt2 exit{r['build_job']['exit_code']}/{r['build_job']['seconds']}s, four incremental actions. One compiler-advisory Warning line; raw SHA256 {r['build_sha256']}. No UHT invocation/reflection lines in this incremental build (test-only change); UHT was actually invoked in attempt1, not re-claimed here. No forced clean/rebuild or extra engine action.\n\n"
for tag in ['focused_look','full_dd23']:
    g=r[tag]
    body+=f"{tag}: discovered{g['discovered']}; {g['completed']}completed/{g['unique']}unique Success, exit{g['job']['exit_code']}/{g['job']['seconds']}s; Warning{g['warning_severity_lines']}, Error{g['error_severity_lines']}; no assertion/failure/duplicate/fatal/ensure/unsupported; GIsCriticalError=0. Raw SHA256 {g['sha256']}.\n\n"
body+='Full ran only after focused gate passed. Exact153 prior DD22 paths retained plus six Look names, CookCoverage Success explicitly observed (full raw log:3241). That Source-literal scan includes the five native constructor Boss01 references repeated in Binding.h; their asset-file presence is pinned by DD23/native_default_assets.json. CookCoverage is content-discovery coverage, not runtime class/skeleton/socket/load/rendering or packaged proof. Warning multiset versus DD22: '+json.dumps(r['warning_delta_vs_DD22'])+'; 63vs63, normalizing only frame/timestamp prefix, epoch and sponsor PID. Embedded TraceServer error text retains Warning severity.\n\n'
body+='Final206 Source hashes unchanged; dependencies/candidates/catalog/HEAD unchanged; no engine/build/compiler process remains at capture. Current DLL '+r['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']+'; EXE unchanged '+r['binary']['Binaries/Win64/OneBossFight.exe']+'.\n\n'
body+='Scope remains isolated typed assignment/compiler-copy/reflection/rejection only. No Look component BeginPlay/Apply/SetEnabledForTest, mesh load, socket fit, runtime rendering, serialized/Details authoring, wiring/reservation/Ready/legacy suppression, PIE/duel/networking/package/all83 closure. KI-131 preserves these limits and the failed attempt. No further Source edit or engine retry performed during attempt2.\n\n'
body+='DD24 C275 staging: five draft source files including six UNRUN test sources are now under Codex/DD24/Staging only; no promotion/handoff/freeze until lead accepts DD23. No GameplayAbility/native BeginPlay/Tick call is in those draft tests. Staging preparation had an offline leftover synthetic-mount label assertion and a malformed diagnostic one-liner, corrected before a staged test file was written; neither ran C++/Unreal or touched Source. Test self-alias review remains part of DD24 freeze.\n\nPlease independently review attempt2 raw files and accept/return. No DD24 Source promotion or new engine operation inferred.\n'
report=here/'ATTEMPT2_REPORT_TO_CLAUDE.md'
report.write_text(body,encoding='utf-8')
summary='DD23 C277 ATTEMPT2 measured: build exit0 (incremental4actions, no UHT invocation), focusedLook6/full159 unique Success, exact prior153+6 and CookCoverage,206 Source unchanged,63warning multiset equal DD22. Attempt1 failed exit3 retained. ATTEMPT2_REPORT_TO_CLAUDE.md awaits independent lead acceptance; DD24 five drafts staging-only, no Source promotion.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
with (root/'Documentation/KNOWN_ISSUES.md').open('a',encoding='utf-8') as f:
    f.write('\n\nKI-131 C277 ATTEMPT2: corrected duplicate fixture passed focused6/full159, CookCoverage Success;206 Source unchanged, warning63 matches DD22. Attempt1 TArray self-alias assertion/exit3 and original evidence stay recorded. All source-only guard/runtime mesh/socket/serialized/activation/networking/package limits remain. Lead run acceptance pending.\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C277: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
rows=[(p,p.relative_to(run).as_posix()) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='evidence_sha256.txt']
for p in [report,here/'capture_safety_attempt2.py',here/'check_run_attempt2.py',here/'finish_capture_attempt2.py',here/'prepare_attempt2.py',here/'report_attempt2.py']:rows.append((p,'../'+p.name))
receipt=run/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+rel+'\n' for p,rel in rows),encoding='utf-8')
assert verify_receipt(receipt,run,root)['all_verified']
(here/'MESSAGE_ATTEMPT2_DELIVERY.txt').write_text(body+'\nAttempt2 receipt '+str(len(rows))+'files SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('Frozen attempt2',len(rows),digest(receipt))
