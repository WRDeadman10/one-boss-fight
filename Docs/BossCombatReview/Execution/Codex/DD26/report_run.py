"""C291 measured report freeze only, after seven focused gates and full pass."""
from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent
root=here.parents[4]
run=here/'run_2026-10-29'
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
r=json.loads((run/'final_verification.json').read_text(encoding='utf-8'))
tags=['preflight','preparation','registry','production_preflight','production_preparation','world_input','world_preparation']
assert all(r[t]['pass'] for t in tags+['full_dd26'])
assert r['focused_disjoint'] and r['focused_union_exact'] and r['source_unchanged'] and r['source_count']==212 and r['exe_unchanged'] and r['head_unchanged']
assert verify_receipt(here/'evidence_sha256.txt',here,root)['all_verified']
body='''# DD26 C291 verification report — independent lead acceptance pending

ONE serialized released sequence: fresh212 Source hashes, nine DD26 pins and frozen DD19-DD25 adapter/Binding/native pins; dependency/candidate/catalog pins and DD25 binaries, HEAD79d55906 all verified. Historical source pins superseded only by exact accepted C291 manifest bytes, explicitly recorded; no other mismatch ignored. Immediate process check found no editor/UBT/compiler. Source stayed frozen throughout.

'''
body+=f"BUILD exit{r['build_job']['exit_code']}/{r['build_job']['seconds']}s; raw SHA256 {r['build_sha256']}. UHT actual lines:{r['uht_lines']}. This incremental15-action build did NOT invoke UHT/reflection; one known compiler-advisory Warning. No forced clean/rebuild or extra build was run to manufacture UHT output.\n\n"
body+='Focused gates below ran ONE AT A TIME in released order, and each raw gate passed before launching the next. Filters have a trailing dot: Preparation. cannot select PreparationRegistry. Every gate requires exact source-name membership, not only a count. The disjoint union is30 unique names, no duplicate or missed focused name; this is separate from the full171 run, not summed into it.\n'
for tag in tags:
    g=r[tag]
    body+=f"\n{tag}: discovered{g['discovered']}; {g['completed']}/{g['unique']}unique Success; exit{g['job']['exit_code']}/{g['job']['seconds']}s, Warning{g['warning_severity_lines']}/Error{g['error_severity_lines']}; SHA256 {g['sha256']}.\n"
    body+=''.join(' - '+p+'\n' for p in g['paths'])
g=r['full_dd26']
body+=f"\nFULL: discovered{g['discovered']}; {g['completed']}/{g['unique']}unique Success; exit{g['job']['exit_code']}/{g['job']['seconds']}s; Warning{g['warning_severity_lines']}/Error{g['error_severity_lines']}; raw SHA256 {g['sha256']}. Exact171 prior DD25 paths retained, NO new automation name, no missing/duplicate/failure, CookCoverage Success. All gates show GIsCriticalError=0, no assertion/fatal/ensure/unsupported failure. Full launched ONLY after all seven focused gates passed.\n\n"
body+='Warning multiset versus DD25: '+json.dumps(r['warning_delta_vs_DD25'])+'. Only frame/timestamp prefix, epoch and sponsor PID normalized. All warnings preserved; embedded TraceServer Error text retains Warning severity.\n\n'
body+='Final212 Source/frozen pins/dependencies/candidates/catalog/HEAD unchanged; DLL '+r['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']+'; EXE unchanged '+r['binary']['Binaries/Win64/OneBossFight.exe']+'. No engine/build/compiler remains at post capture. Raw logs, commands, jobs/exits/times, complete pre/post manifests/pin checks/binary hashes included.\n\n'
body+='No failed DD26 attempt, source fix, retry, asset/pack/git/history operation. Historical DD23 attempt1 remains failed/preserved. This proves the existing preflight/unregistered-preparation/cleanup/registry contract on TWELVE plans in transient isolated never-begun fixtures; PreexistingConsumer negative cases register disposable components, not an active prepared bundle. The six independent110path manifests and prefix/suffix/count expectations are now exercised. Fault injection is synthetic, not an organic configure-failure proof.\n\n'
body+='Does NOT prove active gameplay/startup entrypoint, prepared-component registration or BeginPlay order, legacy suppression in play, authored/serialized/Details definitions, legacy behaviour parity (e.g. first real definition must retain OwnClip death mode), playable boss, runtime mesh/socket/timing fit, duel/networking/PIE gate/package/performance/all83 closure. KI-134 and earlier provenance/residuals remain. No runtime activation order or authoring asset change inferred.\n\nPlease independently review/accept or return this exact run. No further engine/Source work is assumed without a scoped lead order.\n'
report=here/'RUN_REPORT_TO_CLAUDE.md'
report.write_text(body,encoding='utf-8')
summary='DD26 C291 measured: build exit0 (incremental15actions, no UHT invocation), seven focused gates9/6/3/2/3/3/4 allSuccess with disjoint30names, conditional full171uniqueSuccess exactprior171/CookCoverage.212Source unchanged,63warning multiset equals DD25. Codex/DD26/RUN_REPORT_TO_CLAUDE.md independent lead review pending. Twelve-plan transient contract only, no active gameplay/registration/BeginPlay/serialized-authoring/Ready/activation proof.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
with (root/'Documentation/KNOWN_ISSUES.md').open('a',encoding='utf-8') as f:
    f.write('\n\nKI-134 C291 measured: seven focused9/6/3/2/3/3/4 and full171/CookCoverage passed;212Source unchanged. This is isolated transient twelve-plan preflight/unregistered preparation/cleanup/registry evidence, not activation, registration/BeginPlay chronology, authored definition Fields provenance, legacy suppression/behaviour parity, networking/PIE/package/performance/all83 closure. Future authored definitions need110paths. Fault injections remain dev-only synthetic; existing alias/content-lease/epoch limits remain. Lead run acceptance pending.\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C291: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
rows=[(p,p.relative_to(run).as_posix()) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='evidence_sha256.txt']
for p in [report,here/'capture_safety.py',here/'check_run.py',here/'finish_capture.py',here/'prepare_run.py',here/'report_run.py']:rows.append((p,'../'+p.name))
receipt=run/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+rel+'\n' for p,rel in rows),encoding='utf-8')
assert verify_receipt(receipt,run,root)['all_verified']
(here/'MESSAGE_RUN_DELIVERY.txt').write_text(body+'\nRun receipt '+str(len(rows))+'files SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('Frozen DD26 measured evidence',len(rows),digest(receipt))
