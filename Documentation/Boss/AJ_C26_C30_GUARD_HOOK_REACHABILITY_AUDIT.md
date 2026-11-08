# AJ-C26–C30 — guard-contact hook reachability audit

Date: 2026-11-07  
Trigger: C-1004 / AJ-C21–C25  
Status: Static audit complete; no runtime or asset inspection.

## Findings

1. A repository-wide source search finds two `NotifySuccessfulGuardContact()` call sites, both in `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` (direct attack window near line 293 and grab damage near line 415). Both require an accepted resolved hit classified as `Guarded`; `Parried` follows a separate branch.
2. `URPGFrameworkMoveExecutor` is a component on `ARPGFrameworkBossCharacter` (`RPGFrameworkBossCharacter.h:16,66`; created in its constructor at `.cpp:58`). The project describes the arena Ember Warden as the re-skinned pack great-sword boss (`BP_ExampleGreatSwordBoss_C`), but source inspection does not prove that its Blueprint parent carries the framework component or that its pack attack route reaches either notifier call site.
3. The existing guard evidence audit already states this boundary: the hook census does not prove every legacy/pack damage route reaches it (`AC_C11_C15_GUARD_COUNTER_EVIDENCE.md`, AC-C12). The ER input dump maps `IA_Block` to `Gamepad_LeftShoulder`; the new probe also requires the ER input context to report active before starting the test.
4. Therefore, “no successful guarded-contact log” from the new script is inconclusive about the guard-counter logic. It may mean no block contact occurred, or the live arena attack route does not invoke the framework hook. A visible `RPGFrameworkMoveExecutor` component narrows the question but still does not prove contact.

## Probe/handoff update

`pie_er_guard_counter.py` now logs `framework_executor_present` during setup. It still runs only with real L1/R2 input and the live boss AI, waits for the exact notifier diagnostic, and requires the source's `guard counter accepted` diagnostic before the Lead can claim counter-window acceptance. No C++ hook, asset, or runtime behavior was changed.

Lead should preserve the full log for each route. If the component is absent or the guard diagnostic never appears, retain the result as **hook/contact not observed** and stop short of calling it a counter defect; owner hand test or a separately authorized framework-boss fixture is then needed. A confirmed source guard followed by the counter-accepted log is the required evidence chain.

## Validation boundary

Static search and source cross-reference only. No Unreal/Editor/PIE/build/test was run, and no Blueprint class-parent or live component inspection was performed.
