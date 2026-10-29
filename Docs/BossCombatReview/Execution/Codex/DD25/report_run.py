"""C286 measured report after successful serialized gates only."""
from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent
root=here.parents[4]
run=here/'run_2026-10-29'
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
r=json.loads((run/'final_verification.json').read_text(encoding='utf-8'))
assert r['source_unchanged'] and r['source_count']==212 and r['exe_unchanged'] and r['head_unchanged']
assert r['build_job']['exit_code']==0 and not r['build_errors'] and r['focused_death']['pass'] and r['full_dd25']['pass']
assert verify_receipt(here/'native_pins_sha256.txt',root,root)['all_verified']
assert verify_receipt(here/'evidence_sha256.txt',here,root)['all_verified']
body='''# DD25 C286 run report — independent lead acceptance pending

ONE serialized scoped build/focused/full sequence. Fresh212-source manifest, five DD25 pins plus DD21-DD24 pins (accepted Binding replacements explicitly recorded), native Death header/cpp pins, dependency/candidate/catalog pins matched. DD24 binary baseline, HEAD79d55906 and immediate empty engine/build/compiler process check passed. Nothing under Source changed during the run.

'''
body+=f"BUILD exit{r['build_job']['exit_code']}/{r['build_job']['seconds']}s; actual UHT invocation/reflection lines {r['uht_lines']}; {len(r['build_warnings'])}known Warning lines; raw SHA256 {r['build_sha256']}.\n\n"
for tag in ['focused_death','full_dd25']:
    g=r[tag]
    body+=f"{tag}: discovered{g['discovered']}; completed{g['completed']}/{g['unique']}unique Success; exit{g['job']['exit_code']}/{g['job']['seconds']}s; Warning{g['warning_severity_lines']}, Error{g['error_severity_lines']}; no failed/duplicate/fatal/ensure/assertion/unsupported completion, GIsCriticalError=0; raw SHA256 {g['sha256']}.\n\n"
body+='Full launched only after focused raw gate passed. Exact165 prior DD24 paths retained plus six Death names, no missing prior path. CookCoverage Success explicitly present: the source-literal scan includes the two AN_Boss01_DeathLegend/AM_Boss01_DeathLegend references repeated in Binding.h. It is content-discovery coverage, not load/class/skeleton/playback/pose/cooked-package proof. Warning multiset versus DD24: '+json.dumps(r['warning_delta_vs_DD24'])+';63vs63 under frame/timestamp prefix, epoch and sponsor-PID normalization only. Embedded TraceServer error text remains at Warning severity.\n\n'
body+='Final212 Source unchanged; native Death h/cpp pins unchanged; dependencies/candidates/catalog and HEAD unchanged. DLL '+r['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']+'; EXE unchanged '+r['binary']['Binaries/Win64/OneBossFight.exe']+'. No engine/build/compiler remains at post capture. Raw logs/jobs/commands/full manifests/source and binary pins are in run_2026-10-29.\n\n'
body+='No failed DD25 run, retry, silent fix, source/asset/git/native edit. Historical DD23 failed attempt remains preserved. Limits: isolated typed assignment/compiler copy/reflection/rejection only; no Death fixture BeginPlay/Tick/Attach/Preload, pack ability, remains, playback, pose or guard action, serialized/Details authoring, wiring/reservation/Ready/legacy suppression, PIE/duel/networking/package/all83 closure. Authored1e6/int ceilings and both-path rule are not native guards/tuning. Cumulative ClipRestartCount/external times/Age narrowing and KI-083 remain unresolved (KI-133).\n\n'
body+='DD26 C287: no staged/live code edits yet. Read-only stop(a)/(c) findings prepared: six positive fixture manifests need59 paths; ExpandedSubset explicitly encodes five-plan structure. Separate exact-source report follows this run report, before any wiring edit. No asset Fields were inspected using the engine, no broader engine release inferred.\n\nPlease independently review and accept/return this exact run.\n'
report=here/'RUN_REPORT_TO_CLAUDE.md'
report.write_text(body,encoding='utf-8')
summary='DD25 C286 measured: ONE editor build/UHT exit0, focusedDeath6/full171unique Success, exact165+6/CookCoverage,212Source unchanged,63warning multiset matches DD24. Codex/DD25/RUN_REPORT_TO_CLAUDE.md awaits independent lead acceptance. No native Death flow/activation proof. DD26 read-only stop(a)/(c) findings, no wiring code written.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
with (root/'Documentation/KNOWN_ISSUES.md').open('a',encoding='utf-8') as f:
    f.write('\n\nKI-133 C286 measured: focused6/full171 and CookCoverage passed,212Source unchanged; isolated typed assignment/copy/reflection/rejection only. Native Death state machine/ability/clip/ragdoll/pose/remains/KI-083, serialized authoring, wiring/Ready/networking/package remain unproven. C284 authored ceilings are not native guards; cumulative counters/external time/Age narrowing still residual. Lead run acceptance pending.\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C286: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
rows=[(p,p.relative_to(run).as_posix()) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='evidence_sha256.txt']
for p in [report,here/'capture_safety.py',here/'check_run.py',here/'finish_capture.py',here/'prepare_run.py',here/'report_run.py']:rows.append((p,'../'+p.name))
receipt=run/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+rel+'\n' for p,rel in rows),encoding='utf-8')
assert verify_receipt(receipt,run,root)['all_verified']
(here/'MESSAGE_RUN_DELIVERY.txt').write_text(body+'\nReceipt '+str(len(rows))+'files SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('Frozen DD25 run evidence',len(rows),digest(receipt))
