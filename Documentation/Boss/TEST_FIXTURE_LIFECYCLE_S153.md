# Automation-test fixture lifecycle guide (S153)

Choose the smallest fixture that exercises the contract, give every UObject an explicit owner or strong test lease, and make cleanup automatic on assertion failures and early returns. The examples below are current repository patterns, not a requirement to build a world for pure-rule tests.

## 1. World lifetime

For component/world behavior, `RPGTests::FScopedTestWorld` creates a Game `UWorld`, registers an engine world context, calls `InitializeActorsForPlay`, then destroys the context and world in its destructor (`Source/OneBossFight/Tests/RPGAutomationTests.cpp:66-85`). Put it on the test stack before creating world-owned fixtures so it outlives them.

When the feature needs a real `UGameInstance`, follow `FGameWorld` in `RPGBossActivationWorldTests.cpp:74-121`: keep the GI in `TStrongObjectPtr`, initialize it through `InitializeStandalone`, obtain its world, initialize actors, and shut down the GI before removing the world context and destroying the world. Delete copy operations on owning fixture scopes so two destructors cannot tear down the same world.

For test actors, the activation fixture's `SpawnCharacter` uses `SpawnActorDeferred`, configures the mesh before `FinishSpawning`, and returns null on each failure path (`RPGBossActivationWorldTests.cpp:110-121`). For test-only UObjects that are not reachable through a rooted owner, use `TStrongObjectPtr`; otherwise construct with the real outer that owns the object's lifetime.

## 2. UObject and fixture cleanup

Keep assets/definitions alive for the full assertion window with strong leases (for example the three `TStrongObjectPtr<URPGBossDefinition>` members in `RPGBossActivationWorldTests.cpp:351-353`). Components created with an actor as outer are actor-owned; destroy/release the fixture's actors and batch explicitly before tearing down the world when the contract under test requires observable cleanup. Prefer a scope destructor for global cleanup so `return false` cannot bypass it.

Do not let a raw UObject pointer escape the world/owner scope. If a worker operation must test thread rejection, keep the world alive until the worker has completed, and ensure the code path rejects before doing UObject work. Do not capture UObjects in fire-and-forget workers.

## 3. Global console variables

`FCatalogCvarScope` in `RPGCombatCatalogTests.cpp:333-356` is the current restoration pattern. On `Set`, save the old string value and `ECVF_SetByMask` priority before changing the CVar. In the destructor, restore in reverse order: clear the current priority bits, then set the original value with the original priority. Return early safely because the guard owns restoration. Use the same pattern whenever a test changes shared CVar state; never assume a default value or leave the test mutation behind.

## 4. Async completion before teardown

`FRPGActivationWorldInvalidTest` submits a thread-pool call and immediately calls `.Get()` on its future (`RPGBossActivationWorldTests.cpp:547-560`). This is a join point: it proves the worker result before the stack fixture can be destroyed. The case intentionally verifies that `ActivateWorld` called off the game thread returns the named thread rejection without a batch or world-state mutation.

If the feature schedules work that can outlive the test body, retain its future/handle and complete, cancel, or unregister it before fixture teardown. For callbacks that may reference actors, use weak UObject identity and marshal UObject work back to the game thread. A blocking `Get()` is appropriate for this bounded negative test; do not add an unbounded wait that can hang the automation runner.

## Source examples

- `Source/OneBossFight/Tests/RPGAutomationTests.cpp:66-85` — minimal scoped world creation/destruction.
- `Source/OneBossFight/Tests/RPGBossActivationWorldTests.cpp:74-121,351-353,547-560` — game-instance world, actor setup, strong definition leases, and joined worker.
- `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp:333-356,359-372` — CVar value/priority guard and strongly held game-instance/subsystem UObjects.
- `Source/OneBossFight/Tests/README.md:1-14` — test naming and run ownership; only the editor owner runs builds/suites.
