from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parent
ROOT=R.parents[4]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
raw=(R/'editor_raw.log').read_text(errors='replace')
lines=raw.splitlines()
errors=[f'{i}: {s}' for i,s in enumerate(lines,1) if re.search(r'\b\w+: Error:',s)]
warnings=[f'{i}: {s}' for i,s in enumerate(lines,1) if re.search(r'\b\w+: Warning:',s)]
pre=json.loads((R/'pre_state.json').read_text()); post=json.loads((R/'post_state.json').read_text())
diff=json.loads((R/'state_diff.json').read_text()); job=json.loads((R/'job_record.json').read_text(encoding='utf-8-sig'))
saved_paths=diff['saved']['added']+diff['saved']['changed']
saved_pins=[{'path':p,'sha256':sha(ROOT/p),'size':(ROOT/p).stat().st_size} for p in saved_paths]
(R/'saved_findings_sha256.json').write_text(json.dumps(saved_pins,indent=2)+'\n')
summary={'verdict':'FAILED; stop, no retry','editor_exit':job['exit_code'],'helper_exit':'SystemExit: 1 in raw log','warnings':len(warnings),'error_severity':len(errors),'draft_success_lines':[s for s in lines if '[DRAFT_APPLY] Initialized & verified' in s],'source_count':len(post['source']),'content_files':len(post['content']),'data_hashes':sum('sha256' in x for x in post['content']),'diff':diff,'saved_findings':saved_pins}
(R/'result.json').write_text(json.dumps(summary,indent=2)+'\n')
(R/'warning_lines.txt').write_text('\n'.join(warnings)+'\n')
(R/'error_lines.txt').write_text('\n'.join(errors)+'\n')
report=f'''# DD27 / C300 measured first-run failure — 2026-10-29

One launch, no build/tests, no retry or toolkit modification. FAILED before asset creation: `Missing required Unreal API: unreal.SystemLibrary.is_editor` (raw line 1263). The exact frozen guard is draft_boss_profiles.py:148-151. All three JSON profiles passed the helper's structural plan step, but none reached a `[DRAFT_APPLY] Creating` or initialized/readback line. No draft property, enum, array, float32 or soft-path assignment is certified. EmberWarden Fields=110 is an input JSON count only, NOT an editor readback.

Command: UnrealEditor-Cmd.exe C:/UnrealProject/OneBossFight/OneBossFight.uproject -ExecutePythonScript="C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py --input-json C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json --apply" -unattended -nullrhi -nosound -nosplash -abslog=<DD27>/editor_raw.log. command.json and run_once.ps1 preserve exact arguments. No --save.

Editor process exit {job['exit_code']}, duration {job['seconds']:.3f}s. Script reported `SystemExit: 1`; editor exit0 does NOT mean helper success. Error-severity lines={len(errors)}, Warning-severity lines={len(warnings)}. TraceServer Error0x5 occurs inside Warning severity and remains preserved. No separate Python AttributeError traceback: guard detected absent API and returned False, then main raised SystemExit1. Raw traceback:

```
{chr(10).join(errors)}
```

Fresh pre/post engine/compiler checks empty. HEAD bc3fe6a49335f0a68bf5df9d895b8a46f6633aeb. All212 Source hashes equal DD26 post manifest and unchanged after. Toolkit top-level Python/input JSON hashes and binaries unchanged. All11752 Content files have before/after path+size inventories; all16 files under Content/OneBossFight/Data have SHA256. No Content additions/removals/size drift, Data hash drift or Content git-status change. This is C300's permitted minimum Content capture; other Content bytes were not all hashed. Config/ full file hashes unchanged.

Saved findings (preserved in place, not cleaned): one new CrashReportClient ini; changed PackageRestoreData.json, EditorPerProjectUserSettings.ini and UnrealClaude/script_history.json. state_diff.json enumerates paths and saved_findings_sha256.json pins current bytes. These are reported side effects, not suppressed or classified as a clean disk run. The crash-client ini alone is not proof of an engine crash; raw shutdown was orderly with exit0. No further engine launch allowed under this exhausted one-run release.

Raw log SHA256 `{sha(R/'editor_raw.log')}`; stdout `{sha(R/'stdout.log')}`; stderr `{sha(R/'stderr.log')}`; job `{sha(R/'job_record.json')}`. See receipt_sha256.txt for all evidence, pre/post manifests, helper pins, binary pins, scripts and findings.

Request to lead: review a concrete bounded toolkit environment-guard correction and tests from AG, then a fresh one-run release. No guard weakening, toolkit edit, retry, save, compilation of definitions, preflight, preparation, registration, wiring, gameplay, PIE, networking or package claim.
'''
(R/'RUN_REPORT_TO_CLAUDE.md').write_text(report)
message=f'''C300 DD27 ONE RUN FAILED before asset creation. Frozen helper's guard reports missing unreal.SystemLibrary.is_editor (raw1263); main then SystemExit1, despite editor process exit0. All3 profile plans validated structurally, but ZERO draft creation/readback success lines; EmberWarden110Fields is input-only, not readback. No retry/edit/save/build/tests.
Exact command/exit/duration/every Error line/warning count/limits: Codex/DD27/RUN_REPORT_TO_CLAUDE.md. Raw editor SHA256 {sha(R/'editor_raw.log')}; Error severity {len(errors)}, Warning severity {len(warnings)}. Full evidence receipt in Codex/DD27/receipt_sha256.txt.
Pre/post checks: no engine/compiler; HEADbc3fe6a;212Source hashes equal acceptedDD26; toolkit/input/binaries unchanged.11752Content path+size inventory and16Data hashes unchanged; Content git status unchanged; Config hashes unchanged. Saved had1newCrashReportClient ini plus3changed files (PackageRestoreData, editor user settings, UnrealClaude script history), pinned and preserved; not a clean Saved result. No cleanup. Await your bounded AG guard correction and separate rerun release. No runtime/asset/readback pass claimed.'''
(R/'MESSAGE_DELIVERY.txt').write_text(message)
entry='\n\nDD27 C300 measured 2026-10-29: one headless in-memory authoring run FAILED before creation: missing unreal.SystemLibrary.is_editor; script SystemExit1/editor exit0. Content minimum inventories/Data hashes, Config,212Source/toolkit/binaries unchanged; four Saved side effects preserved. No property readback proof, retry/save/build/activation. Evidence Docs/BossCombatReview/Execution/Codex/DD27/RUN_REPORT_TO_CLAUDE.md; lead review pending.\n'
for name in ('TASKS.md','TEST_PLAN.md','DECISIONS.md','KNOWN_ISSUES.md'):
    with (ROOT/'Documentation'/name).open('a',encoding='utf-8') as f:f.write(entry)
with (R.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:f.write(entry)
excluded={'receipt_sha256.txt','MESSAGE_DELIVERY.txt'}
rows=[f'{sha(p)} *{p.name}' for p in sorted(R.iterdir()) if p.is_file() and p.name not in excluded]
(R/'receipt_sha256.txt').write_text('\n'.join(rows)+'\n')
print(json.dumps({'verdict':summary['verdict'],'warnings':len(warnings),'errors':len(errors),'raw_sha256':sha(R/'editor_raw.log'),'receipt_sha256':sha(R/'receipt_sha256.txt'),'receipts':len(rows)}))
