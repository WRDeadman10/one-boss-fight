# 2b runtime witness: concrete delta proposal (NOT implemented, NOT run; needs Codex diff review first)

Order: X-238 "WITNESS CONCRETE DELTA". Everything below is a proposal. Nothing here changed any file except this document.

## What the engine source says (read just now, UE 5.5.4, not assumed)

| fact | source | consequence for the witness |
|---|---|---|
| `UWorld::SpawnActor` calls `Actor->PostSpawnInitialize(...)` and only afterwards `OnActorSpawned.Broadcast(Actor)` | `LevelActor.cpp` 733, 750 | the spawn-trigger `Attach` runs AFTER construction, and after the actor's `BeginPlay` when the world has begun play (not when it has not, and not for a deferred spawn) |
| `UWorld::BeginPlay` runs every world subsystem's `OnWorldBeginPlay` (line 5430) BEFORE `GameMode->StartPlay()` (5436) | `World.cpp` | the world-begin trigger `Attach` runs on placed pawns BEFORE their `BeginPlay` |
| so the two triggers have genuinely different chronology relative to actor `BeginPlay` | both | a witness must exercise each trigger for real, not by calling the private `Attach` |

Component-array order alone is not accepted as chronology (X-238): this proposal does not rely on it.

## Observation: creation order, not array order

A test-only `FUObjectCreateListener` (registered with `GUObjectArray.AddUObjectCreateListener`, removed in the test's cleanup) records every UObject created while a scenario runs, in true creation order, keeping only objects whose outer is the pawn under test (plus their class). Because every registration in `Attach` is `NewObject<URPGx>(Pawn, ...)` followed immediately by `RegisterComponent()`, the creation sequence is the statement sequence; after the scenario, `HasBegunPlay`/`IsRegistered` of each component and the unique names (`RPG...` with no numeric suffix = no duplicate) are read as final state. Components created internally (`URPGBossDeath::Attach`, `URPGDamageResolver::FindOrAdd`) are `NewObject`s on the pawn too, so the listener sees them. Everything else created on that outer is recorded as well, so any interleaving shows. Caveat I accept up front: the listener is called during allocation, so only class and outer are read from it (no component members).

No production API, no debug hook, no change to `RPGPlayerMovesSubsystem.*`, no world-begin rebroadcast. The listener lives in the test file.

## Concrete delta (one new file, no production file)

`Source/OneBossFight/Tests/RPGPlayerMovesAttachWitnessTests.cpp` (new), using the existing `RPGTests::FScopedTestWorld` (`UWorld::CreateWorld(EWorldType::Game)` + `InitializeActorsForPlay`, as in `RPGAutomationTests.cpp` 60-80) and the real pack classes by path:
`/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C` and `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C` (both strings are already used in the repo).

| scenario | route (genuine, public) | records |
|---|---|---|
| W1 spawn trigger, world not begun | `World->SpawnActor` before `World->BeginPlay()` | creation sequence, final state, then after `World->BeginPlay()` that the world-begin loop added nothing |
| W2 world-begin trigger on an already attached pawn | `World->BeginPlay()` after W1: the subsystem's world-begin loop calls `Attach` on the pawn the spawn trigger already attached (the subsystem's spawn handler exists from world init, so every pawn spawned before `BeginPlay` gets both triggers) | no new objects created on the pawn, same component identities and names (idempotence of the second trigger) |
| W3 spawn trigger, world begun | `World->BeginPlay()` first, then `SpawnActor` | creation sequence; components registered after actor `BeginPlay` have `HasBegunPlay` true |
| W4 repeatability | a second `SpawnActor` of the same class in the same world | the two pawns' creation sequences equal each other |

Not covered by any scenario: a pawn that receives ONLY the world-begin trigger (there is no public way to have a pawn exist before the subsystem's spawn handler does), and a deferred-construction spawn. Both are limits, not claims.

Each scenario for the boss class and for the player class. Expected sequence is NOT regenerated from the new code: it is compared against the same test run on the preimage source (below).

## A/B on identical test code (the main evidence)

The new test file uses only public engine behavior, so it compiles and runs against BOTH sources:

1. Restore the two preimages by copying `DD2b/preimages/*` over the two source files (copy, no git checkout), build, run the new tests, keep raw log and the recorded sequences. Binary hash recorded.
2. Re-apply the accepted new files (sha 17bc29c9... / 8bc1a655...), build, run the same tests, keep raw log.
3. Compare the two recorded creation sequences and final states byte for byte; the diff is the verdict. Both source pins and both binary hashes are recorded and the final working tree is verified to equal the accepted pins again.

That is two builds (about 30 s each) and two automation runs (about 1 min each). The standing existing 45 tests run in the same two runs as a regression check.

## Honest limits and risks

- Unverified: that `FScopedTestWorld` (CreateWorld + InitializeActorsForPlay) creates `URPGPlayerMovesSubsystem` and installs its spawn handler. The probe step must show it (the subsystem exists on the world and a spawned pack pawn receives components) before any scenario is trusted.
- Unverified: that the pack Blueprint boss and player spawn cleanly in a bare transient `Game` world under `-nullrhi` (their own BeginPlay logic may log errors or bail). Step 0 is a probe run of the test with no assertions that only logs what happens; if the pack classes cannot be spawned that way I stop and report instead of changing scope. Possible fallback (needs your release): the same test body run in the existing editor PIE harness, which this order does not release.
- This does not exercise the hybrid (player AND boss) class or a null pawn: that needs a class that has both names in its parent chain, which the pack Blueprints do not provide and a native test class cannot be given without a UHT type in a header. Hybrid and null remain SOURCE reasoning (byte-level mapping, 2B_DELIVERY.md), explicitly not exercised.
- The test files are compiled into the main module in all configurations like the existing tests; I will guard the new file the same way the neighbours are guarded.
- No claim that registration chronology equals creation chronology beyond what the statement text shows; the claim is limited to creation order, final registered state, names and duplicates.

## Not requested

No PIE, gate, package, content, pack or driver change. No generic reflection. No change to the helper or the witness baseline.
