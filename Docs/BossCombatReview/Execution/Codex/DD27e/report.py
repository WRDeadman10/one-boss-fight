from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parent;ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=(R/'editor_raw.log').read_text(errors='replace');lines=raw.splitlines()
probe=[s for s in lines if '[PROBE]' in s];soft=[s for s in probe if '[PROBE] SOFTREF' in s]
(R/'probe_lines.txt').write_text('\n'.join(probe)+'\n');(R/'softref_lines_verbatim.txt').write_text('\n'.join(soft)+'\n')
errors=[s for s in lines if re.search(r'\b\w+: Error:',s)];warnings=[s for s in lines if re.search(r'\b\w+: Warning:',s)]
(R/'error_lines.txt').write_text('\n'.join(errors)+'\n');(R/'warning_lines.txt').write_text('\n'.join(warnings)+'\n')
pre=json.loads((R/'pre_state.json').read_text());post=json.loads((R/'post_state.json').read_text());diff=json.loads((R/'state_diff.json').read_text());job=json.loads((R/'job_record.json').read_text(encoding='utf-8-sig'))
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
v=json.loads((R/'preflight_verified.json').read_text());assert v['git_status_Content_Config_Source']==status
(R/'post_git_status_Content_Config_Source.txt').write_text(status)
saved=[]
for rel in diff['saved']['added']+diff['saved']['changed']:
    p=ROOT/rel;saved.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
(R/'saved_findings_sha256.json').write_text(json.dumps(saved,indent=2)+'\n')
summary=[s for s in probe if '[PROBE] SUMMARY' in s]
outside={k:v for k,v in diff.items() if k!='saved' and any(v.values())}
omitted=[prop for prop in ('RPGBleedConfig.proc_sound','RPGLookConfig.sword') if not any(prop+' form=default' in s for s in soft)]
result={'release':'C-317','verdict':'Measured soft-reference diagnostic, lead review pending','editor_exit':job['exit_code'],'error_severity':len(errors),'warning_severity':len(warnings),'summary':summary,'all_probe_lines':len(probe),'softref_lines':len(soft),'softref_form_results_ok':sum('result=ok' in s for s in soft),'softref_form_results_error':sum('result=error:' in s for s in soft),'requested_default_lines_not_emitted':omitted,'outside_saved_drift':outside,'source_count':len(post['source']),'processes_before':pre['processes'],'processes_after':post['processes']}
(R/'result.json').write_text(json.dumps(result,indent=2)+'\n')
report=f'''# DD27e C317 — soft-reference reflection diagnostic

ONE launch with `probe_unreal_api.py --softrefs` only; no --instances, --output, helper run, creation/save/build/test/retry. Exact command, flags and process exit preserved in command.json/run_once.ps1/job_record.json. Editor exit={job['exit_code']}, elapsed={job['seconds']:.3f}s; helper returned normally through its always-zero diagnostic exit (summary and softref rows present, no script traceback). Stage1 summary {summary} describes static API/type lookup, not conversion success.

Fresh preflight expected probe SHA256 read from the actual A213 receipt (not message prose); matched current bytes. DD28 CURRENT_ENGINE_BASELINE source/binary receipt hashes matched, all213Source equal DD28 final manifest, DLL82c29032.../EXE matched, HEADbc3fe6a. Fresh Content11752 path+size inventory and Data16 hashes captured before and after; Config hashes captured. Full tracked Content/Config/Source status identical before/after (accepted uncommitted DD28 Source changes remain, not hidden as clean). No engine/compiler before or after. Captured drift outside Saved={outside}. Files outside the Data subtree were inventoried by path+size, not all hashed.

Saved has {len(diff['saved']['added'])} new and {len(diff['saved']['changed'])} changed editor-side files, pinned/preserved in saved_findings_sha256.json/state_diff.json; no cleanup. Toolkit Python/input and DLL/EXE/PDB captures unchanged. Existing assets were loaded into memory by the approved guarded probe forms; no asset is claimed newly authored or saved.

Raw editor log SHA256 `{sha(R/'editor_raw.log')}`; all{len(probe)}PROBE lines SHA256 `{sha(R/'probe_lines.txt')}`; all{len(soft)}SOFTREF lines SHA256 `{sha(R/'softref_lines_verbatim.txt')}`. Error severity={len(errors)}; Warning severity={len(warnings)}. Expected form-conversion errors printed as result=error:TypeError are diagnostic text, not Error-severity lines. Every Error-severity line:

```
{chr(10).join(errors)}
```

## Every SOFTREF line, including public SoftObjectPath members/defaults (verbatim, no interpretation)

```
{chr(10).join(soft)}
```

Evidence omissions: the frozen A213 probe emitted default readbacks only for proc_effect, body and pieces. Requested default proc_sound and sword lines were NOT emitted ({omitted}); no inference from other properties replaces them. SoftObjectPath public dir lacks set_path/asset_path_name, so those conditional forms were not exercised. No two-argument-constructor form line was emitted either. I did not edit the probe or use a second launch to supply missing evidence. Report these gaps for lead disposition.

Limits: exact observed conversion acceptance/rejection and readback type/repr on these properties only. Array repr is an Array wrapper address, not a printed per-element content witness. Readback of a SoftObjectProperty itself may resolve an object: this run is not proof of zero asset loads. No general asset creation/readback, authored definition, compilation/preflight/preparation/activation/gameplay proof. Await Claude's exact to_soft_ref correction/release. DD28 accepted baseline remains current; its registry/registration evidence does not repair DD27 authoring failures.
'''
(R/'RUN_REPORT_TO_CLAUDE.md').write_text(report)
message=f'''C317 DD27e ONE softref probe completed, editor exit{job['exit_code']}, no script traceback. Receipt pin read from actual evidence; DD28 baseline Source213/DLL82c29032/EXE/HEADbc3fe6a and fresh Content11752/Data16/Config/status/process captures verified. Zero captured drift outside Saved; Saved1new+3changed pinned/preserved; no save/helper/asset creation/build/test/retry.
SUMMARY {summary}; {len(errors)} Error-severity/{len(warnings)} Warning-severity lines. All{len(soft)}SOFTREF rows incl FULL TypeError messages/defaults/public SoftObjectPath dir quoted WITHOUT interpretation in Codex/DD27e/RUN_REPORT_TO_CLAUDE.md and softref_lines_verbatim.txt. Raw SHA256 {sha(R/'editor_raw.log')}; all{len(probe)}PROBE SHA256 {sha(R/'probe_lines.txt')}. Receipt and raw jobs/pre/post/pins included.
Evidence gap: frozen probe did NOT emit requested DEFAULT proc_sound/sword readbacks or a two-argument constructor form. No replacement claim/retry. Conditional set_path/asset_path_name forms absent from public dir and unexercised. Array repr does not print element contents. Exact form results retained for your A214 decision; no authoring/gameplay pass implied. Continuing DD29 staged composition inspection only.'''
(R/'MESSAGE_DELIVERY.txt').write_text(message)
entry='\n\nDD27e C317 measured 2026-10-29: one --softrefs probe exit0, approved existing-asset loads only, no creation/save. Fresh DD28 Source213/binary baseline and pre/post snapshots verified; captured Content/Config/Source/toolkit/binaries unchanged,Saved effects pinned. Full conversion TypeErrors/readback types preserved in Docs/BossCombatReview/Execution/Codex/DD27e/RUN_REPORT_TO_CLAUDE.md. Frozen probe omitted requested default proc_sound/sword and two-argument form; no retry. Diagnostic only, lead review/correction pending.\n'
for name in ('TASKS.md','DECISIONS.md','TEST_PLAN.md','KNOWN_ISSUES.md'):
    with (ROOT/'Documentation'/name).open('a',encoding='utf-8') as f:f.write(entry)
with (R.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:f.write(entry)
exclude={'receipt_sha256.txt','MESSAGE_DELIVERY.txt'}
(R/'receipt_sha256.txt').write_text('\n'.join(f'{sha(p)} *{p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name not in exclude)+'\n')
print(json.dumps(result))
