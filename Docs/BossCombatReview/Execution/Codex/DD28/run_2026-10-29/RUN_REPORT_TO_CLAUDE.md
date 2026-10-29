# DD28 C315 measured registration verification — 2026-10-29

Promoted ONLY accepted preparation.h/.cpp plus new Tests/RPGBossActivationTests.cpp. Source212->213: two existing files changed,210 prior files unchanged,one addition. No other Source/config/content change. New class member and batch-owned registration/Abort flag remain library-only, with no gameplay/startup caller. Claude independent result review pending.

## Fresh safety and build

Before promotion: exact DD26 212-file manifest; all104 accepted dependency/candidate/catalog/native/source pin entries rehashed against DD26's verified actual bytes (historical replacement statuses retained explicitly); DLL/EXE equal DD26 final; HEADbc3fe6a; tracked Source/Content/Config clean; no engine/compiler. Staged three pins and accepted preimages matched. After promotion, exact213 manifest frozen. Before build, manifest, pins, HEAD, binaries and processes checked again. Every gate rechecks Source/HEAD/pins; each engine launch refuses preexisting engine/compiler jobs. No process was killed.

ONE editor Development build, exit0,13s. Actual incremental build had NO UHT invocation/reflection-generation lines; contrary to the expectation in C315, UHT was not run. No claim or forced rerun. Raw build SHA256 `2729516421aafba74e0f8b96bdc4d01b4961dc991ce4fe5b276d98a1353919a8`. Eleven actions include preparation and new Activation test compilation and affected unchanged test units, link and metadata. Three build Warning lines preserved: UnrealClaude missing Niagara and NiagaraEditor plugin dependency declarations, and non-preferred Visual Studio compiler. No build Error line.

## Actual automation

Each focused gate passed before launching the next; full launched only after all five were clean. Exact source-declared name membership, raw discovery/filter, unique completions, job exit0, Error0, GIsCriticalError0 and no fatal/ensure/assertion/unsupported lines were checked for every gate. Trailing dots distinguish Preparation. from PreparationRegistry.

| Gate | Unique / completed Success | Exit | Seconds | Raw log SHA256 |
|---|---|---|---|---|
| activation | 6 / 6 | 0 | 23 | `d0e3749981a94c839719b393fb0cba41fec9d676b2f927af251819e633006467` |
| preparation | 6 / 6 | 0 | 21 | `1f102d03c2cca6d9944aa718a7a53f52f4e81295dd722b533fafa75641489a8b` |
| registry | 3 / 3 | 0 | 24 | `07211d04c274d7a488a2797efe9fb2ca3686e3157edbb15ff9d07250a8f1ff9c` |
| world_preparation | 4 / 4 | 0 | 23 | `59cc2a47fb2be13bf4fbfc60038de0d3638b08a8ad3e53e3ce5ace17739ab8c8` |
| production_preparation | 3 / 3 | 0 | 21 | `6fbd6954ec4dd63ec36ad18aaaed053c95da14c56957c9b6debe399346562a68` |
| full_dd28 | 177 / 177 | 0 | 27 | `90fc79877cd9bdba29c7613639e97c886c25d0e0b4501948945f8fa0cf0d2577` |

Focused union22 disjoint names. Full177uniqueSuccess retains all171 DD26 paths with zero missing and EXACTLY six new Activation names; CookCoverage Success. Full warning multiset63 exactly matches DD26 after the established timestamp/epoch/sponsor-PID normalisation: zero additions/removals. All jobs, raw logs, exact names and gates retained; no failures, fixes or retries occurred in this DD28 run.

## What the six new tests exercise

Success: two bosses register twelve components each in independent expected class order, none begun; target and binding/Ready context counts unchanged. NotGameThread: named refusal, no UObject/state mutation. OwnerBegun: late second owner explicitly dispatched BeginPlay as a negative control AFTER preparation while its components remained unregistered; whole batch refused before any registration, then aborted/destroyed all24. This test's actor BeginPlay control is not gameplay/registered-component BeginPlay proof. StateRefusals: repeated registration preserves the first success; aborted artifacts refused. InjectedFaults: every ordinal1..24 fails AFTER a real registration, then reverse unregister plus Abort destroys all24, restores captured actor/context state and leaves no managed class on any actor. Lifetime: own-registration Abort and repeat are clean; the EXISTING destructor's Abort also restores actors. Existing Preparation6/Registry3/WorldPreparation4/ProductionPreparation3 sources remained UNMODIFIED and passed, including their external-registration ContractViolation branch.

Prevalidation failure consumes the batch via Abort: callers must treat it as gone and take their existing fallback decision, not reuse it. Thread/state refusals preserve an existing success. IsRegistered records the successful batch transition, not continuous monitoring of engine state. External BeginPlay/ownership transitions remain contract violations, not magically reversible gameplay.

This is the first measured registration of all seven newer classes in the never-begun fixture. Their lack of project OnRegister/InitializeComponent overrides remains the source finding; tests prove the observed registered/not-begun shape and cleanup, not an exhaustive engine asset-load/timer side-effect trace.

## Final pins and count clarification

DLL `82c2903228c084799453ebc87ce3d92b2b929b028827ea3ba251ff61a68ce72a`. EXE unchanged `5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65`. Source213 hashes equal frozen post-promotion manifest. All104 dependency/candidate/catalog/native pin comparisons equal (C315 exact preparation replacements accounted for), HEADbc3fe6a unchanged; post-run engine/compiler list empty. final_source_manifest_sha256.txt and final_binary_sha256.txt are the required NEW baseline for future separately released DD27-family engine runs. CURRENT_ENGINE_BASELINE.json points to these measured artifacts, replacing DD26 as the current expected Source/binary baseline; it is not execution permission.

Diff counting: header44 additions consists of40 nonblank+4 blank; cpp167 consists of164 nonblank+3 blank;0 removals. Thus both C315's40/164 and X324's44/167 are the same exact diff under nonblank versus all-added-line counting, not a changed delta. diff_count_convention.json records both.

Limits: isolated synthetic-config/legacy-epoch never-begun registration and cleanup only. No registered component BeginPlay/tick, live binding/readiness/reservation/legacy suppression/startup, authored boss definition, real combat/PIE, packaging/performance proof. Original DD27 failures, DD27b missing pre-state and other historical provenance limits remain preserved. No commit/push/history write.
