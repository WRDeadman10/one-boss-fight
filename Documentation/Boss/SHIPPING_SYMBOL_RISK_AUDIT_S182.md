# Shipping symbol risk scan (S182)

Static source-only review of test-named declarations in production headers. This identifies symbols that appear available to Shipping compilation/reflection; it does not establish presence in a built binary or packaged runtime.

## Suspected Shipping-visible test hooks

These declarations are outside visible `#if !UE_BUILD_SHIPPING` / `WITH_DEV_AUTOMATION_TESTS` guards. Their names and nearby comments identify them as test drivers, while `UFUNCTION` makes the reflected entries directly inspectable/callable in Blueprint where applicable:

- `Source/OneBossFight/Player/RPGBossEncounter.h:71,75` — `HoldForTest` and `ResetForTest` are public BlueprintCallable methods; both declarations are unguarded. `Wake` is explicitly described as tests and scripted encounters at line 78, so its exposure may be intentional and is not counted as a `ForTest` leak.
- `Source/OneBossFight/Player/RPGBuildLoadout.h:127,139,143,147,151,155` — six public BlueprintPure/BlueprintCallable `ForTest` helpers are unguarded.
- `Source/OneBossFight/Player/RPGHitIntake.h:78,82,86,131` — three hit-injection hooks and the bleed override are unguarded BlueprintCallable methods.
- `Source/OneBossFight/Player/RPGLegend.h:196-199` — four unguarded BlueprintCallable test effect triggers. Their `.cpp` bodies contain `#if UE_BUILD_SHIPPING` behavior checks, but that does not remove the declarations/reflected functions or prove the symbols are stripped.
- `Source/OneBossFight/Player/RPGDamageResolver.h:178-182` — unguarded BlueprintCallable `ResolveForTest` and `NoteOverlapForTest` declarations.
- `Source/OneBossFight/Player/RPGBossDeath.h:140,143`, `RPGBossStagger.h:94,139,142,145,148,203,207`, and `RPGSwingTracker.h:87,103,108,121` — unguarded test setters/drivers; some are reflected and several inline setters mutate runtime state.
- Other unguarded test-named declarations include `RPGBossMusic.h:94`, `RPGAttackTracker.h:130`, `RPGBossBleed.h:70`, `RPGBossCloseClipSwap.h:57,61`, `RPGBossLowSweep.h:59`, `RPGBossPosture.h:73`, `RPGBossShockwave.h:61`, `RPGBuildSelect.h:60,63,66`, and `RPGFlaskHud.h:59`.

The existing guarded exceptions found during the scan are `RPGBossHydrationPreparation.h:143` and `RPGBossPreparationRegistry.h:106`, both under `WITH_DEV_AUTOMATION_TESTS`. The scan searched production headers outside `Tests` for `ForTest(` and checked surrounding preprocessor nesting; it did not inspect generated headers, linker maps, cooked packages, or a Shipping build.

## Disposition and limit

Acceptance is met as a risk inventory: the cited unguarded declarations are suspected Shipping-visible test hooks, not proven binary leaks. The `RPGLegend` Shipping branches are runtime no-op/refusal behavior, not compile-time exclusion. A follow-up source-guard or API-surface decision needs Lead review because some helpers may be intentionally callable by project automation/Blueprints. No source changes, build, tests, Editor, or runtime were performed.
