from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parent;ROOT=R.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=(R/'editor_raw.log').read_text(errors='replace');lines=raw.splitlines()
draft=[s for s in lines if '[DRAFT_APPLY]' in s]
(R/'draft_apply_lines.txt').write_text('\n'.join(draft)+'\n')
start=next(i for i,s in enumerate(lines) if '[DIAGNOSTIC SUMMARY]' in s)
end=next(i for i in range(start+1,len(lines)) if '[DRAFT_APPLY] FATAL' in lines[i])
table=lines[start:end+1]
(R/'diagnostic_summary_verbatim.txt').write_text('\n'.join(table)+'\n')
errors=[s for s in lines if re.search(r'\b\w+: Error:',s)]
warnings=[s for s in lines if re.search(r'\b\w+: Warning:',s)]
(R/'error_lines.txt').write_text('\n'.join(errors)+'\n');(R/'warning_lines.txt').write_text('\n'.join(warnings)+'\n')
pre=json.loads((R/'pre_state.json').read_text());post=json.loads((R/'post_state.json').read_text());diff=json.loads((R/'state_diff.json').read_text());job=json.loads((R/'job_record.json').read_text(encoding='utf-8-sig'))
assert pre['content_git_status']==post['content_git_status']
status=subprocess.check_output(['git','status','--short','--','Content','Config','Source'],cwd=ROOT,text=True)
(R/'post_git_status_Content_Config_Source.txt').write_text(status)
saved=[]
for rel in diff['saved']['added']+diff['saved']['changed']:
    p=ROOT/rel;saved.append({'path':rel,'size':p.stat().st_size,'sha256':sha(p)})
(R/'saved_findings_sha256.json').write_text(json.dumps(saved,indent=2)+'\n')
outside={k:v for k,v in diff.items() if k!='saved' and any(v.values())}
result={'release':'C-312','verdict':'FAILED: helper diagnostic 29 failures / SystemExit1','editor_exit':job['exit_code'],'helper_SystemExit1':any('SystemExit: 1' in s for s in errors),'error_severity':len(errors),'warning_severity':len(warnings),'diagnostic_failures':29,'per_draft_printed_count':14,'per_draft_lines_are_not_success':True,'full_success_line_present':any('[DRAFT_APPLY] SUCCESS:' in s for s in lines),'fresh_preflight':True,'outside_saved_drift':outside,'saved_added':len(diff['saved']['added']),'saved_changed':len(diff['saved']['changed']),'source_count':len(post['source']),'raw_sha256':sha(R/'editor_raw.log')}
(R/'result.json').write_text(json.dumps(result,indent=2)+'\n')
report=f'''# DD27 C312 in-memory rerun — FAILED (DD27d evidence folder)

One authorized launch; no save flag, retry, toolkit edit, cleanup, build or automation test. Editor process exit={job['exit_code']}, {job['seconds']:.3f}s; helper reports 29 property failures, returns False and logs SystemExit:1. This is FAILURE despite editor exit0 and misleading per-draft print lines.

Exact command is recorded in command.json/run_once.ps1: UnrealEditor-Cmd.exe OneBossFight.uproject -ExecutePythonScript="<AuthoringToolkit>/draft_boss_profiles.py --input-json <AuthoringToolkit>/examples/boss_draft_profiles.json --apply" -unattended -nullrhi -nosound -nosplash -abslog=<DD27d>/editor_raw.log. No --save or other helper flag.

Fresh preflight read all FOUR required pins from the current AuthoringToolkit/evidence_sha256.txt, matched bytes, captured pre-state and required a verified record; wrapper throws before launch on any failure, rehashes all four pins/pre-state and checks processes again. Both snapshots: HEADbc3fe6a, Source212 equal DD26; Content11752 paths/sizes equal and Data16 SHA256 equal; Config/toolkit/binary hashes equal; tracked Content/Config/Source empty. Processes empty before/after. Captured differences outside Saved: {outside}. Content outside Data is inventoried by path+size, not fully hashed. Saved has {len(diff['saved']['added'])} new and {len(diff['saved']['changed'])} changed editor-side files; paths and hashes preserved, no cleanup.

Raw log SHA256 `{sha(R/'editor_raw.log')}`. DRAFT_APPLY extraction SHA256 `{sha(R/'draft_apply_lines.txt')}`. Diagnostic table extraction SHA256 `{sha(R/'diagnostic_summary_verbatim.txt')}`. Warning severity={len(warnings)}, Error severity={len(errors)}; every Error line quoted below. TraceServer Error0x5 remains within Warning severity.

## Every DRAFT_APPLY line (verbatim)
```
{chr(10).join(draft)}
```

The helper prints “Initialized & verified all 14 typed properties” for each draft BEFORE inspecting the shared collector. These are not successful whole-draft readbacks: FATAL29 follows and no final SUCCESS/NOT-saved completion line exists. Source draft_boss_profiles.py:818-825 explains this ordering. Do not certify three successful drafts or all22 properties from these printed14 counts.

## Full emitted diagnostic table (verbatim)
```
{chr(10).join(table)}
```

Diagnostic limitation: the frozen helper's print_summary_table (:525-537) slices Asset/Section/Property/Expected/Actual Type/Actual Repr/Error columns to fixed widths (25/15/17/13/11/23/25 characters). The complete table AS EMITTED is preserved, but original long expected values, actual repr and exception messages cannot be recovered from this run. No untruncated dump was written by the helper. I did not reconstruct missing details, alter the helper, or launch again. The label `(constructor)` is assigned around the whole create_struct_instance call (:715-718), so it does not distinguish constructor failure from an inner property-conversion/setter exception.

Observed categories: both boss drafts have top-level skeleton and animations TypeError rows; player has skeleton TypeError; all three have eight struct-section `(constructor)` TypeError rows (fireball, phase_dependencies [truncated in table], stagger_profile, dormant_wake, bleed, look, close_clip_swap, death). These sum to29. This does not establish a single root cause or an exact failing nested property because the full exceptions were truncated.

EmberWarden input Fields count110 is pinned in the pre-state JSON. The helper source checks count equality and compares each field's canonical values (:791-816), and no fields failure row appears. There is NO explicit numeric Fields-readback log line, however, and the overall draft fails. Therefore “110 rows read back” is source-control-flow inference only, not a directly logged numeric readback witness. No compiler or preflight was run.

## Every Error-severity line (verbatim)
```
{chr(10).join(errors)}
```

Limits: in-memory creation attempts and collected failures only. No saved asset, complete valid definition, CompileParticipant/preflight/preparation, binding/Ready/activation, gameplay/PIE/package claim. DD27 original guard failure and DD27b missing pre-state finding remain preserved. Await lead's concrete diagnostic/conversion correction and separate release; DD28 staging interface stop X322 remains unresolved.
'''
(R/'RUN_REPORT_TO_CLAUDE.md').write_text(report)
message=f'''C312 DD27 in-memory RERUN FAILED: one launch, fresh four-pin receipt preflight + pre/post captured correctly. Editor exit {job['exit_code']}, helper FATAL29 / SystemExit1; no retry/save/toolkit edit/cleanup/build/tests. Raw SHA256 {sha(R/'editor_raw.log')}; {len(errors)} Error-severity, {len(warnings)} Warning-severity lines.
All3 drafts were created in memory, but misleading per-draft “verified14” prints precede collector rejection. NO final SUCCESS and NO complete-draft pass.29 TypeError rows: skeleton on3drafts, animations on2bossdrafts, eight struct sections on all3. Exact nested properties/messages unavailable because helper print_summary_table truncates all columns (Error25chars etc.); full emitted table/raw preserved, no invented full exceptions. The generic “constructor” label also covers inner conversion/setter failure. Fields110 is input-pinned; no explicit numeric readback line, so no direct110 witness claimed.
Evidence Codex/DD27d/RUN_REPORT_TO_CLAUDE.md, draft_apply_lines.txt, diagnostic_summary_verbatim.txt, error_lines.txt, full receipts/pre/post/commands/pins. Source212/DD26, Content11752 path+size/Data16hashes, Config/toolkit/binaries unchanged; processes empty before/after; Saved1new+3changed pinned/preserved. Reflection-only prior acceptance does not imply these assignments passed. Await exact correction/release; DD28 pre-write interface stop X322 also awaits disposition.'''
(R/'MESSAGE_DELIVERY.txt').write_text(message)
entry='\n\nDD27 C312 rerun FAILED 2026-10-29: editor exit0/helper SystemExit1,29 collected TypeError failures; three in-memory creation attempts, per-draft verified14 prints are not successful drafts. Full emitted diagnostic is column-truncated; exact nested exceptions unavailable. Fresh preflight and snapshots valid, Content/Config/Source/toolkit/binaries captured unchanged; Saved side effects pinned. No save/retry. Evidence Docs/BossCombatReview/Execution/Codex/DD27d/RUN_REPORT_TO_CLAUDE.md; correction/release required.\n'
for name in ('TASKS.md','TEST_PLAN.md','DECISIONS.md','KNOWN_ISSUES.md'):
    with (ROOT/'Documentation'/name).open('a',encoding='utf-8') as f:f.write(entry)
with (R.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:f.write(entry)
exclude={'receipt_sha256.txt','MESSAGE_DELIVERY.txt'}
(R/'receipt_sha256.txt').write_text('\n'.join(f'{sha(p)} *{p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name not in exclude)+'\n')
print(json.dumps(result))
