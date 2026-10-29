"""Write measured C268 report only after all serialized gates passed."""
from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent
root=here.parents[4]
run=here/'run_2026-10-29'
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
r=json.loads((run/'final_verification.json').read_text(encoding='utf-8'))
assert r['source_unchanged'] and r['source_count']==203 and r['exe_unchanged'] and r['head_unchanged']
assert r['build_job']['exit_code']==0 and not r['build_errors']
for tag in ['focused_shockwave','focused_healpunish','full_dd21_dd22']:assert r[tag]['pass']
assert r['uht_lines']
text='''# DD21+DD22 C268 combined run report — lead acceptance pending

ONE serialized released run: fresh203-source manifest, DD21+DD22 pins (shared Binding superseded only by accepted DD22 bytes), dependency/candidate/catalog pins, DD20 binaries and HEAD verified before build. Immediate process check found no editor/UBT/compiler. No source mutation, failed attempt, retry, silent fix or additional engine action.

'''
text+=f"BUILD: exit{r['build_job']['exit_code']}/{r['build_job']['seconds']}s, editor Development. Actual UHT invocation/reflection lines preserved: {r['uht_lines']}. Build Warning lines:{len(r['build_warnings'])}; raw SHA256 {r['build_sha256']}.\n\n"
for tag in ['focused_shockwave','focused_healpunish','full_dd21_dd22']:
    g=r[tag]
    text+=f"{tag}: actual discovered{g['discovered']}, completed{g['completed']}, unique{g['unique']} Success, exit{g['job']['exit_code']}/{g['job']['seconds']}s; Warning{g['warning_severity_lines']}, Error{g['error_severity_lines']}; no duplicate/failure/fatal/ensure/unsupported; GIsCriticalError=0. Raw SHA256 {g['sha256']}.\n\n"
text+='Each focused raw gate passed before the next launch. Full membership is exact DD20 prior141 plus twelve Shockwave/HealPunish names; CookCoverage Success. No missing prior name. Warning multiset versus DD20 (normalizing only frame/timestamp prefix, epoch and sponsor PID): '+json.dumps(r['warning_delta_vs_DD20'])+'. Embedded TraceServer error text remains Warning severity; historical warnings/failures/provenance limits preserved.\n\n'
text+='FINAL:203 Source hashes unchanged, dependency/candidate/catalog pins and HEAD unchanged. DLL '+r['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']+'; EXE unchanged '+r['binary']['Binaries/Win64/OneBossFight.exe']+'. HEAD '+r['head']+'. Full raw commands/jobs/logs/pre/post manifests/pins included in run_2026-10-29.\n\n'
text+='Limits: isolated typed assignment/configuration/compiler copy/reflection/rejection only. No actual Shockwave or HealPunish event/tracker/projectile/hit/damage, serialized/Details authoring, gameplay activation, wiring/reservation/Ready/legacy suppression, networking/PIE/driver gate/package/all83 closure. Authored ceilings/relations are not native guards. Shockwave MoveId is syntactic only; HealPunish native A5 and player drink montage hardcodes plus socket/bone resolution remain UNRESOLVED.\n\n'
text+='Documentation uses next free IDs KI-128 (DD19/DD20 arithmetic residual), KI-129 (DD21 limits), KI-130 (DD22 limits); existing toolkit KI-126/127 preserved. DD19 threshold intermediate overflow caps to finite final threshold; external buildup/attribute/geometry risks remain. DD22 arithmetic audit explicitly does not assume world coordinates are bounded by profile ranges; external geometry/time/narrowing/NaN remain qualified. DD21 native unrestricted DeltaTime is unguarded. ComponentBegunPlay guards remain source-only.\n\nPlease independently review this run. No DD23 source started and no additional release inferred.\n'
(here/'RUN_REPORT_TO_CLAUDE.md').write_text(text,encoding='utf-8')
summary='DD21+DD22 measured C268 (2026-10-29): one build/UHT exit0, focused Shockwave6 then HealPunish6, conditional full153 unique Success with exact prior141+12/CookCoverage,203 Source unchanged. RUN_REPORT_TO_CLAUDE.md awaits independent lead acceptance. No DD23 source or further engine operation released.'
for name in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/name).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
ki=root/'Documentation/KNOWN_ISSUES.md'
old=ki.read_text(encoding='utf-8')
assert all(('KI-'+str(i)) not in old for i in [128,129,130]),'KI ID collision: stop report finalization'
with ki.open('a',encoding='utf-8') as f:
    f.write('''

| KI-128 | Arithmetic residual, C266/C268 | DD19 threshold-growth intermediate may overflow before Min returns finite cap; buildup accumulation and double-to-float health narrowing remain external-input risks. DD20 bounded profile angles do not bound external Distance+PlayerRadius or feet/ground subtraction. Accepted source unchanged; read-only audit Codex/DD21/BLEED_LOWSWEEP_READONLY_ARITHMETIC_AUDIT.md. | Open residual; no lasting nonfinite threshold claimed |
| KI-129 | DD21 measured limits | C268 focused6/full153 isolated configuration passed; no native wave/tick/tracker/hit/damage/serialized authoring proof. MoveId syntactic only. Authored1e6 ceiling is not native unrestricted DeltaTime/nonfinite-world guard. ComponentBegunPlay source-only; unwired. Raw evidence Codex/DD22/run_2026-10-29. | Open; lead run acceptance pending |
| KI-130 | DD22 measured limits | C268 focused6/full153 isolated configuration passed; no native heal/projectile/damage proof. A5/drink montage hardcoded, socket identities syntactic. World-coordinate/arena bounds are external assumptions, not profile validation; FeetZ earlier double-to-float narrowing can overflow, arbitrary external NaN/time/geometry not guarded. Audit Codex/DD22/NATIVE_ARITHMETIC_AUDIT.md. ComponentBegunPlay source-only; unwired; no serialized/Details/full bundle/activation/networking/package proof. | Open; lead run acceptance pending |
''')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C268: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
# Freeze run evidence including the report; no self-reference or message body.
rows=[(p,p.relative_to(run).as_posix()) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='evidence_sha256.txt']
rows.append((here/'RUN_REPORT_TO_CLAUDE.md','../RUN_REPORT_TO_CLAUDE.md'))
for name in ['capture_safety.py','check_run.py','finish_capture.py','prepare_run.py','report_run.py']:
    rows.append((here/name,'../'+name))
receipt=run/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+rel+'\n' for p,rel in rows),encoding='utf-8')
verify_receipt(receipt,run,root)
body=text+'\nEvidence receipt: Codex/DD22/run_2026-10-29/evidence_sha256.txt; '+str(len(rows))+' files; SHA256 '+digest(receipt)+'.\n'
(here/'MESSAGE_RUN_DELIVERY.txt').write_text(body,encoding='utf-8')
print('Run report and measured docs completed; receipt',len(rows),digest(receipt))
