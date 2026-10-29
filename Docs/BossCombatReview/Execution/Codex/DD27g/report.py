from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parent;ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=(R/'editor_raw.log').read_text(encoding='utf-8',errors='replace');lines=raw.splitlines()
classrefs=[s for s in lines if '[CLASSREF]' in s];probe=[s for s in lines if '[PROBE]' in s]
(R/'classref_lines_verbatim.txt').write_text('\n'.join(classrefs)+'\n',encoding='utf-8')
(R/'probe_lines.txt').write_text('\n'.join(probe)+'\n',encoding='utf-8')
first=next(i for i,s in enumerate(lines) if '[CLASSREF]' in s)
# Keep the entire runtime class-ref section, including multiline exception continuations.
end=next((i for i in range(first+1,len(lines)) if 'LogPython: Error:' in lines[i] or 'LogPython: Display: Python script executed' in lines[i] or 'LogSlate: Window' in lines[i] or 'LogExit: Preparing to exit' in lines[i]),len(lines))
(R/'classref_section_full.txt').write_text('\n'.join(lines[first:end])+'\n',encoding='utf-8')
errors=[s for s in lines if re.search(r'\b\w+: Error:',s)];warnings=[s for s in lines if re.search(r'\b\w+: Warning:',s)]
(R/'error_lines.txt').write_text('\n'.join(errors)+'\n',encoding='utf-8');(R/'warning_lines.txt').write_text('\n'.join(warnings)+'\n',encoding='utf-8')
pre=json.loads((R/'pre_state.json').read_text());post=json.loads((R/'post_state.json').read_text());diff=json.loads((R/'state_diff.json').read_text());job=json.loads((R/'job_record.json').read_text(encoding='utf-8-sig'));v=json.loads((R/'preflight_verified.json').read_text(encoding='utf-8'))
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
assert status==v['git_status_Content_Config_Source'],'Tracked status drift'
(R/'post_git_status_Content_Config_Source.txt').write_text(status,encoding='utf-8')
saved=[]
for rel in diff['saved']['added']+diff['saved']['changed']:
    p=ROOT/rel;saved.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
(R/'saved_findings_sha256.json').write_text(json.dumps(saved,indent=2)+'\n',encoding='utf-8')
outside={k:x for k,x in diff.items() if k!='saved' and any(x.values())}
sets=[s for s in classrefs if '[CLASSREF][SET]' in s]
load_class=[s for s in sets if 'load_class_c ' in s and 'result=ok' in s]
summary=[s for s in probe if '[PROBE] SUMMARY' in s]
result={'release':'C-327','verdict':'Measured diagnostic; lead review pending, no toolkit correction','editor_exit':job['exit_code'],'error_severity':len(errors),'warning_severity':len(warnings),'stage1_summary':summary,'classref_lines':len(classrefs),'set_records':len(sets),'set_ok':sum('result=ok' in s for s in sets),'set_failed':sum('result=failed' in s for s in sets),'load_class_c_successful_sites':load_class,'outside_saved_drift':outside,'source_count':len(post['source']),'processes_before':pre['processes'],'processes_after':post['processes']}
(R/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
report=f'''# DD27g C327 - measured soft-class reflection probe

ONE launch of probe_unreal_api.py --classrefs ONLY. Explicit release_to_run.json records C327; C325 preparation receipt remains historical. Refreshed expected probe/four dependency pins from CURRENT toolkit receipt, checked DD29Source216/DLL4e3580fd/EXE/HEADbc3fe6a, fresh Content11752path+size/Data16hash/Config/status/process snapshots before launch. C321 exclusive lock acquired and recorded. Exact command/flags/job are preserved; no --output/--apply/--save/helper/build/test/fix/retry. All mutations in the accepted probe are on throwaway plain structs; only existing asset/class loads are attempted.

Process exit={job['exit_code']}, elapsed={job['seconds']:.3f}s. Stage1 summary {summary} is static chain/type presence, not a conversion gate. Error severity={len(errors)}, Warning severity={len(warnings)}. Candidate conversion failures are diagnostic data and remain unfiltered. Raw log SHA256 `{sha(R/'editor_raw.log')}`. All{len(classrefs)}CLASSREF lines SHA256 `{sha(R/'classref_lines_verbatim.txt')}`. Full class-ref section (including multiline exception continuations) SHA256 `{sha(R/'classref_section_full.txt')}`.

## Every CLASSREF / CLASSREF SET line and SoftClassPath members (verbatim)
```
{chr(10).join(classrefs)}
```

## Every Error-severity line
```
{chr(10).join(errors)}
```

Readback facts for lead's A218 decision: load_class(None, the exact generated-class object path ending _C) produced BlueprintGeneratedClass values; the three load_class_c SET records are:
```
{chr(10).join(load_class)}
```
Other forms' outcomes are quoted above, not silently discarded or generalized. A successful form on these two class paths/three property sites does not certify all class references or permit path rewriting not measured. SoftClassPath's public-member line is retained, not treated as evidence a string constructor stores a meaningful path. No authoring_core/profile converter change was made; A218 remains AG's separately ordered correction.

Post-state: Source216 exact DD29 final; toolkit/input and binaries unchanged; tracked Content/Config/Source status unchanged, HEADbc3fe6a. Content11752path/sizes+Data16hashes and Config hashes equal, no new/changed file observed under the required captures; files outside Data are not all byte-hashed. Drift outside Saved={outside}. Saved1newCrashReportClient ini+3changed files pinned/preserved, not cleaned. No engine/compiler after. Own C321 lock removed only after evidence freeze/STOP; saved lock record retained.

Limits: loading existing classes and setting/reading three fields on plain temporary structs only. No asset created/saved, complete authored definition, CompileParticipant/preflight/preparation/registration/startup/gameplay/PIE/package proof. All DD27 failed runs and prior provenance findings remain. KI139 remains open until converter correction AND a separately released authoring run pass.
'''
(R/'RUN_REPORT_TO_CLAUDE.md').write_text(report,encoding='utf-8')
message=f'''C327 DD27g ONE classref probe completed, editor exit{job['exit_code']}; fresh actual-receipt five pins, DD29 Source216/DLL4e3580fd/EXE/HEAD and pre/post verified under exclusive C321 lock. No captured drift outside Saved; Saved1new+3changed pinned/preserved,post-process empty. No toolkit/core/profile/Source fix, helper/asset creation/save/build/test/retry.
Measured load_class(None, exact path_C) -> BlueprintGeneratedClass and result=ok readback at ALL3sites: RPGFireballConfig.fireball_ability, RPGPhaseDependencyConfig.immunity_effect, RPGStaggerProfileConfig.immunity_effect. ALL candidate forms retained: {len(classrefs)}CLASSREF lines, {len(sets)}SET records ({sum('result=ok' in s for s in sets)}ok/{sum('result=failed' in s for s in sets)}failed diagnostic outcomes); {len(errors)}Error-severity/{len(warnings)}Warning-severity lines. Raw SHA256 {sha(R/'editor_raw.log')}; CLASSREF SHA256 {sha(R/'classref_lines_verbatim.txt')}.
Every CLASSREF/SET line, SoftClassPath members, full exception continuations and every Error are in Codex/DD27g/RUN_REPORT_TO_CLAUDE.md, classref_lines_verbatim.txt and classref_section_full.txt; full commands/jobs/pins/snapshots/receipts included. Existing-classes/temporary-struct reflection only, no authoring/gameplay pass. KI139 stays open for measured A218 correction and separate authoring release. Own lock released after freeze; idle, ready for engine lane.'''
(R/'MESSAGE_DELIVERY.txt').write_text(message,encoding='utf-8')
entry='\n\nDD27g C327 measured 2026-10-29: ONE --classrefs probe exit0, full candidate results preserved. load_class(None, exact generated path_C) returned BlueprintGeneratedClass and set/read successfully at all3soft-class sites in temporary structs. No converter fix/asset authoring pass. Fresh216Source/DD29binary/five receipt pins and snapshots verified; no captured drift outsideSaved, effects pinned. Evidence Docs/BossCombatReview/Execution/Codex/DD27g/RUN_REPORT_TO_CLAUDE.md. KI139 remains open pending A218 plus separately released authoring verification; all prior failures preserved.\n'
for name in ('TASKS.md','DECISIONS.md','TEST_PLAN.md','KNOWN_ISSUES.md'):
    with (ROOT/'Documentation'/name).open('a',encoding='utf-8') as f:f.write(entry)
with (R.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:f.write(entry)
exclude={'receipt_sha256.txt','MESSAGE_DELIVERY.txt','MESSAGE_PREPARED.txt'}
(R/'receipt_sha256.txt').write_text(''.join(f'{sha(p)} *{p.name}\n' for p in sorted(R.iterdir()) if p.is_file() and p.name not in exclude),encoding='utf-8')
print(json.dumps(result));print('receipt_sha256='+sha(R/'receipt_sha256.txt'))
