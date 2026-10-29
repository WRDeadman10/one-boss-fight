# DD18 larger integration batch: SOURCE ONLY (Claude, 2026-10-28, order X-285 / Codex/DD18_LARGE_WORLD_PREPARATION_BATCH.md)

Nothing was built: no UHT, no build, no automation, no engine process, no git operation, no asset load, no Content/Config/Script/existing-Source edit. The DD17 X-284 revision was delivered first (C-245, Claude/DD17/17_REVISION_X284.md) and the 185-file baseline below was saved AFTER it and BEFORE any DD18 file existed.

## The six new files (CRLF, 0 bare LF/CR; only the two pack class /Game/ literals, in each test file, as DD14/DD16/DD17)
- `Player/RPGBossWorldPreparation.h` 47 lines `8a71cdf98fe3063c9ac48e17cc02a295f06bf4ef719cc99d0875814c48898933`
- `Player/RPGBossWorldPreparation.cpp` 198 lines `ce6a1b31dfb2e80f9439766d25f9ac77a5b6a2b8c05721264c30dcba3e0e417c`
- `Player/RPGBossPreparationRegistry.h` 163 lines `d9d813c7711e5ccdeba1e8a063c1adc44d76ae4ad6986f5d4d826ffa62f4ddd2`
- `Player/RPGBossPreparationRegistry.cpp` 524 lines `253a47f47f3812d1c4754dea9c36620e59923347e3d359b807682c9fbe26792c`
- `Tests/RPGBossWorldPreparationTests.cpp` 935 lines `fb867b159223253d756e6a07e0d44a45378ea99f0c6f8eb3e606b95b8eb1ec90`
- `Tests/RPGBossPreparationRegistryTests.cpp` 969 lines `38729988591eadbb313a79fc1d4f002a4c02dcc56553398d95777468cbc2368a`
Diff `six_file.diff` sha256 `d12f305ad75f599ee44b5d5b6ad909e3b1890441c6a97da0c6badc2f109762b0`; `Review/` holds the final copies, the states before the independent review and the edit deltas. Manifest 185 -> 191: `manifest_diff.txt` is exactly six added lines and ZERO changed or removed old lines (every prior 185 byte preserved). 24/24 pins, 13/13 dependency pins (preparation, input compiler, preflight, binding, catalog, the DD17/DD16/DD14 tests), 14/14 candidate assets, 7/7 default catalog assets, ForWorld/Initialize line-range pins (copied from DD17) verify; HEAD 79d55906 and both binaries (DLL 3009ff5f..., exe 5495fb88...) unchanged; no engine/build process.

## A. `RPGBossWorldPreparation::PrepareWorldBatch(World, Binding, Selections, ManifestHash)` -> `FRPGWorldPreparationResult {Errors, TUniquePtr<FRPGPreparedBatch> Batch}` (move-only)
Composes the accepted `CompileWorldInput` (epoch only from the world's own game instance, production configs, whole-batch preflight) and DD15 `PrepareBatch`. No caller epoch/config/plan/callback, no fallback, no duplicated validator (every input and layer diagnostic is the nested diagnostic of its stage: `WorldInput.*`, `Preflight.*`, `Preparation.*`; `WorldPrep.*` only for the facade's own checks). Game thread only (refused before any UObject access). One facade-local checkpoint (world, game instance, the ForWorld epoch pointer == the very lease of the compiled input, the binding through a retained weak reference: valid, not destroying, in the world, not begun, same GUID, same participants matching the compiled input request by request, every member actor/definition valid, in the world, not begun) runs after the input stage and after the preparation stage; a failure after the preparation aborts precisely this call's components and appends the cleanup errors (`WorldPrep.Drift`, `WorldPrep.CleanupAfterDrift`, `WorldPrep.ContractViolation`); no artifact escapes; an earlier independent artifact is never touched. Read-only summaries and Abort/destructor ownership only; no Register/Commit/Activate/Ready, BindEncounter, participant component, legacy disposition or target/reset operation; no UCLASS, subsystem or process-static map.
Judgement call: DD17's `Checkpoint` is private to its .cpp; reusing it would need an exported seam in a file not released for edits. Instead of a seam the facade re-implements the identity checks it needs locally (small, listed above). The exact optional delta that would remove that duplication (NOT applied): export `RPGBossWorldInputCompiler::FCheckpointContext` with `Capture(World, Binding)` and `bool Holds(FString& Why)` wrapping the existing anonymous `Checkpoint`, and have the facade call it; this needs your release because it edits the DD17 files.

## B. `FRPGBossPreparationRegistry(UWorld*)`, `TryPrepareAndReserve(Binding, Selections, ManifestHash)`, `Release(Token&)`, move-only `FRPGPreparationLeaseToken`
Per-world, non-copyable, non-movable, explicitly owned; no global registry/subsystem/hook. Private shared state (`FRPGPreparationRegistryState`, global-scope struct in the .cpp) held by the registry as `TSharedRef` and by tokens as `TWeakPtr` only: a token that outlives the registry is invalid and safe. Tokens carry the registry GUID, a never-reused serial starting at 1 and the encounter GUID; validation is by registry identity AND serial (and the GUID must match the entry), never by GUID alone. Admission: game thread only (else `Reservation.NotGameThread`, ContractViolation, nothing touched); closed registry refused; same-registry re-entry refused (`bAdmitting`, RAII); world and binding checked; conflicts BEFORE any allocation: a duplicate encounter GUID or any actor of ANY role already reserved (quarantined reservations still reserve) -> `Reservation.DuplicateEncounter` / `Reservation.ActorConflict` (Conflict); then `PrepareWorldBatch`; then a final gate (registry still open, same world, artifact matches the encounter, no conflict: a defence, because the admission guard makes a change impossible) and only then the entry (serial, GUID, weak actors of all roles, the artifact) is published; any failure leaves every earlier reservation untouched and no provisional entry. Failure families: InvalidInput, Conflict, Drift, PreparationFailed, ContractViolation (classified by token prefix; the nested diagnostics are returned unchanged). Release (registry or token, same code): game thread only, wrong registry refused untouched, stale/consumed/repeated Stale (token cleared), otherwise `Abort()` of exactly the entry's artifact; the entry (GUID and actors) is freed ONLY after a clean abort; a not clean abort QUARANTINES (entry kept with diagnostics, the artifact reset, token consumed, admission not reopened, no rollback, repair or deletion claimed). A cleanup failure during admission also publishes a quarantined entry. Registry destruction: closes admission first, aborts every Active artifact once on the game thread (unclean aborts are logged), clears the entries; tokens become invalid. Off the game thread: mutations refused, reads neutral; destroying a held token or the registry off-thread is flagged (ensure), does no UObject cleanup and is NOT experimented with. Dev-only `FRPGPreparationLeaseToken::ForgeForTest` (WITH_DEV_AUTOMATION_TESTS) exists only to prove serial-based validation. A reservation is an incomplete unregistered native subset per registry, not a global uniqueness claim, not a context, not Ready, no authority to suppress a legacy attachment.

## C. Tests (expected 3 + 1 + 3 = 7; suite 129 only as an expectation until a released run); real UGameInstance lifecycle copied from DD17 (InitializeStandalone, Shutdown, DestroyWorldContext, DestroyWorld; startup cvars read, logged and required at their defaults, never changed); no Legacy epoch, no mock, no author callback
WorldPreparation (`OneBossFight.Binding.WorldPreparation.*`): `PositiveAndAbort`, `LateInvalidAndCollision`, `SecondPreparation`, `Refusals`.
PreparationRegistry (`OneBossFight.Binding.PreparationRegistry.*`): `AdmissionAndConflicts`, `ReleaseAndTokens`, `Lifetime`.

### Ownership / failure matrix (EXECUTED = asserted by a test once released; SOURCE-ONLY = not executable safely, checked in code only)
| Case | Where | Status |
|---|---|---|
| two bosses + target, 10 components, GI epoch lease, per-owner values, unregistered/uninitialized/not begun/unticked | WorldPreparation.PositiveAndAbort | EXECUTED |
| explicit abort and scope-exit abort restore components/context/mesh/dirty after the loads | PositiveAndAbort | EXECUTED |
| invalid late member allocates nothing (preflight layer) | LateInvalidAndCollision | EXECUTED |
| real later name collision cleans earlier participants; blocker kept; only the blocker removed; retry succeeds | LateInvalidAndCollision | EXECUTED |
| second independent preparation (new binding, then same binding) refused, first undamaged; prepares again after abort | SecondPreparation | EXECUTED |
| facade refusals (no world, no binding, bad hash, missing selection, off-thread) + control | WorldPreparation.Refusals | EXECUTED |
| two disjoint encounters coexist, identical slot strings | Registry.AdmissionAndConflicts | EXECUTED |
| duplicate GUID with disjoint actors; target overlap; boss overlap; cross-role overlaps | AdmissionAndConflicts | EXECUTED |
| no binding; bad manifest hash (InvalidInput) | AdmissionAndConflicts | EXECUTED |
| failed late preparation preserves reservations; same encounter admitted after the blocker is removed | AdmissionAndConflicts | EXECUTED |
| clean release; re-admission with a NEW serial; repeated/consumed, forged-old-serial, forged-GUID, wrong-registry tokens cannot release the replacement | Registry.ReleaseAndTokens | EXECUTED |
| lease dies first; registry dies first (two live artifacts, surviving tokens invalid, WrongRegistry for a new registry); owners destroyed first; world torn down first | Registry.Lifetime | EXECUTED |
| off-thread admission, registry release, token release refused, nothing changed | Registry.Lifetime | EXECUTED |
| quarantine (unclean cleanup: external registration/begun/re-ownership) | registry .cpp | SOURCE-ONLY (needs a registered component) |
| world/epoch/GI/binding drift between stages or before publication | facade, registry | SOURCE-ONLY (needs a callback, cvar or injection) |
| same-registry re-entry | registry .cpp | SOURCE-ONLY |
| `Reservation.Closed` after destruction starts | registry .cpp | SOURCE-ONLY |
| destroying a held token or the registry off the game thread | .cpp | NOT RUN (unsafe worker-destructor experiment) |

## Independent passes
Two read-only sub-agents reviewed the production source and the two test files (notes and what was done for each finding in `Review/independent_review_notes.txt`): no compile error was found; fixes include quarantine on a cleanup failure during admission, thread-neutral reads, one stale-token rule, tighter classification, a vacuous cross-registry check made real, registry destruction with several artifacts, stricter lifetime assertions, cross-role overlaps, InvalidInput cases and the facade refusal test. Supplemental, not an acceptance.

## Judgement calls / limits
1. The facade re-implements its small identity checks instead of an exported DD17 seam (optional delta above, not applied).
2. `WorldGone` is InvalidInput on purpose (documented): whether a destroyed world still resolves is not deterministic for the test.
3. A stale token is cleared; WrongRegistry and Refused leave it.
4. A quarantined entry is reached only on a not-clean abort or a cleanup failure during admission; it cannot be executed in a test now.
5. The tests inherit the DD15/DD16/DD17 limits: collected-name reuse is not claimed (the retries reuse destroyed uncollected objects), manifest hash and rows are caller data, transient definitions, no cold load, the game-instance `Init` creates all game-instance subsystems.
6. Every claim is a source claim until a released build: not compiled, not run.

## Slips stated
None new in this package (the baseline was saved before the files). Two edit scripts of mine aborted on an assertion before changing anything (line-wrap mismatches in DD17's header text) and one multi-heredoc shell command failed to parse earlier; nothing ran. I also caught, by re-reading after the review edits, two bugs of my own (a helper hard-coding a valid hash in the bad-hash case, and a fixture set added after the start capture) and fixed them before the final hashes.

## Next (needs Codex)
Review DD17's X-284 revision and this batch; then one serialized release for the build and the focused `OneBossFight.Binding.WorldInput`, `WorldPreparation` and `PreparationRegistry` runs, then the full suite. Any compile or run failure stops before any fix with the first failing source and logs preserved.
