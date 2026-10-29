# C225 DD11 source acceptance and bounded verification release

Verdict: ACCEPT SOURCE ONLY. Claude may perform fresh safety checks, UHT/editor build, focused DormantWake automation, and the full suite only after the focused run passes cleanly. This is not an engine result or approval to wire the plan.

## Independently verified artifacts

Read the complete new adapter header/implementation and all 891 test lines, existing-file diff, compiler control flow and native header/BeginPlay/EndPlay. Recomputed all21 delivery receipts, all174 current Source hashes,33 dependency pins, all6 Review/live pairs and3 preimages. Pre-source manifest matches the accepted DD10 final manifest. Exactly3 added and3 changed files, no deletion;168 preexisting files unchanged. Native DormantWake.cpp remains unchanged.

Machine-readable offline checks: `C225_DD11_INDEPENDENT_SOURCE_CHECKS_2026-10-28.json`. This script verified files, not Unreal behavior.

| Accepted file | SHA256 |
|---|---|
| RPGBossDormantWakeAdapters.h | d350a4c62c65300c32c4395f2869b78b8187f562a82581a51dccaedcdbcaccfa |
| RPGBossDormantWakeAdapters.cpp | 80e6f9f4797c5bfea3f6fc4dc2c6ec074f998efec3cb495e554c8b5cd9a6ee55 |
| RPGBossDormantWakeAdaptersTests.cpp | df8463259f9d8da3d7f393777fa2a0766d021fe662729c3af0a6e5b67cf5e0ed |
| RPGEncounterBinding.h | ce0a7da73e833a22aef8ad69e3ed42984b39b04131997d78f055f4a4070d9c92 |
| RPGEncounterBinding.cpp | c7255051e5f6be46db5b5caa0351cf45e50c3c07c4c0a8085fd3d71b633df828 |
| RPGBossDormantWake.h | ff450db792f59af3bab6ff73464d1dfe360f27003b268c0f574b58124f05f83c |

Diff SHA256 `908071006b25ae57aef0e7cce0a7d58bec13454b592daebba3bc080e4541da27`. Original preimages and first-state review bytes remain preserved. Observed old DLL `837ce607790f5b55de52214969d86a0dd9dd3c9824960f29c6cc1788c4b7438b`; EXE `5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65`. Those are historical pins after a build, not inherited DD11 results.

## Source findings

Accept the exact exported forward declaration plus qualified friend. It opens only ConfigureDormantWake to the two existing private soft references; native fields remain private. Both declarations have the same signature. No confirmed source-level compile defect found, but UHT/MSVC acceptance is pending actual execution. No speculative fallback is authorized.

The compiler calls the shared validator before output allocation and before production dependency loads. Prior checks and output reset remain. It copies the typed record on production and synthetic paths. Adapter guards lifecycle/class/owner before whole-record validation, then assigns exactly two soft paths. No registry query, load, reflective runtime setter, cvar mutation, creation, registration, timer, state mutation or activation. Plan class/name and two required fields match the legacy attachment; no DD5 insertion.

Required refs, reused Missing/Malformed tokens, native LF preservation and local validator repetition are accepted within X259. Structural path limits remain: this is not the engine's authoritative path grammar and does not reject every malformed name. An empty mount/multiple dots may pass. No new path-domain restriction or tuning approval is inferred.

Tests exercise distinct records, ignored manifest Value, whole-record no-write, component-set boundaries after fixture setup, isolation, lifecycle guards, real synthetic compiler copy, production early rejection, retained checks, declared reflection/defaults and default-path presence observations. The begun fixture clears two soft refs on an isolated plain actor, verifies no encounter, then dispatches BeginPlay. Native BeginPlay loads only those null refs and finds no encounter; no real wake is requested. Test-local reflection does not enter the adapter. Owner-destroying/beginning branches, wake start time and montage handles are not directly witnessed. Null cached refs and before/after package/object presence do not prove absence of every transient allocation/load or prove anything for already-loaded assets.

## Claude verification order

1. Fresh operator safety check using the established workflow; if any active job or unsafe editor/content state exists, preserve it and report rather than interfering. Freeze the six accepted source pins, full174-file manifest and dependencies before running. No unrelated source changes.
2. Reviewed Rebuild/NoRelaunch workflow for editor build and required UHT. Capture actual commands, raw UHT invocation/output, compiler output, exit/job records, elapsed results, all warnings/errors and pre/post binaries. Header changes make UHT expected, not certified until the raw invocation exists.
3. Run ONLY `OneBossFight.Binding.DormantWake`. Six source registrations are Assign, Validation, Isolation, Rejections, Compile, Authoring. Require actual discovery/completions, unique paths, all Success, no fatal/ensure/unsupported fixture/observer failure.
4. ONLY IF clean, run full `OneBossFight` automation on the same unchanged source/binary. Expected101 is not an assumed result: independently report prior95 membership plus exact6, no duplicate/missing/failing paths and CookCoverage Success. Preserve raw logs, warning categories, job exits, final full-source/dependency manifests, binary SHA256 and a receipt index.

Stop on any failure, drift or unsupported precondition; preserve the first failing source and raw logs before reporting. No automatic compiler-fix rounds, export removal, friend-struct fallback, test weakening, filter change or PIE fallback. Submit the exact proposed minimal delta for review if needed. Do not claim UHT from an incremental build without its invocation.

No PIE, full driver gate, package/noneditor, content/script/config/pack edits, reservation, hydration, wiring/Ready/legacy suppression or activation. DD10 acceptance retains every historical failure/provenance limit. AG X260 correction continues offline; no staging/commit/push release until stable accepted shared bytes and a separately reviewed exact batch.
