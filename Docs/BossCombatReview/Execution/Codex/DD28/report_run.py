from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[4];R=H/'run_2026-10-29'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
final=json.loads((R/'final_verification.json').read_text());assert final['source_exact'] and final['source_count']==213
tags=('activation','preparation','registry','world_preparation','production_preparation','full_dd28')
gates={tag:json.loads((R/f'{tag}_gate.json').read_text()) for tag in tags}
assert all(r['pass'] for r in gates.values())
rows=[]
for tag,g in gates.items():
    rows.append(f'| {tag} | {g["unique"]} / {g["completed"]} | {g["job"]["exit_code"]} | {g["job"]["seconds"]} | `{sha(R/f"automation_{tag}.log")}` |')
full=gates['full_dd28'];build=final['build']
report=f'''# DD28 C315 measured registration verification — 2026-10-29

Promoted ONLY accepted preparation.h/.cpp plus new Tests/RPGBossActivationTests.cpp. Source212->213: two existing files changed,210 prior files unchanged,one addition. No other Source/config/content change. New class member and batch-owned registration/Abort flag remain library-only, with no gameplay/startup caller. Claude independent result review pending.

## Fresh safety and build

Before promotion: exact DD26 212-file manifest; all104 accepted dependency/candidate/catalog/native/source pin entries rehashed against DD26's verified actual bytes (historical replacement statuses retained explicitly); DLL/EXE equal DD26 final; HEADbc3fe6a; tracked Source/Content/Config clean; no engine/compiler. Staged three pins and accepted preimages matched. After promotion, exact213 manifest frozen. Before build, manifest, pins, HEAD, binaries and processes checked again. Every gate rechecks Source/HEAD/pins; each engine launch refuses preexisting engine/compiler jobs. No process was killed.

ONE editor Development build, exit0,13s. Actual incremental build had NO UHT invocation/reflection-generation lines; contrary to the expectation in C315, UHT was not run. No claim or forced rerun. Raw build SHA256 `{build['raw_sha256']}`. Eleven actions include preparation and new Activation test compilation and affected unchanged test units, link and metadata. Three build Warning lines preserved: UnrealClaude missing Niagara and NiagaraEditor plugin dependency declarations, and non-preferred Visual Studio compiler. No build Error line.

## Actual automation

Each focused gate passed before launching the next; full launched only after all five were clean. Exact source-declared name membership, raw discovery/filter, unique completions, job exit0, Error0, GIsCriticalError0 and no fatal/ensure/assertion/unsupported lines were checked for every gate. Trailing dots distinguish Preparation. from PreparationRegistry.

| Gate | Unique / completed Success | Exit | Seconds | Raw log SHA256 |
|---|---|---|---|---|
{chr(10).join(rows)}

Focused union22 disjoint names. Full177uniqueSuccess retains all171 DD26 paths with zero missing and EXACTLY six new Activation names; CookCoverage Success. Full warning multiset63 exactly matches DD26 after the established timestamp/epoch/sponsor-PID normalisation: zero additions/removals. All jobs, raw logs, exact names and gates retained; no failures, fixes or retries occurred in this DD28 run.

## What the six new tests exercise

Success: two bosses register twelve components each in independent expected class order, none begun; target and binding/Ready context counts unchanged. NotGameThread: named refusal, no UObject/state mutation. OwnerBegun: late second owner explicitly dispatched BeginPlay as a negative control AFTER preparation while its components remained unregistered; whole batch refused before any registration, then aborted/destroyed all24. This test's actor BeginPlay control is not gameplay/registered-component BeginPlay proof. StateRefusals: repeated registration preserves the first success; aborted artifacts refused. InjectedFaults: every ordinal1..24 fails AFTER a real registration, then reverse unregister plus Abort destroys all24, restores captured actor/context state and leaves no managed class on any actor. Lifetime: own-registration Abort and repeat are clean; the EXISTING destructor's Abort also restores actors. Existing Preparation6/Registry3/WorldPreparation4/ProductionPreparation3 sources remained UNMODIFIED and passed, including their external-registration ContractViolation branch.

Prevalidation failure consumes the batch via Abort: callers must treat it as gone and take their existing fallback decision, not reuse it. Thread/state refusals preserve an existing success. IsRegistered records the successful batch transition, not continuous monitoring of engine state. External BeginPlay/ownership transitions remain contract violations, not magically reversible gameplay.

This is the first measured registration of all seven newer classes in the never-begun fixture. Their lack of project OnRegister/InitializeComponent overrides remains the source finding; tests prove the observed registered/not-begun shape and cleanup, not an exhaustive engine asset-load/timer side-effect trace.

## Final pins and count clarification

DLL `{final['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']}`. EXE unchanged `{final['binary']['Binaries/Win64/OneBossFight.exe']}`. Source213 hashes equal frozen post-promotion manifest. All104 dependency/candidate/catalog/native pin comparisons equal (C315 exact preparation replacements accounted for), HEADbc3fe6a unchanged; post-run engine/compiler list empty. final_source_manifest_sha256.txt and final_binary_sha256.txt are the required NEW baseline for future separately released DD27-family engine runs. CURRENT_ENGINE_BASELINE.json points to these measured artifacts, replacing DD26 as the current expected Source/binary baseline; it is not execution permission.

Diff counting: header44 additions consists of40 nonblank+4 blank; cpp167 consists of164 nonblank+3 blank;0 removals. Thus both C315's40/164 and X324's44/167 are the same exact diff under nonblank versus all-added-line counting, not a changed delta. diff_count_convention.json records both.

Limits: isolated synthetic-config/legacy-epoch never-begun registration and cleanup only. No registered component BeginPlay/tick, live binding/readiness/reservation/legacy suppression/startup, authored boss definition, real combat/PIE, packaging/performance proof. Original DD27 failures, DD27b missing pre-state and other historical provenance limits remain preserved. No commit/push/history write.
'''
(R/'RUN_REPORT_TO_CLAUDE.md').write_text(report)
message=f'''C315 DD28 PROMOTION+VERIFICATION completed, measured review pending. Only3 accepted Source files promoted:212->213,210 prior files unchanged. Fresh pre-promotion and pre-build Source/pins/HEAD/binary/process checks passed;104 dependency/candidate/catalog/native/source pin entries verified; no job interference.
ONE editor build exit0/13s,3 Warning lines (Niagara/NiagaraEditor plugin dependencies and compiler advisory),0errors. NO UHT invocation in the actual incremental build; I did not force one or claim one. Focused Activation6 -> Preparation6 -> PreparationRegistry3 -> WorldPreparation4 -> ProductionPreparation3 all uniqueSuccess and exact source membership (22 total), then full177 uniqueSuccess: all prior171 retained+exact6 Activation, CookCoverageSuccess,0Error/fatal/ensure/assertion, GIsCriticalError0. Full warning multiset63 equals DD26 (zero added/removed). No failure/fix/retry. Existing four suites remain UNMODIFIED.
Raw build SHA256 {build['raw_sha256']}; full log SHA256 {sha(R/'automation_full_dd28.log')}. Evidence Codex/DD28/run_2026-10-29/RUN_REPORT_TO_CLAUDE.md with all raw gates/jobs/names/pins/manifests. Final DLL {final['binary']['Binaries/Win64/UnrealEditor-OneBossFight.dll']}; EXE unchanged.213Source/pins/HEADbc3fe6a stable,post-process empty. Future DD27-family preflights now MUST use DD28 final_source_manifest_sha256.txt / final_binary_sha256.txt (CURRENT_ENGINE_BASELINE.json records this), not DD26.
Diff count clarified: header44=40nonblank+4blank,cpp167=164nonblank+3blank,0removed; same accepted bytes. KI137 now states prevalidation failure Aborts/consumes batch and first measured never-begun registration of seven new classes. Negative OwnerBegun control dispatches actor BeginPlay only while all prepared components remain unregistered; registration never begins any owned component. Library-only/no caller, no ticking/binding/Ready/reservation/suppression/startup/authored definition/gameplay claim. DD27 failures remain preserved. Await independent acceptance/next exact release.'''
(R/'MESSAGE_RUN_DELIVERY.txt').write_text(message)
entry='\n\nDD28 C315 measured 2026-10-29 / lead review pending: accepted3files promoted,Source213 stable; one incremental editor build exit0,NO UHT invocation,3warnings. Focused Activation6/Preparation6/Registry3/WorldPreparation4/ProductionPreparation3 allpassed; full177uniqueSuccess=prior171+exact6,CookCoverageSuccess,0Error/fatal/ensure/assertion,GIsCriticalError0. Warning multiset63 unchangedvsDD26;104pins/HEADbc3fe6a stable,EXE unchanged. Evidence Docs/BossCombatReview/Execution/Codex/DD28/run_2026-10-29/RUN_REPORT_TO_CLAUDE.md. Future engine-Python baseline is DD28 final213manifest/binaries, not DD26. KI-137: PREvalidation failure Aborts/consumes batch; first measured never-begun registration of all7newclasses, not complete engine-side-effect tracing. No runtime caller/BeginPlay/tick/binding/Ready/reservation/suppression/startup/authored-definition/gameplay/PIE/package proof. Existing suites unmodified; no retry/git writes.\n'
for name in ('TASKS.md','DECISIONS.md','TEST_PLAN.md','KNOWN_ISSUES.md'):
    with (ROOT/'Documentation'/name).open('a',encoding='utf-8') as f:f.write(entry)
with (H.parent/'CURRENT_TASK.md').open('a',encoding='utf-8') as f:f.write(entry)
exclude={'evidence_sha256.txt','MESSAGE_RUN_DELIVERY.txt'}
files=[p for p in R.iterdir() if p.is_file() and p.name not in exclude]
files += [H/n for n in ('promote_and_capture.py','check_gate.py','finish_capture.py','report_run.py','post_source_manifest_sha256.txt')]
files += [H.parent/'CURRENT_ENGINE_BASELINE.json']
rows=[]
for p in sorted(files):
    rel=__import__('os').path.relpath(p,R).replace('\\','/')
    rows.append(f'{sha(p)} *{rel}')
(R/'evidence_sha256.txt').write_text('\n'.join(rows)+'\n')
print(json.dumps({'receipts':len(rows),'receipt_sha256':sha(R/'evidence_sha256.txt'),'full_unique':177,'focused_unique':22,'report_sha256':sha(R/'RUN_REPORT_TO_CLAUDE.md')}))
