"""C283 report only after raw focused/full gates pass. No UE execution."""
from pathlib import Path
import json,sys
here=Path(__file__).resolve().parent
root=here.parents[4]
run=here/'run_2026-10-29'
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
r=json.loads((run/'final_verification.json').read_text(encoding='utf-8'))
assert r['source_unchanged'] and r['source_count']==209 and r['exe_unchanged'] and r['head_unchanged']
assert r['build_job']['exit_code']==0 and not r['build_errors'] and r['focused_closeclipswap']['pass'] and r['full_dd24']['pass']
assert verify_receipt(here/'evidence_sha256.txt',here,root)['all_verified']
body='''# DD24 C283 run report — independent lead acceptance pending

ONE serialized scoped verification. Fresh209-source manifest and DD24/DD21/DD22/DD23 pins matched (Binding replacements explicitly recorded as reviewed); dependency/candidate/catalog pins, DD23 attempt2 binaries, HEAD79d55906 verified. Immediate process check clear. No Source write or engine action beyond the released build/focused/full sequence.

'''
body+=f"BUILD exit{r['build_job']['exit_code']}/{r['build_job']['seconds']}s; UHT invocation/reflection actual lines:{r['uht_lines']}; Warning lines{len(r['build_warnings'])}; raw SHA256 {r['build_sha256']}.\n\n"
for tag in ['focused_closeclipswap','full_dd24']:
    g=r[tag]
    body+=f"{tag}: discovered{g['discovered']}, {g['completed']}completed/{g['unique']}unique Success; exit{g['job']['exit_code']}/{g['job']['seconds']}s; Warning{g['warning_severity_lines']}, Error{g['error_severity_lines']}; no failed/duplicate/assertion/fatal/ensure/unsupported result, GIsCriticalError=0; raw SHA256 {g['sha256']}.\n\n"
body+='Focused raw gate checked before full. Full exact159 prior DD23 paths plus six CloseClipSwap names, no missing prior path. CookCoverage Success explicitly observed; the three native constructor Boss01/Animations references repeated in Binding.h are included in that source-literal scan. This is content-discovery coverage, not class/skeleton/timing/load/playback or packaged proof. Warning multiset against DD23 attempt2: '+json.dumps(r['warning_delta_vs_DD23_attempt2'])+';63vs63, normalizing only frame/timestamp prefix, epoch and sponsor PID. Embedded TraceServer error text preserved at Warning severity.\n\n'
body+='Final209 Source unchanged, dependencies/candidates/catalog/HEAD unchanged, EXE unchanged. DLL '+r['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']+'; EXE '+r['binary']['Binaries/Win64/OneBossFight.exe']+'. No engine/build/compiler remains at post capture. Raw logs/jobs/commands/manifests/binary pins in run_2026-10-29.\n\n'
body+='No failed DD24 build/test attempt, retry, silent fix or Source change during run. DD23 attempt1 failure remains preserved; DD23 acceptance is separately bounded. DD24 evidence is isolated typed configuration/compiler copy/reflection/rejection only: no native BeginPlay/Tick/Preload, ability reflection, montage load/live swap, serialized/Details authoring, wiring/Ready/activation/PIE/duel/networking/package/all83 proof. KI-132 remains binding.\n\n'
body+='DD25 findings X-310 confirmed C284: restart limit amended to authored int32 range0..1000000, not native guard/tuning; cumulative counters/external Age narrowing remain separate residuals. Attach reuses Existing without Mode assignment; possible duplicate claim retracted. No runtime reproduction/native edit/Source promotion. DD25 staging follows amended C281/C284.\n\nPlease independently review actual raw evidence and accept/return. No further engine operation inferred.\n'
report=here/'RUN_REPORT_TO_CLAUDE.md'
report.write_text(body,encoding='utf-8')
summary='DD24 C283 measured: ONE editor build/UHT exit0, focusedCloseClipSwap6/full165 unique Success, exact159+6/CookCoverage,209 Source unchanged;63warning multiset equals DD23attempt2. Codex/DD24/RUN_REPORT_TO_CLAUDE.md independent lead acceptance pending. No live swap/activation proof. DD25 findings resolved C284; amended staging-only contract, no Source promotion.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
with (root/'Documentation/KNOWN_ISSUES.md').open('a',encoding='utf-8') as f:
    f.write('\n\nKI-132 C283 measured: focused6/full165 configuration tests and CookCoverage passed. Runtime ability/class/skeleton/montage/timing/4entries-3candidates mapping/swap, serialized/Details, full-bundle/Ready/activation/networking/package remain unproven. No native BeginPlay/Tick/Preload or runtime reflection invoked on the CloseClipSwap fixture. Lead run acceptance pending.\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C283: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
rows=[(p,p.relative_to(run).as_posix()) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='evidence_sha256.txt']
for p in [report,here/'capture_safety.py',here/'check_run.py',here/'finish_capture.py',here/'prepare_run.py',here/'report_run.py']:rows.append((p,'../'+p.name))
receipt=run/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+rel+'\n' for p,rel in rows),encoding='utf-8')
assert verify_receipt(receipt,run,root)['all_verified']
(here/'MESSAGE_RUN_DELIVERY.txt').write_text(body+'\nReceipt '+str(len(rows))+'files SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('Run evidence frozen:',len(rows),digest(receipt))
