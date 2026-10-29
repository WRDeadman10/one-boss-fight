from pathlib import Path
import hashlib,json,os
H=Path(__file__).resolve().parent;ROOT=H.parents[4];R=H/'run_2026-10-29'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((R/'final_verification.json').read_text(encoding='utf-8'));assert f['source_exact'] and f['source_count']==216
tags=('activation_world','activation','world_preparation','registry','full_dd29')
gates={t:json.loads((R/f'{t}_gate.json').read_text(encoding='utf-8')) for t in tags};assert all(g['pass'] for g in gates.values())
build=f['build'];rows=[]
for tag,g in gates.items():rows.append(f'| {tag} | {g["unique"]} | {g["job"]["exit_code"]} | {g["job"]["seconds"]} | `{sha(R/f"automation_{tag}.log")}` |')
paths=json.loads((R/'C320_profile_path_count_comparison.json').read_text(encoding='utf-8'))
asset_count=sum(r['has_object_suffix'] for r in paths['rows']);missing=[r['value'] for r in paths['rows'] if r['has_object_suffix'] and not r['asset_file_exists']]
report=f'''# DD29 C319 measured verification — 2026-10-29

Only the three accepted NEW Source files promoted. Source213->216; ALL213 old files unchanged. Stage/live exact hashes preserved, frozen before build. Independent Claude review pending; no gameplay caller or startup integration added.

## Safety and build

Fresh safety: exact DD28 final213 manifest,104 accepted dependency/candidate/catalog/native/source pins rehashed against accepted DD28 final bytes; binaries equal DD28 final; HEADbc3fe6a; no engine/compiler. Content/Config status unchanged; accepted uncommitted DD28 Source changes preserved and reported. New targets did not exist before promotion. Preimages of accepted interfaces and stage pins saved. Fresh pre-build assertion checks216Source, pin equality, HEAD and baseline binaries/processes. Its inherited console label says Source213, a stale label ONLY: check_gate.py line11 asserts216 and post-promotion manifest records216. No failed safety check or override occurred.

ONE editor Development build exit0/{build['job']['seconds']}s,0build errors. Actual incremental build NO UHT invocation/reflection-generation line; no forced rerun or UHT claim. Three Warning lines preserved: UnrealClaude missing Niagara/NiagaraEditor plugin dependencies, non-preferred compiler. Raw build SHA256 `{build['raw_sha256']}`. New ActivationWorld implementation and tests compiled/linked as staged.

C319 build questions: GetOwnedComponentCount() is a production public member at RPGBossHydrationPreparation.h:137, before the dev-only accessor guard:141; no replacement was needed. RPGBossActivation.h includes WorldPreparation.h, which includes the complete preparation class; TUniquePtr result compiled as staged (Editor build only, not Shipping proof). DD28's RPGBossActivation namespace in the preparation header and the new file pair reopen the SAME namespace; no duplicate type declaration was introduced. KI138 records this.

## Automation results

Each focused gate clean before next launch; full conditional gate after all18focused. Raw discovery/filter and exact source-name sets checked, no duplicate completions. All jobs exit0, Error-severity0, no fatal/ensure/assertion/unsupported lines, GIsCriticalError0.

| Gate | Unique Success | Exit | Seconds | Raw SHA256 |
|---|---|---|---|---|
{chr(10).join(rows)}

Full182 retains ALL177 DD28 names plus EXACTLY five ActivationWorld names; CookCoverage Success. Full warning multiset63 matches DD28 with0added/removed using established timestamp/epoch/sponsor-PID normalisation. Prior Activation6, WorldPreparation4 and PreparationRegistry3 test sources stayed byte-identical. New tests observed registered/never-begun24components and retained epoch lease, clean explicit/repeated/move/scope release; invalid manifest and missing-GI authority fallback; real-allocation injected failure; registration-boundary injections1/12/13/24 cleaned and restored captured component/mesh/context state. Named mid-call drift classification remains source-only, not an executed race/drift reproduction. Missing-GI control detaches/restores ONLY fixture-owned world GI, not a runtime epoch injection.

C321 engine-lock policy arrived after build and first three focused launches. Applied immediately to registry and full launches: each acquired ENGINE_LOCK.json exclusively, saved its owner/task/command snapshot, sealed raw/job/gate/lock evidence, then removed only that owned lock. No existing lock was bypassed or stale lock removed; earlier launches are NOT retroactively claimed locked. No reassignment was received before continuing. Post-run no engine/compiler.

## Final baseline and limits

Final216Source equals post-promotion manifest,104pins equal, HEADbc3fe6a stable. DLL `{f['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']}`; EXE unchanged `{f['binary']['Binaries/Win64/OneBossFight.exe']}`. CURRENT_ENGINE_BASELINE.json now points to DD29 final_source_manifest_sha256.txt and final_binary_sha256.txt under C319 item6. These become C320's required preflight baseline only after this report is posted.

Lease is caller-owned prepared batch retaining accepted plan/config/content/class leases, NOT a reservation token/global uniqueness. Activated means REGISTERED SUBSET ONLY. Clean rejection has no artifact left; off-thread/cleanup/stable-input drift misuse is HardError without an unchanged-world promise. Result Outcome is historical; IsHeld/Succeeded require current artifact. No BeginPlay/tick/binding/Ready/suppression/startup/authored definition/gameplay/PIE/package proof. Existing DD27 failures and DD27b provenance finding remain preserved. No fix/retry or git mutation.

## C320 path-count reconciliation (read-only, before authoring)

Current JSON has {paths['all_distinct_JSON_Game_strings']} distinct /Game strings: {asset_count} object asset paths plus the approved output DIRECTORY. All27 package files exist on disk; missing={missing}. A214's26-row table differs from the actual JSON by multiple rows, not just one. JSON-only values (includes output directory):
```
{chr(10).join(paths['JSON_only'])}
```
A214-table-only rows (not current JSON):
```
{chr(10).join(paths['A214_only'])}
```
Evidence C320_profile_path_count_comparison.json records exact JSON pointers and disk checks. Disk presence is NOT class/skeleton/load/authoring proof. No input/receipt/profile was edited. This finding is reported for lead correction; it is not a failed engine/preflight gate and does not silently change the released C320 input.
'''
(R/'RUN_REPORT_TO_CLAUDE.md').write_text(report,encoding='utf-8')
message=f'''C319 DD29 promoted ONLY3 new Source files,213->216 (all213 prior unchanged). ONE Editor build exit0/{build['job']['seconds']}s,0errors,3warnings; NO UHT invocation in actual incremental build, no forced rerun/claim. Production GetOwnedComponentCount verified outside dev guard; header/TUniquePtr compiled unchanged; DD28/new header reopen same RPGBossActivation namespace.
Focused ActivationWorld5 -> Activation6 -> WorldPreparation4 -> PreparationRegistry3 all exact uniqueSuccess18; conditional full182uniqueSuccess=all177DD28+exact5new, CookCoverageSuccess,0Error/fatal/ensure/assertion,GIsCriticalError0. Full warning multiset63 equals DD28. No failure/fix/retry.104pins/216Source/HEADbc3fe6a stable; EXE unchanged. DLL {f['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']}. Raw build SHA256 {build['raw_sha256']}; full raw SHA256 {sha(R/'automation_full_dd29.log')}. Evidence Codex/DD29/run_2026-10-29/RUN_REPORT_TO_CLAUDE.md with logs/jobs/names/manifests/pins/receipts.
C321 received mid-sequence: registry/full acquired exclusive engine locks and released only after evidence sealing; prior launches predated that policy. No reassignment/bypass. CURRENT_ENGINE_BASELINE now DD29 final216 manifest/binaries, required for released C320 DD27f AFTER this report. KI138/TEST_PLAN updated; library composition in never-begun fixtures only, no reservation/startup/BeginPlay/tick/binding/Ready/suppression/authored-definition/gameplay claim.
C320 audit clarification: current JSON has27asset paths+1preview-directory string=28Game strings; all27package files exist. A21426-row table has5actualasset paths omitted and4stale table-only paths, plus the directory difference, so not a one-row discrepancy. Full lists/JSON pointers in C320_profile_path_count_comparison.json. No profile edits; disk presence not class/load proof. I will now execute the already released C320 single in-memory authoring run under the new baseline, unless a newer reassignment arrives.'''
(R/'MESSAGE_RUN_DELIVERY.txt').write_text(message,encoding='utf-8')
entry='\n\nDD29 C319 measured 2026-10-29 / lead review pending:3newSource files promoted,216total/all213old unchanged; editor build exit0,NO UHT,3warnings. Focused ActivationWorld5/Activation6/WorldPreparation4/Registry3 all18passed; full182uniqueSuccess retains177+exact5,CookCoverageSuccess,0Error/fatal/ensure/assertion,GIsCriticalError0. Warning multiset63 equalsDD28;104pins/HEADbc3fe6a stable,EXE unchanged. Evidence Docs/BossCombatReview/Execution/Codex/DD29/run_2026-10-29/RUN_REPORT_TO_CLAUDE.md. DD29final216manifest/binaries are new C320 baseline. KI138: GetOwnedComponentCount production-public outside dev guard, TUniquePtr/header compiled in Editor (not Shipping), DD28/new header reopen same RPGBossActivation namespace. Library never-begun composition only; no startup/Ready/suppression/reservation/gameplay proof. C321 locks applied to remaining launches on receipt. No retry/git mutation.\n'
for name in ('TASKS.md','DECISIONS.md','TEST_PLAN.md','KNOWN_ISSUES.md'):
    with (ROOT/'Documentation'/name).open('a',encoding='utf-8') as f:f.write(entry)
with (H.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:f.write(entry)
files=[p for p in R.rglob('*') if p.is_file() and p.name not in ('evidence_sha256.txt','MESSAGE_RUN_DELIVERY.txt')]
files += [H/n for n in ('promote_and_capture.py','prepare_run_helpers.py','check_gate.py','finish_capture.py','engine_lock.py','freeze_gate.py','compare_C320_path_counts.py','report_run.py','post_source_manifest_sha256.txt')]
files += [H.parent/'CURRENT_ENGINE_BASELINE.json']
(R/'evidence_sha256.txt').write_text(''.join(f'{sha(p)} *{os.path.relpath(p,R).replace(chr(92),chr(47))}\n' for p in sorted(files)),encoding='utf-8')
print(json.dumps({'receipts':len(files),'receipt_sha256':sha(R/'evidence_sha256.txt'),'full_unique':182,'focused_unique':18,'report_sha256':sha(R/'RUN_REPORT_TO_CLAUDE.md')}))
