# Queue H H041–H044 — cook, package and startup-cost audit

**Static source/config audit and run protocol only. No assets cooked, package built, or performance measurement made.**

## H041 — dependency and cook map

The selected definition has soft object references to two `URPGBossDefinition` assets (`Source/OneBossFight/Player/RPGBossEncounterDefinition.h:24-25`). Those definitions in turn carry a soft skeleton and animation list (`RPGEncounterBinding.h:293-317`); other config records include animation, mesh, sound, Niagara and ability class references (for example `:92,104-156,221-250`). The startup selection route calls `LoadSynchronous` for the two definitions (`RPGEncounterSelectionSubsystem.cpp:110-111`); the production definition compiler also synchronously loads declared skeleton/animation dependencies (`RPGBossWorldInputCompiler.h` contract comments).

`Config/DefaultGame.ini:19-28` always cooks `/Game/OneBossFight/Data`, `/Boss01`, `/Levels`, and related project folders; lines 30-46 name several pack folders used by current configs. This is a directory inclusion rule, not proof that a particular asset exists, its soft-reference dependency graph is complete, or a packaged runtime load succeeds. The G044 script refuses until typed boss/player definition assets and a canonical manifest receipt exist (`Scripts/Editor/create_g044_encounter_definition.py:45-70`). The current repository has no such saved `URPGBossDefinition` assets per `G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md:8`; thus there is no authored root asset graph to certify as cooked.

Required cook evidence after prerequisites exist: inventory the root encounter asset and all referenced definition/skeleton/animation/mesh/ability/effect/sound packages; run the project's cook/package; verify each expected package is present in the cook manifest and loadable in the target binary; capture missing soft-reference warnings and exact content hash. Do not infer inclusion solely from `DirectoriesToAlwaysCook`.

## H042 — offline cook-gap fixture disposition

**BLOCKED / no fixture added.** The audit found missing authoring prerequisites (definition assets and manifest receipt), not a verified defect in an existing cook-plan/manifest implementation. An offline test that merely asserts today's deliberate G044 refusal would not prove a cook gap and risks treating absence of authored content as a packaging bug. Resume only when a concrete manifest/cook-plan defect is identified from a real package or authoritative cook manifest.

## H043 — fresh packaged smoke protocol

Protocol is prepared, but a Shipping data-path run is **blocked** by the current opt-in mechanism. `rpg.EncounterDefinition` is compiled only under `#if !UE_BUILD_SHIPPING` (`RPGEncounterSelectionSubsystem.cpp`); production default selection is owner-gated, and no approved Shipping selection provider exists. Do not add a default or Shipping CVar to make the test pass.

When a Shipping-safe selector is approved, create independent fresh package runs with exact binary SHA-256, platform/config, content/cook manifest hash, map, settings, seed, driver/input identity, and logs. First run a negative control with selection absent and prove no data route; then a selected definition run with exact asset/manifest identity and either a stable pre-activation refusal or success. Assert the Shipping binary has no debug CVar, no unintended legacy boss attach on selected failure, no fallback, and a clean terminal result. Keep both raw logs, receipts and cook manifest. If the selected success cannot be selected without debug mechanisms, report BLOCKED rather than substituting Development evidence.

## H044 — source-derived startup cost and memory ownership

Source establishes one-time startup work, not a measured time or byte budget:

- actor census is O(number of current `APawn`s), performed once during selected world startup (`RPGEncounterSelectionSubsystem.cpp:88-105`);
- two typed definition soft references are synchronously loaded before activation (`:110-111`); downstream compile loads declared skeletons/animations on the game thread (`RPGBossWorldInputCompiler.h` contract);
- one transient `ARPGEncounterBinding` owns copied slot/actor/definition references; the GameInstance store keeps the selected definition, not pawn pointers (`RPGEncounterSelectionSubsystem.h:13-38`);
- activation owns a batch lease and later release/teardown runs on the game thread (`RPGBossActivation.cpp`); unresolved cleanup can retain artifacts rather than destroy unsafely.

Measure in Claude's packaged run: time from world startup callback entry to activation outcome; count and size of synchronously loaded packages attributable to selected definitions; before/after resident memory using the same platform tool/window; transient binding and owned registered component counts; release latency and retained object count after teardown. Report repeated cold and warm starts separately, exact binary/content identity and sample distribution. No numeric performance budget is assigned here because there is no observed baseline or owner-approved limit for this new path.
