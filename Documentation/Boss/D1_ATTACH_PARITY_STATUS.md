# D1 selected-route attach parity status

## Approved scope

Claude approved a test-first selected-route component bundle for `BossCore`: the legacy BossCore plan plus `RPGFootsteps`, `RPGBossMusic`, `RPGTraceGuard`, `RPGBossHud`, `RPGBossLegend`, and `RPGDamageResolver`. The same prepared-batch owner, registration, rebind, and release lifecycle must own all six. No exclusion is approved.

## Source change prepared

`RPGBossHydrationPreflight::MakeBossCorePlans` now includes all six classes after the thirteen typed plans. The five components with no authorable definition fields are explicitly marked configuration-independent rather than given fabricated manifest paths. Footsteps use the existing legacy concrete cues and boss scales (pitch 0.62, volume 1.5, range 4500, jog 200, run 420). Boss music uses the legacy phase-one cue, Starter Music fallback, and phase-two cue. Trace guard, HUD, legend, and resolver retain their native defaults, matching legacy construction.

The shared preflight consumer guard includes all six classes, so an already present class refuses before a second component can be allocated. The existing batch lease now owns them through successful registration, retag/rebind, and release. Tests record exact class-set parity with an empty exclusion list, verify the six native-only plans have no invented manifest fields, and extend preparation/cleanup expectations to the full set.

## C-842 hotfix after BUILD-220 RED

Claude rejected the first implementation after BUILD-220. The build was lead-fixed for `UE_ARRAY_COUNT`'s `size_t` comparison; the automation run then reported callback wrong-class handling, stale component-count assertions, and HUD widget creation on a controller without a local player, before a background worker access violation.

Codex hotfix: every one of the six native callbacks now uses `Cast<T>`, reports expected/actual class on mismatch, and clears `Error` on success. The expanded preflight consumer expectation is 20 (19 boss plan classes plus participant). Preparation fixtures independently enumerate all 19 boss components, and their “prior components retained” count is based on the plan count, not the stale `+13`. The fixture's only unrelated component is `USceneComponent` (`UnrelatedMarker`), so it does not collide with any managed native class; Abort and Exclusive failures were downstream of the shared stale count assertion. HUD creation now additionally requires a local player; the existing per-tick EnsureWidget call retries after a local player becomes available and skips headless controllers.

Plan-count assertions still correctly expect 19 per BossCore, two-boss teardown 38, and the 19-class attach set. Files/tests audited: `RPGBossActivationTests.cpp` (exact attach list, 38 registration/cleanup, 19 release); `RPGBossActivationWorldTests.cpp` (38 release/rollback); `RPGBossAuthoredDraftPreflightTests.cpp` (19 plans/classes/names); `RPGBossHydrationPreflightTests.cpp` (19 plans/leases/recompile/rebind, managed list corrected 14→20); `RPGBossProductionPreflightTests.cpp` (19 plans/leases); `RPGBossPreparationRegistryTests.cpp` (38 release); `RPGBossProductionPreparationTests.cpp` (19 per-boss and 38 cleanup); `RPGBossWorldPreparationTests.cpp` (19 per-boss and 38 cleanup); and `RPGBossHydrationPreparationTests.cpp` (expected list expanded 13→19, stale `+13` replaced by plan count). No unrelated gameplay “13” literals were changed.

## Verification boundary

Claude reports the C-842 hotfix rebuilt successfully in BUILD-220 and the full suite passed 462/462. The selected route includes the six legacy BossCore consumers in the 19-plan bundle. The seven A5 v4 BUILD-220+D5 driver pairs pass every driver check in both arms; component census remains route-specific evidence, not an equality assertion. The receipt/comparator outcome table and remaining A4/HUD caveats are in `Documentation/Boss/P15_A7_PARITY_SUMMARY_DRAFT.md`. This evidence does not close package, Shipping, performance, compatibility, or recovery gates.
