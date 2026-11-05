# Automation fixture isolation audit (Queue D82)

Read-only inventory of test world/object ownership and process-global state handling. No test, build, or Editor run was performed.

## World and object ownership

- A source scan finds 28 test translation units calling `UWorld::CreateWorld`. Twenty-six register engine world contexts and destroy those contexts during teardown. The new executor harness follows that paired pattern.
- `RPGBossStaggerClusterAdaptersTests.cpp` is the context-free single-world exception: its local fixture destroys its world; spawned actors are world-owned and the standalone component objects use `TStrongObjectPtr`.
- `RPGEncounterBindingTests.cpp` is the other exception: it creates three transient worlds without engine contexts. Its `ON_SCOPE_EXIT` destroys the live A/B worlds; the test explicitly destroys and nulls A before recreating it, so the final recreated A is also covered by that scope exit. Assertions/setup failures return through the scope guard.
- The other test fixtures generally pair context and world teardown in local fixture destructors. `RPGBossPreparationRegistryTests.cpp` has multiple explicit world/context lifetimes in one source file, so its destroy-call count exceeds its first create-context count.
- Actor fixtures are spawned into their owning test world. Standalone UObject fixtures are commonly held by `TStrongObjectPtr`; temporary test data uses local values/shared pointers. The source scan found no assignment to `GWorld` in test sources.

## Shared process state

- `RPGCombatCatalogTests.cpp` uses `FCatalogCvarScope`, which saves each CVar value and SetBy flags and restores them in reverse order from its destructor.
- `RPGBossExecutorHarnessTests.cpp` now uses an equivalent scoped CVar guard for `rpg.BossProofSuppressMontageEnd`, including restoration of the original value and SetBy flags on early return.
- Other CVar references found by the scan are reads/precondition checks. `RPGBossActivationWorldTests.cpp` temporarily clears the fixture world's GameInstance and restores it before assertions; `RPGBossWorldInputCompilerTests.cpp` owns its synthetic GameInstance and detaches/shuts it down during fixture teardown.
- No test-source write to a process-global world pointer or unscoped CVar assignment was found in the reviewed matches. Static source search cannot prove teardown after process crashes, engine-level object/GC behavior, or mutations hidden behind indirect helper calls.

## Scope and disposition

This is a source inventory rather than runtime proof that every destructor runs under every failure mode. The context-free fixtures are explicit and locally owned; the main robustness gap is that the activation-world GameInstance control restoration is manual rather than scope-guarded, although the inspected test has no early return between clearing and restoring it. No production or existing test code was changed for D82.
