# Draft notes: RPGPlayerMovesAttachWitnessTests.cpp (X-239)

Status: DRAFT only. Not in `Source`, not compiled, not run, no build or A/B restore performed. It supersedes the table in `../2B_WITNESS_PROPOSAL.md` where they differ (W2b is dropped, see below).

## X-239 concern -> where the draft handles it

| X-239 concern | handling in the draft |
|---|---|
| `FScopedTestWorld` is local to RPGAutomationTests.cpp | own RAII `FWitnessWorld` in an anonymous namespace (same CreateWorld / world context / InitializeActorsForPlay / DestroyWorld sequence), non-copyable |
| spawn return pawn is unknown during creation callbacks | the listener keeps only ordinal, class pointer, outer POINTER VALUE and a game-thread flag; `Since(mark, Pawn)` filters after `SpawnActor` returned |
| read base identity only during construction | callback reads `GetClass()` and `GetOuter()` only. Engine source: both are set in the `UObjectBase` constructor initializer list before `AddObject` runs the listeners (UObjectBase.cpp 128-135, UObjectArray.cpp 304). Nothing derived, registered or BeginPlay-dependent is called there |
| preload classes | `LoadClass<AActor>` + `FlushAsyncLoading()` before the recorder is registered and before the world exists |
| unrelated / threaded callbacks, listener cleanup | mutex in the recorder; per-record game-thread flag, any off-thread record with the pawn as outer is an error; engine listener array is NOT locked (UObjectArray.cpp 301 "@todo threading"), so add/remove happens only on the game thread after the flush; RAII `Stop()`, also from `OnUObjectArrayShutdown`; recorder declared after the world so it is removed first; truncation is an error |
| subsystem / spawn hook / pack spawn preconditions must fail explicitly | class load, class is a pawn (the world-begin loop is `TActorIterator<APawn>`), world created, `GetSubsystem<URPGPlayerMovesSubsystem>()` non-null, world not already begun, spawn non-null, pack identity via public `IsPackBoss`/`IsPackPlayer`, hook attached at least something: each is `AddError` + return false |
| name suffix absence is not duplicate proof | per-class count from `GetComponents` must be exactly 1 for every expected class, the project-component set must have exactly the expected size, and identities (pointer sets) are compared across W2/W3; names are not used |
| creation sequence + final state, not registration chronology | stated in the file header; `HasBegunPlay` / `HasActorBegunPlay` / world flag are LOGGED only. Verified in engine source that a bare world has no GameMode, so `GameMode->StartPlay()` never runs and actors never BeginPlay here (World.cpp 5429-5441) |
| keep W1 + W2 (first spawn then repeated world-begin) vs world-begin-only; hybrid / null / deferred limits | W1 spawn before the world-begin broadcast; W2 `World->BeginPlay()` on the already attached pawn (nothing created, identities equal); W3 second pawn after the broadcast gets the same sequence and leaves the first pawn untouched. A pawn that gets ONLY the world-begin trigger, hybrid, null and deferred spawns are listed in the file header as not exercised |

## Dropped from the proposal

W2b (destroy some components, run the world-begin step, expect only those re-created) would have proved that the loop really visits the pawn. Dropped: `NewObject<T>(Pawn, TEXT("RPGBossStagger"))` would reuse the name of a component still pending destruction, which the engine handles by re-constructing in place, so identities, listener notifications and GC behaviour become unreliable. That the world-begin loop visits the pawn therefore stays SOURCE reasoning, not an observation. Stated in the draft comments.

## Expected values

The expected boss (21) and player (10) creation sequences are typed from the statement order of the PREIMAGE (not derived from the new code), matching the baseline in `Step2Preparation/LEGACY_ATTACH_BASELINE_2026-10-26.json` for the boss and the preimage's nine player registrations after player footsteps. If the probe shows extra project components created inside other components, the draft is adapted and re-posted for review, not loosened silently.

## Output used by the A/B diff

Lines `RPGATTACHWITNESS|<label>|<scenario>|<kind>|<value>` (kinds RPG, FULL, STATE, CREATED, WORLDBEGUN, ACTORBEGUN) are extracted from each run's raw log (timestamps stripped) and diffed. FULL contains every object created with the pawn as outer (class paths); if FULL differs between A and B for reasons that do not involve the project's components, I will report it with the difference and not hide it behind the RPG line.

## Known risks I could not check without building

- Whether the pack Blueprint boss and player spawn in a bare world under `-nullrhi` (probe).
- Whether anything else with the pawn as outer interleaves between the project's components (FULL shows it).
- Compile errors: every engine API used was checked against the engine headers/source (listener signatures, `GetSubsystem`, `HasBegunPlay`, `FlushAsyncLoading`, `GetComponents`, `FUObjectArray::FUObjectCreateListener`), but nothing was compiled.
- Adds 2 automation tests (45 -> 47 discovered) once promoted.
