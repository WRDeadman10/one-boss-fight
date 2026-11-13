# Queue BD Batch 5: X21–X25 test-hook and Shipping surface

## X21 — reflected hook inventory

The named headers expose these relevant Blueprint surfaces:

| Class | Hook surface | Source boundary |
|---|---|---|
| `URPGDamageResolver` | `ResolveForTest`, `NoteOverlapForTest` are unconditional `UFUNCTION(BlueprintCallable)` declarations | `RPGDamageResolver.h:188–193`; implementation has `UE_BUILD_SHIPPING` stub branch at `.cpp:248–276` |
| `ARPGFrameworkBossCharacter` | `InitializeWithProfileForTest`, `StartCardForTest`, `StartComboForTest`, `SpawnFrameworkBossForTest` put the `UFUNCTION` macro under `WITH_EDITORONLY_DATA`; C++ declarations remain after the conditional | `RPGFrameworkBossCharacter.h:23–38`; implementations have Shipping refusal branches (`.cpp:66–86,161–190`) |
| `URPGDodgeTiming` | Three guard-counter helpers use `meta=(DevelopmentOnly)` | `RPGDodgeTiming.h:123–131`; metadata alone is not Shipping UHT/reflection evidence |
| `URPGIFrameMonitor` | diagnostics and `DebugForceOwned` have Blueprint-facing declarations | `RPGIFrameMonitor.h:45–83`; require target-specific reflection/binary inspection before claims |

This is a source declaration inventory only. It does not establish whether generated Shipping reflection tables or callable Blueprint nodes contain these methods.

## X22 — guard pattern comparison

The framework boss demonstrates the project's current conditional-`UFUNCTION` source pattern, while damage resolver test hooks leave the macro unconditional and use inert Shipping bodies. Both patterns require an actual target build/UHT or symbol inspection to prove their reflected surface. `DevelopmentOnly` is metadata, not proof of exclusion. No code change is proposed here; Lead should choose a single desired Shipping policy for test nodes before editing declarations.

## X23 — test bridge route reuse

Framework bridge implementations reject in Shipping and delegate in Development to profile resolution, explicit same-world target initialization, and the real executor (`RPGFrameworkBossCharacter.cpp:66–133,161–212`). The bridge is an explicit-card test seam, not ordinary selector/production encounter proof. DamageResolver test entry points call `Resolve` with a generated payload but are still declared as UFUNCTIONs in source. Keep declaration visibility distinct from body behavior and proof route.

## X24 — registration names in source

The source registers pure resolver policy under `OneBossFight.Combat.DamageResolver.Decide` (`Tests/RPGAutomationTests.cpp:182`) and bridge refusal checks under `OneBossFight.Framework.Runtime.LiveTestBridgeNullProfile` / `LiveTestBridgeSpawnRejectsInvalidInputs` (`Tests/RPGFrameworkRuntimeTests.cpp:46–70`). The owned-tag retry policy registers `OneBossFight.Player.OwnedTagCleanup.RetryPolicy` (`Tests/RPGOwnedTagCleanupTests.cpp:6–8`). These are source registrations, not a report that tests were run in this batch.

## X25 — Lead Shipping/UHT evidence checklist

For each named hook, Lead should capture target/configuration and engine/UHT version; exact Editor and Shipping targets; declaration preprocessor state; generated header/reflection table result; cooked Blueprint node visibility if applicable; native symbol scan with known limitations; and the relevant locked-runner/build identity. Record absent/present distinctly for UHT, binary symbol, and Blueprint node observations. Use the C-1155 task-specific runner and locks for any authorized engine/build operation; this report does not request or perform one.

## Scope

Header/source and test-registration audit only. No tests run, no code edited, and no UHT/Shipping/build/Editor/PIE/lock operation. Supporting context: `BC_X36_X40_SURFACE_LOCKS_READONLY.md`.
