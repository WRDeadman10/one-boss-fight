from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parent;ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=(R/'editor_raw.log').read_text(encoding='utf-8',errors='replace');lines=raw.splitlines()
tags=[s for s in lines if '[DRAFT_APPLY]' in s]
(R/'draft_apply_lines.txt').write_text('\n'.join(tags)+'\n',encoding='utf-8')
start=next(i for i,s in enumerate(lines) if '[DIAGNOSTIC SUMMARY]' in s)
end=next(i for i in range(start+1,len(lines)) if '[DRAFT_APPLY] FATAL' in lines[i])
table=lines[start:end+1]
(R/'diagnostic_summary_verbatim.txt').write_text('\n'.join(table)+'\n',encoding='utf-8')
details_start=next(i for i,s in enumerate(lines) if '[DIAGNOSTIC SUMMARY DETAILS (UNTRUNCATED)]' in s)
details=lines[details_start:end+1]
(R/'failure_details_verbatim.txt').write_text('\n'.join(details)+'\n',encoding='utf-8')
errors=[s for s in lines if re.search(r'\b\w+: Error:',s)];warnings=[s for s in lines if re.search(r'\b\w+: Warning:',s)]
(R/'error_lines.txt').write_text('\n'.join(errors)+'\n',encoding='utf-8');(R/'warning_lines.txt').write_text('\n'.join(warnings)+'\n',encoding='utf-8')
first=next(i for i,s in enumerate(lines) if '[DRAFT_APPLY]' in s)
(R/'all_draft_apply_blocks.txt').write_text('\n'.join(lines[first:end+1])+'\n',encoding='utf-8')
pre=json.loads((R/'pre_state.json').read_text());post=json.loads((R/'post_state.json').read_text());diff=json.loads((R/'state_diff.json').read_text());job=json.loads((R/'job_record.json').read_text(encoding='utf-8-sig'));v=json.loads((R/'preflight_verified.json').read_text(encoding='utf-8'))
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
assert status==v['git_status_Content_Config_Source'],'Tracked status drift'
(R/'post_git_status_Content_Config_Source.txt').write_text(status,encoding='utf-8')
saved=[]
for rel in diff['saved']['added']+diff['saved']['changed']:
    p=ROOT/rel;saved.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
(R/'saved_findings_sha256.json').write_text(json.dumps(saved,indent=2)+'\n',encoding='utf-8')
outside={k:x for k,x in diff.items() if k!='saved' and any(x.values())}
failures=[s for s in tags if '[DRAFT_APPLY][FAILURE]' in s]
fields=[s for s in tags if 'fields rows read back:' in s]
draft_counts=[s for s in tags if 'properties set,' in s]
assert len(failures)==9 and any('SystemExit: 1' in s for s in errors)
result={'release':'C-320','verdict':'FAILED; 9 collected authoring failures; stop/no fix/no retry','editor_exit':job['exit_code'],'helper_exit':'SystemExit: 1','failure_records':len(failures),'error_severity':len(errors),'warning_severity':len(warnings),'fields_readback_lines':fields,'per_draft_counts':draft_counts,'outside_saved_drift':outside,'source_count':len(post['source']),'processes_before':pre['processes'],'processes_after':post['processes'],'DD29_report_posted_before_run':v['DD29_report_id']}
(R/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
report=f'''# C320 DD27f in-memory authoring — FAILED, stop/no fix/no retry

DD29 verification was completed/reported as {v['DD29_report_id']} BEFORE this launch; fresh preflight verified four actual toolkit receipt entries, DD29final216Source/DLL4e3580fd/EXE, HEADbc3fe6a, Content11752 path+size/Data16hashes, Config/status/process snapshots. C321 ENGINE_LOCK acquired exclusively and recorded, no existing lock bypass. Exact command/arguments in command.json/run_once.ps1: draft_boss_profiles.py --input-json examples/boss_draft_profiles.json --apply, same headless flags -unattended -nullrhi -nosound -nosplash. No --save or additional helper flag. ONE launch, no toolkit/profile/Source fix, retry, build, test, asset save or cleanup.

Editor process exit={job['exit_code']}, elapsed={job['seconds']:.3f}s, helper SystemExit:1;9failures. Raw editor SHA256 `{sha(R/'editor_raw.log')}`. Error severity={len(errors)}; Warning severity={len(warnings)}. No complete-draft SUCCESS. Three in-memory creation attempts each report19properties set/3failed. Exact per-draft and Fields witnesses below. EmberWarden now has a DIRECT110of110readback witness, distinct from overall authoring success (which failed).

## All tagged DRAFT_APPLY lines (full continuation text is also preserved in all_draft_apply_blocks.txt)
```
{chr(10).join(tags)}
```

## Full untruncated failure details, including multiline exception continuations
```
{chr(10).join(details)}
```

Observed failures per draft: fireball.fireball_ability TypeError (Name cannot convert to SoftClassProperty); phase_dependencies.immunity_effect and stagger_profile.immunity_effect RuntimeError (the generated-class path does not exist or did not load through the chosen API). Source RPGEncounterBinding.h:92,106,128 declares ALL THREE as TSoftClassPtr<UObject>. This establishes a soft-CLASS distinction in the remaining failures; it does not prove whether the immunity API's existence check or load failed. The package file's disk presence was already verified in the offline count artifact, so do not call that proof the class object is loadable, or call the package absent. Collector actual_type=NoneType/actual_repr=None is what the failure record stores, not a fresh readback of the rejected property's default. No guessed correction applied.

## Every Error-severity line
```
{chr(10).join(errors)}
```

Post-state: zero captured drift outside Saved={outside}; Source216 exact DD29 final, toolkit/input and binaries unchanged; HEADbc3fe6a, tracked Content/Config/Source status same (existing accepted uncommitted Source changes retained). Content11752paths/sizes and Data16hashes unchanged,Config hashes unchanged; no new .uasset/.umap under Content. These are the required minimum inventory/hash checks; other Content bytes were not all hashed. Saved1newCrashReportClient ini+3changed files pinned/preserved; no cleanup. No engine/compiler after. C321 own lock is released only after evidence freeze/STOP; lock record retained in the bundle.

Limits: attempted in-memory creation and partial readback only. No asset saved, full valid authored definition, CompileParticipant/preflight/preparation/registration/Ready/startup/gameplay/PIE/package claim. All prior failed runs and DD27b missing-pre-state finding remain. C320 path-count reconciliation is in the DD29 report:27actualassetpaths+1previewdirectory, all package files present, multiple differences versus A214's table. Await exact lead correction and fresh release. Idle, ready for engine lane after this failure report; no further engine task inferred.
'''
(R/'RUN_REPORT_TO_CLAUDE.md').write_text(report,encoding='utf-8')
message=f'''C320 DD27f FAILED; STOP, no fix/retry. DD29 report X328 preceded the ONE authoring launch. Fresh four receipt pins + DD29 Source216/DLL4e3580fd/EXE/HEAD and snapshots verified; C321 exclusive engine lock held. Editor exit{job['exit_code']}, helper SystemExit1 with9collected failures; {len(errors)}Error-severity/{len(warnings)}Warning-severity lines. Raw SHA256 {sha(R/'editor_raw.log')}.
Each of3in-memory drafts:19properties set,3failed. Failures per draft: fireball.fireball_ability rejects Name as SoftClassProperty; phase_dependencies.immunity_effect and stagger_profile.immunity_effect report generated-class path does not exist or did not load. Native Binding.h:92/106/128 are ALL TSoftClassPtr<UObject>. Full nine untruncated records incl multiline exceptions in Codex/DD27f/failure_details_verbatim.txt and RUN_REPORT_TO_CLAUDE.md. Do not infer immunity package absent: disk package existed; the selected API failed class-object conversion/existence/load.
DIRECT Fields readback now logged: EmberWarden110of110; other drafts0of0. No overall SUCCESS, no saved asset/compiled definition/preflight/gameplay claim. Content11752path+size/Data16hashes, Config,216Source,toolkit/input/binaries/status unchanged; Saved1new+3changed pinned/preserved; post-process empty. All raw logs/job/command/manifest/pins/receipt preserved, own lock removed after freeze. No toolkit/profile/Source edit or cleanup. Await bounded correction/release. Idle, ready for engine lane.'''
(R/'MESSAGE_DELIVERY.txt').write_text(message,encoding='utf-8')
entry='\n\nDD27f C320 FAILED 2026-10-29: one in-memory authoring launch after DD29 reportX328, exclusiveC321lock/fresh216Source-DD29binary/fourreceipt preflight. Editor exit0/helperSystemExit1;9failures (3perdraft: Name->FireballAbility SoftClassProperty and immunity-effect generated-class existence/load failures). DIRECT EmberWarden Fields110of110 readback; per-draft19properties set/3failed, no complete success. Full untruncated errors in Docs/BossCombatReview/Execution/Codex/DD27f/RUN_REPORT_TO_CLAUDE.md. Captured Content/Config/Source/toolkit/binaries unchanged,Saved effects pinned. No save/fix/retry/cleanup. Await lead correction; KI135 unresolved authoring path now specifically includes soft-CLASS handling.\n'
for name in ('TASKS.md','DECISIONS.md','TEST_PLAN.md','KNOWN_ISSUES.md'):
    with (ROOT/'Documentation'/name).open('a',encoding='utf-8') as f:f.write(entry)
with (R.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:f.write(entry)
exclude={'receipt_sha256.txt','MESSAGE_DELIVERY.txt'}
(R/'receipt_sha256.txt').write_text(''.join(f'{sha(p)} *{p.name}\n' for p in sorted(R.iterdir()) if p.is_file() and p.name not in exclude),encoding='utf-8')
print(json.dumps(result))
print('receipt_sha256='+sha(R/'receipt_sha256.txt'))
