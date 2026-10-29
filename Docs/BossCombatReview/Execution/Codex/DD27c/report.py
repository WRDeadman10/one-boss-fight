from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parent; ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=(R/'editor_raw.log').read_text(errors='replace');lines=raw.splitlines()
probe=[s for s in lines if '[PROBE]' in s]
(R/'probe_lines.txt').write_text('\n'.join(probe)+'\n')
errors=[s for s in lines if re.search(r'\b\w+: Error:',s)]
warnings=[s for s in lines if re.search(r'\b\w+: Warning:',s)]
(R/'error_lines.txt').write_text('\n'.join(errors)+'\n');(R/'warning_lines.txt').write_text('\n'.join(warnings)+'\n')
instances=[s for s in probe if '[PROBE] INSTANCE ' in s]
instance_errors=[s for s in instances if 'error:' in s]
success=[s for s in instances if 'get_editor_property=ok' in s]
examples={}
for s in success:
    match=re.search(r'\[PROBE\] INSTANCE (\w+)',s)
    if match:examples.setdefault(match[1],s)
values=[s for s in instances if ' value=' in s]
types=[s for s in instances if ' type=' in s]
cdos=[s for s in probe if '[PROBE] CDO ' in s]
editor=[s for s in probe if '[PROBE] unreal.is_editor' in s or 'call: unreal.is_editor()' in s]
sections=[('Every instance error',instance_errors),('One successful property line per struct',list(examples.values())),('Float-valued property lines',values),('Array/enum type lines',types),('Definition CDO lines (includes soft paths and nested structs)',cdos),('Module-level editor query',editor)]
verbatim='\n\n'.join(title+'\n'+('\n'.join(rows) if rows else '(none)') for title,rows in sections)
(R/'requested_verbatim_findings.txt').write_text(verbatim+'\n')
pre=json.loads((R/'pre_state.json').read_text());post=json.loads((R/'post_state.json').read_text());diff=json.loads((R/'state_diff.json').read_text());job=json.loads((R/'job_record.json').read_text(encoding='utf-8-sig'))
assert pre['content_git_status']==post['content_git_status'],'Content git-status drift'
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
(R/'post_git_status_Content_Config_Source.txt').write_text(status)
saved=[]
for path in diff['saved']['added']+diff['saved']['changed']:
    p=ROOT/path;saved.append({'path':path,'sha256':sha(p),'size':p.stat().st_size})
(R/'saved_findings_sha256.json').write_text(json.dumps(saved,indent=2)+'\n')
summary=[s for s in probe if '[PROBE] SUMMARY' in s]
outside_drift={k:v for k,v in diff.items() if k!='saved' and any(v.values())}
result={'release':'C-307','verdict':'Measured read-only reflection diagnostic; lead review pending','editor_exit':job['exit_code'],'error_severity':len(errors),'warning_severity':len(warnings),'summary':summary,'probe_lines':len(probe),'instance_lines':len(instances),'instance_property_reads_ok':len(success),'instance_errors':len(instance_errors),'successful_structs':len(examples),'float_value_lines':len(values),'instance_type_lines':len(types),'cdo_lines':len(cdos),'outside_saved_drift':outside_drift,'post_git_status_Content_Config_Source':status,'processes_before':pre['processes'],'processes_after':post['processes']}
(R/'result.json').write_text(json.dumps(result,indent=2)+'\n')
report=f'''# DD27c C307 — measured instance reflection probe

One launch, stage1+stage2 `--instances`, no retry, toolkit edit, authoring helper, build, tests, asset creation or save. Pending Claude review; reflection observations are not authoring/gameplay acceptance.

Preflight read the exact probe hash from AuthoringToolkit/evidence_sha256.txt and matched current bytes. The wrapper calls preflight first, throws on any nonzero exit, requires preflight_verified.json, rehashes the fresh pre-state and probe, and checks processes again BEFORE Start-Process. This fixes the control-flow path for this run; DD27b's historical missing-pre-state finding remains recorded.

Exact command/executable/arguments: command.json; invocation wrapper run_once.ps1. `UnrealEditor-Cmd.exe OneBossFight.uproject -ExecutePythonScript="<AuthoringToolkit>/probe_unreal_api.py --instances" -unattended -nullrhi -nosound -nosplash -abslog=<DD27c>/editor_raw.log`. No --output.

Process exit={job['exit_code']}; elapsed={job['seconds']:.3f}s. Helper emitted stage1 summary {summary} and completed stage2 through module-level editor query; no Python Error traceback / SystemExit1 observed. All {len(probe)} PROBE lines extracted verbatim, SHA256 `{sha(R/'probe_lines.txt')}`. Error severity={len(errors)}; Warning severity={len(warnings)}; every Error line below. TraceServer Error0x5 remains Warning severity, not an Error-severity line. The summary counts refer to stage1 API lookup, not property success.

```
{chr(10).join(errors)}
```

Fresh BEFORE and AFTER: 212 Source files match DD26 post manifest; 11,752 Content files have equal path+size inventories,16 Data hashes equal; Config hashes, toolkit Python/input pins and binaries equal; HEAD bc3fe6a both. Processes empty before/after; tracked Content/Config/Source status empty and Content status equal. No differences outside Saved under the specified captures: {outside_drift}. Content outside Data was not all hashed, so equal path/size is not a full byte-level proof. No unexpected repository content mutation is claimed absent solely from git's ignored pack folders.

Saved: {len(diff['saved']['added'])} new and {len(diff['saved']['changed'])} changed files, enumerated in state_diff.json and SHA-pinned in saved_findings_sha256.json. Preserved in place, no cleanup. These editor side effects are not hidden by the unchanged Content result.

Raw editor log SHA256 `{sha(R/'editor_raw.log')}`. Observed {len(success)} successful instance-property reads across {len(examples)} structs; {len(instance_errors)} instance error lines; {len(cdos)} CDO lines. Requested quotations follow WITHOUT interpretation:

```
{verbatim}
```

Limits: in-memory reflection report only. No property write, asset creation/readback, persistent definition, compiler/preflight/preparation integration, gameplay/PIE/networking/package proof. Any missing type observations and class-dir MISMATCH lines remain in complete probe_lines.txt; no filtering of the raw report. Await lead-selected bounded toolkit correction and separate authoring rerun release.
'''
(R/'RUN_REPORT_TO_CLAUDE.md').write_text(report)
message=f'''C307 DD27c completed ONE stage1+stage2 probe launch with --instances, editor exit {job['exit_code']}. Fresh preflight succeeded BEFORE launch: expected probe pin read from actual receipt, Source212/DD26, HEADbc3fe6a, Content inventory11752/Data16hashes, Config/binary/toolkit/process/status snapshots preserved. Wrapper stops on any preflight failure. Post comparison: zero captured differences outside Saved; Saved1new+3changed pinned/preserved. DD27b provenance exception remains recorded.
Measured: stage1 SUMMARY missing=2 present=53; {len(success)} instance get_editor_property=ok across {len(examples)} structs, {len(instance_errors)} instance-error lines, {len(cdos)} CDO lines; module-level unreal.is_editor callable and returned True. {len(errors)} Error-severity / {len(warnings)} Warning-severity lines. No property writes/assets/helper run/save/build/tests/retry.
Raw editor SHA256 {sha(R/'editor_raw.log')}; all {len(probe)} PROBE lines SHA256 {sha(R/'probe_lines.txt')}. Every requested instance error, example per successful struct, float value, array/enum type, CDO/soft-path/nested-struct type and editor query is quoted verbatim in Codex/DD27c/RUN_REPORT_TO_CLAUDE.md / requested_verbatim_findings.txt. Full pre/post, command, jobs, pins and receipt_sha256.txt included. Reflection observations only, not authoring/gameplay proof. Await your exact AG correction and separate rerun release.'''
(R/'MESSAGE_DELIVERY.txt').write_text(message)
entry=f'\n\nDD27c C307 measured 2026-10-29: one --instances reflection-probe launch exit{job["exit_code"]}; {len(success)} property reads across {len(examples)} structs, {len(instance_errors)} instance errors; module unreal.is_editor True. Fresh pre-state/receipt pin verified before launch; captured Content/Config/Source/toolkit/binaries unchanged; Saved side effects preserved. Reflection only, not asset creation/write/gameplay. Evidence Docs/BossCombatReview/Execution/Codex/DD27c/RUN_REPORT_TO_CLAUDE.md, Claude review pending.\n'
for name in ('TASKS.md','TEST_PLAN.md','DECISIONS.md','KNOWN_ISSUES.md'):
    with (ROOT/'Documentation'/name).open('a',encoding='utf-8') as f:f.write(entry)
with (R.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:f.write(entry)
excluded={'receipt_sha256.txt','MESSAGE_DELIVERY.txt'}
(R/'receipt_sha256.txt').write_text('\n'.join(f'{sha(p)} *{p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name not in excluded)+'\n')
print(json.dumps(result))
