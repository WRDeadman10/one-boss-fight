# DD18 larger integration batch for Claude

Direct owner requests substantially more Claude work. Finish and deliver the DD17 lifecycle correction X284 FIRST, preserving true before-revision bytes. Then continue this complete SOURCE-ONLY implementation batch without waiting for routine acknowledgments. DD17 review remains a gate before any execution; no build or automatic retry is released.

## Exclusive files

SIX NEW files only: Player/RPGBossWorldPreparation.h/.cpp, Player/RPGBossPreparationRegistry.h/.cpp, Tests/RPGBossWorldPreparationTests.cpp and Tests/RPGBossPreparationRegistryTests.cpp, under Source/OneBossFight. No existing Source edits beyond DD17's already released correction. Save full185 baseline AFTER that revision and BEFORE creating these files. Final191manifest preserves every prior185 byte. Pin exact dependencies. Missing indispensable seams require an exact proposed delta, not silent scope expansion. No overlap with AG staged Python files.

## A. Actual world-bound preparation facade

Implement explicitly called PrepareWorldBatch(World, Binding, Selections, ManifestHash), returning a move-only result with Errors and uniquely owned prepared artifact only on full success. Compose accepted CompileWorldInput and DD15 PrepareBatch. No caller epoch/config/plan/callback, manufactured fallback or duplicated validator logic. Preserve nested layer diagnostics. Nothing auto-calls this API.

Recheck exact world/GI/published epoch, binding identity/world/GUID/snapshot/lifecycle and participant identities around both stages. A failed final check aborts precisely this call's allocations and appends cleanup errors; no artifact escapes and no earlier independent artifact is damaged. Return-value ownership avoids stale out parameters. Game-thread lifetime only. Inherit explicit native bAutoRegister/uncollected-name-reuse limitations, not protection against external registration.

Read-only summaries and Abort/destructor ownership only. No Register/Commit/Activate/Ready, BindEncounter, participant component, legacy disposition or target/reset operation. Manifest hash/rows remain caller-supplied even though epoch comes from GI. No new UCLASS/subsystem/process-static world map.

## B. Explicit registry-scoped reservation and lifetime

Implement a noncopyable explicitly owned per-world preparation registry with TryPrepareAndReserve(Binding, Selections, ManifestHash). Registry owns the artifacts and returns move-only lease tokens with registry identity, unique serial/nonce and encounter identity. A token surviving registry destruction must be safe: private shared state plus weak token ownership or equivalent; never a dangling raw registry pointer. Game-thread-only lifetime explicit.

Refuse duplicate encounter GUID and overlapping actor ownership across ALL roles inside this registry, target-only included. Two different disjoint encounters coexist; identical slot strings across different encounters are legal. One batch can contain two bosses and one target. This is per-registry scope, not a global uniqueness claim across arbitrary separately created registries; a future coordinator must own the authoritative instance. Do not edit context ownership to force integration.

Pre-check conflicts before consumer allocation; publish registry GUID/actor entries only after whole-batch compile/preparation and final identity checks succeed. Failure leaves all previous reservations/artifacts intact and no provisional entries/allocations from this attempt. Guard same-registry reentrant admission without caller callbacks. Distinguish invalid inputs, conflicts, world/epoch/binding drift, preparation errors and contract violations. Validate tokens by registry identity and serial, never GUID alone. Stale/wrong-registry/repeated release cannot destroy replacement resources.

Release or lease destruction aborts exactly its owned unregistered artifact, freeing indices only after clean cleanup. Registry destruction closes admission, cleans all artifacts once and safely invalidates surviving tokens. External registration/begun/reownership cleanup failure leaves a quarantined reservation with diagnostics; do not silently reopen admission or claim rollback. No auto unregister/repair/delete. No UObject cleanup from worker destruction; define safe refusal/violation behavior. World/owner destruction cannot dereference stale identities.

This reserves only an INCOMPLETE UNREGISTERED native subset. It does not publish combat context, hydrated Ready, successful activation, full playable bundle or authority to suppress legacy attachment. No production component registration.

## C. Substantial actual tests

Use real test-local UGameInstance/catalog lifecycle and production-compatible transient definitions/native character meshes/animation leases as DD17. No injected Legacy epoch, process cvar changes or authored assets. Copy needed cpp-local fixture setup without editing previous helpers. Unsupported positive setup is failure, not a mock substitution.

WorldPreparation tests: successful two-boss+target10components; exact actual GI epoch/configs/per-owner values; all managed consumers unregistered/uninitialized/not-begun/unticked; explicit/scope abort restores components/context/mesh/dirty state after legitimate loads; invalid late member allocates nothing; real later name collision cleans earlier participants; retry removes only fixture-owned blocker; second independent preparation refuses without damaging first.

Registry tests: two disjoint encounters coexist; duplicate GUID with disjoint actors rejected; same slot strings across encounters accepted; overlap of boss and target actors rejected; failed late preparation preserves existing reservation; clean release allows same actors/GUID with NEW serial; repeated/stale/wrong-registry token cannot release replacement; lease dies first; registry dies first; actor/world dies first; safe off-thread refusal. Snapshot actual object sets/context/counts before/after. Prefer actual partial allocation/name collision to generic injection. No tests that only mirror constants.

Epoch/binding drift or reentrancy not safely exercisable without author callbacks must be labeled source-checked/unexercised. No arbitrary callback/cvar framework. External-registration quarantine is optional to test now: if exercised, show the exact test-owned isolated registration delta for lead review and do not begin gameplay. Otherwise state the gap; production must still fail closed. No unsafe worker destructor experiment.

## D. Integrated delivery/gates

Deliver actual source/diffs/Review191manifest/native constructor+catalog+compiler+adapter+preparation and asset pins/SHA receipts, exact test names and ownership/failure matrix distinguishing executed/source-only cases. No extra design proposal or repeated baseline tests instead of implementation. Preserve intermediate source/review deltas and failures.

May deliver DD17 revision, then facade, then registry/tests as actual code chunks while continuing nondependent work. Rejected ownership invariants must be fixed before extending dependent code. Independent source review of the whole batch before any build; then lead issues one serialized focused/full verification order. No automatic compiler fix rounds.

No old Source edits, engine/PIE/driver gate/package/noneditor execution, assets/scripts/config/pack/git changes, startup hooks, context publication, actual activation, target/reset wiring or legacy suppression. Claude remains sole later engine operator, AG only later specifically approved-batch git operator. All83/networking required; A5visuals parked. This larger batch advances input -> owned preparation -> scoped reservation lifetime, not final framework completion.
