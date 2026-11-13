# Queue BE Batch 2 — default-off framework encounter selection

Date: 2026-11-10  
Status: source READY; live selected-framework encounter acceptance remains with Claude.

## Delivered

- `URPGBossEncounterDefinition` can explicitly select a native framework boss and carry its framework profile. Validation rejects a missing profile on that route and rejects a profile on the pack route.
- The new `rpg.FrameworkEncounterSelection` CVar is registered with code default `0`; framework selection is refused until it is explicitly set to `1`. No project configuration default or legacy startup setting changed.
- Selection counts exactly one locally possessed pack player and exactly one candidate boss. The framework route rejects any competing pack boss before it spawns a binding. The pack route continues to select the existing pack boss.
- A transient binding carries the profile and one participant generation. The selected framework actor's initializer checks the exact boss/player slots, reverse target slots, binding/actor world, and generation before initializing from that binding.
- Added native coverage for default-off refusal, opt-in exact participants/profile/generation, pack selection while the gate is off, and mixed framework/pack census refusal. Existing no-selection legacy startup coverage remains in the full suite.

## Validation

- `python Scripts/Tools/test_check_shipping_guards.py`: 4/4 passed.
- `python Scripts/Tools/check_doc_links.py`: rerun after documentation updates (recorded in the mailbox READY post).
- `Scripts/Editor/run_be_x06_x10_locked_build.ps1`: final run `BUILD_EXIT=0`, `SUITE_EXIT=0`, 508 started / 508 passed / 0 failed, complete; DD27j `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`; no assets; both locks released.
- Focused native test `OneBossFight.Binding.EncounterSelection.FrameworkOptInAndExactBinding`: Success in the pinned suite.
- The first compile found a missing explicit lambda capture in the new selected-binding validator. It was corrected before the successful full build above.

## Acceptance boundary

This batch proves source and native automation behavior. It does not claim a live map route, a saved encounter-definition asset, packaged behavior, or Lead acceptance. Framework selection stays opt-in and default-off; pack and no-selection legacy behavior remain the default.

Receipt: `Docs/BossCombatReview/Execution/Codex/BE_X06_X10_FRAMEWORK_SELECTION/Run_20261110_173330/`.
